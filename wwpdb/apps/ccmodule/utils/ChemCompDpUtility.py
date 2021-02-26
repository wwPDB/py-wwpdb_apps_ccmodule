##
# File:     NmrDpUtility.py
# Date:     03-Mar-2021
#
# Updates:
# 03-Mar-2021  wmb - add methods for:

import os
import sys
from logging                                            import getLogger, StreamHandler, Formatter, DEBUG, INFO
from subprocess                                         import call,Popen,PIPE
from wwpdb.utils.wf.WfDataObject                        import WfDataObject
from mmcif.io.PdbxReader                                import PdbxReader
from wwpdb.apps.ccmodule.chem.PdbxChemCompAssign        import PdbxChemCompAssignReader
from wwpdb.apps.ccmodule.chem.ChemCompAssign            import ChemCompAssign
from wwpdb.apps.ccmodule.io.ChemCompAssignDataStore     import ChemCompAssignDataStore
from wwpdb.apps.ccmodule.reports.ChemCompReports        import ChemCompReport
from wwpdb.apps.ccmodule.utils.ChemCompConfig           import ChemCompConfig
from wwpdb.utils.session.WebRequest                     import InputRequest
from wwpdb.utils.config.ConfigInfo                      import ConfigInfo

class ChemCompDpInputs:
    FILE_CC_ASSIGN = 'file_cc_assign'

