##
# File:     ChemCompDpUtility.py
# Date:     03-Mar-2021
#

import os
import sys
import shutil
from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
from wwpdb.apps.ccmodule.chem.ChemCompAssign import ChemCompAssign
from wwpdb.apps.ccmodule.utils.ChemCompConfig import ChemCompConfig
from wwpdb.apps.ccmodule.utils.LigandAnalysisState import LigandAnalysisState
from wwpdb.apps.ccmodule.io.ChemCompDataExport import ChemCompDataExport
from wwpdb.apps.ccmodule.chem.PdbxChemCompAssign import PdbxChemCompAssignReader
from wwpdb.apps.ccmodule.chem.ChemCompAssignDepictLite import ChemCompAssignDepictLite
from wwpdb.utils.session.WebRequest import InputRequest
from wwpdb.utils.config.ConfigInfo import ConfigInfo
from wwpdb.utils.config.ConfigInfoApp import ConfigInfoAppCommon
from pathlib import Path
from wwpdb.io.locator.PathInfo import PathInfo
from wwpdb.utils.dp.RcsbDpUtility import RcsbDpUtility
from wwpdb.io.locator.ChemRefPathInfo import ChemRefPathInfo


class ChemCompDpInputs:
    FILE_CC_ASSIGN = 'file_cc_assign'


