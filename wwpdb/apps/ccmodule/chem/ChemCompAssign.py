##
# File:  ChemCompAssign.py
# Date:  13-Sept-2010
# Updates:
#
# 2010-10-05    RPS    Added getDataForInstncSrch() to support instance searching interface ("Level 2" searching)
# 2010-10-08    RPS    doAssignWf() now rerunning cc-assign action to generate local result files
# 2010-11-22    RPS    Checkpoint Update: Exploring use of separate thread for running assignment operations (currently only done in WFM context)
# 2010-11-28    RPS    getDataForInstncSrch() simplified -- some tasks previously here now handled by ChemCompAssignDataStore
# 2010-12-03    RPS    getDataForInstncSrch()--updated to address issue of failures on first pass fetches of data from chem comp files
#                        for top hit candidates when the respective files were still pending creation.
#
# 5-Dec-2010   jdw     Add support for parameter adjustment and targeted instance search - doAssignInstance()
#                      Test cases provided in the ChemCompAssignTests.py
# 2010-12-10    RPS    WFE/M related code updated to mimic implementation used in standalone "rcsb" mode.
# 2010-12-15    RPS    Introducing support for rerunning instance search with adjusted parameters.
# 2010-12-17    RPS    Update to doAssignInstance_NEW() necessary to support proper location of supporting files when in WFM environment.
# 2011-01-17    RPS    Consolidated doAssign() and doAssignWf() into single doAssign() method.
#                        Cleaned up doAssignInstance() variants into single doAssignInstance() method.
# 2011-02-03    RPS    Addition of doAssignValidation() and other updates to support validation of chem comp IDs to be used in force assignment.
# 2011-02-16    RPS    __ccAssignOp() updated with call to RcsbDpUtility for creation of a version of the coordinate data file that
#                        can be used for loading into jmol
# 2011-03-31    RPS    doAssignValidation() updated to accommodate proper handling of TMP_IDs when files are uploaded for processing on shared server
# 2011-06-01    RPS    Created getTopHitsDataForInstnc(), to improve function modularity and better support rerunning of assignment searches.
# 2011-06-14    RPS    createDataStore(), updateDataStoreForInstnc(), and __synchronizeDataStore() moved to here from ChemCompWebApp class to improve cohesion
#                        synchronizeDataStore() now capturing warning messages from cc-assign reporting results
# 2011-06-15    RPS    1). __syncTopHitsData() created to consolidate redundant code for updating datastore with most up-to-date top hits info
#                      2). Support for processing instance matching warning messages for display to user
#                      3). Update to accommodate new composite scoring scheme for ligand matching.
# 2011-07-07    RPS    Updated check for isWorkflow to check for "wf_instance" as valid filesource
# 2011-07-14    RPS    Updated with comments in support of generating "restructuredtext" documentation
# 2011-09-13    RPS    Updated __synchronizeDataStore function to set default values for top Hit CcId = 'None' and for top Hit CcId Score = 'n.a.' so as to agree
#                        with what is expected as default values by ChemCompAssignDepict code.
# 2012-07-03    RPS    saveState() method added for capturing current state of chem component assignments.
# 2012-09-12    RPS    saveState() updated code used only for testing purposes.
#                        Improved code for gathering data required for instance browser view.
# 2012-10-05    RPS    saveState() updated to simplify signature/argument list.
# 2012-12-03    RPS    Introducing support for ChemComp "Lite" processing as occurs in deposition context (vs. annotation context).
# 2012-12-12    RPS    More support for ChemComp "Lite" processing
# 2013-02-21    RPS    More updates for ChemComp "Lite" processing --> use of "exact match" searching now replacing "id match" testing and
#                        exporting chem-comp-depositor-info.cif file to workflow storage
# 2013-03-01    RPS    Minor improvements in saveState() handling
# 2013-03-05    zf     added doAssignInstanceComp() to support for assignment using chemical component file
# 2013-03-31    RPS    Introduced support for persisting component-definition and component-image files to workflow storage in DEP UI context.
# 2013-04-08    RPS    Fixed issue with proper handling when saving state and reporting back status to ChemCompWebApp.
# 2013-04-09    RPS    ChemCompDataExport class now being leveraged in self.__ccLiteUploadFileHndling()
# 2013-04-10    RPS    Improved file handling for "Lite" LigModule in self.__ccLiteUploadFileHndling()
# 2013-04-12    RPS    Adjusted sequence of actions saveState() to better accommodate file handling for "Lite" LigModule.
# 2013-04-19    ZF     Updated doAssignValidation() and __ccAssignValidationOp(), using individual built chemical component file
#                      instead of model coordinate file for force match
# 2013-04-30    RPS    Updated to capture whether or not given ligand instance consists of just a single atom.
# 2013-06-11    RPS    Accommodating new 'deposit' filesource/storage type.
# 2013-06-25    RPS    Return value of doAssign simplified to single dictionary (prior form was dictionary within dictionary,
#                        which is no longer necessary).
#                      getDataForInstncSrch() and getTopHitsDataForInstnc() updated for efficiency.
# 2013-07-16    RPS    Updated for "intermittent" serialization of UI state to "deposit" storage.
# 2013-07-22    RPS    More updates for improved handling of files uploaded by depositor.
# 2013-08-12    RPS    Introduced use of cc-dpstr-progress files
# 2013-10-04    RPS    Accommodating propagation of any data gathered in LigModLite of Dep UI.
# 2013-10-08    RPS    In saveState(), call to __ccLiteUploadFileHndling() is now correctly invoked before generation of cc-dpstr-info file
# 2014-01-31    RPS    Updated synchronizeDataStore() to handle instance identifiers with lowercase alpha characters properly
#                        Ensuring comparisons of author assigned Ligand ID with CCIDs from dictionary are done via equivalent uppercase forms.
# 2014-03-07    RPS    Removing debugging reference to D_013067-cc-dpstr-info.cif.
# 2014-04-25    RPS    Improving handling of files uploaded via LigandLite UI, so that proper mapping of partition numbers is strictly enforced
#                        throughout all user sessions.
#                      Also, now tracking temporal order in which files are uploaded so that it can be determined
#                        which files have "last word" versioning precedence.
#                      "Intermittent" updates of data for individual LigandID's by LigandLite no longer triggering file updates for all ligands
#                        (just for the given ligand ID).
# 2014-05-13    RPS    Fix to allow LigMod to proceed even when there is failure to register names of the depositor provided img, ccdef files.
# 2016-02-15    ZF     Add filename into __extractCatFrmDpstrInfo function.
# 2016-02-17    RPS    Updates to accompany removal of obsolete code (i.e. ChemCompWebAppLite does not generate updated model files, so code related to this updated).
# 2017-03-27    RPS    Generating cc-dpstr-info file on intermittent saves now.
# 2017-04-11    RPS    Updates to accommodate identification of ligands selected by depositor as "ligands of interest"
# 2017-05-03    RPS    Updates so that LOI tracking can succeed even in cases where annotator reruns ligand search and consequently changes value for "author" assigned CCID
# 2017-05-24    RPS    Corrected for missing variable initialization in updateWithDepositorInfo().
# 2017-09-19    ZF     Add runMultiAssignValidation() and change doAssignValidation() to multiprocessing mode
# 2021-02-25    ZF     Add self.__origUpdIdMap & self.__sortCompositeMatchScore()
# 2022-05-23    ZF     Move the __getDpstrOrigCcids() method call from __synchronizeDataStore() method to doAssignValidation() for multiple instances case
##
"""
Residue-level chemical component extraction operations.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import multiprocessing
import os
import sys
import shutil
import traceback
import inspect

#
from rcsb.utils.multiproc.MultiProcUtil import MultiProcUtil
from wwpdb.utils.dp.RcsbDpUtility import RcsbDpUtility
from wwpdb.utils.config.ConfigInfo import ConfigInfo
from wwpdb.apps.ccmodule.chem.PdbxChemCompAssign import PdbxChemCompAssignReader
from wwpdb.apps.ccmodule.io.ChemCompDataImport import ChemCompDataImport
from wwpdb.apps.ccmodule.io.ChemCompDataExport import ChemCompDataExport
from wwpdb.apps.ccmodule.io.ChemCompIo import ChemCompReader
from wwpdb.apps.ccmodule.io.ChemCompAssignDataStore import ChemCompAssignDataStore
from wwpdb.apps.ccmodule.utils.ChemCompConfig import ChemCompConfig
from mmcif.io.PdbxReader import PdbxReader
from pathlib import Path
from wwpdb.io.locator.PathInfo import PathInfo
from mmcif.io.IoAdapterCore import IoAdapterCore


class ChemCompAssign(object):
    """Residue-level chemical component assignment operations

    """
    _CC_REPORT_DIR = 'cc_analysis'
    _CC_ASSIGN_DIR = 'assign'
    _CC_HTML_FILES_DIR = 'html'

    def __init__(self, reqObj, verbose=False, log=sys.stderr):
        """

         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        self.__verbose = verbose
        self.__lfh = log
        self.__debug = True
        self.__devTest = False
        #
        self.__reqObj = reqObj
        #
        self.__sObj = self.__reqObj.newSessionObj()
        self.__sessionPath = self.__sObj.getPath()
        # self.__sessionRelativePath = self.__sObj.getRelativePath()
        self.__sessionId = self.__sObj.getId()
        #
        #
        self.__ccLinkRadii = None
        self.__ccTargetInstanceId = None
        self.__ccBondRadii = None
        #
        self.__ccValidateInstIdList = None
        self.__ccValidationRefFilePth = None
        #
        self.__origUpdIdMap = {}
        #
        self.__cI = ConfigInfo()
        #
        self.__setup()
        self.__pathInfo = PathInfo()
        #

    def __setup(self):
        context = self.__getContext()

        if context == 'standalone':
            self.__depId = 'D_0'
            self.__modelDirPath = self.__sessionPath
            self.__ccReportPath = os.path.join(self.__sessionPath, 'assign')
        elif context == 'workflow' or context == 'unknown':
            self.__modelDirPath = self.__sessionPath
            self.__ccReportPath = os.path.join(self.__sessionPath, 'assign')
        elif context == 'deposition':
            self.__depId = self.__reqObj.getValue('identifier')
            self.__depositPath = Path(PathInfo().getDepositPath(self.__depId)).parent
            self.__modelDirPath = os.path.join(self.__depositPath, self.__depId)
            self.__ccReportPath = os.path.join(self.__depositPath, self.__depId, self._CC_REPORT_DIR)

        self.normal = ['ALA', 'CYS', 'ASP', 'GLU', 'PHE', 'GLY', 'HIS', 'ILE',
                       'LYS', 'LEU', 'MET', 'ASN', 'PRO', 'GLN', 'ARG', 'SER',
                       'THR', 'VAL', 'TRP', 'TYR', 'C', 'G', 'T', 'A', 'U',
                       'DC', 'DA', 'DU', 'DT', 'DG',
                       'HOH', 'TIP', 'WAT', 'OH2', 'MSE']
        #

    def __getContext(self):
        filesource = self.__reqObj.getValue('filesource')
        depid = self.__reqObj.getValue('identifier')

        if depid == 'TMP_ID':
            return 'standalone'

        if filesource == 'deposit':
            return 'deposition'

        if filesource in ['wf-archive', 'wf_archive', 'wf-instance', 'wf_instance']:
            return 'workflow'

        # in case we can't find out the context (as it happens with the standalone
        # ligmod) we fall back to get model files from the sessions path
        return 'unknown'

    def setLinkRadii(self, ccLinkRadii=None):
        if ccLinkRadii is not None:
            self.__ccLinkRadii = str(ccLinkRadii)

    def getLinkRadii(self):
        return self.__ccLinkRadii

    def setBondRadii(self, ccBondRadii=None):
        if ccBondRadii is not None:
            self.__ccBondRadii = str(ccBondRadii)

    def getBondRadii(self):
        return self.__ccBondRadii

    def setTargetInstanceId(self, ccTargetInstanceId=None):
        if ccTargetInstanceId is not None:
            self.__ccTargetInstanceId = str(ccTargetInstanceId)

    def getTargetInstanceId(self):
        return self.__ccTargetInstanceId

    def setValidationCcRefFilePath(self, p_ccRefFilePth=None):
        if p_ccRefFilePth is not None:
            self.__ccValidationRefFilePth = str(p_ccRefFilePth)

    def getValidationCcRefFilePath(self):
        return self.__ccValidationRefFilePth

    def setInstanceIdListForValidation(self, p_instIdList=None):
        if p_instIdList is not None:
            self.__ccValidateInstIdList = str(p_instIdList)

    def getInstanceIdListForValidation(self):
        return self.__ccValidateInstIdList

    def doAssign(self, exactMatchOption=False):
        """ ----   CC Assign Search entry point   ----
            Local copy of PDBx coordinate held by WFM environment is made.
            The ``cc-assign`` and ``cc-link`` RcsbDpUtility operations are then invoked
            on this local copy of the coordinate file.

            :param `exactMatchOption`:  whether or not to run abbreviated exact match search
                (e.g. as when requested by wwPDB Common Tool Deposition UI = Lite Lig Module).

            :Returns:
                ``dataDict``: return dictionary of assignment result information for
                this deposition corresponding to cif categories:

                            + 'pdbx_entry_info'
                            + 'pdbx_instance_assignment'
                            + 'pdbx_match_list'
                            + 'pdbx_atom_mapping'
                            + 'pdbx_missing_atom'

        """
        # the return dictionary -
        dataDict = {}
        #
        bIsWorkflow = self.__isWorkflow()
        #
        if bIsWorkflow:
            depDataSetId = self.__reqObj.getValue("identifier")
        else:
            caller = self.__reqObj.getValue("caller")
            filePath = self.__reqObj.getValue('filePath')
            fileType = self.__reqObj.getValue('fileType')
            fpModel = filePath
            (_pth, fileName) = os.path.split(filePath)
            (fN, _fileExt) = os.path.splitext(fileName)
            if (fN.upper().startswith("D_")):
                depDataSetId = fN.upper()
            elif (fN.lower().startswith("rcsb")):
                depDataSetId = fN.lower()
            else:
                depDataSetId = "TMP_ID"
            #
            identifier = self.__reqObj.getValue("identifier")
            if identifier:
                depDataSetId = identifier
            #
        #
        if self.__verbose:
            self.__lfh.write("+ChemCompAssign.doAssign() - Starting \n")
            #
            if bIsWorkflow:
                self.__lfh.write("+ChemCompAssign.doAssign() - site id  is %s\n" % self.__cI.get("SITE_PREFIX"))
                self.__lfh.write("+ChemCompAssign.doAssign() - deposition data set id  %s\n" % depDataSetId)
            else:
                self.__lfh.write("+ChemCompAssign.doAssign() - caller  %s\n" % caller)
                self.__lfh.write("+ChemCompAssign.doAssign() - file path  %s\n" % filePath)
                self.__lfh.write("+ChemCompAssign.doAssign() - file type  %s\n" % fileType)
            #
            self.__lfh.flush()
        #
        if bIsWorkflow:
            ccI = ChemCompDataImport(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            #
            # Remote path details --
            #
            fpModel = ccI.getModelPdxFilePath()
            fpLink = ccI.getChemCompLinkFilePath()
            fpAssign = ccI.getChemCompAssignFilePath()
            #
            if self.__verbose:
                self.__lfh.write("+ChemCompAssign.doAssign() - model file path  %s\n" % fpModel)
                self.__lfh.write("+ChemCompAssign.doAssign() - link file path  %s\n" % fpLink)
                self.__lfh.write("+ChemCompAssign.doAssign() - assign file path  %s\n" % fpAssign)

        #
        # Local path details - i.e. for processing within given session
        #
        assignDirPath = os.path.join(self.__sessionPath, 'assign')
        ccLinkFilePath = os.path.join(self.__sessionPath, depDataSetId + '-cc-link.cif')
        ccAssignFilePath = os.path.join(self.__sessionPath, depDataSetId + '-cc-assign.cif')
        # pdbxOutFilePath = os.path.join(self.__sessionPath, depDataSetId + '-model-update.cif')
        pdbxFileName = depDataSetId + '-model.cif'
        pdbxFilePath = os.path.join(self.__sessionPath, pdbxFileName)
        #
        try:
            ############################################################################################################
            # Make local copy of coordinate file
            ############################################################################################################
            # os.chdir(self.__sessionPath)  # Confimed no longer needed
            if fpModel is not None and os.access(fpModel, os.R_OK):
                shutil.copyfile(fpModel, pdbxFilePath)
            #
            os.system("cd %s ; env > LOGENV" % self.__sessionPath)
            ############################################################################################################
            # invoke RcsbDpUtility 'cc-link' operation
            ############################################################################################################
            self.__ccLinkOp(pdbxFilePath, ccLinkFilePath, self.__ccLinkRadii)
            if os.access(ccLinkFilePath, os.R_OK):
                if self.__verbose:
                    self.__lfh.write("+ChemCompAssign.doAssign() - link file created: %s\n" % ccLinkFilePath)
            else:
                if self.__verbose:
                    self.__lfh.write("+ChemCompAssign.doAssign() - NO link file created.\n")
                ccLinkFilePath = None
            ############################################################################################################
            # invoke RcsbDpUtility 'cc-assign' operation
            ############################################################################################################

            self.__ccAssignOp(depDataSetId, pdbxFilePath, assignDirPath, ccAssignFilePath, ccLinkFilePath, self.__ccBondRadii, self.__ccTargetInstanceId, exactMatchOption)
            #
            if os.access(ccAssignFilePath, os.R_OK):
                if self.__verbose:
                    self.__lfh.write("+ChemCompAssign.doAssign() - assignment file created: %s\n" % ccAssignFilePath)
            else:
                if self.__verbose:
                    self.__lfh.write("+ChemCompAssign.doAssign() - NO assignment file created.\n")
                ccAssignFilePath = None
            #
            self.__lfh.flush()

            #########################################################################################################
            # interrogate resulting assign results file for desired match data
            #########################################################################################################
            dataDict = self.processCcAssignFile(ccAssignFilePath)

        #
        except:  # noqa: E722 pylint: disable=bare-except
            if (self.__verbose):
                self.__lfh.write("+ChemCompAssign.doAssign() - pre-processing failed id:  %s\n" % depDataSetId)
                traceback.print_exc(file=self.__lfh)
                self.__lfh.flush()

        #
        return dataDict

    def processCcAssignFile(self, pathToAssignFile):
        dataDict = {}

        #########################################################################################################
        # interrogate resulting assign results file for desired match data
        #########################################################################################################
        pR = PdbxChemCompAssignReader(self.__verbose, self.__lfh)
        pR.setFilePath(filePath=pathToAssignFile)
        pR.getBlock()
        for cN in ['pdbx_entry_info', 'pdbx_instance_assignment', 'pdbx_match_list', 'pdbx_atom_mapping', 'pdbx_missing_atom']:
            if pR.categoryExists(cN):
                dataDict[cN] = pR.getCategory(catName=cN)

        return dataDict

    def saveState(self, pathDict, context="annot", mode=None):
        """ Method for capturing current state of chem component assignments.
            Chemical component selections via user interface are captured in an exported cc-assign-final.cif file
            And updated model file is generated to reflect these assignments for each ligand instance

            :Params:
                ``context``:
                    will by default be "annot" for annotation pipeline processing, unless specified as "deposit"
                    when called by ChemComWebAppLite for DepUI

                ``mode``:
                    'completed' if annotator has designated all assignments for all ligands and wishes to
                        conclude work in the ligand module.
                    'unfinished' if annotator wishes to leave ligand module but resume work at a later point.
                    'intermittent' save of state on intermittent commits of ligand description data for an
                                    *individual* ligand ID (i.e. not for entire dataset of ligands)
                                    this mode is used when user chooses to update information
                                    being submitted for an individual ligand ID.

        """
        identifier = self.__reqObj.getValue("identifier")
        bPickleExportOk = False
        bUpdtdAssgnExportOk = False
        bFinishedWithLigMod = False
        bUpdtdMdlFileOk = False
        bUpdtdMdlFileMsg = ""
        bUpdtdDpstrInfoFileOk = False
        bUpdtdDpstrProgressFileOk = False
        bSuccess = False
        #
        if 'mdlFileFlPth' in pathDict and pathDict['mdlFileFlPth'] is not None:
            # if this path has been supplied, indicates that annotator is done with LigModule
            bFinishedWithLigMod = True
        className = self.__class__.__name__
        methodName = inspect.currentframe().f_code.co_name
        #
        bIsWorkflow = self.__isWorkflow()
        #
        if bIsWorkflow:
            depDataSetId = identifier
        else:
            caller = self.__reqObj.getValue("caller")
            filePath = self.__reqObj.getValue('filePath')
            fileType = self.__reqObj.getValue('fileType')

            if identifier:
                depDataSetId = identifier
            else:
                # fpModel = filePath
                (_pth, fileName) = os.path.split(filePath)
                (fN, _fileExt) = os.path.splitext(fileName)
                if (fN.upper().startswith("D_")):
                    depDataSetId = fN.upper()
                elif (fN.lower().startswith("rcsb")):
                    depDataSetId = fN.lower()
                else:
                    depDataSetId = "TMP_ID"
        #
        if self.__verbose:
            self.__lfh.write("+%s.%s() - Starting \n" % (className, methodName))
            #
            if bIsWorkflow:
                self.__lfh.write("+%s.%s() - site id  is %s\n" % (className, methodName, self.__cI.get("SITE_PREFIX")))
                self.__lfh.write("+%s.%s() - deposition data set id  %s\n" % (className, methodName, depDataSetId))
            else:
                self.__lfh.write("+%s.%s() - caller  %s\n" % (className, methodName, caller))
                self.__lfh.write("+%s.%s() - file path  %s\n" % (className, methodName, filePath))
                self.__lfh.write("+%s.%s() - file type  %s\n" % (className, methodName, fileType))
            #
            self.__lfh.flush()
        #

        #
        # Local path details - i.e. for processing within given session
        #
        assignDirPath = self.__ccReportPath
        assignFileUpdtdPath = os.path.join(assignDirPath, depDataSetId + '-cc-assign-updated.cif')
        pdbxFileName = depDataSetId + '-model.cif'
        pdbxFilePath = os.path.join(self.__modelDirPath, pdbxFileName)
        pdbxOutFilePath = os.path.join(self.__modelDirPath, depDataSetId + '-model-update.cif')
        #
        dpstrInfoDirPath = self.__ccReportPath
        dpstrInfoFilePath = os.path.join(dpstrInfoDirPath, depDataSetId + '-cc-dpstr-info.cif')
        # dpstrUpdtdPdbxFilePath = os.path.join(dpstrInfoDirPath, depDataSetId + '-cc-model-w-dpstr-info.cif')

        #
        try:

            # Need to query ChemCompAssignDataStore to obtain latest state info
            ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)

            # '''
            # ################### BEGIN: RPS, 20120703: block being called just for TEST purposes ####################################
            # # normally, will only generate updated model file on absolute FINISH of the ligand module
            # if assignFileUpdtdPath is not None:
            #     bUpdtdMdlFileOk = self.__ccInstanceUpdateOp(pdbxFilePath, assignFileUpdtdPath, pdbxOutFilePath)

            #     if bUpdtdMdlFileOk and os.access(pdbxOutFilePath, os.R_OK):
            #         if self.__verbose:
            #             self.__lfh.write("+%s.%s() - updated model file created for TESTING ONLY: %s\n" % pdbxOutFilePath)
            #     else:
            #         if self.__verbose:
            #             self.__lfh.write("+%s.%s() - problem creating updated model file for TESTING purposes at %s\n" % pdbxOutFilePath)
            # ################### END: block for TEST purposes ###########################################################
            # '''

            if context == "annot":
                if ccADS.wasBorn():
                    # then capture current state of annotator assigned chem comp IDs to export file first to local sessions directory
                    bUpdtdAssgnExportOk = ccADS.doExportUpdatedCcAssignments(assignDirPath, assignFileUpdtdPath, depDataSetId)
                    if not bUpdtdAssgnExportOk:
                        self.__lfh.write("+%s.%s() - problem generating updated cc-assign file to %r \n" % (className, methodName, assignFileUpdtdPath))
                    else:
                        self.__lfh.write("+%s.%s() - successfully generated updated cc-assign file at: %r \n" % (className, methodName, assignFileUpdtdPath))
                        # additionally we are copying file to workflow instance area (renamed with appropriate workflow conventions)
                        if os.access(assignFileUpdtdPath, os.R_OK):
                            if pathDict['ccAssignFinalFileDirPth'] is not None and os.access(pathDict['ccAssignFinalFileDirPth'], os.R_OK):
                                shutil.copyfile(assignFileUpdtdPath, pathDict['ccAssignFinalFileFlPth'])
                            else:
                                if self.__verbose:
                                    self.__lfh.write("+%s.%s() ---- WARNING ---- NO updated cc-assign file file created for workflow storage because did not obtain valid file/path reference.\n" %  # noqa: E501
                                                     (className, methodName))

                ############################################################################################################
                # invoke RcsbDpUtility 'cc-instance-update' operation to create updated model file
                ############################################################################################################

                # only if annotator is finished with all assignments (which is true if valid value for path to an updated model file is supplied as param)
                # we update the model with user-selected chem comp assignments and save as separate updated-model cif file in local sessions directory
                if bFinishedWithLigMod and (assignFileUpdtdPath is not None):
                    bUpdtdMdlFileOk, bUpdtdMdlFileMsg = self.__ccInstanceUpdateOp(pdbxFilePath, assignFileUpdtdPath, pdbxOutFilePath)

                    if bUpdtdMdlFileOk and os.access(pdbxOutFilePath, os.R_OK):
                        # additionally we are making copy of updated model file for storage in workflow instance area (renamed with appropriate workflow conventions)
                        if bIsWorkflow:
                            if 'mdlFileFlPth' in pathDict and pathDict['mdlFileDirPth'] is not None and os.access(pathDict['mdlFileDirPth'], os.R_OK):
                                shutil.copyfile(pdbxOutFilePath, pathDict['mdlFileFlPth'])

                        if self.__verbose:
                            self.__lfh.write("+%s.%s() - updated model file created: %s\n" % (className, methodName, pdbxOutFilePath))
                    else:
                        if self.__verbose:
                            self.__lfh.write("+%s.%s() - NO updated model file created.\n" % (className, methodName))
                else:
                    if self.__verbose:
                        self.__lfh.write("+%s.%s() ---- WARNING ---- NO updated model file created for workflow storage because did not obtain valid file/path reference.\n" %
                                         (className, methodName))
                #
            elif context == "deposit":

                if bIsWorkflow:
                    #######################################################################################################################
                    # create status file to track progress for addressing mismatched ligand IDS (ONLY relevant in workflow managed context)
                    #######################################################################################################################
                    # check that workflow storage paths have been provided then store copy of updated depositor info file in workflow storage
                    if pathDict['dpstrPrgrssFileFlPth'] is not None and pathDict['dpstrPrgrssFileDirPth'] is not None and os.access(pathDict['dpstrPrgrssFileDirPth'], os.R_OK):
                        if ccADS.wasBorn():
                            bUpdtdDpstrProgressFileOk = ccADS.doExportDepositorProgress(pathDict['dpstrPrgrssFileDirPth'], pathDict['dpstrPrgrssFileFlPth'], depDataSetId, mode)
                    #
                    if not bUpdtdDpstrProgressFileOk:
                        self.__lfh.write("+%s.%s() - problem generating updated cc-dpstr-progress file to %r \n" % (className, methodName, pathDict['dpstrPrgrssFileFlPth']))
                    else:  # things went as planned
                        self.__lfh.write("+%s.%s() - successfully generated updated cc-dpstr-progress file at: %r \n" % (className, methodName, pathDict['dpstrPrgrssFileFlPth']))

                    #################################################################
                    # need to perform handling of any files uploaded by depositor
                    #################################################################
                    authAssgndGrp = None
                    if mode is not None and mode == "intermittent":
                        authAssgndGrp = str(self.__reqObj.getValue("auth_assgnd_grp"))
                    self.__ccLiteUploadFileHndling(ccADS, authAssgndGrp)

                ################################################################################################
                # create dedicated cif file to house "depositor info" for mismatched ligands
                ################################################################################################

                # creating file in local session work area when saving in "unfinished" and "completed" modes
                if ccADS.wasBorn():
                    bUpdtdDpstrInfoFileOk = ccADS.doExportUpdatedDepositorInfo(dpstrInfoDirPath, dpstrInfoFilePath, depDataSetId)
                #
                if not bUpdtdDpstrInfoFileOk:
                    self.__lfh.write("+%s.%s() - problem generating updated cc-dpstr-info file to %r \n" % (className, methodName, dpstrInfoFilePath))
                else:  # things went as planned
                    self.__lfh.write("+%s.%s() - successfully generated updated cc-dpstr-info file at: %r \n" % (className, methodName, dpstrInfoFilePath))

                    # additionally creating file in "deposit" archive area when saving in "completed" mode
                    if bIsWorkflow:
                        # check that workflow storage paths have been provided then store copy of updated depositor info file in workflow storage
                        if pathDict['dpstrInfoFileFlPth'] is not None and pathDict['dpstrInfoFileDirPth'] is not None and os.access(pathDict['dpstrInfoFileDirPth'], os.R_OK):
                            shutil.copyfile(dpstrInfoFilePath, pathDict['dpstrInfoFileFlPth'])

                self.__lfh.flush()

            #################################################################################################################################
            # ask ChemCompAssignDataStore to persist its state by serializing to a pic file
            #################################################################################################################################
            if ccADS.wasBorn():
                # viewing of non-candidates currently not being persisted for purposes of save to WFM, so purging lists and reserializing
                ccADS.purgeNewCandidatesLists()
                ccADS.serialize()
                ccADS.dumpData(self.__lfh)
                # the pic file is then exported to appropriate workflow instance directory
                if pathDict['picFileFlPth'] is not None and pathDict['picFileDirPth'] is not None:
                    bPickleExportOk = ccADS.doExport(pathDict['picFileDirPth'], pathDict['picFileFlPth'])
                    if not bPickleExportOk:
                        self.__lfh.write("+%s.%s() - problem generating cc-assign-details file to %r \n" % (className, methodName, pathDict['picFileFlPth']))
                    else:
                        self.__lfh.write("+%s.%s() - successfully generated cc-assign-details file at: %r \n" % (className, methodName, pathDict['picFileFlPth']))
                else:
                    if self.__verbose:
                        self.__lfh.write("+%s.%s() ---- WARNING ---- NO updated cc-assign-details file created for workflow storage because did not obtain valid file/path reference\n" %
                                         (className, methodName))

        except:  # noqa: E722 pylint: disable=bare-except
            if (self.__verbose):
                self.__lfh.write("+%s.%s() - pre-processing failed id:  %s\n" % (className, methodName, depDataSetId))
                traceback.print_exc(file=self.__lfh)
                self.__lfh.flush()
                # return oD
        #
        if context == "annot":
            if bFinishedWithLigMod:
                bSuccess = (bUpdtdMdlFileOk and bUpdtdAssgnExportOk and bPickleExportOk)
            else:
                bSuccess = (bUpdtdAssgnExportOk and bPickleExportOk)
        elif context == "deposit":
            if mode is not None and mode == "intermittent":
                bSuccess = bPickleExportOk
            else:
                bSuccess = (bUpdtdDpstrInfoFileOk and bPickleExportOk)
        #
        return bSuccess, bUpdtdMdlFileMsg

    def createDataStore(self, p_dataDict, p_exactMatchOption=False):
        """ Method for building a completely new chem comp assign datastore
            Used for those scenarios when a deposition dataset has no previously persisted datastore
            (e.g. deposition is being processed for the very first time)

            :Params:
                ``p_dataDict``: a dictionary of assignment information for this deposition corresponding to
                    data derived from cif categories in the chem component assignment file :
                    'pdbx_entry_info','pdbx_instance_assignment','pdbx_match_list','pdbx_atom_mapping','pdbx_missing_atom'
                ``p_exactMatchOption``: indicates whether we can abbreviated version of chem comp assign search handling for just exact matches
                                    i.e. in the case of chem comp lite module

            :Returns:
                ChemCompAssignDataStore object
        """
        if self.__verbose:
            self.__lfh.write("+ChemCompAssign.createDataStore() starting\n")
        #
        self.__lfh.flush()
        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
        if not ccADS.wasBorn():
            self.__synchronizeDataStore(p_dataDict, ccADS, p_exactOption=p_exactMatchOption)
            self.__lfh.flush()
        #
        ccADS.dump(self.__lfh)
        ccADS.dumpData(self.__lfh)
        ccADS.serialize()

        return ccADS

    def updateDataStoreForInstnc(self, p_instId, p_dataDict, preFlag=False, preCcidDict=None):
        """ Method for updating datastore as required on rerunning of chem comp assignment searches
            Used in scenarios where the deposition dataset has a previously persisted datastore that will
            be updated for information pertaining to a given instance ID for which new information exists

            :Params:

                + ``p_dataDict``: a dictionary of assignment information for this deposition corresponding to
                    data derived from cif categories in the chem component assignment file :
                    'pdbx_entry_info','pdbx_instance_assignment','pdbx_match_list','pdbx_atom_mapping','pdbx_missing_atom'
                + ``p_instId``: the instance ID for which the assignment search was rerun and for which information is being updated

            :Returns:
                updated ChemCompAssignDataStore object
        """
        if self.__verbose:
            self.__lfh.write("+ChemCompAssign.updateDataStoreForInstnc() starting\n")
        #
        if preCcidDict is None:
            preCcidDict = {}

        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
        if ccADS.wasBorn():
            self.__synchronizeDataStore(p_dataDict, ccADS, p_instId, preFlag=preFlag, preCcidDict=preCcidDict)
        #

        return ccADS

    def getDataForInstncSrch(self, p_srchIdsL, p_ccAssgnDataStr):
        """ Obtaining data points required for Instance Search UI
            Interrogates instance-level assign.cif files only for those instance IDs
            selected in batch search summary view for further instance searching/processing

            :Params:

                + `p_srchIdsL`: list of instance IDs to be processed via the Instance Search UI
                + `p_ccAssgnDataStr`: a Chem Comp Assign Datastore object
        """
        depDataSetId = "D_0" if self.__reqObj.getValue("identifier") in [None, 'TMP_ID'] else self.__reqObj.getValue("identifier")
        sessionId = self.__reqObj.getValue("sessionid")
        if self.__verbose:
            self.__lfh.write("+ChemCompAssign.getDataForInstncSrch() - Starting getAssignDataForInstSrch() \n")
            self.__lfh.write("+ChemCompAssign.getDataForInstncSrch() - deposition data set id  %s\n" % depDataSetId)
            self.__lfh.write("+ChemCompAssign.getDataForInstncSrch() - session id  %s\n" % sessionId)
            self.__lfh.flush()
        #
        assignDirPath = self.__ccReportPath

        try:
            # os.chdir(self.__modelDirPath)  # No longer needed

            for srchId in p_srchIdsL:
                # dd is data dictionary for a given instance of chem component
                dd = {}
                #######################################################
                #    set up access to instance level assignment data
                #######################################################
                # below is instance specific chem comp cif file for data at cc *instance* level
                chemCompFilePathAbs = os.path.join(self.__pathInfo.getDepositPath(depDataSetId), 'assign', srchId, srchId + ".cif")
                if not os.access(chemCompFilePathAbs, os.R_OK):
                    # i.e. if not in Workflow Managed context, must be in standalone dev context where we've run cc-assign search locally
                    # and therefore produced cc-assign results file in local session area
                    chemCompFilePathAbs = os.path.join(assignDirPath, srchId, srchId + '.cif')
                #
                if p_ccAssgnDataStr.getCcName(srchId) is None:
                    if os.access(chemCompFilePathAbs, os.R_OK):
                        if self.__verbose:
                            self.__lfh.write("+ChemCompAssign.getDataForInstncSrch() - instance specific chem comp cif file found: %s\n" % chemCompFilePathAbs)
                            #
                        ccR = ChemCompReader(self.__verbose, self.__lfh)
                        ccR.setFilePath(filePath=chemCompFilePathAbs)
                        ##################################################################################################
                        #    Currently getting data contained in "chem_comp" and "chem_comp_bond" cif categories
                        ##################################################################################################
                        #
                        dd['chem_comp'] = ccR.getChemCompDict()
                        dd['chem_comp_bond'] = ccR.getBonds()
                        #
                        chemCompName = dd['chem_comp'].get('_chem_comp.name', "")
                        chemCompFormula = dd['chem_comp'].get('_chem_comp.formula', "")
                        chemCompFormalChrg = dd['chem_comp'].get('_chem_comp.pdbx_formal_charge', "")
                        #
                        p_ccAssgnDataStr.setCcName(srchId, chemCompName)
                        p_ccAssgnDataStr.setCcFormula(srchId, chemCompFormula)
                        p_ccAssgnDataStr.setCcFormalChrg(srchId, chemCompFormalChrg)

                    else:
                        if self.__verbose:
                            self.__lfh.write("+ChemCompAssign.getDataForInstncSrch() - NO instance specific chem comp cif file  found for %s at %s\n" % (srchId, chemCompFilePathAbs))

                self.getTopHitsDataForInstnc(srchId, p_ccAssgnDataStr, assignDirPath)

        except:  # noqa: E722 pylint: disable=bare-except
            if (self.__verbose):
                self.__lfh.write("+ChemCompAssign.getDataForInstncSrch() - failed while retrieving chem comp data\n")
                traceback.print_exc(file=self.__lfh)
                self.__lfh.flush()

    def getTopHitsDataForInstnc(self, p_instId, p_ccAssgnDataStr, p_assignDirPath):
        """ For given instance of author ligand, obtains data pertaining to any top hit candidates
            identified by the chem comp assignment search

            :Params:

                + ``p_instId``: instance ID for which top hits data is being asked
                + ``p_ccAssgnDataStr``: a Chem Comp Assign Datastore object to be updated with top hits data
                + ``p_assignDirPath``: path to assign directory
        """

        ########################################################################################################################
        #   getting chem comp data for each candidate in top hits list for the ligand instance
        ########################################################################################################################
        # rnkdMtchL will serve as updated list of tuples of form (topHitCcId, topHitCcIdScore, matchWarning, ccName, ccFormula)
        rnkdMtchL = []
        # generation of chem comp reference material may take some time so need to maintain below
        # list of those still pending as we fetch data for chem comp references to be used in the instance search UI
        absntCcRefL = []
        #
        for tupL in p_ccAssgnDataStr.getTopHitsList(p_instId):

            if len(tupL) < 4:
                # at this point if tupL consists only of Top Hit record with just (topHitCcId, topHitCcIdScore, matchWarning) then
                # it needs to be updated with ccName and ccFormula as these are needed for display in the instance level UI
                ccid = tupL[0]
                if ccid.lower() != 'none':
                    self.__syncTopHitsData(p_instId, tupL, p_assignDirPath, rnkdMtchL, absntCcRefL, "first pass")
        #
        if self.__verbose:
            self.__lfh.write("+ChemCompAssign.getTopHitsDataForInstnc() - after first pass on reading top hit cc ref files for %s, have %s absent CC ids pending\n" %
                             (p_instId, len(absntCcRefL)))
        #
        # need to check for top hit cc references for which we were not able to update data due to the data not being generated yet by ChemCompReports
        while len(absntCcRefL) > 0:
            for tupL in absntCcRefL:
                self.__syncTopHitsData(p_instId, tupL, p_assignDirPath, rnkdMtchL, absntCcRefL, "return")

        if len(rnkdMtchL) > 0:
            if self.__verbose:
                self.__lfh.write("+ChemCompAssign.getTopHitsDataForInstnc() - rnkdMtchL is: %r\n" % rnkdMtchL)
            #
            # rnkdMtchL.sort(key=lambda match: match[1])
            if len(rnkdMtchL) > 1:
                rnkdMtchL = self.__sortCompositeMatchScore(rnkdMtchL)
            #
            p_ccAssgnDataStr.setTopHitsList(p_instId, rnkdMtchL)

    def validCcId(self, ccId):
        """ Verify existence of Chem Comp dictionary file

                Checks that CC ID simply has corresponding directory in server repository of ligand dict data

            :Returns:
                'rtrnCode': integer indicating success or failure on validation
                    0: passes
                    1: fails, ID does not exist
                    -1: error occurred

        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+%s.%s() starting\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
        #
        rtrnCode = -1
        ccConfig = ChemCompConfig(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        pathPrefix = ccConfig.getPath('chemCompCachePath')
        validationPth = os.path.join(pathPrefix, ccId[:1], ccId, ccId + '.cif')
        #
        if os.access(validationPth, os.R_OK):
            rtrnCode = 0
            if self.__verbose:
                self.__lfh.write("+%s.%s() %s PASSES simple validation.\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, ccId))

        else:
            rtrnCode = 1
            if self.__verbose:
                self.__lfh.write("+%s.%s() %s FAILS simple validation.\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, ccId))

        return rtrnCode

    def doAssignValidation(self):
        """ Perform "full" validation of chem comp ID being assigned to experimental data. i.e. check that:

                + given Chem Comp ID is not obsolete AND
                + given Chem Comp ID would be returned as result of cc-assign match query for the given ligand instance.

            :Returns:
                if fails return error message
                else return empty string
        """
        #
        if not self.__ccValidateInstIdList:
            return 'No Instance List defined'
        #
        depDataSetId = self.__reqObj.getValue("identifier")
        sessionId = self.__reqObj.getValue("sessionid")
        authAssgnCcId = self.__reqObj.getValue("auth_assgn_grp")

        if self.__verbose:
            self.__lfh.write("+ChemCompAssign.doAssignValidation() - Starting\n")
            self.__lfh.write("+ChemCompAssign.doAssignValidation() - deposition data set id  %s\n" % depDataSetId)
            self.__lfh.write("+ChemCompAssign.doAssignValidation() - session id  %s\n" % sessionId)
            self.__lfh.write("+ChemCompAssign.doAssignValidation() - author assigned chem comp ID  %s\n" % authAssgnCcId)
            self.__lfh.write("+ChemCompAssign.doAssignValidation() - CC instid validation list  : %s\n" % self.__ccValidateInstIdList)
            self.__lfh.flush()
        #
        if self.__cI.get('USE_COMPUTE_CLUSTER'):
            numProc = len(self.__ccValidateInstIdList.split(','))
        else:
            numProc = int(multiprocessing.cpu_count() / 2)
        mpu = MultiProcUtil(verbose=self.__verbose)
        mpu.set(workerObj=self, workerMethod="runMultiAssignValidation")
        mpu.setWorkingDir(self.__sessionPath)
        _ok, _failList, retLists, diagList = mpu.runMulti(dataList=self.__ccValidateInstIdList.split(','), numProc=numProc, numResults=1)
        if diagList:
            return '\n'.join(diagList)
        #
        flag = False
        origCcidDict = {}
        if len(retLists[0]) > 1:
            flag = True
            origCcidDict = self.__getDpstrOrigCcids()
        #
        for retResult in retLists[0]:
            pR = PdbxChemCompAssignReader(self.__verbose, self.__lfh)
            pR.setFilePath(filePath=retResult[1])
            pR.getBlock()
            dd = {}
            for cN in ['pdbx_entry_info', 'pdbx_instance_assignment', 'pdbx_match_list', 'pdbx_atom_mapping', 'pdbx_missing_atom']:
                if pR.categoryExists(cN):
                    dd[cN] = pR.getCategory(catName=cN)
                #
            #
            ccADS = self.updateDataStoreForInstnc(retResult[0], dd, preFlag=flag, preCcidDict=origCcidDict)
            ccADS.serialize()
        #

        return ''

    def runMultiAssignValidation(self, dataList, procName, optionsD, workingDir):  # pylint: disable=unused-argument
        """ Perform multiprocessing version of "full" validation of chem comp ID being assigned to experimental data.
        """
        authAssgnCcId = self.__reqObj.getValue("auth_assgn_grp")
        idList = []
        retList = []
        errList = []
        for instId in dataList:
            assignVldtnDirPath = os.path.join(self.__sessionPath, 'assign', 'validation', authAssgnCcId, instId)
            vldtnLogFilePth = os.path.join(assignVldtnDirPath, 'cc-assign-validation.log')

            if not os.access(assignVldtnDirPath, os.R_OK):
                os.makedirs(assignVldtnDirPath)
            else:
                shutil.rmtree(assignVldtnDirPath)
                os.makedirs(assignVldtnDirPath)
            #
            mdlfilePath = os.path.join(self.__sessionPath, 'assign', instId, instId + '.cif')
            if not os.access(mdlfilePath, os.R_OK):
                self.__lfh.write("+ChemCompAssign.doAssignValidation() - %s not found.\n" % mdlfilePath)
                errList.append('Chemical component file ' + mdlfilePath + ' not found.')
                continue
            #
            ccAssignVldtnFilePath = os.path.join(assignVldtnDirPath, 'cc-assign-validation.cif')
            completed = self.__ccAssignValidationOp(instId, mdlfilePath, assignVldtnDirPath, ccAssignVldtnFilePath, 'cc-assign-validation.log')
            if completed:
                if os.access(ccAssignVldtnFilePath, os.R_OK):
                    idList.append(instId)
                    retList.append((instId, ccAssignVldtnFilePath))
                elif os.access(vldtnLogFilePth, os.R_OK):
                    ifh = open(vldtnLogFilePth, 'r')
                    errList.append(ifh.read())
                    ifh.close()
                else:
                    errList.append('Run Force Match failed for instance ' + instId + ' (No output files, probably crashed).')
                    self.__lfh.write("+ChemCompAssign.doAssignValidation() - Run Force Match failed for instance %s (No output files, probably crashed).\n" % instId)
                #
            else:
                errList.append('Run Force Match failed for instance ' + instId + ' (Exception).')
                self.__lfh.write("+ChemCompAssign.doAssignValidation() - Run Force Match failed for instance %s (Exception).\n" % instId)
            #
        #
        return idList, retList, errList

    def doAssignInstance(self):
        """  Instance assignment entry point  - with support for parameter adjustment ...
        """
        # oD is the return dictionary -
        oD = {}
        dd = {}
        #
        depDataSetId = self.__reqObj.getValue("identifier")
        sessionId = self.__reqObj.getValue("sessionid")
        assignDirPath = self.__ccReportPath

        if self.__verbose:
            self.__lfh.write("+ChemCompAssign.doAssignInstance() - Starting doAssignInstance() \n")
            self.__lfh.write("+ChemCompAssign.doAssignInstance() - deposition data set id  %s\n" % depDataSetId)
            self.__lfh.write("+ChemCompAssign.doAssignInstance() - session id  %s\n" % sessionId)
            # self.__lfh.write("+ChemCompAssign.doAssignInstance() - caller           %s\n" % caller)
            # self.__lfh.write("+ChemCompAssign.doAssignInstance() - model file path  %s\n" % filePath)
            # self.__lfh.write("+ChemCompAssign.doAssignInstance() - file type        %s\n" % fileType)
            self.__lfh.write("+ChemCompAssign.doAssignInstance() - target instance  %s\n" % self.__ccTargetInstanceId)
            self.__lfh.write("+ChemCompAssign.doAssignInstance() - bond radii ext   %s\n" % self.__ccBondRadii)
            self.__lfh.write("+ChemCompAssign.doAssignInstance() - link radii ext   %s\n" % self.__ccLinkRadii)
            self.__lfh.flush()
        #
        bIsWorkflow = self.__isWorkflow()
        #
        if not bIsWorkflow:
            depDataSetId = depDataSetId.lower()
            mdlFileName = depDataSetId + '.cif'
        else:
            mdlFileName = depDataSetId + '-model.cif'
        #
        mdlfilePath = os.path.join(self.__modelDirPath, mdlFileName)
        ccLinkFilePath = os.path.join(assignDirPath, self.__ccTargetInstanceId, depDataSetId + '-cc-rerun-link.cif')
        #
        # store the assignments in the instance directory --
        ccAssignFilePath = os.path.join(assignDirPath, self.__ccTargetInstanceId, 'instance-rerun-assign.cif')
        #
        try:
            # os.chdir(self.__modelDirPath)  # no longer needed
            os.system("cd %s ; env > LOGENV" % self.__modelDirPath)
            #
            # bond distance calculation is done on the full model file using current link radii setting.
            #
            if os.access(mdlfilePath, os.R_OK):
                self.__lfh.write("+ChemCompAssign.doAssignInstance() - model file found: %s\n" % mdlfilePath)
            else:
                self.__lfh.write("+ChemCompAssign.doAssignInstance() - NO model file found at: %s\n" % mdlfilePath)
                mdlfilePath = None

            self.__ccLinkOp(mdlfilePath, ccLinkFilePath, self.__ccLinkRadii)
            if os.access(ccLinkFilePath, os.R_OK):
                self.__lfh.write("+ChemCompAssign.doAssignInstance() - link file created: %s\n" % ccLinkFilePath)
            else:
                self.__lfh.write("+ChemCompAssign.doAssignInstance() - NO link file created.\n")
                ccLinkFilePath = None
            #

            self.__ccAssignOneInstanceOp(depDataSetId, self.__ccTargetInstanceId, assignDirPath, ccAssignFilePath, ccLinkFilePath, self.__ccBondRadii)
            #
            if os.access(ccAssignFilePath, os.R_OK):
                self.__lfh.write("+ChemCompAssign.doAssignInstance() - assignment file created: %s\n" % ccAssignFilePath)
            else:
                self.__lfh.write("+ChemCompAssign.doAssignInstance() - NO assignment file created.\n")
                ccAssignFilePath = None

            pR = PdbxChemCompAssignReader(self.__verbose, self.__lfh)
            pR.setFilePath(filePath=ccAssignFilePath)
            pR.getBlock()
            for cN in ['pdbx_entry_info', 'pdbx_instance_assignment', 'pdbx_match_list', 'pdbx_atom_mapping', 'pdbx_missing_atom']:
                if pR.categoryExists(cN):
                    dd[cN] = pR.getCategory(catName=cN)

        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                self.__lfh.write("+ChemCompAssign.doAssignInstance() - pre-processing failed for:  %s\n" % mdlfilePath)
                traceback.print_exc(file=self.__lfh)
                self.__lfh.flush()
                # return oD

        oD['sessionid'] = self.__sessionId
        # oD['filename'] = fileName
        oD['linkFilePath'] = ccLinkFilePath
        oD['assignFilePath'] = ccAssignFilePath
        oD['assignDirPath'] = assignDirPath
        oD['dataDict'] = dd
        oD['identifier'] = depDataSetId
        #
        return oD

    def doAssignInstanceComp(self):
        """  Instance assignment entry point  - with edited chemical component ...
        """
        # oD is the return dictionary -
        oD = {}
        dd = {}
        #
        depDataSetId = self.__reqObj.getValue("identifier")
        sessionId = self.__reqObj.getValue("sessionid")
        assignDirPath = self.__ccReportPath

        if self.__verbose:
            self.__lfh.write("+ChemCompAssign.doAssignInstanceComp() - Starting doAssignInstanceComp() \n")
            self.__lfh.write("+ChemCompAssign.doAssignInstanceComp() - session id  %s\n" % sessionId)
            self.__lfh.write("+ChemCompAssign.doAssignInstanceComp() - target instance  %s\n" % self.__ccTargetInstanceId)
            self.__lfh.flush()
        #
        mdlfilePath = os.path.join(assignDirPath, self.__ccTargetInstanceId, self.__ccTargetInstanceId + '.cif')
        #
        # store the assignments in the instance directory --
        ccAssignFilePath = os.path.join(assignDirPath, self.__ccTargetInstanceId, 'instance-rerun-assign.cif')
        #
        try:
            # os.chdir(self.__modelDirPath)  # Believe safe to remove
            os.system("cd %s ; env > LOGENV" % self.__modelDirPath)
            #
            # bond distance calculation is done on the full model file using current link radii setting.
            #
            if os.access(mdlfilePath, os.R_OK):
                self.__lfh.write("+ChemCompAssign.doAssignInstanceComp() - model file found: %s\n" % mdlfilePath)
            else:
                self.__lfh.write("+ChemCompAssign.doAssignInstanceComp() - NO model file found at: %s\n" % mdlfilePath)
                mdlfilePath = None

            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__cI.get("SITE_PREFIX"), verbose=True)
            dp.setWorkingDir(assignDirPath)
            dp.addInput(name="id", value=depDataSetId)
            dp.addInput(name="cc_instance_id", value=self.__ccTargetInstanceId, type='param')
            #
            # Compute the path to the file -
            iFilePath = os.path.join(assignDirPath, self.__ccTargetInstanceId, self.__ccTargetInstanceId + '.cif')
            dp.imp(iFilePath)
            dp.op("chem-comp-assign-comp")

            dp.exp(ccAssignFilePath)
            #
            if os.access(ccAssignFilePath, os.R_OK):
                self.__lfh.write("+ChemCompAssign.doAssignInstanceComp() - assignment file created: %s\n" % ccAssignFilePath)
            else:
                self.__lfh.write("+ChemCompAssign.doAssignInstanceComp() - NO assignment file created.\n")
                ccAssignFilePath = None

            pR = PdbxChemCompAssignReader(self.__verbose, self.__lfh)
            pR.setFilePath(filePath=ccAssignFilePath)
            pR.getBlock()
            for cN in ['pdbx_entry_info', 'pdbx_instance_assignment', 'pdbx_match_list', 'pdbx_atom_mapping', 'pdbx_missing_atom']:
                if pR.categoryExists(cN):
                    dd[cN] = pR.getCategory(catName=cN)

        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                self.__lfh.write("+ChemCompAssign.doAssignInstanceComp() - pre-processing failed for:  %s\n" % mdlfilePath)
                traceback.print_exc(file=self.__lfh)
                self.__lfh.flush()
                # return oD

        oD['sessionid'] = self.__sessionId
        # oD['filename'] = fileName
        oD['linkFilePath'] = ''
        oD['assignFilePath'] = ccAssignFilePath
        oD['assignDirPath'] = assignDirPath
        oD['dataDict'] = dd
        oD['identifier'] = depDataSetId
        #
        return oD

    def updateWithDepositorInfo(self, p_ccAssgnDtaStr):
        """ Method for updating ChemCompAssign datastore with any info obtained from depositor using the DepUI's LigandLite UI
            Called by the annotation pipeline ChemCompWebApp

            :Params:

                + ``p_ccAssgnDtaStr``: reference to CC data store

        """

        className = self.__class__.__name__
        methodName = inspect.currentframe().f_code.co_name
        if self.__verbose:
            self.__lfh.write("+++%s.%s() STARTING\n" % (className, methodName))
            self.__lfh.flush()
        #
        dpstrInfoL = None
        dpstrUploadL = None
        dpstrRsrchL = None

        dpstrFileSource = "archive"
        # dpstrFileSource = "deposit"   #in interim getting file from deposit storage until transfer from deposit to annotation storage is stable

        if not self.__isWorkflow():
            dpstrInfoFlPth = None
        else:
            ccI = ChemCompDataImport(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            dpstrInfoFlPth = ccI.getChemCompDpstrInfoFilePath(fileSource=dpstrFileSource)

        if dpstrInfoFlPth is not None and os.access(dpstrInfoFlPth, os.R_OK):
            dpstrInfoDict = self.__processCcDpstrInfoFile(dpstrInfoFlPth)
            dpstrInfoL = dpstrInfoDict['dpstrInfoList']
            dpstrUploadL = dpstrInfoDict['dpstrUploadList']
            dpstrRsrchL = dpstrInfoDict['dpstrRsrchList']

        else:
            if self.__verbose:
                self.__lfh.write("+++%s.%s() unable to access file at: %s\n" % (className, methodName, dpstrInfoFlPth))

        if dpstrInfoL:
            for dpstrInfoD in dpstrInfoL:
                for k, v in dpstrInfoD.items():
                    if self.__verbose:
                        self.__lfh.write("+++%s.%s() key[%s] and value, %s\n" % (className, methodName, k, v))
                        self.__lfh.flush()
                    #
                #
                authAssgndGrp = dpstrInfoD['comp_id']
                dpstrCcType = dpstrInfoD['type']
                dpstrAltCcId = dpstrInfoD['alt_comp_id']
                dpstrCcDscptrStr = dpstrInfoD['descriptor']
                dpstrCcDscptrType = dpstrInfoD['descriptor_type']
                dpstrCcName = dpstrInfoD['name']
                dpstrCcFrmla = dpstrInfoD['formula']
                dpstrComments = dpstrInfoD['details']

                p_ccAssgnDtaStr.addGrpToGlbllyRslvdLst(authAssgndGrp)
                p_ccAssgnDtaStr.initializeGrpInfo(authAssgndGrp)
                p_ccAssgnDtaStr.setDpstrCcType(authAssgndGrp, dpstrCcType)
                p_ccAssgnDtaStr.setDpstrAltCcId(authAssgndGrp, dpstrAltCcId.upper())
                p_ccAssgnDtaStr.setDpstrCcDscrptrStr(authAssgndGrp, dpstrCcDscptrStr)
                p_ccAssgnDtaStr.setDpstrCcDscrptrType(authAssgndGrp, dpstrCcDscptrType)
                p_ccAssgnDtaStr.setDpstrCcName(authAssgndGrp, dpstrCcName)
                p_ccAssgnDtaStr.setDpstrCcFrmla(authAssgndGrp, dpstrCcFrmla)
                p_ccAssgnDtaStr.setDpstrComments(authAssgndGrp, dpstrComments)
                #
                if authAssgndGrp in self.__origUpdIdMap:
                    for updId in self.__origUpdIdMap[authAssgndGrp]:
                        p_ccAssgnDtaStr.addGrpToGlbllyRslvdLst(updId)
                        p_ccAssgnDtaStr.initializeGrpInfo(updId)
                        p_ccAssgnDtaStr.setDpstrCcType(updId, dpstrCcType)
                        p_ccAssgnDtaStr.setDpstrAltCcId(updId, dpstrAltCcId.upper())
                        p_ccAssgnDtaStr.setDpstrCcDscrptrStr(updId, dpstrCcDscptrStr)
                        p_ccAssgnDtaStr.setDpstrCcDscrptrType(updId, dpstrCcDscptrType)
                        p_ccAssgnDtaStr.setDpstrCcName(updId, dpstrCcName)
                        p_ccAssgnDtaStr.setDpstrCcFrmla(updId, dpstrCcFrmla)
                        p_ccAssgnDtaStr.setDpstrComments(updId, dpstrComments)
                    #
                #
            #
        #
        if dpstrUploadL:
            for dpstrUpldD in dpstrUploadL:

                for k, v in dpstrUpldD.items():
                    if self.__verbose:
                        self.__lfh.write("+++%s.%s() key[%s] and value, %s\n" % (className, methodName, k, v))
                        self.__lfh.flush()

                authAssgndGrp = dpstrUpldD['comp_id']
                upldFileName = dpstrUpldD['upload_file_name']
                upldFileType = dpstrUpldD['upload_file_type']

                # DEV TESTING
                if self.__devTest is True:
                    if upldFileName == 'ABC-sketch.sdf':
                        upldFileName = 'D_1100200119_ccdef_P1.sdf.V2'

                    if upldFileName == 'XYZ-sketch.sdf':
                        upldFileName = 'D_1100200147_ccdef_P1.sdf.V1'

                    if upldFileName == 'test-par.cif':
                        continue

                contentTypeDict = self.__cI.get('CONTENT_TYPE_DICTIONARY')

                # NOTE: all content types below should probably be specified as "upload" variant, e.g. 'component-image-upload' and 'component-definition-upload'

                # handling sdf files
                if upldFileType == 'sdf':
                    self.__registerFilePaths('component-sketch', upldFileName, upldFileType, p_ccAssgnDtaStr, authAssgndGrp, dpstrFileSource)
                    #
                    if authAssgndGrp in self.__origUpdIdMap:
                        for updId in self.__origUpdIdMap[authAssgndGrp]:
                            self.__registerFilePaths('component-sketch', upldFileName, upldFileType, p_ccAssgnDtaStr, updId, dpstrFileSource)
                        #
                    #
                else:
                    # handling of any files that were uploaded. we will register filename/path info with chemCompDataStore so that these can be recalled
                    # by ChemCompWebApp when it looks to load any files provided by the depositor into the session directory for working use.
                    if upldFileType in contentTypeDict['component-image'][0]:
                        self.__registerFilePaths('component-image', upldFileName, upldFileType, p_ccAssgnDtaStr, authAssgndGrp, dpstrFileSource)
                        #
                        if authAssgndGrp in self.__origUpdIdMap:
                            for updId in self.__origUpdIdMap[authAssgndGrp]:
                                self.__registerFilePaths('component-image', upldFileName, upldFileType, p_ccAssgnDtaStr, updId, dpstrFileSource)
                            #
                        #
                    elif upldFileType in contentTypeDict['component-definition'][0]:
                        self.__registerFilePaths('component-definition', upldFileName, upldFileType, p_ccAssgnDtaStr, authAssgndGrp, dpstrFileSource)
                        #
                        if authAssgndGrp in self.__origUpdIdMap:
                            for updId in self.__origUpdIdMap[authAssgndGrp]:
                                self.__registerFilePaths('component-definition', upldFileName, upldFileType, p_ccAssgnDtaStr, updId, dpstrFileSource)
                            #
                        #
                    else:
                        if self.__verbose:
                            self.__lfh.write("+%s.%s() ---------------WARNING---------------: Processing skipped for unexpected file type '%s' found for file(s) uploaded for ligid '%s'.\n" %  # noqa: E501
                                             (className, methodName, upldFileType, authAssgndGrp))

        if dpstrRsrchL:
            for dpstrRsrchD in dpstrRsrchL:
                for k, v in dpstrRsrchD.items():
                    if self.__verbose:
                        self.__lfh.write("+++%s.%s() key[%s] and value, %s\n" % (className, methodName, k, v))
                        self.__lfh.flush()

                authAssgndGrp = dpstrRsrchD['auth_comp_id']

                p_ccAssgnDtaStr.addGrpToRsrchSelectedLst(authAssgndGrp)

        p_ccAssgnDtaStr.dumpData(self.__lfh)
        p_ccAssgnDtaStr.serialize()

    ################################################################################################################
    # ------------------------------------------------------------------------------------------------------------
    #      Private helper methods
    # ------------------------------------------------------------------------------------------------------------
    #

    def __registerFilePaths(self, p_contentType, p_upldFileName, p_upldFileType, p_ccADS, p_ligId, p_dpstrFileSource):
        """ Method for storing data in ChemCompAssign datastore that relates to name/path information for any files
            uploaded by the depositor using LigandLite UI.
            This method, information is used by the annotation pipeline ChemCompWebApp in order to create local copies of the files for use within the LigMod UI

            :Params:

                + ``p_contentType``: currently can be one of 'component-sketch', 'component-image', 'component-definition'
                + ``p_upldFileName``: filename
                + ``p_upldFileType``: type as corresponds to file extension (e.g. png, sdf, etc)
                + ``p_ccADS``: reference to CC data store
                + ``p_ligId``: ligandID
                + ``p_dpstrFileSource``: "archive" vs. "deposit" storage source
        """
        className = self.__class__.__name__
        methodName = inspect.currentframe().f_code.co_name

        try:
            upldFilePartnNum = (p_upldFileName.split("_P")[1]).split(".", 1)[0]
            # need to preserve partition number b/c the P# is how we distinguish one ligand ID from another.

            fileHndlingCatalog = {'component-sketch' : ('getChemCompSketchFilePath', 'setDpstrSketchFile', 'setDpstrSketchFileWfPath'),
                                  'component-image' : ('getChemCompImageFilePath', 'setDpstrUploadFile', 'setDpstrUploadFileWfPath'),
                                  'component-definition' : ('getChemCompDefntnFilePath', 'setDpstrUploadFile', 'setDpstrUploadFileWfPath')}
            ccI = ChemCompDataImport(self.__reqObj, verbose=self.__verbose, log=self.__lfh)

            mthd0, mthd1, mthd2 = fileHndlingCatalog[p_contentType]
            getImportPth = getattr(ccI, mthd0, None)
            registerFileName = getattr(p_ccADS, mthd1, None)
            registerFileWfPath = getattr(p_ccADS, mthd2, None)

            if not self.__isWorkflow():  # FOR STANDALONE TESTING PURPOSES
                wfFlPth = '/wwpdb_da/da_top/wwpdb_da_test/source/python/wwpdb/apps/ccmodule/data/D_013067/' + p_upldFileName
            else:
                wfFlPth = getImportPth(format=p_upldFileType, fileSource=p_dpstrFileSource, partitionNum=upldFilePartnNum)
                # above call gets us path to supporting file based on filetype and partition number (which maps to specific ligand ID, with version number
                #   being highest version number available

            wfFlName = os.path.basename(wfFlPth)  # here we are stripping off the ".V{#}" extension to get filename that ends with recognizable extension
            wfIDirPth = (os.path.split(wfFlPth))[0]
            #
            if self.__verbose and self.__debug:
                self.__lfh.write("+%s.%s() - p_upldFileName is: [%s] and wfFlName is: [%s]\n" % (className, methodName, p_upldFileName, wfFlName))
            # RPS: found need to turn this off for testing 10/4/13 --- assert( wfFlName == p_upldFileName ), ("+%s.%s()
            #      -- ASSERTION ERROR: p_upldFileName is: [%s] but wfFlName is: [%s]\n" % (className, methodName, p_upldFileName, wfFlName) )
            #
            if wfFlPth is not None and wfIDirPth is not None and os.access(wfIDirPth, os.R_OK):
                registerFileName(p_ligId, p_upldFileType, wfFlName)
                registerFileWfPath(p_ligId, p_upldFileType, wfFlName, wfFlPth)
                p_ccADS.serialize()

        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                self.__lfh.write("+%s.%s() - failed to register paths for import of depositor provided file:  %s\n" % (className, methodName, p_upldFileName))
                traceback.print_exc(file=self.__lfh)
                self.__lfh.flush()

    def __getDpstrOrigCcids(self):
        rtrnDict = {}

        ccI = ChemCompDataImport(self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        # parse model file to get _pdbx_nonpoly_scheme.pdb_mon_id
        # _pdbx_nonpoly_scheme.auth_mon_id and equivalent in _pdbx_branch_scheme.
        #
        fpModel = ccI.getModelPdxFilePath()

        #
        if self.__verbose:
            self.__lfh.write("+ChemCompAssign.__getDpstrOrigCcids() - model file path  %s\n" % fpModel)

        if fpModel and os.access(fpModel, os.R_OK):
            categories = ('pdbx_branch_scheme', 'pdbx_nonpoly_scheme')  # tuple is hashable and can be used with lru_cache

            ioUtil = IoAdapterCore()
            container = ioUtil.readFile(
                inputFilePath=fpModel,
                selectList=categories,
            )
            #
            if len(container) == 0:
                return rtrnDict

            for category in categories:
                clist = container[0].getObj(category)

                if clist is None:
                    clist = []

                # clist = cifObj.GetValue(category)
                for Dict in clist:
                    if ('pdb_mon_id' not in Dict) or ('auth_mon_id' not in Dict):
                        continue
                    #
                    pdbWorkingCcid = Dict['pdb_mon_id'].upper()
                    dpstrOrigCcid = Dict['auth_mon_id'].upper()
                    #
                    if pdbWorkingCcid == 'HOH':
                        continue
                    #
                    rtrnDict[pdbWorkingCcid] = dpstrOrigCcid
                    #
                    if pdbWorkingCcid != dpstrOrigCcid:
                        if dpstrOrigCcid in self.__origUpdIdMap:
                            if pdbWorkingCcid not in self.__origUpdIdMap[dpstrOrigCcid]:
                                self.__origUpdIdMap[dpstrOrigCcid].append(pdbWorkingCcid)
                            #
                        else:
                            self.__origUpdIdMap[dpstrOrigCcid] = [pdbWorkingCcid]
                        #
                    #
                #
            #
        #
        return rtrnDict

    def __synchronizeDataStore(self, p_dataDict, p_ccAssgnDataStore, p_instId=None, p_exactOption=False, preFlag=False, preCcidDict=None):
        """ Method for synchronizing datastore object with information
            from the chem component assignment search results

            :Params:

                + ``p_dataDict``: a dictionary of assignment information for this deposition corresponding to
                    data derived from cif categories in the chem component assignment file :
                    'pdbx_entry_info','pdbx_instance_assignment','pdbx_match_list','pdbx_atom_mapping','pdbx_missing_atom'
                + ``p_ccAssgnDataStore``: DataStore object to be synchronized with content from the p_dataDict assignment data dictionary
                + ``p_instId``: the instance ID for which the assignment search was rerun and for which information is being updated
                    this will be None when creating a cc assignment datastore for the very first time for a given deposition dataset
                + ``p_exactOption``: flag for whether abbreviated search for just exact matches should be run, as in case of lite ligand module
        """
        if self.__verbose:
            self.__lfh.write("+ChemCompAssign.__synchronizeDataStore() -- starting\n")
        self.__lfh.flush()
        #
        if preCcidDict is None:
            preCcidDict = {}
        # parameterize for name of cif category representing assignment results for chemical components
        instncAssignCtgryName = 'pdbx_instance_assignment'
        #
        if (instncAssignCtgryName in p_dataDict) and (len(p_dataDict[instncAssignCtgryName]) > 0):

            # sorting assignment records by entity group for given instance record (i.e. het_id) and then by assignment status (i.e. "close match", "no match",  "passed")
            srtdAssignL = sorted(p_dataDict[instncAssignCtgryName], key=lambda row: row['_pdbx_instance_assignment.het_id'])
            srtdAssignL = sorted(srtdAssignL, key=lambda row: row['_pdbx_instance_assignment.status'])

            # get original depositor CCIDs
            if preFlag:
                origCcidDict = preCcidDict
            else:
                origCcidDict = self.__getDpstrOrigCcids()
            #

            for row in srtdAssignL:

                ####################################################################################################################################
                ####################################################################################################################################
                #    START for-loop
                #    in this for-loop we iterate through records in the 'pdbx_instance_assignment' category
                #   We take inventory of each instance ID in the assignment data and then,
                #    IF creating a brand new data store we use each instance ID as cross reference for
                #    obtaining information from other categories in the assignment data.
                #    OTHERWISE, when updating an already existing datastore with new assignment search results,
                #    we only take action if an inventoried instance ID corresponds to an instance ID that is being updated
                #    (i.e. via input parameter identifying which instance ID to update)
                ####################################################################################################################################
                #
                #
                topHitCcId = 'None'
                topHitCcIdScore = 'n.a.'
                instId = 'not found'
                topMtchStatus = 'not found'
                authAssgndId = 'not found'
                assgnmntWarning = 'not found'
                singleAtomFlag = 'n'  # default to no
                # rnkdMtchL will be list for tracking candidate hits for given instance ID and corresponding composite match score, match warnings
                # i.e list of tuples of form (topHitCcId, topHitCcIdScore, matchWarning)
                rnkdMtchL = []
                # candidateCcIdLst will be list for remembering which candidate CC IDs have been encountered
                candidateCcIdLst = []
                #
                if '_pdbx_instance_assignment.inst_id' in row:
                    # instId = row['_pdbx_instance_assignment.inst_id'].upper()
                    instId = row['_pdbx_instance_assignment.inst_id']
                    # now have instance ID for chemical component, serves as primary key
                #
                if self.__verbose:
                    self.__lfh.write("+ChemCompAssign.__synchronizeDataStore() -- found instanceid %s in chem comp assignment file.\n" % instId)
                #
                if ((p_instId is not None) and (instId == p_instId)) or (p_instId is None):

                    if p_instId is None:
                        # this is the first time the data store is being created
                        # for the deposition so need to capture author assigned ID (which may change value if annotator reruns ligModule and decides to update CC code)
                        # and we also caputre the "master" CCID originally submitted by depositor (which will remain unaltered througout all processing)
                        if '_pdbx_instance_assignment.het_id' in row:
                            # authAssgndId = (row['_pdbx_instance_assignment.het_id']).upper()
                            authAssgndId = (row['_pdbx_instance_assignment.het_id'])

                            dpstrOrigCcid = origCcidDict.get(authAssgndId)
                            p_ccAssgnDataStore.setDpstrOrigCcIdMaster(instId, dpstrOrigCcid)
                    #
                    if '_pdbx_instance_assignment.status' in row:
                        topMtchStatus = row['_pdbx_instance_assignment.status']
                    #
                    if '_pdbx_instance_assignment.single_atom_flag' in row:
                        singleAtomFlag = row['_pdbx_instance_assignment.single_atom_flag']
                        if self.__debug:
                            self.__lfh.write("+%s.%s() getting single_atom_flag for instid '%s' and it is: '%s'\n" %
                                             (self.__class__.__name__, inspect.currentframe().f_code.co_name, instId, singleAtomFlag))
                    #
                    if p_exactOption is False:
                        if '_pdbx_instance_assignment.warning_message' in row:
                            assgnmntWarning = row['_pdbx_instance_assignment.warning_message']
                            assgnmntWarning = assgnmntWarning.replace('?', 'n.a.')
                            assgnmntWarning = assgnmntWarning.replace('\n', '<br />')
                        #
                        ##############################################################################
                        #    START building ranked candidate hit list
                        #    establish lookup list for ranked candidate hits for a given instance id.
                        #    will cull this data from the 'pdbx_match_list' cif category
                        ##############################################################################
                        #
                        if ('pdbx_match_list' in p_dataDict) and (len(p_dataDict['pdbx_match_list']) > 0):

                            glblAssignMtchList = p_dataDict['pdbx_match_list']
                            cnt = 0
                            for dict in glblAssignMtchList:  # pylint: disable=redefined-builtin
                                if dict['_pdbx_match_list.inst_id'] == instId:
                                    # ''' creating composite score A/B/C/D/E derived from
                                    #     A = heavy atom match (%)
                                    #     B = match of chiral centers present, independent of handness (%)
                                    #     C = match of the handness of the chiral centers (%)
                                    #     D = match of aromatic flags
                                    #     E = match of bond order
                                    # '''
                                    cmpstScore = dict['_pdbx_match_list.heavy_atom_match_percent'] + ' / ' + dict['_pdbx_match_list.chiral_center_match_percent'] + \
                                        ' / ' + dict['_pdbx_match_list.chiral_center_match_with_handness_percent'] + ' / ' + dict['_pdbx_match_list.aromatic_match_flag'] + \
                                        ' / ' + dict['_pdbx_match_list.bond_order_match_percent']
                                    cmpstScore = cmpstScore.replace('?', 'n.a.')
                                    matchWarning = "n.a."
                                    if '_pdbx_match_list.warning_message' in dict:
                                        matchWarning = dict['_pdbx_match_list.warning_message']
                                        matchWarning = matchWarning.replace('?', 'n.a.')
                                        matchWarning = matchWarning.replace('\n', '<br />')
                                    rnkdMtchL.append(((dict['_pdbx_match_list.reference_id']).upper(), cmpstScore, matchWarning))
                                    candidateCcIdLst.append((dict['_pdbx_match_list.reference_id']).upper())
                                    cnt += 1
                                    if cnt == 5:
                                        # currently annotators asking to see only up to top 5 hits
                                        break
                            #
                            # rnkdMtchL.sort(key=lambda match: match[1])   #sorting by composite match score
                            if len(rnkdMtchL) > 1:
                                rnkdMtchL = self.__sortCompositeMatchScore(rnkdMtchL)
                            #
                            topHitCcId = (len(rnkdMtchL) and [(rnkdMtchL[0][0])] or ['None'])[0]
                            topHitCcIdScore = (len(rnkdMtchL) and [(rnkdMtchL[0][1])] or ['n.a.'])[0]

                        ##############################################################################
                        #    END OF building ranked candidate hit list
                        ##############################################################################

                        ##############################################################################
                        #    START obtain atom level mapping data
                        ##############################################################################
                        atomMapDict = {}
                        if ('pdbx_atom_mapping' in p_dataDict) and (len(p_dataDict['pdbx_atom_mapping']) > 0):
                            glblAtomMapLst = p_dataDict['pdbx_atom_mapping']
                            for ccId in candidateCcIdLst:
                                atomMapDict[ccId] = []
                            for dict in glblAtomMapLst:
                                if dict['_pdbx_atom_mapping.inst_id'] == instId:
                                    refId = dict['_pdbx_atom_mapping.reference_id']
                                    if refId in candidateCcIdLst:
                                        atomMapDict[refId].append((dict['_pdbx_atom_mapping.inst_atom_name'], dict['_pdbx_atom_mapping.reference_atom_name']))
                        ##############################################################################
                        #    END OF obtaining atom level mapping data
                        ##############################################################################
                    else:  # exactOption is True
                        # then we just need to know if an exact match has occurred but against an
                        # chem comp ID that is DIFFERENT from the cc ID specified by the depositor

                        if topMtchStatus.startswith('ligand match'):
                            topHitCcId = (topMtchStatus.split('ligand match ')).pop()
                        elif topMtchStatus == 'passed':
                            topHitCcId = authAssgndId.upper()

                        if authAssgndId.upper() != topHitCcId.upper():
                            p_ccAssgnDataStore.addGrpToAttnReqdLst(authAssgndId)
                            if self.__debug:
                                self.__lfh.write("+%s.%s() top hit differs from auth assigned ID, '%s', for %s and it is: %s\n" %
                                                 (self.__class__.__name__, inspect.currentframe().f_code.co_name, authAssgndId, instId, topHitCcId))
                            self.__lfh.flush()
                        rnkdMtchL.append((topHitCcId.upper(), 'n.a.', 'n.a.'))

                    ##############################################################################
                    #    Update CC Assign Data Store with the data
                    ##############################################################################
                    ##
                    p_ccAssgnDataStore.setBatchBestHit(instId, topHitCcId, topMtchStatus, topHitCcIdScore)
                    p_ccAssgnDataStore.setTopHitsList(instId, rnkdMtchL)
                    p_ccAssgnDataStore.setCcSingleAtomFlag(instId, singleAtomFlag)

                    if p_exactOption is False:
                        p_ccAssgnDataStore.setAtomMapDict(instId, atomMapDict)
                        p_ccAssgnDataStore.setCcAssgnWarning(instId, assgnmntWarning)
                    if p_instId is None:
                        p_ccAssgnDataStore.setAnnotAssignment(instId, "Not Assigned")
                        p_ccAssgnDataStore.setAuthAssignment(instId, authAssgndId)
                    ##
                    ###################################################

                ####################################################################################################################################
                #    END OF for-loop
                ####################################################################################################################################
                ####################################################################################################################################

    def __ccLiteUploadFileHndling(self, p_ccADS, p_ligId=None):
        """ Method for processing any files that were uploaded by the depositor to supplement
        the data collection for the deposition. Files will be copied to workflow storage
        and file names will be registered with the ChemCompAssignDataStore for recall purposes.
        Currently, component-definition, component-image, and sdf files are recognized file types.

        This method is called on calls to "saveState" by the LigandLite UI

        :Params:

                + ``p_ccADS``: reference to CC data store
                + ``p_ligId``: ligandID, when specified, indicates "intermittent" update of data
                                that pertains to just a single ligandID

        """
        className = self.__class__.__name__
        methodName = inspect.currentframe().f_code.co_name
        #
        # assignDirPath = os.path.join(self.__sessionPath, 'assign')
        #
        _ccE = ChemCompDataExport(self.__reqObj, verbose=self.__verbose, log=self.__lfh)  # noqa: F841
        #
        contentTypeDict = self.__cI.get('CONTENT_TYPE_DICTIONARY')
        for ligId in p_ccADS.getGlbllyRslvdGrpList():

            if p_ligId is not None and p_ligId.upper() != ligId.upper():
                continue
                # i.e. if specific p_ligId is specified when this method is called
                # then we will only move onto the below processing if we have the
                # ligand ID we are looking for, otherwise skip/continue at top of loop

            # any ligId in the GlbllyRslvdGrpList will already have a unique/dedicated Partition number assoc'd to it
            partitionId = p_ccADS.getRslvdGrpPartNumber(ligId)

            # technically speaking, sdf files are not "uploaded" but are generated by any
            # sketches created by depositor if using the marvinsketch editor provided in the UI
            # for the time-being the sdf files are being handled as if they were uploaded

            # check if marvinsketch was used to create an sdf file
            sbmttdStrctrData = p_ccADS.getDpstrSubmitChoice(ligId)
            if sbmttdStrctrData is not None and sbmttdStrctrData == 'sketch':
                defntnFlName = ligId + '-sketch.sdf'
                self.__storeFile('component-sketch', p_ccADS, defntnFlName, partitionId, 'sdf', ligId)

            # then check if any files were uploaded
            dpstrUploadFilesDict = p_ccADS.getDpstrUploadFilesDict()
            if ligId in dpstrUploadFilesDict:
                dpstrUploadFilesOrderLst = p_ccADS.getDpstrUploadFilesOrder(ligId)
                prevFileName = ""
                for uploadedFileNm in dpstrUploadFilesOrderLst:
                    # dpstrUploadFilesOrderLst is list that preserves the order in which files were uploaded
                    # we use it here so that we can determine which files were most recently uploaded and so
                    # which files deserve the highest version number when copy is made that complies with
                    # the wwPDB Common Tool naming convention (i.e. D_<ID#>_<content-type-acronym>_<P#>.<ext>.<V#>)

                    if uploadedFileNm.upper() != prevFileName.upper():
                        prevFileName = uploadedFileNm
                        for fileType in dpstrUploadFilesDict[ligId]:
                            if fileType in contentTypeDict['component-image'][0]:
                                for fileName in dpstrUploadFilesDict[ligId][fileType].keys():
                                    if fileName.upper() == uploadedFileNm.upper():
                                        self.__storeFile('component-image', p_ccADS, fileName, partitionId, fileType, ligId)

                            elif fileType in contentTypeDict['component-definition'][0] :
                                for fileName in dpstrUploadFilesDict[ligId][fileType].keys():
                                    if fileName.upper() == uploadedFileNm.upper():
                                        self.__storeFile('component-definition', p_ccADS, fileName, partitionId, fileType, ligId)

                            else:
                                if self.__verbose:
                                    self.__lfh.write("+%s.%s() ---------------WARNING---------------: Processing skipped for unexpected file type '%s' found for file(s) uploaded for ligid '%s'.\n" %  # noqa: E501
                                                     (className, methodName, fileType, ligId))

        #
        p_ccADS.dumpData(self.__lfh)

    def __storeFile(self, p_contentType, p_ccADS, p_fileName, p_partitionId, p_fileType, p_ligId):
        """ Method for copying any files uploaded by the depositor using LigandLite UI to deposit storage area for eventual use by annotation pipeline.
            Information regarding name/path information is stored in CC data store.
            This method is used by the deposition pipeline ChemCompWebAppLite

            :Params:

                + ``p_contentType``: currently can be one of 'component-sketch', 'component-image', 'component-definition'
                + ``p_ccADS``: reference to CC data store
                + ``p_fileName``: filename
                + ``p_partitionId``: P# is being used as vehicle for mapping between one ligand ID from another
                + ``p_fileType``: type as corresponds to file extension (e.g. png, sdf, etc)
                + ``p_ligId``: ligandID
        """
        className = self.__class__.__name__
        methodName = inspect.currentframe().f_code.co_name
        #
        fileHndlingCatalog = {'component-sketch': ('getChemCompSketchFilePath', 'setDpstrSketchFileWfPath'),
                              'component-image': ('getChemCompImageFilePath', 'setDpstrUploadFileWfPath'),
                              'component-definition': ('getChemCompDefntnFilePath', 'setDpstrUploadFileWfPath')}
        #
        ccE = ChemCompDataExport(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        # methods to be dynamically determined
        getExportPth = None
        recordWfPath = None
        #
        try:
            mthd0, mthd1 = fileHndlingCatalog[p_contentType]
            getExportPth = getattr(ccE, mthd0, None)
            recordWfPath = getattr(p_ccADS, mthd1, None)
            #
            filePth = os.path.join(self.__sessionPath, p_fileName)
            if self.__verbose and self.__debug:
                self.__lfh.write("+%s.%s() - depositor provided file determined to be: [%s].\n" % (className, methodName, filePth))
                self.__lfh.write("+%s.%s() - partitionCnt before calling getExportPth is: '%s'.\n" % (className, methodName, p_partitionId))
            wfFlPth = getExportPth(format=p_fileType, partitionNum=p_partitionId)
            wfDirPth = (os.path.split(wfFlPth))[0]
            if wfFlPth is not None and wfDirPth is not None and os.access(wfDirPth, os.R_OK) and os.access(filePth, os.R_OK):
                recordWfPath(p_ligId, p_fileType, p_fileName, wfFlPth)
                shutil.copyfile(filePth, wfFlPth)
                shutil.copyfile(filePth, os.path.join(wfDirPth, p_fileName))  # safety measure so as to retain copy of uploaded file as originally named
                p_ccADS.serialize()
                if self.__verbose:
                    self.__lfh.write("+%s.%s() - Copied depositor provided component file '%s' to workflow as '%s'.\n" % (className, methodName, filePth, wfFlPth))
            else:
                if self.__verbose:
                    self.__lfh.write("+%s.%s() - ERROR: Due to access problem depositor provided component file '%s' NOT copied to workflow at path: '%s'.\n" %
                                     (className, methodName, filePth, wfFlPth))
        except:  # noqa: E722 pylint: disable=bare-except
            if (self.__verbose):
                self.__lfh.write("+%s.%s() - failed to handle storage of depositor provided file:  %s\n" % (className, methodName, p_fileName))
                traceback.print_exc(file=self.__lfh)
                self.__lfh.flush()

    def __processCcDpstrInfoFile(self, pathToDpstrInfoFile):
        '''Called by annotation LigandModule
        '''
        className = self.__class__.__name__
        methodName = inspect.currentframe().f_code.co_name

        if (self.__verbose):
            self.__lfh.write("\n+++++%s.%s() -- STARTING\n" % (self.__class__.__name__,
                                                               inspect.currentframe().f_code.co_name))
            self.__lfh.flush()

        rtrnDict = {}
        dpstrInfoLst = []
        dpstrUploadLst = []
        dpstrRsrchLst = []

        #########################################################################################################
        # ['pdbx_chem_comp_depositor_info','pdbx_chem_comp_upload_depositor_info']:
        #########################################################################################################
        try:
            myContainerList = []
            if pathToDpstrInfoFile is not None and os.access(pathToDpstrInfoFile, os.R_OK):

                ifh = open(pathToDpstrInfoFile, "r")
                pRd = PdbxReader(ifh)
                pRd.read(myContainerList)
                c0 = myContainerList[0]
                #
                if (self.__verbose):
                    self.__lfh.write("\n%s.%s() -- about to parse 'pdbx_chem_comp_depositor_info' category from file: %s\n" % (self.__class__.__name__,
                                                                                                                               inspect.currentframe().f_code.co_name,
                                                                                                                               pathToDpstrInfoFile))
                    self.__lfh.flush()

                dpstrInfoLst = self.__extractCatFrmDpstrInfo(c0, 'pdbx_chem_comp_depositor_info', pathToDpstrInfoFile)
                if not len(dpstrInfoLst) > 0:
                    if (self.__verbose):
                        self.__lfh.write("\n%s.%s() -- Unable to find 'pdbx_chem_comp_depositor_info' category in file: %s\n" % (self.__class__.__name__,
                                                                                                                                 inspect.currentframe().f_code.co_name,
                                                                                                                                 pathToDpstrInfoFile))
                self.__lfh.flush()

                if (self.__verbose):
                    self.__lfh.write("\n%s.%s() -- about to parse 'pdbx_chem_comp_upload_depositor_info' category from file: %s\n" % (self.__class__.__name__,
                                                                                                                                      inspect.currentframe().f_code.co_name,
                                                                                                                                      pathToDpstrInfoFile))
                    self.__lfh.flush()

                dpstrUploadLst = self.__extractCatFrmDpstrInfo(c0, 'pdbx_chem_comp_upload_depositor_info', pathToDpstrInfoFile)
                if not len(dpstrUploadLst) > 0:
                    if (self.__verbose):
                        self.__lfh.write("\n%s.%s() -- Unable to find 'pdbx_chem_comp_upload_depositor_info' category in file: %s\n" % (self.__class__.__name__,
                                                                                                                                        inspect.currentframe().f_code.co_name,
                                                                                                                                        pathToDpstrInfoFile))
                self.__lfh.flush()

                dpstrRsrchLst = self.__extractCatFrmDpstrInfo(c0, 'pdbx_entity_instance_feature', pathToDpstrInfoFile)
                if not len(dpstrRsrchLst) > 0:
                    if (self.__verbose):
                        self.__lfh.write("\n%s.%s() -- Unable to find 'pdbx_entity_instance_feature' category in file: %s\n" % (self.__class__.__name__,
                                                                                                                                inspect.currentframe().f_code.co_name,
                                                                                                                                pathToDpstrInfoFile))
                self.__lfh.flush()

            else:
                if (self.__verbose):
                    self.__lfh.write("\n%s.%s() -- Unable to access file at: %s\n" % (self.__class__.__name__,
                                                                                      inspect.currentframe().f_code.co_name,
                                                                                      pathToDpstrInfoFile))
        except:  # noqa: E722 pylint: disable=bare-except
            if (self.__verbose):
                self.__lfh.write("+%s.%s() - failed to parse dpstr info file at:  %s\n" % (className, methodName, pathToDpstrInfoFile))
                traceback.print_exc(file=self.__lfh)
                self.__lfh.flush()

        rtrnDict['dpstrInfoList'] = dpstrInfoLst
        rtrnDict['dpstrUploadList'] = dpstrUploadLst
        rtrnDict['dpstrRsrchList'] = dpstrRsrchLst

        return rtrnDict

    def __extractCatFrmDpstrInfo(self, container, categoryNm, filename):

        rtrnLst = []

        catObj = container.getObj(categoryNm)
        if catObj is not None:
            if (self.__verbose):
                self.__lfh.write("\n%s.%s() -- '%s' cat obj found in dpstrInfo cif file.\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, categoryNm))

            #
            # Get column name index.
            #
            itDict = {}
            # itNameList=catObj.getItemNameList()
            attrNameList = catObj.getAttributeList()
            for idxIt, itAttribNm in enumerate(attrNameList):
                itDict[str(itAttribNm).lower()] = idxIt
            #
            for row in catObj.getRowList():
                if (self.__verbose):
                    self.__lfh.write("\n%s.%s() -- '%s' cat obj has row.\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, categoryNm))
                entryDict = {}
                try:
                    for k, v in itDict.items():
                        entryDict[k] = row[v]
                    rtrnLst.append(entryDict)
                except:  # noqa: E722 pylint: disable=bare-except
                    pass
        else:
            if (self.__verbose):
                self.__lfh.write("\n%s.%s() -- Unable to find '%s' category in file: %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, categoryNm, filename))

        return rtrnLst

    def __ccAssignOp(self, depDataSetId, pdbxPath, assignDirPath, ccAssignFilePath, ccLinkFilePath=None, ccBondRadii=None, ccTargetInstanceId=None, exactMatchOption=False):
        """Performs chemical component assignment calculation on PDBx format files - this will do assignments on the full pdbx file but
           apply parameter changes to specific instance.
        """
        try:
            siteId = self.__cI.get("SITE_PREFIX")
            #
            maxitCnvrtdCifFilePth = os.path.join(self.__sessionPath, depDataSetId + "-jmol-mdl.cif")
            #
            if (self.__verbose):
                self.__lfh.write("+ChemCompAssign.__ccAssignOp() - exactMatchOption is      : %s\n" % exactMatchOption)
            #
            if exactMatchOption is True:
                # operation = "chem-comp-assign-skip"
                operation = "chem-comp-assign-exact"
            else:
                operation = "chem-comp-assign"
            # use RcsbDpUtility to run the chem comp assignment search
            dpAssign = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=siteId)
            dpAssign.setWorkingDir(assignDirPath)
            dpAssign.addInput(name="id", value=depDataSetId)
            if (ccLinkFilePath is not None) and os.path.exists(ccLinkFilePath):
                dpAssign.addInput(name="cc_link_file_path", value=ccLinkFilePath, type='file')
            if ccBondRadii is not None:
                dpAssign.addInput(name="cc_bond_radii", value=ccBondRadii, type='param')
            if ccTargetInstanceId is not None:
                dpAssign.addInput(name="cc_instance_id", value=ccTargetInstanceId, type='param')
            dpAssign.imp(pdbxPath)
            dpAssign.op(operation)
            dpAssign.exp(ccAssignFilePath)
            # now use RcsbDpUtility to create a version of the coordinate data file that can be used for loading into jmol
            dpCnvrt = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=siteId, verbose=True)
            dpCnvrt.setWorkingDir(self.__sessionPath)
            dpCnvrt.imp(pdbxPath)
            dpCnvrt.op("cif2cif-pdbx-skip-process")
            dpCnvrt.exp(maxitCnvrtdCifFilePth)

            # if (self.__cleanUp): dp.cleanup()
            if self.__verbose:
                self.__lfh.write("+ChemCompAssign.__ccAssignOp() - PDBx file path      : %s\n" % pdbxPath)
                self.__lfh.write("+ChemCompAssign.__ccAssignOp() - CC assign file path : %s\n" % ccAssignFilePath)
                if not exactMatchOption:
                    self.__lfh.write("+ChemCompAssign.__ccAssignOp() - maxit converted cif file path: %s\n" % maxitCnvrtdCifFilePth)
                    self.__lfh.write("+ChemCompAssign.__ccAssignOp() - CC target instance  : %s\n" % ccTargetInstanceId)
                    self.__lfh.write("+ChemCompAssign.__ccAssignOp() - CC bond radii       : %s\n" % ccBondRadii)

            return True
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return False

    def __ccAssignOneInstanceOp(self, depDataSetId, ccTargetInstanceId, assignDirPath, ccAssignFilePath, ccLinkFilePath=None, ccBondRadii=None):
        """Performs chemical component assignment calculation on a single instance file assuming that a previous
           batch assignment has been already performed.
        """
        try:
            siteId = self.__cI.get("SITE_PREFIX")
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=siteId)
            dp.setWorkingDir(assignDirPath)
            dp.addInput(name="id", value=depDataSetId)
            if (ccLinkFilePath is not None) and os.path.exists(ccLinkFilePath):
                dp.addInput(name="cc_link_file_path", value=ccLinkFilePath, type='file')
            if ccBondRadii is not None:
                dp.addInput(name="cc_bond_radii", value=ccBondRadii, type='param')
            if ccTargetInstanceId is not None:
                dp.addInput(name="cc_instance_id", value=ccTargetInstanceId, type='param')
            #
            # Compute the path to the file -
            iFilePath = os.path.join(assignDirPath, ccTargetInstanceId, ccTargetInstanceId + '_coord.cif')
            dp.imp(iFilePath)
            dp.op("chem-comp-assign")

            dp.exp(ccAssignFilePath)
            # if (self.__cleanUp): dp.cleanup()
            if (self.__verbose):
                self.__lfh.write("+ChemCompAssign.__ccAssignOneInstanceOp() - instance file path  : %s\n" % iFilePath)
                self.__lfh.write("+ChemCompAssign.__ccAssignOneInstanceOp() - CC assign file path : %s\n" % ccAssignFilePath)
                self.__lfh.write("+ChemCompAssign.__ccAssignOneInstanceOp() - CC target instance  : %s\n" % ccTargetInstanceId)
                self.__lfh.write("+ChemCompAssign.__ccAssignOneInstanceOp() - CC bond radii       : %s\n" % ccBondRadii)
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return False

    def __ccAssignValidationOp(self, instId, compPath, assignVldtnDirPath, ccAssignVldtnFilePath, ccVldtnLogFile):
        """Performs validation checking on prospective ID being assigned to deposition chem components
        """
        if (self.__verbose):
            self.__lfh.write("+ChemCompAssign.__ccAssignValidationOp() - Starting\n")
            self.__lfh.write("+ChemCompAssign.__ccAssignValidationOp() - CC file path      : %s\n" % compPath)
            self.__lfh.write("+ChemCompAssign.__ccAssignValidationOp() - CC assign validation file path : %s\n" % ccAssignVldtnFilePath)
            self.__lfh.write("+ChemCompAssign.__ccAssignValidationOp() - CC instid validation list  : %s\n" % instId)
            self.__lfh.write("+ChemCompAssign.__ccAssignValidationOp() - CC validation reference file path  : %s\n" % self.__ccValidationRefFilePth)
        try:
            siteId = self.__cI.get("SITE_PREFIX")
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=siteId, verbose=True)
            dp.setWorkingDir(assignVldtnDirPath)
            dp.addInput(name="id", value=self.__reqObj.getValue("identifier"))
            dp.addInput(name="cc_validation_ref_file_path", value=self.__ccValidationRefFilePth, type='param')
            dp.addInput(name="cc_validation_instid_list", value=instId, type='param')
            dp.addInput(name="cc_validation_log_file", value=ccVldtnLogFile, type='param')
            dp.imp(compPath)
            dp.op("chem-comp-assign-validation")
            dp.exp(ccAssignVldtnFilePath)
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return False

    def __ccInstanceUpdateOp(self, pdbxInpPath, assignFileUpdtdPath, pdbxOutPath):
        """Performs chemical component assignment update operations on PDBx format model files.
        """
        try:
            #
            siteId = self.__cI.get("SITE_PREFIX")
            instncUpdateDirPath = os.path.join(self.__sessionPath, "cc-instance-update")
            instncUpdateLogPath = os.path.join(self.__sessionPath, "instncUpdate.log")
            if os.access(instncUpdateLogPath, os.R_OK):
                os.remove(instncUpdateLogPath)
            #
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=siteId)
            dp.setWorkingDir(instncUpdateDirPath)
            #
            if (assignFileUpdtdPath is not None) and os.path.exists(assignFileUpdtdPath):
                dp.addInput(name="cc_assign_file_path", value=assignFileUpdtdPath, type='file')
            #
            dp.imp(pdbxInpPath)
            dp.op("chem-comp-instance-update")
            dp.exp(pdbxOutPath)
            dp.expLog(instncUpdateLogPath)
            msg = ""
            if os.access(instncUpdateLogPath, os.R_OK):
                ifh = open(instncUpdateLogPath, "r")
                sIn = ifh.read().strip()
                ifh.close()
                #
                if (len(sIn) > 0) and (not sIn.endswith("Finished!")):
                    msg = sIn
                #
            #
            if not os.access(pdbxOutPath, os.R_OK):
                if msg != "":
                    msg += "\n"
                #
                msg += "Update model failed."
            #
            # if (self.__cleanUp): dp.cleanup()
            if (self.__verbose):
                self.__lfh.write("+ChemCompAssign.__ccInstanceUpdateOp() - PDBx file path:          %s\n" % pdbxInpPath)
                self.__lfh.write("+ChemCompAssign.__ccInstanceUpdateOp() - updated CC-assign file path:     %s\n" % assignFileUpdtdPath)
                self.__lfh.write("+ChemCompAssign.__ccInstanceUpdateOp() - PDBx output file path:   %s\n" % pdbxOutPath)
            #
            if msg != "":
                return False, msg
            #
            return True, msg
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return False, traceback.format_exc()

    def __syncTopHitsData(self, p_instId, p_tupL, p_assignDirPath, p_rnkdMtchL, p_absntCcRefL, p_state):
        """ For given instance ID, synchronizes info on top hits matches already captured with additional
            data from chem component files which is needed for display in instance searching UI

            :Params:

                + ``p_instId``: the instance ID for which Top Hits Data is being updated
                + ``p_tupL``: tuple representing a top hit record for the given instance ID, consists of (topHitCcId, topHitCcIdScore, matchWarning)
                        This tuple represents info that will be superceded with tuple containing fuller data set of (topHitCcId, topHitCcIdScore, matchWarning, ccName, ccFormula)
                + ``p_assignDirPath``: path of server directory housing assignment data
                + ``p_rnkdMtchL``: rnkdMtchL will serve as updated Top Hits list of tuples of form (topHitCcId, topHitCcIdScore, matchWarning, ccName, ccFormula)
                        This listing will be used to replace the incomplete listing currently contained in the datastore
                + ``p_absntCcRefL``: list of chem comp references still pending as we fetch data to be used in the instance search UI
                + ``p_state``: whether this method is being called on "first pass" or on a "return" visit

            :Helpers:
                wwpdb.apps.ccmodule.io.ChemCompIo.ChemCompReader
        """
        ccid = p_tupL[0]
        score = p_tupL[1]
        matchWarning = p_tupL[2]
        ccRefFilePath = os.path.join(p_assignDirPath, 'rfrnc_reports', ccid, ccid + '.cif')
        #
        if os.access(ccRefFilePath, os.R_OK):
            if self.__verbose:
                self.__lfh.write("+ChemCompAssign.__syncTopHitsData) - processing top hits for %s and reference chem comp file found on %s check: %s\n" %
                                 (p_instId, p_state, ccRefFilePath))

            ccRefR = ChemCompReader(self.__verbose, self.__lfh)
            ccRefR.setFilePath(filePath=ccRefFilePath)
            refD = {}
            ##################################################################################################
            #    Getting data contained in "chem_comp" cif category
            ##################################################################################################
            #
            try:
                refD = ccRefR.getChemCompDict()
                #
                chemCompName = refD.get('_chem_comp.name', "")
                chemCompFormula = refD.get('_chem_comp.formula', "")

                p_rnkdMtchL.append((ccid, score, matchWarning, chemCompName, chemCompFormula))
                if p_state == "return":
                    p_absntCcRefL.remove(p_tupL)
                    if self.__verbose:
                        self.__lfh.write("+ChemCompAssign.__syncTopHitsData() - processing top hits for %s, now have %s absent CC ids pending\n" % (p_instId, len(p_absntCcRefL)))
            except:  # noqa: E722 pylint: disable=bare-except
                if (self.__verbose):
                    self.__lfh.write("+ChemCompAssign.__syncTopHitsData() - failed while retrieving chem comp data on %s check for chem comp %s as candidate for %s\n" %
                                     (p_state, ccid, p_instId))
                    traceback.print_exc(file=self.__lfh)
                    self.__lfh.flush()
            #

        else:
            if p_state == "first pass":
                if self.__verbose:
                    self.__lfh.write("+ChemCompAssign.__syncTopHitsData() - processing top hits for %s and NO reference chem comp file found on first pass for %s\n" %
                                     (p_instId, ccRefFilePath))
                p_absntCcRefL.append(p_tupL)

    def __ccLinkOp(self, pdbxPath, ccLinkPath, ccLinkRadii=None):
        """Performs chemical component linkage calculation on PDBx format files.

        """
        try:
            #
            siteId = self.__cI.get("SITE_PREFIX")
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=siteId)
            pth = os.path.join(self.__sessionPath, 'cc-link')
            if (ccLinkRadii is not None):
                dp.addInput(name='cc_link_radii', value=ccLinkRadii, type='param')
            dp.setWorkingDir(pth)
            dp.imp(pdbxPath)
            dp.op("chem-comp-link")
            dp.exp(ccLinkPath)
            # if (self.__cleanUp): dp.cleanup()
            if (self.__verbose):
                self.__lfh.write("+ChemCompAssign.__ccLinkOp() - PDBx file path      : %s\n" % pdbxPath)
                self.__lfh.write("+ChemCompAssign.__ccLinkOp() - CC link file path   : %s\n" % ccLinkPath)
                self.__lfh.write("+ChemCompAssign.__ccLinkOp() - link radii extension: %s\n" % ccLinkRadii)
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return False

    def __isWorkflow(self):
        """ Determine if currently operating in Workflow Managed environment

            :Returns:
                boolean indicating whether or not currently operating in Workflow Managed environment
        """
        #
        fileSource = str(self.__reqObj.getValue("filesource")).lower()
        #
        if fileSource in ['archive', 'wf-archive', 'wf_archive', 'wf-instance', 'wf_instance', 'deposit']:
            # if the file source is any of the above then we are in the workflow manager environment
            return True
        else:
            # else we are in the standalone dev environment
            return False

    def __sortCompositeMatchScore(self, inMatchList):
        """
        """
        scale = (10000.0, 1000.0, 100.0, 10.0, 1.0)
        #
        matchListWithFloatScore = []
        for matchTup in inMatchList:
            total_score = 0.0
            compositeList = matchTup[1].split(" / ")
            if len(compositeList) == 5:
                for i in range(len(compositeList)):
                    # match_val = compositeList[i]
                    local_score = 0.0
                    try:
                        local_score = float(compositeList[i])
                    except:  # noqa: E722 pylint: disable=bare-except
                        if compositeList[i] == "match":
                            local_score = 100.0
                        #
                    #
                    total_score += (scale[i] * local_score) / 100.0
                #
            #
            matchListWithFloatScore.append((matchTup, total_score))
        #
        matchListWithFloatScore.sort(reverse=True, key=lambda match: match[1])
        #
        outMatchList = []
        for matchTup in matchListWithFloatScore:
            outMatchList.append(matchTup[0])
        #
        return outMatchList


if __name__ == '__main__':
    pass
#