class ChemCompDpUtility(object):
    """ Wrapper class for ligand analysis operations
    """
    _CC_REPORT_DIR = 'cc_report'
    _CC_ASSIGN_DIR = 'assign'
    
    def __init__(self, depId, verbose=False, log=sys.stderr):
        self._verbose = False
        self._debug = False
        self._lfh = log
        self._logger = self._setupLog(log)

        # auxiliary input resource
        self._inputParamDict = {}
        self._depId = depId
        self._cI = ConfigInfo()
        # setting up session object
        self._setupSession(self._depId)
        # setting up chem comp config
        self._ccConfig = ChemCompConfig(self._reqObj, self._verbose, self._lfh)
        self._depositPath = os.path.join(self._cI.get('SITE_DEPOSIT_STORAGE_PATH'), self._cI.get('DEPOSIT_DIR_NAME'))
        self._ccReportPath = os.path.join(self._depositPath, self._depId, self._CC_REPORT_DIR)
        self._depositAssignPath = os.path.join(self._depositPath, self._depId, self._CC_ASSIGN_DIR)
    
    def doAnalysis(self):
        try:
            # first we get the data dict from the cc assign file
            rDict = self._processCcAssignFile()
            cca = ChemCompAssign(self._reqObj, self._verbose, self._lfh)
            
            # instantiate a ChemCompAssignDataStore object to store deposition information
            ccAssignDataStore = cca.createDataStore(rDict, True)

            # listing assignment keys
            instIdList = ccAssignDataStore.getAuthAssignmentKeys()
            
            if len(instIdList) == 0:
                # if we get an empty list here, there nothing else to do
                self._logger.warning('Empty assignment keys')
                return
            
            ccIdAlreadySeenList=[]
            fitTupleDict={}

            for instId in instIdList:
                if self._verbose:
                    self._logger.debug('instId item: {}', instId)
                
                authAssignmentId = ccAssignDataStore.getAuthAssignment(instId)
                topHitCcId = ccAssignDataStore.getBatchBestHitId(instId)

                if authAssignmentId not in fitTupleDict:
                    fitTupleDict[authAssignmentId] = {}
                    fitTupleDict[authAssignmentId]['alignList'] = []
                    fitTupleDict[authAssignmentId]['masterAlignRef'] = None 
                
                # this file will hold information of ligand instance
                instanceChemCompFilePath = os.path.join(self._depositAssignPath, instId, instId + '.cif')

                # report material for this experimental instance
                self._genLigandReportData(instId, instanceChemCompFilePath, 'exp')

        
        except Exception as e:
            self._logger.error('Error performing ligand analysis', exc_info=True)

    def _processCcAssignFile(self):
        """Interrogate resulting assign results file for desired match data.
        This was originally a method from ChemCompAssign class.

        Raises:
            RuntimeError: raised when no cc assign input file was provided
            IOError: raised when trying to read the cc assign input file

        Returns:
            dict: dictionary with match data ?
        """
        dataDict = {}

        # checking if the required cc assign file was provided
        if ChemCompDpInputs.FILE_CC_ASSIGN not in self._inputParamDict:
            raise RuntimeError('Chemical components assignment file is required')
        
        fPath = self._inputParamDict[ChemCompDpInputs.FILE_CC_ASSIGN]

        if not os.access(fPath, os.R_OK):
            raise IOError('Could not read file "{}"'.format(fPath))

        pR = PdbxChemCompAssignReader(self._verbose, self._lfh)
        pR.setFilePath(filePath=fPath)
        pR.getBlock()

        for cN in ['pdbx_entry_info','pdbx_instance_assignment','pdbx_match_list','pdbx_atom_mapping','pdbx_missing_atom']:
            if pR.categoryExists(cN):
                dataDict[cN]=pR.getCategory(catName=cN)
        
        return dataDict
    
    def _genLigandReportData(self, instId, instanceCcAbsFilePath=None, rtype='ref'):
        """Generate the actual report file. The file path is based on
        the deposition ID and instance ID, as:

        /<deposit_path>/<deposit_id>/cc_report/<instance_id>/...

        Args:
            instId (str): instance ID
            instanceCcAbsFilePath (str): path to instance ID ".cif" file
            type (str): report type (either "exp" or "ref" for now)
        """
        ccReport = ChemCompReport(self._reqObj, self._verbose, self._lfh)

        if rtype == 'exp':
            ccReport.setFilePath(instanceCcAbsFilePath, instId)
        elif rtype == 'ref':
            ccReport.setDefinitionId(definitionId=instId.lower())
        
        ccReport.doReport(type=rtype, ccAssignPthMdfier=instId)

        # maybe we should catch every exception and re-raise them with a proper
        # exception for failed report generation

        if self._verbose:
            filePaths = ccReport.getReportFilePaths()
            
            for k,v in filePaths.items():
                self._logger.debug('Coordinate file reporting -- key: {}, value: {}', k, v)

    def addInput(self, name=None, value=None, type='file'):
        """Add a named input and value to the dictionary of input parameters.

        Args:
            name (str, optional): one of the keys declared in ChemCompDpInputs. Defaults to None.
            value (str, optional): value of provided key. Defaults to None.
            type (str, optional): type of input. Defaults to 'file'.

        Raises:
            ValueError: if user provides an unknown type of input
            ValueError: if absolute path of file could not be created

        Returns:
            bool: if operation was successful
        """
        try:
            if type == 'param':
                self._inputParamDict[name] = value
            elif type == 'file':
                self._inputParamDict[name] = os.path.abspath(value)
            elif type == 'file_list':
                self._inputParamDict[name] = [os.path.abspath(f) for f in value]
            else:
                raise ValueError('Error - Unknown input type {}'.format(type))

                return False

            return True

        except Exception as e:
            raise ValueError('Error - %s', str(e))

            return False
    
    def _setupSession(self, depId):
        """Setup the session object (even though we don't rely on sessions here)
        used by auxiliary classes.

        Args:
            depId (str): deposition ID

        Raises:
            ValueError: if deposition ID was not provided
        """
        if depId is None:
            raise ValueError('Deposition ID must be provided')

        self._reqObj = InputRequest({}, self._verbose, self._lfh)
        self._reqObj.setValue('WWPDB_SITE_ID', self._cI.get('SITE_PREFIX'))
        self._reqObj.setValue('TOP_WWPDB_SESSIONS_PATH', self._cI.get('TOP_WWPDB_SESSIONS_PATH'))
        self._reqObj.setValue('identifier', depId)

        # self._sessionId = self._reqObj.getSessionId()
        # self._sessionObj=self._reqObj.newSessionObj()
        # self._sessionPath = self._sessionObj.getPath()

    def _setupLog(self, log_file):
        """Setup a Logger instance to use the same file as provided
        by the 'log' parameters

        Args:
            log_file (IOStream): a file-like object

        Returns:
            Logger: instance of Logger class
        """
        logger = getLogger(__name__)
        handler = StreamHandler(log_file)

        formatter = Formatter('+%(module)s.%(funcName)s() ++ %(message)s\n')
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        
        if self._verbose:
            logger.setLevel(DEBUG)
        else:
            logger.setLevel(INFO)

        return logger