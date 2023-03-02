##
# File:    ChemCompDataImport.py
# Date:    21-Sep-2010
#
# Update:
#
# 2011-01-17    RPS    Added getChemCompAssignDetailsFilePath()
# 2013-06-11    RPS    Accommodating new 'deposit' filesource/storage type.
# 2013-10-23    RPS    Updates in support of handling data propagation from LigandLite of DepUI to LigandModule of annotation.
# 2022-11-13    ZF     Changed sketch file type from 'component-definition-deposit' to 'component-definition-upload'
##

"""
Class to encapsulate data import for chemical component files from the workflow directory hierarchy.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"


import sys
import os
import os.path
import traceback

from wwpdb.io.locator.DataReference import DataFileReference


class ChemCompDataImport(object):
    """ Controlling class for data import operations

        Supported file sources:
        + archive         -  WF archive storage
        + wf-instance     -  WF instance storage

    """
    def __init__(self, reqObj=None, verbose=False, log=sys.stderr):
        self.__verbose = verbose
        self.__reqObj = reqObj
        self.__lfh = log
        #
        self.__sessionObj = None
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompDataImport() starting\n")
            self.__lfh.flush()
        #
        self.__setup()
        #

    def __setup(self):

        try:
            self.__sessionObj = self.__reqObj.getSessionObj()
            # self.__sessionPath = self.__sessionObj.getPath()
            self.__fileSource = str(self.__reqObj.getValue("filesource")).lower()
            self.__identifier = str(self.__reqObj.getValue("identifier")).upper()
            self.__instance = str(self.__reqObj.getValue("instance")).upper()
            if self.__fileSource not in ['archive', 'wf-archive', 'wf-instance', 'wf_archive', 'wf_instance', 'deposit']:
                self.__fileSource = 'archive'
            #
            if (self.__verbose):
                self.__lfh.write("+ChemCompDataImport.__setup() file source %s\n" % self.__fileSource)
                self.__lfh.write("+ChemCompDataImport.__setup() identifier  %s\n" % self.__identifier)
                self.__lfh.write("+ChemCompDataImport.__setup() instance    %s\n" % self.__instance)
                #
                self.__lfh.flush()
        except:  # noqa: E722 pylint: disable=bare-except
            if (self.__verbose):
                self.__lfh.write("+ChemCompDataImport.__setup() sessionId %s failed\n" % self.__sessionObj.getId())

    def getModelPdxFilePath(self):
        return self.__getWfFilePath(contentType='model', format='pdbx', fileSource=self.__fileSource, version='latest')

    def getChemCompLinkFilePath(self):
        return self.__getWfFilePath(contentType='chem-comp-link', format='pdbx', fileSource=self.__fileSource, version='latest')

    def getChemCompAssignFilePath(self):
        return self.__getWfFilePath(contentType='chem-comp-assign', format='pdbx', fileSource=self.__fileSource, version='latest')

    def getChemCompAssignDetailsFilePath(self):
        return self.__getWfFilePath(contentType='chem-comp-assign-details', format='pic', fileSource=self.__fileSource, version='latest')

    # ####  BEGIN file handling for LigandLite types #####

    def getChemCompDpstrInfoFilePath(self, fileSource):
        return self.__getWfFilePath(contentType='chem-comp-depositor-info', format='pdbx', fileSource=fileSource, version='latest')

    def getChemCompSketchFilePath(self, format='sdf', fileSource="archive", partitionNum=None):  # pylint: disable=redefined-builtin
        return self.__getWfFilePath(contentType='component-definition-upload', format=format, fileSource=fileSource, version='latest', partitionNum=partitionNum)

    def getChemCompImageFilePath(self, format, fileSource="archive", partitionNum=None):  # pylint: disable=redefined-builtin
        return self.__getWfFilePath(contentType='component-image-upload', format=format, fileSource=fileSource, version='latest', partitionNum=partitionNum)

    def getChemCompDefntnFilePath(self, format, fileSource="archive", partitionNum=None):  # pylint: disable=redefined-builtin
        return self.__getWfFilePath(contentType='component-definition-upload', format=format, fileSource=fileSource, version='latest', partitionNum=partitionNum)

    # ####  END file handling for LigandLite types #####

    def __getWfFilePath(self, contentType='model', format='pdbx', fileSource='archive', version='latest', partitionNum=None):  # pylint: disable=redefined-builtin
        try:
            fPath = self.__getWfFilePathRef(contentType=contentType, format=format, fileSource=fileSource, version=version, partitionNum=partitionNum)
            if self.__verbose:
                self.__lfh.write("+ChemCompDataImport.__getWfFilePath() checking %s  path %s\n" % (contentType, fPath))
            if fPath is not None and os.access(fPath, os.R_OK):
                return fPath
            else:
                return None
        except:  # noqa: E722 pylint: disable=bare-except
            if (self.__verbose):
                traceback.print_exc(file=self.__lfh)
                self.__lfh.flush()
            return None

    def __getWfFilePathRef(self, contentType='model', format='pdbx', fileSource='archive', version='latest', partitionNum=None):  # pylint: disable=redefined-builtin
        """ Return the path to the latest version of the
        """
        #
        # Get PDBx model file -
        #
        dfRef = DataFileReference()
        self.__lfh.write("+ChemCompDataImport.__getWfFilePath() site id is %s\n" % dfRef.getSitePrefix())

        dfRef.setDepositionDataSetId(self.__identifier)
        if fileSource in ['archive', 'wf-archive', 'wf_archive']:
            dfRef.setStorageType('archive')
        elif fileSource == 'deposit':
            dfRef.setStorageType('deposit')
        elif fileSource in ['wf-instance', 'wf_instance']:
            dfRef.setWorkflowInstanceId(self.__instance)
            dfRef.setStorageType('wf-instance')
        else:
            self.__lfh.write("+ChemCompDataImport.__getWfFilePath() Bad file source for %s id %s wf id %s\n" %
                             (contentType, self.__identifier, self.__instance))
        #
        dfRef.setContentTypeAndFormat(contentType, format)
        dfRef.setVersionId(version)
        #
        if partitionNum:
            dfRef.setPartitionNumber(partitionNum)
        #
        fP = None
        if dfRef.isReferenceValid():
            dP = dfRef.getDirPathReference()
            fP = dfRef.getFilePathReference()
            if (self.__verbose):
                self.__lfh.write("+ChemCompDataImport.__getWfFilePath() file directory path: %s\n" % dP)
                self.__lfh.write("+ChemCompDataImport.__getWfFilePath() file           path: %s\n" % fP)
        else:
            self.__lfh.write("+ChemCompDataImport.__getWfFilePath() bad reference for %s id %s wf id %s\n" %
                             (contentType, self.__identifier, self.__instance))

        self.__lfh.flush()
        #
        return fP


if __name__ == '__main__':
    di = ChemCompDataImport()
