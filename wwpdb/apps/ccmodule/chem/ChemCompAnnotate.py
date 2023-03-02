##
# File:  ChemCompAnnotate.py
# Date:  14-Aug-2010
# Updates:
# 14-Aug-2010 jdw - Refactor -
#
##
"""
Annotation functions -
"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import os
import sys
import shutil


from wwpdb.apps.ccmodule.utils.ChemCompConfig import ChemCompConfig


class ChemCompAnnotate(object):
    """Chemical component annotation operations -

    """
    def __init__(self, reqObj, verbose=False, log=sys.stderr):
        """Chemical component annotation operations -


         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        self.__verbose = verbose
        self.__lfh = log
        # self.__debug = True
        #
        self.__reqObj = reqObj
        #
        self.__sObj = self.__reqObj.getSessionObj()
        self.__sessionPath = self.__sObj.getPath()
        self.__sessionRelativePath = self.__sObj.getRelativePath()
        #
        self.__ccConfig = ChemCompConfig(reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        self.__definitionId = None
        self.__definitionFilePath = None
        self.__annotatedFileName = None
        self.__annotatedFilePath = None
        self.__annotatedRelativeFilePath = None

    def setDefinitionId(self, definitionId):
        """Set an existing chemical component identifier in archive collection as
           the report target
        """
        self.__definitionId = str(definitionId).upper()
        if self.__annotatedFileName is None:
            self.__annotatedFileName = self.__definitionId + "-upd.cif"
        return self.__getFilePathFromId(self.__definitionId)

    def setFilePath(self, definitionFilePath, definitionId="TMP"):
        self.__definitionFilePath = definitionFilePath
        if (not os.access(self.__definitionFilePath, os.R_OK)):
            return False
        self.__definitionId = str(definitionId).upper()
        if self.__annotatedFileName is None:
            self.__annotatedFileName = self.__definitionId + "-upd.cif"
        return True

    def getFilePath(self):
        return self.__definitionFilePath

    def __getFilePathFromId(self, ccId):
        """
        """
        idUc = str(ccId).upper()
        fileName = idUc + ".cif"
        self.__definitionFilePath = os.path.join(self.__ccConfig.getPath('chemCompCachePath'), idUc[0:1], idUc[0:3], fileName)
        #
        if (not os.access(self.__definitionFilePath, os.R_OK)):
            return False
        return True

    def setAnnotatedFileName(self, fileName):
        self.__annotatedFileName = fileName

    def getAnnotatedFilePath(self):
        return (self.__annotatedFilePath)

    def getAnnotatedRelativeFilePath(self):
        return (self.__annotatedRelativeFilePath)

    ##
    ##
    def doAnnotate(self):
        """ annotation operation -
        """
        #
        swap = "SWAP"
        #
        dirPath = os.path.join(self.__sessionPath, self.__definitionId)
        dirRelativePath = os.path.join(self.__sessionRelativePath, self.__definitionId)
        # create the report path in the session directory
        #
        if (not os.access(dirPath, os.F_OK)):
            try:
                os.makedirs(dirPath)
            except:  # noqa: E722 pylint: disable=bare-except
                return False
        #
        #
        # make a local copy of the file (if required)
        #
        (_pth, fileName) = os.path.split(self.__definitionFilePath)
        lclPath = os.path.join(dirPath, fileName)
        if (self.__definitionFilePath != lclPath):
            shutil.copyfile(self.__definitionFilePath, lclPath)
            #
            if (self.__verbose):
                self.__lfh.write("+ChemCompAnnotate.doAnnotate() - Copied input file %s to local path %s \n" %
                                 (self.__definitionFilePath, lclPath))
                self.__lfh.flush()
        #
        #
        logPath = os.path.join(dirPath, "annotate.log")
        outFile = self.__annotatedFileName
        #
        if str(swap).upper() == "SWAP":
            cmd = self.__ccConfig.getPath("annotateFileScript") + " " + \
                self.__ccConfig.getPath("binPath") + " " + dirPath + " " + fileName + \
                " " + outFile + " SWAP > " + logPath + " 2>&1"
        else:
            cmd = self.__ccConfig.getPath("annotateFileScript") + " " + \
                self.__ccConfig.getPath("binPath") + " " + dirPath + " " + fileName + \
                " " + outFile + " > " + logPath + " 2>&1"
        if (self.__verbose):
            self.__lfh.write("+ChemCompAnnotate.doAnnotate() directory path  = %s\n" % dirPath)
            self.__lfh.write("+ChemCompAnnotate.doAnnotate() Target filename = %s\n" % fileName)
            self.__lfh.write("+ChemCompAnnotate.doAnnotate() Output filename = %s\n" % outFile)
            self.__lfh.write("+ChemCompAnnotate.doAnnotate() Swap option     = %s\n" % str(swap))
            self.__lfh.write("+ChemCompAnnotate.doAnnotate() Log    path     = %s\n" % logPath)
            self.__lfh.write("+ChemCompAnnotate.doAnnotate() command string  = %s\n" % cmd)

        os.system(cmd)
        #
        outPath = os.path.join(dirPath, outFile)
        if os.path.exists(outPath):
            self.__annotatedFilePath = outPath
            self.__annotatedRelativeFilePath = os.path.join(dirRelativePath, self.__annotatedFileName)
            return True
        else:
            return False
    ##

    def getAnnotatedFileText(self):
        #
        textData = ""
        try:
            if os.path.exists(self.__annotatedFilePath):
                textData = open(self.__annotatedFilePath).read()
        except:  # noqa: E722 pylint: disable=bare-except
            pass

        return textData
