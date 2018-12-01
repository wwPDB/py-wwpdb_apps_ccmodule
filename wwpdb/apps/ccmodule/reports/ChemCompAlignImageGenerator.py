##
# File:  ChemCompAlignImageGenerator.py
# Date:  31-Oct-2014
##
"""
Utility Class for generating aligned ligand images

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

import os, sys, time, string, traceback, signal, datetime

from subprocess                       import call,Popen,PIPE
from wwpdb.utils.oe_util.oedepict.OeDepict        import OeDepict
from wwpdb.utils.oe_util.build.OeChemCompIoUtils  import OeChemCompIoUtils
from wwpdb.utils.config.ConfigInfo      import ConfigInfo
#

class ChemCompAlignImageGenerator(object):
    """Utility Class for generating aligned ligand images
    """
    def __init__(self, reqObj=None, verbose=False, log=sys.stderr):
        self.__reqObj=reqObj
        self.__verbose=verbose
        self.__lfh=log
        #
        self.__sObj=self.__reqObj.getSessionObj()
        self.__sessionPath=self.__sObj.getPath()
        #
        self.__siteId = str(self.__reqObj.getValue("WWPDB_SITE_ID"))
        self.__cI = ConfigInfo(self.__siteId)
        #

    def generateImages(self, instId=None, instFile=None, hitList=[]):
        if (not instId) or (not instFile):
            return
        #
        self.__imagePath = os.path.join(self.__sessionPath, 'assign', instId, 'image')
        if not os.access(self.__imagePath, os.F_OK):
            try:
                os.makedirs(self.__imagePath)
            except:
                return
            #
        #
        foundList = []
        imageFile = os.path.join(self.__imagePath, 'image.txt')
        ofh = open(imageFile, 'w')
        ofh.write(instId + ' ' + instFile + '\n')
        for id in hitList:
            refFile = os.path.join(self.__cI.get('SITE_CC_CVS_PATH'), id[0], id, id + '.cif')
            if not os.access(refFile, os.F_OK):
                continue
            #
            ofh.write(id + ' ' + refFile + '\n')
            #
            list = []
            list.append(id);
            list.append(refFile);
            foundList.append(list)
        #
        ofh.close()
        #
        if foundList:
            cmdfile = os.path.join(self.__imagePath, 'timeoutscript.csh')
            ofh=open(cmdfile, 'w')
            ofh.write('#!/bin/tcsh -f\n')
            ofh.write('#\n')
            envdict = self.__reqObj.getRawValue("script_env")
            if not envdict:
                envdict = {}
            for param in envdict:
                ofh.write('setenv ' + param + ' ' + envdict[param] + '\n')
            #
            #ofh.write('source ' + self.__cI.get('SITE_DEPLOY_PATH') + '/scripts/env/runtime-environment.csh\n')
            ofh.write('cd ' + self.__imagePath + '\n')
            ofh.write('python -m wwpdb.apps.ccmodule.reports.ChemCompBigAlignImages image.txt\n')
            ofh.write('#\n')
            ofh.close()
            st = os.stat(cmdfile)
            os.chmod(cmdfile, 0o777)
            #
            logfile = os.path.join(self.__imagePath, 'timeoutscript.log')
            returnCode = self.__runTimeout(cmdFile=cmdfile, logFile=logfile)
            if returnCode == 0:
                FounImage = True
                imageFile = os.path.join(self.__imagePath, instId + '.svg')
                if not os.access(imageFile, os.F_OK):
                    FounImage = False
                #
                for id in hitList:
                    imageFile = os.path.join(self.__imagePath, id  + '.svg')
                    if not os.access(imageFile, os.F_OK):
                        FounImage = False
                    #
                #
                if FounImage:
                    return
                #
            #
        #
        self.__generateSingleImage(Id=instId, FileName=instFile)
        self.__generateSingleImage(Id=instId, FileName=instFile, size=1000, labelAtomName=True, suffix='_Big')
        if foundList:
            for list in foundList:
                self.__generateSingleImage(Id=list[0], FileName=list[1])
                self.__generateSingleImage(Id=list[0], FileName=list[1], size=1000, labelAtomName=True, suffix='_Big')
                #
            #
        #

    def __runTimeout(self, cmdFile=None, logFile=None, timeout=10):
        """ Execute the command as a subprocess with a timeout.
        """
        className = self.__class__.__name__
        methodName = sys._getframe().f_code.co_name
        self.__lfh.write("+++%s.%s() -- STARTING with time out set at %d (seconds)\n" %(className, methodName, timeout) )
        #
        start = datetime.datetime.now()
        try:
            process = Popen(cmdFile, stdout=PIPE, stderr=PIPE, shell=False, close_fds=True, preexec_fn=os.setsid)
            while process.poll() == None:
                time.sleep(0.1)
                now = datetime.datetime.now()
                if (now - start).seconds> timeout:
                    os.killpg(process.pid, signal.SIGKILL)
                    os.waitpid(-1, os.WNOHANG)
                    self.__lfh.write("+++%s.%s() -- Execution terminated by timeout %d (seconds)\n" %(className, methodName, timeout) )
                    if logFile is not None:
                        ofh=open(logFile,'a')
                        ofh.write("+++%s.%s() -- Execution terminated by timeout %d (seconds)\n" %(className, methodName, timeout) )
                        ofh.close()
                    #
                    return None
                #
            #
        except:
            traceback.print_exc(file=self.__lfh)
        #
        output = process.communicate()
        self.__lfh.write("+++%s.%s() -- completed with stdout data %r\n" %(className, methodName, output[0]) )
        self.__lfh.write("+++%s.%s() -- completed with stderr data %r\n" %(className, methodName, output[1]) )
        self.__lfh.write("+++%s.%s() -- completed with return code %r\n" %(className, methodName, process.returncode) )
        return process.returncode

    def __generateSingleImage(self, Id=None, FileName=None, size=300, labelAtomName=False, suffix=''):
        try:
            oeU = OeChemCompIoUtils(verbose=self.__verbose, log=self.__lfh)
            oemList = oeU.getFromPathList([FileName], use3D=True, coordType='model')
            oedInputTupl = (Id, oemList[0], "")
            oed = OeDepict(verbose=self.__verbose, log=self.__lfh)
            oed.setMolTitleList([oedInputTupl])
            oed.setDisplayOptions(imageSizeX=size, imageSizeY=size, labelAtomName=labelAtomName, labelAtomCIPStereo=True, 
                                  labelAtomIndex=False, labelBondIndex=False,  highlightStyleFit='ballAndStickInverse', 
                                  bondDisplayWidth=1.0)
            oed.setGridOptions(rows=1, cols=1, cellBorders=False)
            oed.prepare()
            imgPth = os.path.join(self.__imagePath, Id + suffix + '.svg')
            oed.write(imgPth)
        except:
            traceback.print_exc(file=self.__lfh)
        #
