##
# File:     NmrDpUtility.py
# Date:     03-Mar-2021
#
# Updates:
# 03-Mar-2021  wmb - add methods for:

import os
import sys
from logging                                            import getLogger, StreamHandler, Formatter, DEBUG, INFO
from threading                                          import Timer
from subprocess                                         import call, Popen, PIPE
from mmcif.io.PdbxReader                                import PdbxReader
from wwpdb.utils.wf.WfDataObject                        import WfDataObject
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
                
                authAssignedId = ccAssignDataStore.getAuthAssignment(instId)
                topHitCcId = ccAssignDataStore.getBatchBestHitId(instId)

                # if instId == '1_H_0G7_701_':
                #     # print('>>>', authAssignmentId, topHitCcId, instIdList)
                #     return

                if authAssignedId not in fitTupleDict:
                    fitTupleDict[authAssignedId] = {}
                    fitTupleDict[authAssignedId]['alignList'] = []
                    fitTupleDict[authAssignedId]['masterAlignRef'] = None 

                # report material and imaging setup for this experimental instance
                instanceChemCompFilePath = os.path.join(self._depositAssignPath, instId, instId + '.cif')
                self._genLigandReportData(instId, instanceChemCompFilePath, 'exp')
                self._imagingSetupForLigandInstance(instId, authAssignedId, fitTupleDict, instanceChemCompFilePath)

                # report material and imaging setup for the author assigned instance
                if authAssignedId not in ccIdAlreadySeenList and self._checkLigandPath(authAssignedId):
                    self._genLigandReportData(authAssignedId, rtype='ref')
                    self._imagingSetupForTopHit(authAssignedId, authAssignedId, fitTupleDict)
                    ccIdAlrdySeenLst.append(authAssignedId)
                
                # report material and imaging setup for the best dictionary reference
                if topHitCcId not in ccIdAlreadySeenList and topHitCcId.lower() != 'none':
                    self._genLigandReportData(topHitCcId, rtype='ref')
                    self._imagingSetupForTopHit(authAssignedId, topHitCcId, fitTupleDict)
                    ccIdAlrdySeenLst.append(topHitCcId)
            
            self._genAligned2dImages(fitTupleDict)

        
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
        Raises:
            Exception:
                - if using "ref" mode, must pass a valid instance ID
                - if using "exp" mode, must pass a valid (and accessible) ".cif" file
        """
        ccReport = ChemCompReport(self._reqObj, self._verbose, self._lfh)

        if rtype == 'exp':
            # this is for experimental instances
            ccReport.setFilePath(instanceCcAbsFilePath, instId)
        elif rtype == 'ref':
            # this is for reference instances
            ccReport.setDefinitionId(definitionId=instId.lower())
        
        ccReport.doReport(type=rtype, ccAssignPthMdfier=instId)

        # maybe we should catch every exception and re-raise them with a proper
        # exception for failed report generation

        if self._verbose:
            filePaths = ccReport.getReportFilePaths()
            
            for k,v in filePaths.items():
                self._logger.debug('Coordinate file reporting -- key: {}, value: {}', k, v)

    def _imagingSetupForLigandInstance(self, instId, authAssignedId, fitTupleDict, instanceCcAbsFilePath):
        """Setup for generating instance images.

        Args:
            instId (str): instance ID
            authAssignmentId (str): author assigned ID
            fitTuplDict (dict): dictionary containing image related data
            instanceCcAbsFilePath (str): path to instance ".cif" file
        """
        instImageOutputPath = os.path.join(self._ccReportPath, instId + '.svg')

        if fitTupleDict[authAssignedId]['masterAlignRef'] is None:
            fitTupleDict[authAssignedId]['masterAlignRef'] = (instId, instanceCcAbsFilePath, instImageOutputPath)
        else:
            fitTupleDict[authAssignedId]['alignList'].append((instId, instanceCcAbsFilePath, instImageOutputPath))
    
    def _imagingSetupForTopHit(self, instId, authAssignedId, fitTupleDict):
        """Setup for generating ligand reference images.

        Args:
            instId (str): instance ID
            authAssignmentId (str): author assigned ID
            fitTuplDict (dict): dictionary containing image related data
        Raises:
            IOError: if we were not able to read the ligand ".cif" file from
                the ligand dict
        """
        pathPrefix = self._ccConfig.getPath('chemCompCachePath')
        chemCompCifPath = os.path.join(pathPrefix, instId[:1], instId, instId + '.cif')
        refImageOutputPath = os.path.join(self._ccReportPath, instId + '.svg')

        if os.access(chemCompCifPath, os.R_OK):
            fitTupleDict[authAssignedId]['alignList'].append((instId, chemCompCifPath, refImageOutputPath))
        else:
            # raising here since it's expected to be able to read the ligand ".cif"
            # file from the ligand dict
            raise IOError('Could not access file "{}"'.format((chemCompCifPath)))
    
    def _checkLigandPath(self, ccid):
        """Helper method to check if a given ligand has a correspondent
        entry in the dictionary.

        Args:
            ccid (str): ligand ID

        Returns:
            bool: True if the ligand has an entry in the dictionary, False otherwise
        """
        ccDictPrefix = self._ccConfig.getPath('chemCompCachePath')
        ligandEntryPath = os.path.join(pathPrefix, ccid[:1], ccid, ccid + '.cif')

        if not os.access(ligandEntryPath, os.R_OK):
            if self._verbose:
                self._logger.debug('Ligand ID %s has no corresponding dict ref file at %s', ccid, ligandEntryPath)

            return False

        return True
    
    def _genAligned2dImages(self, fitTupleDict):
        redoCcidLst = []

        for ccid in fitTupleDict:
            try:
                if fitTupleDict[ccid]['alignList'] is not None and len(fitTupleDict[ccid]['alignList']) > 0:
                    fileListPath = os.path.join(self._ccReportPath, 'alignfilelist_{}.txt'.format(ccid))
                    logPath = os.path.join(self._ccReportPath, 'alignfile_{}.log'.format(ccid))
                    
                    self._createAlignFileList(ccid, fileListPath, fitTupleDict)
                    if not self._alignImages(ccid, fileListPath):
                        redoCcidLst.append(ccid)
                else:
                    # there is no match for the ccid, no valid auth assigned id,
                    # and there is only one instance of the experimental ccid
                    # there will only be one image to generate
                    redoCcidLst.append(ccid)
                
            except:
                self._logger.error('Error aligning images for ligand "%s"', ccid, exc_info=True)
                
            # safeguard measure required if above process fails silently
            # so we check to see if the master image was not generated and add the ccid to the redo list
            masterImgPath = fitTupleDict[ccid]['masterAlignRef'][2]
            if not os.access(masterImgPath, os.F_OK):
                self._logger.warning('WARNING: could not find expected master image file at %s, so had to revisit image generation for ccid: %s', masterImgPath, ccid)
                redoCcidLst.append(ccid)
        
        # generate non-aligned images for those cases where exception occurred due to timeout/error
        pathList = []
        for ccid in redoCcidLst:
            try:
                imgTupl = fitTupleDict[ccid]['masterAlignRef']
                pathList.append(imgTupl)
                
                for anImgTupl in fitTupleDict[ccid]['alignList']:
                    pathList.append( anImgTupl )
                
                logPath = os.path.join(self._ccReportPath,'genimagefile_'+ccid+'.log')
                
                for title, path, imagePath in pathList:
                    if not self._genImages(title, path, imagePath):
                        self._logger.warning('WARNING: image generation failed for: %s',(imagePath))
            except:
                self._logger.error('Error generating non-aligned images for ligand "%s"', ccid, exc_info=True)
        
        return
    
    def _createAlignFileList(self, ccid, fileListPath, fitTupleDict):
        """Utility to write the align list file.

        Args:
            ccid (str): ligand ID
            fileListPath (str): path to the align list file
            fitTupleDict (dict): dictionary containing image related data
        """
        _MASTER_REFS = (
            'MASTER_ID:{}\n'
            'MASTER_DEF_PTH:{}\n'
            'MASTER_IMG_PTH:{}\n'
        )

        _ALIGN_REFS = (
            'ALIGN_ID:{}\n'
            'ALIGN_DEF_PTH:{}\n'
            'ALIGN_IMG_PTH:{}\n'
        )

        with open(fileListPath, 'w') as f:
            f.write('ASSIGN_PATH:{}\n'.format(self._ccReportPath))

            f.write(_MASTER_REFS.format(
                fitTupleDict[ccid]['masterAlignRef'][0],
                fitTupleDict[ccid]['masterAlignRef'][1],
                fitTupleDict[ccid]['masterAlignRef'][2])
            )

            for (thisId, fileDefPath, imgFilePth) in fitTupleDict[ccid]['alignList']:
                f.write(_ALIGN_REFS.format(thisId, fileDefPath, imgFilePth))
    
    def _alignImages(self, ccid, fileListPath):
        cmd = ['python', '-m', 'wwpdb.apps.ccmodule.reports.ChemCompAlignImages', '-v', '-i', ccid, '-f', fileListPath]
        kill_process = lambda process: process.terminate()
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False, close_fds=True, preexec_fn=os.setsid)
        timer = Timer(10, kill_process, [process])

        try:
            timer.start()
            stdout, stderr = process.communicate()
        finally:
            timer.cancel()

        if process.returncode == 0 or process.returncode == None:
            return False
        
        return True
    
    def _genImages(self, title, path, imagePath):
        cmd = ['python', '-m', 'wwpdb.apps.ccmodule.reports.ChemCompGenImage', '-v', '-i', title, '-f', path, '-o', imagePath]
        kill_process = lambda process: process.terminate()
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False, close_fds=True, preexec_fn=os.setsid)
        timer = Timer(10, kill_process, [process])

        try:
            timer.start()
            stdout, stderr = process.communicate()
        finally:
            timer.cancel()
        
        if process.returncode == 0 or process.returncode == None:
            return False
        
        return True

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
        self._reqObj.setValue('SessionsPath', self._cI.get('TOP_WWPDB_SESSIONS_PATH'))
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