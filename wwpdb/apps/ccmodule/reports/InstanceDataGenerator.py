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
__author__ = "Zukang Feng"
__email__ = "zfeng@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import os
import sys
import multiprocessing
import traceback

from wwpdb.apps.ccmodule.reports.ChemCompAlignImageGenerator import ChemCompAlignImageGenerator
from wwpdb.apps.ccmodule.reports.ChemCompReports import ChemCompReport
#


class InstanceDataGenerator(object):
    """Utility Class for generating report material that will support 2D,3D renderings.
    """
    def __init__(self, reqObj=None, dataStore=None, verbose=False, log=sys.stderr):
        self.__reqObj = reqObj
        self.__ccAssignDataStore = dataStore
        self.__verbose = verbose
        self.__lfh = log
        #
        # Leave the following call due to potential side effects.
        self.__sObj = self.__reqObj.getSessionObj()  # pylint: disable=unused-private-member
        # self.__sessionPath = self.__sObj.getPath()
        #

    def run(self):
        # depId = str(self.__reqObj.getValue("identifier")).upper()
        instIdLst = self.__ccAssignDataStore.getAuthAssignmentKeys()
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
            rrG = RefReportGenerator(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            self.__runMultiprocessing(uniqList, rrG, 'runReportGenerator')
        #
        irG = InstReportGenerator(reqObj=self.__reqObj, dataStore=self.__ccAssignDataStore, verbose=self.__verbose, log=self.__lfh)
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
        workers = [MultiProcWorker(processLabel=str(i + 1), taskQueue=taskQueue, resultQueue=resultQueue,
                                   workerFunc=workerFunc, log=self.__lfh, verbose=self.__verbose) for i in range(numProc)]
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
            _msg = resultQueue.get()  # noqa: F841
        #
        try:
            for w in workers:
                w.terminate()
                w.join(1)
            #
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                traceback.print_exc(file=self.__lfh)
            #
        #


class MultiProcWorker(multiprocessing.Process):
    """
    """
    def __init__(self, processLabel='', taskQueue=None, resultQueue=None, workerFunc=None, log=sys.stderr, verbose=False):  # pylint: disable=unused-argument
        multiprocessing.Process.__init__(self)
        self.__processLabel = processLabel
        self.__taskQueue = taskQueue
        self.__resultQueue = resultQueue
        self.__workerFunc = workerFunc
        # self.__lfh = log
        # self.__verbose = verbose

    def run(self):
        while True:
            nextList = self.__taskQueue.get()
            if nextList is None:
                break
            #
            self.__workerFunc(dataList=nextList, processLabel=self.__processLabel)
            self.__resultQueue.put("OK")
        #


class RefReportGenerator(object):
    """
    """
    def __init__(self, reqObj=None, verbose=False, log=sys.stderr):
        self.__reqObj = reqObj
        self.__verbose = verbose
        self.__lfh = log
        #

    def runReportGenerator(self, dataList=None, processLabel=None):  # pylint: disable=unused-argument
        ccReport = ChemCompReport(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        for ccId in dataList:
            ccReport.setDefinitionId(definitionId=ccId.lower())
            ccReport.doReport(type='ref', ccAssignPthMdfier=ccId)
        #


class InstReportGenerator(object):
    """
    """
    def __init__(self, reqObj=None, dataStore=None, verbose=False, log=sys.stderr):
        self.__ccAssignDataStore = dataStore
        self.__reqObj = reqObj
        self.__verbose = verbose
        self.__lfh = log
        #
        self.__sObj = self.__reqObj.getSessionObj()
        self.__sessionPath = self.__sObj.getPath()
        #

    def runReportGenerator(self, dataList=None, processLabel=None):  # pylint: disable=unused-argument
        for instId in dataList:
            chemCompFilePathAbs = os.path.join(self.__sessionPath, 'assign', instId, instId + '.cif')
            instChemCompRprt = ChemCompReport(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            instChemCompRprt.setFilePath(chemCompFilePathAbs, instId)
            instChemCompRprt.doReport(type='exp', ccAssignPthMdfier=instId)
            #
            mtchL = self.__ccAssignDataStore.getTopHitsList(instId)
            HitList = []
            for tupL in mtchL:
                HitList.append(tupL[0])
            #
            ccaig = ChemCompAlignImageGenerator(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            ccaig.generateImages(instId=instId, instFile=chemCompFilePathAbs, hitList=HitList)
        #
