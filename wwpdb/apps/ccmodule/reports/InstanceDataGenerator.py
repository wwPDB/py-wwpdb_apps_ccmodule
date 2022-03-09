##
# File:  InstanceDataGenerator.py
# Date:  27-feb-2015
##
"""
Utility Class for generating report material that will support 2D,3D renderings.

This software was developed as part of the World Wide Protein Data Bank
Common Deposition and Annotation System Project

Copyright (c) 2012 wwPDB

This software is provided under a Creative Commons Attribution 3.0 Unported
License described at http://creativecommons.org/licenses/by/3.0/.

"""
__docformat__ = "restructuredtext en"
__author__    = "Zukang Feng"
__email__     = "zfeng@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.01"

import os, sys, multiprocessing, traceback

from wwpdb.apps.ccmodule.reports.ChemCompAlignImageGenerator import ChemCompAlignImageGenerator
from wwpdb.apps.ccmodule.reports.ChemCompReports             import ChemCompReport
from wwpdb.io.locator.PathInfo                               import PathInfo
#



class InstanceDataGenerator(object):
    """Utility Class for generating report material that will support 2D,3D renderings.
    """
    def __init__(self, reqObj=None, dataStore=None, verbose=False, log=sys.stderr):
        self.__reqObj=reqObj
        self.__ccAssignDataStore=dataStore
        self.__verbose=verbose
        self.__lfh=log
        #
        self.__sObj=self.__reqObj.getSessionObj()
        self.__sessionPath=self.__sObj.getPath()
        #

    def run(self):
        depId = str(self.__reqObj.getValue("identifier")).upper()
        instIdLst = self.__ccAssignDataStore.getAuthAssignmentKeys()
        context = self.__getContext()
        self.__lfh.write("instIdLst=%d\n" % len(instIdLst))
        if len(instIdLst) == 0:
            return
        #
        refList = []
        for instId in instIdLst:
            mtchL = self.__ccAssignDataStore.getTopHitsList(instId)
            for tupL in mtchL:
                refList.append(tupL[0])
            #
        #
        if len(refList) > 0:
            uniqList = sorted(set(refList))
            self.__lfh.write("uniqList=%d\n" % len(uniqList))
            rrG = RefReportGenerator(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh,context=context)
            self.__runMultiprocessing(uniqList, rrG, 'runReportGenerator')
        #
        irG = InstReportGenerator(reqObj=self.__reqObj,dataStore=self.__ccAssignDataStore,verbose=self.__verbose,log=self.__lfh,context=context)
        self.__runMultiprocessing(instIdLst, irG, 'runReportGenerator')

    def __runMultiprocessing(self, dataList, workerObj, workerMethod):
        """
        """
        numProc = int(multiprocessing.cpu_count() / 2)
        if numProc == 0:
            numProc = 1
        #
        if numProc > len(dataList):
            numProc = len(dataList)
        #
        subLists = [dataList[i::numProc] for i in range(numProc)]
        workerFunc = getattr(workerObj, workerMethod)
        #
        taskQueue = multiprocessing.Queue()
        resultQueue = multiprocessing.Queue()
        #
        workers = [ MultiProcWorker(processLabel=str(i+1), taskQueue=taskQueue, resultQueue=resultQueue, \
                    workerFunc=workerFunc, log=self.__lfh, verbose=self.__verbose) for i in range(numProc) ]
        for w in workers:
            w.start()
        #
        for subList in subLists:
            taskQueue.put(subList)
        #
        for i in range(numProc):
            taskQueue.put(None)
        #
        for i in range(len(subLists)):
            msg = resultQueue.get()
        #
        try:
            for w in workers:
                w.terminate()
                w.join(1)
            #
        except:
            if self.__verbose:
                traceback.print_exc(file=self.__lfh)
            #
        #
    
    def __getContext(self):
        filesource = self.__reqObj.getValue('filesource')
        depid = self.__reqObj.getValue('identifier')

        if depid == 'TMP_ID':
            return 'standalone'
        
        if filesource == 'deposit':
            return 'deposition'
        
        if filesource in ['archive', 'wf-archive', 'wf_archive', 'wf-instance', 'wf_instance']:
            return 'workflow'
        
        # in case we can't find out the context (as it happens with the standalone
        # ligmod) we fall back to get model files from the sessions path
        return 'unknown'

class MultiProcWorker(multiprocessing.Process):
    """
    """
    def __init__(self, processLabel='', taskQueue=None, resultQueue=None, workerFunc=None, log=sys.stderr, verbose=False):
        multiprocessing.Process.__init__(self)
        self.__processLabel = processLabel
        self.__taskQueue = taskQueue
        self.__resultQueue = resultQueue
        self.__workerFunc = workerFunc
        self.__lfh=log
        self.__verbose=verbose

    def run(self):
        while True:
            nextList=self.__taskQueue.get()
            if nextList is None:
                break
            #
            try:
                # not catching possible exceptions here was leading to the process
                # being deadlocked, don't know why
                self.__workerFunc(dataList=nextList, processLabel=self.__processLabel)
            except:
                self.__lfh.write("ERROR - Exception when running function %s with args %s\n" % (self.__workerFunc.__name__, nextList))
                traceback.print_exc(file=self.__lfh)
            self.__resultQueue.put("OK")
        #

class RefReportGenerator(object):
    """
    """
    def __init__(self, reqObj=None, verbose=False, log=sys.stderr, context=None):
        self.__reqObj=reqObj
        self.__verbose=verbose
        self.__lfh=log
        self.__context=context
        #

    def runReportGenerator(self, dataList=None, processLabel=None):
        self.__lfh.write("enter RefReportGenerator.runReportGenerator, context %s\n" % self.__context)
        ccReport = ChemCompReport(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
        for ccId in dataList:
            ccReport.setDefinitionId(definitionId=ccId.lower())
            ccReport.doReport(type='ref',ccAssignPthMdfier=ccId)
        #

class InstReportGenerator(object):
    """
    """
    def __init__(self, reqObj=None, dataStore=None, verbose=False, log=sys.stderr, context=None):
        self.__ccAssignDataStore=dataStore
        self.__reqObj=reqObj
        self.__verbose=verbose
        self.__lfh=log
        self.__context=context
        #
        self.__sObj=self.__reqObj.getSessionObj()
        self.__sessionPath=self.__sObj.getPath()
        #

    def runReportGenerator(self, dataList=None, processLabel=None):
        self.__lfh.write("enter InstReportGenerator.runReportGenerator, context %s\n" % self.__context)
        for instId in dataList:
            if self.__context == 'workflow':
                instancePath = PathInfo().getInstancePath(self.__reqObj.getValue('identifier'), self.__reqObj.getValue('instance'))
                chemCompFilePathAbs = os.path.join(instancePath,'assign',instId,instId+'.cif')
            else:
                chemCompFilePathAbs = os.path.join(self.__sessionPath,'assign',instId,instId+'.cif')

            instChemCompRprt=ChemCompReport(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
            instChemCompRprt.setFilePath(chemCompFilePathAbs,instId)
            instChemCompRprt.doReport(type='exp',ccAssignPthMdfier=instId)
            #
            mtchL = self.__ccAssignDataStore.getTopHitsList(instId)
            HitList = []
            for tupL in mtchL:
                HitList.append(tupL[0])
            #
            ccaig = ChemCompAlignImageGenerator(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)

            isWorkflow = self.__context == 'workflow'
            ccaig.generateImages(instId=instId, instFile=chemCompFilePathAbs, hitList=HitList, isWorkflow=isWorkflow)
        #