class ChemCompDpUtility(object):
    """ Wrapper class for ligand analysis operations
    """
    _CC_REPORT_DIR = 'cc_analysis'
    _CC_ASSIGN_DIR = 'assign'
    _CC_HTML_FILES_DIR = 'html'

    def __init__(self, depId, verbose=False, log=sys.stderr):
        self._verbose = verbose
        self._debug = False
        self._lfh = log
        self._logger = self._setupLog(log)

        # auxiliary input resource
        self._inputParamDict = {}
        self._depId = depId
        self._cI = ConfigInfo()
        self._cICommon = ConfigInfoAppCommon()

        # templates path
        self._templatePath = os.path.join(self._cI.get('SITE_WEB_APPS_TOP_PATH'), 'htdocs', 'ccmodule_lite')

        # setting up session object
        self._setupSession(self._depId)

        # setting up chem comp config
        self._ccConfig = ChemCompConfig(self._reqObj, self._verbose, self._lfh)
        self._ccRefPathInfo = ChemRefPathInfo(configObj=self._cI, configCommonObj=self._cICommon,
                                              verbose=self._verbose, log=self._lfh)
        self._depositPath = Path(PathInfo().getDepositPath(self._depId)).parent
        self._ccReportPath = os.path.join(self._depositPath, self._depId, self._CC_REPORT_DIR)
        self._depositAssignPath = os.path.join(self._depositPath, self._depId, self._CC_ASSIGN_DIR)
        self._ligState = LigandAnalysisState(self._depId, self._verbose, self._lfh)

    def doAnalysis(self):
        self._logger.info('Starting analysis for deposition "%s"', self._depId)

        try:
            # checking if there is already a cc_analysis folder and removing if so
            # this is to ensure that the report folder will contain only data to
            # the most recent deposition
            if os.path.exists(self._ccReportPath):
                self._logger.info('Removing existing %s directory', self._CC_ASSIGN_DIR)
                shutil.rmtree(self._ccReportPath, ignore_errors=True)

            os.makedirs(self._ccReportPath, exist_ok=True)

            # initializing the ligand state monitor
            self._ligState.init()

            # first we get the data dict from the cc assign file
            rDict = self._processCcAssignFile()
            cca = ChemCompAssign(self._reqObj, self._verbose, self._lfh)

            # instantiate a ChemCompAssignDataStore object to store deposition information
            if self._verbose:
                self._logger.debug('Creating datastore for resulting assign details')

            ccAssignDataStore = cca.createDataStore(rDict, True)

            # listing assignment keys
            if self._verbose:
                self._logger.debug('Getting author assignment keys')

            instIdList = ccAssignDataStore.getAuthAssignmentKeys()
            origCcId = set(map(ccAssignDataStore.getAuthAssignment, instIdList))

            if len(instIdList) == 0:
                # if we get an empty list here, there nothing else to do
                self._logger.warning('Empty assignment keys')
                self._ligState.finish()
                return

            ccIdAlreadySeenList = []
            fitTupleDict = {}

            updateStep = .3 / len(instIdList)

            for instId in instIdList:
                if self._verbose:
                    self._logger.debug('instId item: %s', instId)

                authAssignedId = ccAssignDataStore.getAuthAssignment(instId)
                topHitCcId = ccAssignDataStore.getBatchBestHitId(instId)

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
                    ccIdAlreadySeenList.append(authAssignedId)

                # report material and imaging setup for the best dictionary reference
                if topHitCcId not in ccIdAlreadySeenList and topHitCcId.lower() != 'none':
                    self._genLigandReportData(topHitCcId, rtype='ref')
                    self._imagingSetupForTopHit(authAssignedId, topHitCcId, fitTupleDict)
                    ccIdAlreadySeenList.append(topHitCcId)

                self._ligState.addProgress(updateStep, instId)

            self._genAligned2dImages(fitTupleDict)

            # parse cif files for data needed in instance browser
            # as we're creating a datastore from scratch
            cca.getDataForInstncSrch(instIdList, ccAssignDataStore)
            ccAssignDataStore.dumpData(self._lfh)
            ccAssignDataStore.serialize()

            self._importDepositorFiles(ccAssignDataStore)
            self._saveLigModState('intermittent')

            ccAD = ChemCompAssignDepictLite(self._reqObj, self._verbose, self._lfh)
            ccAD.generateInstancesMainHtml(ccAssignDataStore, origCcId)

            self._ligState.addProgress(.3)
            self._ligState.finish()
        except Exception as _e:  # noqa: F841
            self._logger.error('Error performing ligand analysis', exc_info=True)
            self._ligState.abort()

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

        if self._verbose:
            self._logger.debug('Reading assign results for desired match data.')

        pR = PdbxChemCompAssignReader(self._verbose, self._lfh)
        pR.setFilePath(filePath=fPath)
        pR.getBlock()

        for cN in ['pdbx_entry_info', 'pdbx_instance_assignment', 'pdbx_match_list', 'pdbx_atom_mapping', 'pdbx_missing_atom']:
            if pR.categoryExists(cN):
                dataDict[cN] = pR.getCategory(catName=cN)

        return dataDict

    def _genLigandReportData(self, instId, instanceCcAbsFilePath=None, rtype='ref'):
        """Generate the actual report file. The file path is based on
        the deposition ID and instance ID, as:

        /<deposit_path>/<deposit_id>/cc_analysis/<instance_id>/...

        Args:
            instId (str): instance ID
            instanceCcAbsFilePath (str): path to instance ID ".cif" file
            type (str): report type (either "exp" or "ref" for now)
        Raises:
            Exception:
                - if using "ref" mode, must pass a valid instance ID
                - if using "exp" mode, must pass a valid (and accessible) ".cif" file
        """
        if self._verbose:
            self._logger.debug('Generating report for %s (%s), %s.', instId, rtype, instanceCcAbsFilePath)

        tmpDir = os.path.join(self._ccReportPath, "logs")
        os.makedirs(tmpDir, exist_ok=True)

        definitionFilePath = ''
        if rtype == 'exp':
            # this is for experimental instances
            definitionFilePath = instanceCcAbsFilePath
        elif rtype == 'ref':
            # this is for reference instances
            definitionFilePath = self._ccRefPathInfo.getFilePath(str(instId).upper())

        dp = RcsbDpUtility(tmpPath=tmpDir, siteId=self._cI.get('SITE_PREFIX'), verbose=self._verbose, log=self._lfh)
        dp.addInput(name="type", value=rtype)
        dp.addInput(name="defid", value=instId)
        dp.addInput(name="ccreport_path", value=self._ccReportPath)
        dp.addInput(name="definition_file_path", value=definitionFilePath)
        dp.addInput(name="cc_path_modifier", value=instId)
        dp.op("chem-comp-do-report")

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

    def _imagingSetupForTopHit(self, authAssignedId, topHitCcId, fitTupleDict):
        """Setup for generating ligand reference images.

        Args:
            instId (str): instance ID
            authAssignmentId (str): author assigned ID
            fitTuplDict (dict): dictionary containing image related data
        Raises:
            IOError: if we were not able to read the ligand ".cif" file from
                the ligand dict
        """
        ccDictPrefix = self._ccConfig.getPath('chemCompCachePath')
        chemCompCifPath = os.path.join(ccDictPrefix, topHitCcId[:1], topHitCcId, topHitCcId + '.cif')
        refImageOutputPath = os.path.join(self._ccReportPath, topHitCcId + '.svg')

        if os.access(chemCompCifPath, os.R_OK):
            fitTupleDict[authAssignedId]['alignList'].append((topHitCcId, chemCompCifPath, refImageOutputPath))
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
        ligandEntryPath = os.path.join(ccDictPrefix, ccid[:1], ccid, ccid + '.cif')

        if not os.access(ligandEntryPath, os.R_OK):
            self._logger.warning('Ligand ID %s has no corresponding dict ref file at %s', ccid, ligandEntryPath)

            return False

        return True

    def _genAligned2dImages(self, fitTupleDict):
        """Generate images used in the report.

        Args:
            fitTupleDict (dict): dictionary containing image related data
        """
        if self._verbose:
            self._logger.debug('Starting image generation.')

        redoCcidLst = []

        updateStep = .2 / len(fitTupleDict)

        for ccid in fitTupleDict:
            self._logger.info('Performing image alignment tasks for %s.', ccid)

            try:
                if fitTupleDict[ccid]['alignList'] is not None and len(fitTupleDict[ccid]['alignList']) > 0:
                    fileListPath = os.path.join(self._ccReportPath, 'alignfilelist_{}.txt'.format(ccid))
                    # logPath = os.path.join(self._ccReportPath, 'alignfile_{}.log'.format(ccid))

                    self._createAlignFileList(ccid, fileListPath, fitTupleDict)
                    if not self._alignImages(ccid, fileListPath):
                        redoCcidLst.append(ccid)
                else:
                    # there is no match for the ccid, no valid auth assigned id,
                    # and there is only one instance of the experimental ccid
                    # there will only be one image to generate
                    redoCcidLst.append(ccid)

            except:  # noqa: E722 pylint: disable=bare-except
                self._logger.error('Error aligning images for ligand "%s"', ccid, exc_info=True)

            # safeguard measure required if above process fails silently
            # so we check to see if the master image was not generated and add the ccid to the redo list
            masterImgPath = fitTupleDict[ccid]['masterAlignRef'][2]
            if not os.access(masterImgPath, os.F_OK):
                self._logger.warning('WARNING: could not find expected master image file at %s, so had to revisit image generation for ccid: %s', masterImgPath, ccid)
                redoCcidLst.append(ccid)

            self._ligState.addProgress(updateStep, ccid)

        # generate non-aligned images for those cases where exception occurred due to timeout/error
        pathList = []
        for ccid in redoCcidLst:
            self._logger.info('Performing image generation tasks for %s.', ccid)

            try:
                imgTupl = fitTupleDict[ccid]['masterAlignRef']
                pathList.append(imgTupl)

                for anImgTupl in fitTupleDict[ccid]['alignList']:
                    pathList.append(anImgTupl)

                # logPath = os.path.join(self._ccReportPath, 'genimagefile_' + ccid + '.log')

                for title, path, imagePath in pathList:
                    if not self._genImages(title, path, imagePath):
                        self._logger.warning('WARNING: image generation failed for: %s', (imagePath))
            except:  # noqa: E722 pylint: disable=bare-except
                self._logger.error('Error generating non-aligned images for ligand "%s"', ccid, exc_info=True)
            finally:
                self._ligState.addProgress(updateStep, ccid)

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
        tmpDir = os.path.join(self._ccReportPath, "img_align_logs")
        os.makedirs(tmpDir, exist_ok=True)

        dp = RcsbDpUtility(tmpPath=tmpDir, siteId=self._cI.get('SITE_PREFIX'), verbose=self._verbose, log=self._lfh)
        dp.addInput(name="ccid", value=ccid)
        dp.addInput(name="file_list_path", value=fileListPath)
        returncode = dp.op("chem-comp-align-images")

        if self._verbose:
            self._logger.debug('Image alignment process returned with %s', returncode)

        if returncode != 0:
            return False

        return True

    def _genImages(self, title, path, imagePath):
        tmpDir = os.path.join(self._ccReportPath, "img_gen_logs")
        os.makedirs(tmpDir, exist_ok=True)

        dp = RcsbDpUtility(tmpPath=tmpDir, siteId=self._cI.get('SITE_PREFIX'), verbose=self._verbose, log=self._lfh)
        dp.addInput(name="title", value=title)
        dp.addInput(name="path", value=path)
        dp.addInput(name="image_path", value=imagePath)
        returncode = dp.op("chem-comp-gen-images")

        if self._verbose:
            self._logger.debug('Image generation process returned with %s', returncode)

        if returncode != 0:
            return False

        return True

    def _importDepositorFiles(self, ccAssignDataStore):
        """Copy user edited files to the report path.

        Args:
            ccAssignDataStore (ChemComAssignDataStore): current datastore
        """
        contentTypeDict = self._cI.get('CONTENT_TYPE_DICTIONARY')

        self._logger.info('Processing previously addressed ligand groups')

        for ligId in ccAssignDataStore.getGlbllyRslvdGrpList():
            if self._verbose:
                self._logger.debug('Processing ligand %s', ligId)

            try:
                # technically speaking, sdf files are not "uploaded" but are generated by any
                # sketches created by depositor if using the marvinsketch editor provided in the UI
                # for the time-being the sdf files are being handled as if they were uploaded

                # check if marvinsketch was used to create an sdf file
                submittedStructureData = ccAssignDataStore.getDpstrSubmitChoice(ligId)
                if submittedStructureData is not None and submittedStructureData == 'sketch':
                    definitionFileName = ligId + '-sketch.sdf'
                    reportDefinitionFilePath = os.path.join(self._ccReportPath, definitionFileName)
                    wfFilePath = ccAssignDataStore.getDpstrSketchFileWfPath(ligId, definitionFileName, 'sdf')

                    self._copyFileToReportDir(wfFilePath, reportDefinitionFilePath)
                # then check if any files were uploaded
                dpstrUploadFilesDict = ccAssignDataStore.getDpstrUploadFilesDict()
                if ligId in dpstrUploadFilesDict:
                    for fileType in dpstrUploadFilesDict[ligId]:
                        if fileType in contentTypeDict['component-image'][0]:
                            for fileName in dpstrUploadFilesDict[ligId][fileType].keys():
                                reportImageFilePath = os.path.join(self._ccReportPath, fileName)
                                wfImageFilePath = ccAssignDataStore.getDpstrUploadFileWfPath(ligId, fileType, fileName)

                                self._copyFileToReportDir(wfImageFilePath, reportImageFilePath)
                        elif fileType in contentTypeDict['component-definition'][0]:
                            for fileName in dpstrUploadFilesDict[ligId][fileType].keys():
                                reportDefinitionFilePath = os.path.join(self._ccReportPath, fileName)
                                wfDefinitionFilePath = ccAssignDataStore.getDpstrUploadFileWfPath(ligId, fileType, fileName)

                                self._copyFileToReportDir(wfDefinitionFilePath, reportDefinitionFilePath)
            except:  # noqa: E722 pylint: disable=bare-except
                if self._verbose:
                    self._logger.error('----- WARNING ----- processing failed id: %s', self._depId, exc_info=True)

    def _copyFileToReportDir(self, sourceFilePath, destFilePath):
        """Helper method to copy files between CC folders.

        Args:
            sourceFilePath (str): path to source file
            destFilePath (str): path to destination file

        Raises:
            IOError: if there was some problem accessing the source file.
        """
        if sourceFilePath is not None and os.access(sourceFilePath, os.R_OK):
            shutil.copyfile(sourceFilePath, destFilePath)

            if self._verbose:
                self._logger.debug('Copied workflow file from %s to report path %s', sourceFilePath, destFilePath)
        else:
            raise IOError('Error when attempting to copy file from %s to report path as %s' % (sourceFilePath, destFilePath))

    def _saveLigModState(self, mode):
        """Persist state of user's chem comp module session which involves capturing updated:
            - ChemCompAssignDataStore pickle file as 'chem-comp-assign-details' file.
            - cc depositor info file is generated if user has completed Ligand Lite submission -- this file is used to propagate
                the relevant depositor provided info to the annotation pipeline

            Args:
                mode (str):
                    'completed' if annotator has designated all assignments for all ligands and wishes to
                        conclude work in the ligand module.
                    'unfinished' if annotator wishes to leave ligand module but resume work at a later point.
                    'intermittent' save of state on intermittent commits of ligand description data for an
                                    *individual* ligand ID (i.e. not for entire dataset of ligands)
                                    this mode is used when user chooses to update information
                                    being submitted for an individual ligand ID.
            Returns:
                ok: boolean indicating success/failure of the save operation
        """
        pathDict = {}
        # pickle file
        pathDict['picFileDirPth'] = None
        pathDict['picFileFlPth'] = None
        # depositor info file
        pathDict['dpstrInfoFileDirPth'] = None
        pathDict['dpstrInfoFileFlPth'] = None
        # depositor progress file
        pathDict['dpstrPrgrssFileDirPth'] = None
        pathDict['dpstrPrgrssFileFlPth'] = None

        fileSource = str(self._reqObj.getValue('filesource')).strip().lower()
        bSuccess = False
        depId = self._depId

        # determine if currently operating in Workflow Managed environment
        bIsWorkflow = False
        if fileSource in ['archive', 'wf-archive', 'wf_archive', 'wf-instance', 'wf_instance', 'deposit']:
            bIsWorkflow = True

        if bIsWorkflow:
            depId = depId.upper()
        else:
            depId = depId.lower()

        if fileSource:
            ccE = ChemCompDataExport(self._reqObj, self._verbose, self._lfh)
            pathDict['dpstrInfoFileFlPth'] = ccE.getChemCompDpstrInfoFilePath()

            if pathDict['dpstrInfoFileFlPth']:
                pathDict['dpstrInfoFileDirPth'] = os.path.split(pathDict['dpstrInfoFileFlPth'])[0]

                if self._verbose:
                    self._logger.debug('CC depositor info export directory path: %s', pathDict['dpstrInfoFileDirPth'])
                    self._logger.debug('CC depositor info export file path: %s', pathDict['dpstrInfoFileFlPth'])
            else:
                self._logger.warning('---- WARNING ---- No path obtained for CC depositor info export file, id %s', depId)

            # pickle file
            pathDict['picFileFlPth'] = ccE.getChemCompAssignDetailsFilePath()

            if pathDict['picFileFlPth']:
                pathDict['picFileDirPth'] = os.path.split(pathDict['picFileFlPth'])[0]

                if (self._verbose):
                    self._logger.debug('CC assign details export directory path: %s', pathDict['picFileDirPth'])
                    self._logger.debug('CC assign details export file path: %s', pathDict['picFileFlPth'])
            else:
                self._logger.warning('---- WARNING ---- No path obtained for CC assign details export file, id %s', depId)

            # chem comp depositor progress file
            pathDict['dpstrPrgrssFileFlPth'] = os.path.join(self._depositPath, depId, 'cc-dpstr-progress')
            pathDict['dpstrPrgrssFileDirPth'] = os.path.split(pathDict['dpstrPrgrssFileFlPth'])[0]

            if (self._verbose):
                self._logger.debug('CC assign dpstr progress directory path: %s', pathDict['dpstrPrgrssFileDirPth'])
                self._logger.debug('CC assign dpstr progress file path: %s', pathDict['dpstrPrgrssFileFlPth'])
        else:
            self._logger.warning('processing undefined filesource %r', fileSource)

        # call on ChemCompAssign to save current state of ligand assignments
        cca = ChemCompAssign(self._reqObj, self._verbose, self._lfh)
        bSuccess, _msg = cca.saveState(pathDict, context='deposit', mode=mode)

        return bSuccess

    def addInput(self, name=None, value=None, type='file'):  # pylint: disable=redefined-builtin
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

                return False  # pylint: disable=unreachable

            return True

        except Exception as e:
            raise ValueError('Error - %s', str(e))  # pylint: disable=raise-missing-from,raising-format-tuple

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
        self._reqObj.setValue('TOP_WWPDB_SESSIONS_PATH', self._cICommon.get_site_web_apps_top_sessions_path())
        self._reqObj.setValue('SessionsPath', self._cICommon.get_site_web_apps_sessions_path())
        self._reqObj.setValue('identifier', depId)
        self._reqObj.setValue('filesource', 'deposit')
        self._reqObj.setValue('TemplatePath', self._templatePath)

        if self._verbose:
            self._logger.debug('Session: %s', str(self._reqObj))

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
