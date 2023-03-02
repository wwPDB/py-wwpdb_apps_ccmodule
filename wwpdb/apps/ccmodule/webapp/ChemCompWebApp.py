##
# File:  ChemCompWebApp.py
# Date:  25-Jul-2010
# Updates:
# 2010-08-09    jdw    Verify file upload for extract on Linux.
#                      All requests for session path information via SessionManager object.
# 2010-08-24    jdw    __newSession() -> __getSession() acquires existing session.
# 2010-08-24    jdw    Add edit methods -
# 2010-08-24    jdw    Add entry point for workflow launch.
#                      Add options to map session path to worflow instance file storage
#                      Revised session directory handling
# 2010-09-24    RPS    Added call stubs for handling save/close operations--currently these
#                      support communicating status (open|waiting|closed) to WF status DB. But
#                      functionality for persisting updates for session/archive yet to be implemented.
#                      Introduced use of HTML template for Batch Summary Results Display.
# 2010-10-05    RPS    _launchInstncSrchUi() added in support of instance searching interface ("Level 2" searching)
# 2010-10-08    RPS    _launchWfInstncSrchUi() added in support of instance searching interface ("Level 2" searching)
# 2010-10-11    RPS    Accommodating need to access supporting session datafiles under /workflow/ directory hierarchy
# 2010-11-22    RPS    Checkpoint update: introduced use of ReportHelperThread and added logging to track duration of specific
#                        assignment operations
# 2010-11-28    RPS    Updated to make use of ChemCompAssignDataStore class as vehicle for maintaining/updating assignment data
#                      Also updated _editLaunchOp to begin meeting needs of integrating new edit/create new ligand functionality
# 2010-11-30    RPS    Score for candidate matches now defined as XX/YY/ZZ where:
#                                XX = % of matched chiral centers over total chiral centers in the query
#                                YY = % of matched atoms over total atoms in the target
#                                ZZ = % of matched chiral centers over total chiral centers in the target
# 2010-12-02    RPS    Changes to accommodate more items being manipulated in tuple members of ChemCompAssignDataStore's TopHitsList
# 2010-12-03    RPS    Experimental ligand instances now using shared set of chem comp reference report material when the ligand instances
#                        are in the same entity group.
# 2010-12-03    RPS    Introduced functionality for registering assignment udpates with ChemCompAssignDataStore
# 2010-12-09    RPS    Updated __createCCassignDataStore() for handling of atom-level mapping data.
# 2010-12-10    RPS    WFE/M related code updated to mimic implementation used in standalone "rcsb" mode.
# 2010-12-15    RPS    Introducing support for rerunning chem comp searches with adjusted parameters.
#                      Also supporting reload of global summary of ligand processing on batch summary page.
# 2010-12-17    RPS    Updates to _reloadGlblSmmry(), _launchWfInstncSrchUi(), _launchInstncSrchUi(), _rerunEntityGrpSrch(), _rerunEntityGrpSrch()
#                        _rerunInstncSrch(), _assignInstnc(). Necessary to support proper location of supporting files when in WFM environment.
# 2011-01-03    RPS    Consolidating _launchWfInstncSrchUi() and _launchInstncSrchUi() into single _launchInstncSrchUi() method call.
#                        Also consolidating _launchWfOp() and _assignFileOp() into single _chemCompAssignOp() method call.
#                        Created helper method __isWorkflow() to determine whether or not working in context of Workflow Manager
# 2011-01-05    RPS    Divided functionality originally in _chemCompAssignOp() method into separate _launchBatchSrchSummary() and _chemCompAssignOp()
#                        methods in order to support immediate loading of Batch Search Summary page with subsequent ajax call populate page with
#                        assignment results summary.
# 2011-01-11    RPS    Updated with functionality for remembering parameters used for rerunning assignment searches with adjusted deltas for link and bond radii
#                        Also consolidated redundant code into __rerunAssgnSrch() method
# 2011-01-12    RPS    Added/changed order of calls to serialize chem comp data store in order to ensure that assignments were not getting lost during concomitant
#                        asynchronous requests for _assgnInstnc() for several instance IDs in context of "All Instance" interface mode.
# 2011-01-17    RPS    Updated to support persistence and retrieval of pickled cc assign details file that represents state of ligand instance processing/assignments
#                        This allows annotator user to save work in progress and resume at a later point.
# 2011-01-18    RPS    Added _newCcDefinedForInstnc(), _getNewCcIdForInstnc() in support of interaction with ligand editor component.
#                         _validateCcId() added for validation of CC IDs in cases of force assignment and future case of adding other CC IDs to comparison panel.
#                         _assignInstnc() updated to accommodate incoming list of instance IDs (for scenario of assigning via All Instances view).
#                         _chemCompAssignOp() corrected for whitespace error.
# 2011-01-25    RPS    __createDataStore() updated to replace "?" (i.e. null) with "n.a." for components of the composite score.
# 2011-02-03    RPS    Updated validateCcId to leverage more comprehensive validation strategy.
# 2011-02-09    RPS    __createDataStore() and __updateDataStoreForEntityGrp() updated to handle cases where no top hits are found for given ligands
# 2011-02-16    RPS    _launch3dEnvironView() added.
# 2011-02-22    RPS    _generateEntityBrowser() added and _launchBatchSrchSummary() updated as per new strategy of having Batch Search Summary View
#                        and Instance Searching View reside on single web page/browser window.
# 2011-03-04    RPS    _launch3dEnvironView() and _launchBatchSrchSummary() updated to support provision of 3D environment view within same webpage as Chem Component Searching UI
# 2011-03-04    RPS    _getNonCandidate() added to support comparison of arbitrary non-candidate chem components in dictionary to ligand in question.
#                          _validateCcId() updated to support "full" vs. "simple" modes of validation
# 2011-03-31    RPS    launch3dEnvironView() updated to accommodate proper handling of TMP_IDs when files are uploaded for processing on shared server
# 2011-05-17    RPS     _rerunInstncSrch() updated to call ChemCompAssignDepict.doRender_InstanceProfile()
# 2011-05-25    RPS    _getNonCandidate() renamed to getNewCandidate() to minimize confusion.
#                      _viewOp() method updated for new stand-alone Ligand Editor tool
#                      synchronizeDataStore() method created in order to replace instances of redundant code for handling
#                            synchronization of data store with chem comp assign results info.
# 2011-06-14    RPS    __createDataStore(), __updateDataStoreForInstnc(), and __synchronizeDataStore() moved to ChemCompAssign class to improve cohesion
# 2011-06-23    RPS    __updateWfTrackingDb() created. Functionality for rendering cc assign batch search summary and 3d environ view moved to
#                      ChemCompAssignDepict class. ChemCompWebAppWorker URL identifiers reorganized.
# 2011-06-30    jdw    Various path changes for PDBe configuration --
# 2011-06-23    RPS    Restored URL mapping for registering newly created CC ID (had been erroneously deleted)
# 2011-07-07    RPS    Applied fix (interim?) for creating usable "WorkflowPath"
#                      Updated check for isWorkflow to check for "wf_instance" as valid filesource
# 2011-07-08    RPS    Code cleanup/removed obsolete methods. _ccAssign_validateCcId() updated to obtain path to cc dictionary reference files via ChemCompConfig method
# 2011-07-13    RPS    Updated with comments in support of generating "restructuredtext" documentation
# 2011-08-01    RPS    ccAssign_rerunInstncSrch() updated to use new function signature for ChemCompAssignDepict.doRender_InstanceProfile().
# 2011-08-10    RPS    Updated to accommodate decoupling of directory used for files created/manipulated for given user session from directory used for
#                          Workflow Management data storage. Change primarily impacted self.__getSession() function, which no longer diverts creation of session specific
#                          directories to WFM directory structure in context of WFM operation. Instead creates "sessions" directory as direct child of configured "Top Path"
# 2011-08-24    RPS    _editLaunchOp() updated to fix error in defining path needed by editor for locating support files needed for the given session
# 2011-09-15    RPS    Modified in order to adopt strategy of process forking so that child processes assume workload for chem-comp-assign searching and for
#                        generation of report material used for instance-level interface.
# 2011-09-22    RPS    topPath now being derived from ConfigInfoData based on siteId value.
# 2011-11-18    RPS    Interim changes to allow further development of stand alone ligand tool functionality such as cc-extract within the
#                        consolidated common tool setup.
# 2012-03-27    RPS    Updated to reflect improved organization of html template files as stored on server.
# 2012-06-11    RPS    Updated __saveLigModState so that it additionally generates "chem-comp-select" file that captures annotator chem comp assignment selections
#                        and which is used as input for update of the model file.
# 2012-07-03    RPS    Updated __saveLigModState. Creation of "chem-comp-select" file no longer necessary. Instead generating updated cc-assign cif file
#                        that captures annotator chem comp assignment selections and which is used as input for update of the model file.
# 2012-10-05    RPS    __saveLigModState() updated to reflect simplification of ChemCompAssign.saveState() signature/argument list.
# 2012-10-10    RPS    Now deriving path of sessions directory from ConfigInfoData.
# 2012 12-05    jdw    Add sketchOp() sketchSaveOp()
# 2013-03-05    ZF     added _ccAssign_rerunInstncCompSrch() to support for assignment using chemical component file
# 2013-03-22    RPS    'cif' content format no longer valid so replaced with 'pdbx' when getting valid file/path reference for coordinate model file.
# 2013-04-08    RPS    Corrected to apply correct version numbers on files persisted to workflow storage.
#                        Introducing use of ChemCompDataExport to manage export of files to workflow storage.
# 2013-04-17    ZF     Add checking if assgnCcId is in HitList in _ccAssign_assignInstnc()
#                      Updated _ccAssign_validateCcId(), return error message instead of status code
# 2013-06-25    RPS    Updated _ccAssign_generateBatchData() to reflect simplified return object coming back from call to
#                        ChemCompAssign.doAssign() method.
# 2013-10-22    RPS    Updated to support data propagation from DepUI/LigLite.
# 2013-11-04    ZF     Add extract pdbid information functionality
# 2013-12-02    RPS    Fixed bug in __importDepositorFiles() affecting proper handling of files uploaded by depositor.
# 2013-12-11    RPS    Fixed bug affecting generation of 2D images occurring only on revisits to LigMod.
# 2014-02-11    RPS    Now importing WfTracking from wwpdb.api.status.dbapi.WfTracking (instead of from wwpdb.apps.ccmodule.utils.WfTracking)
# 2014-05-22    RPS    Updates to support display of entry title in header of webpage.
# 2014-10-22    ZF     Allow special ion water complex ligands to be forced matched in _ccAssign_validateCcId
# 2014-11-03    ZF     Add ChemCompAlignImageGenerator class in _ccAssign_getNewCandidate & __generateInstanceLevelData to generate aligned images
# 2015-03-01    ZF     Re-implemented _ccAssign_generateBatchData()
# 2019-11-12    ZF     Added option for deposition id input in standalone mode
# 2020-08-27    ZF     Added blocking 'REF_ONLY' status ligands
#
##
"""
Chemical component editor tool web request and response processing modules.

This software was developed as part of the World Wide Protein Data Bank
Common Deposition and Annotation System Project

Copyright (c) 2010 wwPDB

This software is provided under a Creative Commons Attribution 3.0 Unported
License described at http://creativecommons.org/licenses/by/3.0/.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.07"

import os
import sys
import time
import traceback
import ntpath
import shutil
from time import localtime, strftime
import inspect

from wwpdb.utils.session.WebRequest import InputRequest, ResponseContent
#
from wwpdb.apps.ccmodule.view.ChemCompView import ChemCompView
#
from wwpdb.apps.ccmodule.chem.ChemCompAssign import ChemCompAssign
from wwpdb.apps.ccmodule.chem.ChemCompAssignDepict import ChemCompAssignDepict
#
from wwpdb.apps.ccmodule.search.ChemCompSearch import ChemCompSearch
from wwpdb.apps.ccmodule.search.ChemCompSearchDepict import ChemCompSearchDepict
from wwpdb.apps.ccmodule.search.ChemCompSearchDb import ChemCompSearchDb
from wwpdb.apps.ccmodule.search.ChemCompSearchDbDepict import ChemCompSearchDbDepict
#
from wwpdb.apps.ccmodule.reports.ChemCompAlignImageGenerator import ChemCompAlignImageGenerator
from wwpdb.apps.ccmodule.reports.ChemCompReports import ChemCompReport
from wwpdb.apps.ccmodule.reports.InstanceDataGenerator import InstanceDataGenerator
from wwpdb.apps.ccmodule.sketch.ChemCompSketch import ChemCompSketch
from wwpdb.apps.ccmodule.sketch.ChemCompSketchDepict import ChemCompSketchDepict
#
from wwpdb.utils.wf.dbapi.WfTracking import WfTracking
from wwpdb.apps.ccmodule.utils.ChemCompConfig import ChemCompConfig
#
from wwpdb.apps.ccmodule.io.ChemCompAssignDataStore import ChemCompAssignDataStore
from wwpdb.apps.ccmodule.io.ChemCompDataImport import ChemCompDataImport
from wwpdb.apps.ccmodule.io.ChemCompDataExport import ChemCompDataExport
from wwpdb.apps.ccmodule.io.ChemCompIo import ChemCompReader
#
from wwpdb.utils.config.ConfigInfo import ConfigInfo
from wwpdb.utils.config.ConfigInfoApp import ConfigInfoAppCommon
#
from wwpdb.io.file.mmCIFUtil import mmCIFUtil
#
from wwpdb.utils.oe_util.oedepict.OeDepict import OeDepict
from wwpdb.utils.oe_util.build.OeBuildMol import OeBuildMol
#
from wwpdb.io.locator.PathInfo import PathInfo
from wwpdb.utils.dp.RcsbDpUtility import RcsbDpUtility


class ChemCompWebApp(object):
    """Handle request and response object processing for the chemical component editor tool application.

    """
    def __init__(self, parameterDict=None, verbose=False, log=sys.stderr, siteId="WWPDB_DEV"):
        """
        Create an instance of `ChemCompWebApp` to manage a ligand editor web request.

         :param `parameterDict`: dictionary storing parameter information from the web request.
             Storage model for GET and POST parameter data is a dictionary of lists.
         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        if parameterDict is None:
            parameterDict = {}
        self.__verbose = verbose
        self.__lfh = log
        self.__debug = False
        self.__siteId = siteId
        self.__cI = ConfigInfo(self.__siteId)
        self.__cICommon = ConfigInfoAppCommon(self.__siteId)
        self.__topPath = self.__cI.get('SITE_WEB_APPS_TOP_PATH')
        self.__topSessionPath = self.__cICommon.get_site_web_apps_top_sessions_path()
        self.__sessionsPath = self.__cICommon.get_site_web_apps_sessions_path()
        self.__templatePath = os.path.join(self.__topPath, "htdocs", "ccmodule")
        #

        if isinstance(parameterDict, dict):
            self.__myParameterDict = parameterDict
        else:
            self.__myParameterDict = {}

        if (self.__verbose):
            self.__lfh.write("+ChemCompWebApp.__init() - REQUEST STARTING ------------------------------------\n")
            self.__lfh.write("+ChemCompWebApp.__init() - dumping input parameter dictionary \n")
            self.__lfh.write("%s" % (''.join(self.__dumpRequest())))

        self.__reqObj = InputRequest(self.__myParameterDict, verbose=self.__verbose, log=self.__lfh)
        #
        self.__reqObj.setValue("TopSessionPath", self.__topSessionPath)
        self.__reqObj.setValue("SessionsPath", self.__sessionsPath)
        self.__reqObj.setValue("TemplatePath", self.__templatePath)
        self.__reqObj.setValue("TopPath", self.__topPath)
        self.__reqObj.setValue("WWPDB_SITE_ID", self.__siteId)
        os.environ["WWPDB_SITE_ID"] = self.__siteId
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        #
        if (self.__debug):
            self.__lfh.write("-----------------------------------------------------\n")
            self.__lfh.write("+ChemCompWebApp.__init() Leaving _init with request contents\n")
            self.__reqObj.printIt(ofh=self.__lfh)
            self.__lfh.write("---------------ChemCompWebApp - done -------------------------------\n")
            self.__lfh.flush()

    def doOp(self):
        """ Execute request and package results in response dictionary.

        :Returns:
             A dictionary containing response data for the input request.
             Minimally, the content of this dictionary will include the
             keys: CONTENT_TYPE and REQUEST_STRING.
        """
        stw = ChemCompWebAppWorker(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        rC = stw.doOp()
        if (self.__debug):
            rqp = self.__reqObj.getRequestPath()
            self.__lfh.write("+ChemCompWebApp.doOp() operation %s\n" % rqp)
            self.__lfh.write("+ChemCompWebApp.doOp() return format %s\n" % self.__reqObj.getReturnFormat())
            if rC is not None:
                if self.__debug:
                    self.__lfh.write("%s" % (''.join(rC.dump())))
            else:
                self.__lfh.write("+ChemCompWebApp.doOp() return object is empty\n")

        #
        # Package return according to the request return_format -
        #
        return rC.get()

    def __dumpRequest(self):
        """Utility method to format the contents of the internal parameter dictionary
           containing data from the input web request.

           :Returns:
               ``list`` of formatted text lines
        """
        retL = []
        retL.append("\n-----------------ChemCompWebApp().__dumpRequest()-----------------------------\n")
        retL.append("Parameter dictionary length = %d\n" % len(self.__myParameterDict))
        for k, vL in self.__myParameterDict.items():
            retL.append("Parameter %30s :" % k)
            for v in vL:
                retL.append(" ->  %s\n" % v)
        retL.append("-------------------------------------------------------------\n")
        return retL


class ChemCompWebAppWorker(object):
    def __init__(self, reqObj=None, verbose=False, log=sys.stderr):
        """
         Worker methods for the chemical component editor application

         Performs URL - application mapping and application launching
         for chemical component editor tool.

         All operations can be driven from this interface which can
         supplied with control information from web application request
         or from a testing application.
        """
        self.__verbose = verbose
        self.__lfh = log
        self.__reqObj = reqObj
        self.__sObj = None
        self.__sessionId = None
        self.__sessionPath = None
        self.__rltvSessionPath = None
        self.__siteId = str(self.__reqObj.getValue("WWPDB_SITE_ID"))
        self.__cI = ConfigInfo(self.__siteId)
        self.__ccConfig = ChemCompConfig(reqObj, verbose=self.__verbose, log=self.__lfh)
        self.__modelFilePath = None
        #
        self.__pathInstncsVwTmplts = "templates/workflow_ui/instances_view"
        self.__pathSnglInstcTmplts = self.__pathInstncsVwTmplts + "/single_instance"
        self.__pathSnglInstcEditorTmplts = self.__pathSnglInstcTmplts + "/editor"
        #
        self.__appPathD = {'/service/environment/dump': '_dumpOp',
                           '/service/cc/view': '_viewOp',
                           '/service/cc/adminops': '_dumpOp',
                           '/service/cc/search/cc-index': '_searchIndexOp',
                           '/service/cc/search/cc-db': '_searchDbOp',
                           '/service/cc/search/cc-graph': '_searchGraphOp',
                           '/service/cc/report': '_reportOp',
                           '/service/cc/edit/launch': '_editLaunchOp',
                           '/service/cc/chopper/launch': '_chopLaunchOp',
                           '/service/cc/assign-file': '_ccAssign_BatchSrchSummary',
                           '/service/cc/new-session/wf': '_ccAssign_BatchSrchSummary',
                           '/service/cc/new_session/wf': '_ccAssign_BatchSrchSummary',
                           # ##############  below are URLs created for WFM/common tool development effort######################
                           '/service/cc/assign/wf/new_session': '_ccAssign_BatchSrchSummary',
                           '/service/cc/assign/view/batch': '_ccAssign_generateBatchData',
                           '/service/cc/assign/view/batch/data_check': '_ccAssign_checkForBatchData',
                           '/service/cc/assign/view/batch/data_load': '_ccAssign_loadBatchSmmry',
                           '/service/cc/assign/view/instance': '_ccAssign_generateEntityBrowser',
                           '/service/cc/assign/assign-instance': '_ccAssign_assignInstnc',
                           '/service/cc/assign/assign_instance': '_ccAssign_assignInstnc',
                           '/service/cc/assign/rerun-instnc-srch': '_ccAssign_rerunInstncSrch',
                           '/service/cc/assign/rerun_instnc_srch': '_ccAssign_rerunInstncSrch',
                           '/service/cc/assign/rerun_instnc_comp_srch': '_ccAssign_rerunInstncCompSrch',
                           '/service/cc/assign/rerun-entitygrp-srch': '_ccAssign_rerunEntityGrpSrch',
                           '/service/cc/assign/rerun_entitygrp_srch': '_ccAssign_rerunEntityGrpSrch',
                           '/service/cc/assign/view/batch/refresh': '_ccAssign_reloadGlblSmmry',
                           '/service/cc/assign/view/instance/new_ccid_defined': '_ccAssign_setNewCcDefinedForInstnc',
                           '/service/cc/assign/view/instance/get_new_ccid': '_ccAssign_getNewCcIdForInstnc',
                           '/service/cc/assign/validate_ccid': '_ccAssign_validateCcId',
                           '/service/cc/assign/view/instance/3d_environ': '_ccAssign_3dEnvironView',
                           '/service/cc/assign/view/instance/get_new_candidate': '_ccAssign_getNewCandidate',
                           '/service/cc/assign/wf/exit_not_finished': '_ccAssign_exit_notFinished',
                           '/service/cc/assign/wf/exit_finished': '_ccAssign_exit_Finished',
                           '/service/cc/assign/view/dpstr_info': '_viewDpstrInfo',
                           ###################################################################################################
                           '/service/cc/sketch': '_sketchOp',
                           '/service/cc/sketch-save': '_sketchSaveOp'
                           }

    def doOp(self):
        """Map operation to path and invoke operation.

            :Returns:

            Operation output is packaged in a ResponseContent() object.
        """
        return self.__doOpException()

    def __doOpNoException(self):  # pylint: disable=unused-private-member
        """Map operation to path and invoke operation.  No exception handling is performed.

            :Returns:

            Operation output is packaged in a ResponseContent() object.
        """
        #
        reqPath = self.__reqObj.getRequestPath()
        if reqPath not in self.__appPathD:
            # bail out if operation is unknown -
            rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            rC.setError(errMsg='Unknown operation')
            return rC
        else:
            mth = getattr(self, self.__appPathD[reqPath], None)
            rC = mth()
        return rC

    def __doOpException(self):
        """Map operation to path and invoke operation.  Exceptions are caught within this method.

            :Returns:

            Operation output is packaged in a ResponseContent() object.
        """
        #
        try:
            reqPath = self.__reqObj.getRequestPath()
            if reqPath not in self.__appPathD:
                # bail out if operation is unknown -
                rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
                rC.setError(errMsg='Unknown operation')
            else:
                mth = getattr(self, self.__appPathD[reqPath], None)
                rC = mth()
            return rC
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            rC.setError(errMsg='Operation failure')
            return rC

    ################################################################################################################
    # ------------------------------------------------------------------------------------------------------------
    #      Top-level REST methods
    # ------------------------------------------------------------------------------------------------------------
    #
    def _dumpOp(self):
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        rC.setHtmlList(self.__reqObj.dump(format='html'))
        return rC

    def _viewOp(self):
        """ Call to display data for given chem component in comparison grid of standalone version of chem comp module.
            Delegates primary processing to ChemCompView class.

            :Helpers:
                wwpdb.apps.ccmodule.view.ChemCompView.ChemCompView

            :Returns:
                Operation output is packaged in a ResponseContent() object.
        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompWebAppWorker._viewOp() starting\n")
        #
        self.__getSession()
        sessionId = self.__sessionId
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._viewOp() session ID is: %s\n" % sessionId)
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        ccV = ChemCompView(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        rtrnCode = ccV.doView()
        #
        if self.__verbose:
            self.__lfh.write("+ChemCompWebAppWorker._viewOp() - return code is %s\n" % str(rtrnCode))

        rC.addDictionaryItems({'sessionid': str(sessionId)})
        rC.setStatusCode(str(rtrnCode))

        return rC

    def _sketchOp(self):
        """  Lauch chemical sketch applet (MarvinSketch) on the input chemical component definition id/file.


             jdw - Currently tested using input parameters ccid=XXX and pulling defintion files from
                   the working copy of the chemical component repository.
        """
        #
        isFile = False
        self.__getSession()

        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._sketchOp() sessionId %s \n" % self.__sessionId)

        self.__reqObj.setReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        if self.__isFileUpload():
            # make a copy of the file in the session directory and set 'fileName'
            self.__uploadFile()
            isFile = True
        #
        ccId = self.__reqObj.getValue('ccid')
        inputFormat = self.__reqObj.getValue('inputformat')
        #
        ccSk = ChemCompSketch(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        if isFile:
            filePath = os.path.join(self.__sessionPath, self.__reqObj.getValue("fileName"))
            if len(ccId) > 0:
                ccSk.setFilePath(filePath, inputFormat, ccId=ccId)
            else:
                ccSk.setFilePath(filePath, inputFormat)
        else:
            ccSk.setCcId(ccId)

        rD = ccSk.doSketch()
        if len(rD) > 0:
            cvD = ChemCompSketchDepict(self.__verbose, self.__lfh)
            oL = cvD.doRender(rD)
            rC.setHtmlList(oL)
        else:
            rC.setError(errMsg='No component data found')

        return rC

    def _sketchSaveOp(self):
        """  Catch the output of the sketch applet (MarvinSketch) that is returned as in
             SDF format as a string in input parameter molData.

             Currently just saving this file in the session directory.
        """
        #
        # isFile = False
        self.__getSession()

        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._sketchSaveOp() sessionId %s \n" % self.__sessionId)

        self.__reqObj.setReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        ccId = self.__reqObj.getValue('ccid')
        # inputFormat = self.__reqObj.getValue('inputformat')
        molData = self.__reqObj.getValue('MolData')
        #
        try:
            fp = os.path.join(self.__sessionPath, ccId, ccId + '-sketch.sdf')
            ofh = open(fp, 'w')
            ofh.write("%s\n" % molData)
            ofh.close()
            rC.setHtmlList(["Saved file %s" % fp])
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            rC.setError(errMsg='SketchSaveOp - file save failed')
        #
        # ccSk=ChemCompSketch(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
        return rC

    def _editLaunchOp(self):
        """ Launch chemical component editor

            :Returns:
                Operation output is packaged in a ResponseContent() object.
        """
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._editLaunchOp() \n")
        #

        sessionId = str(self.__reqObj.getValue("sessionid"))
        depId = str(self.__reqObj.getValue("identifier")).upper()
        instanceId = str(self.__reqObj.getValue("instanceid"))
        fileSource = str(self.__reqObj.getValue("filesource")).lower()
        wfInstId = str(self.__reqObj.getValue("instance")).upper()
        #
        self.__getSession()
        #
        # self.__reqObj.setDefaultReturnFormat(return_format="html")
        self.__reqObj.setReturnFormat(return_format='json')
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        relatedInstanceIds = ''
        bIsWorkflow = self.__isWorkflow()
        if bIsWorkflow:
            t_depId = depId.upper()
        else:
            t_depId = depId.lower()
        #
        pickleFilePath = os.path.join(self.__sessionPath, 'assign', t_depId + '-cc-assign-details.pic')
        if os.access(pickleFilePath, os.R_OK):
            ccAssignDataStore = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
            ccId = ccAssignDataStore.getAuthAssignment(instanceId)
            instIdLst = ccAssignDataStore.getAuthAssignmentKeys()
            if ccId and instIdLst:
                relatedInstList = []
                for instId in instIdLst:
                    if instId == instanceId:
                        continue
                    #
                    rccId = ccAssignDataStore.getAuthAssignment(instId)
                    if rccId != ccId:
                        continue
                    #
                    relatedInstList.append(instId)
                #
                if relatedInstList:
                    relatedInstanceIds = ",".join(relatedInstList)
                #
            #
        #

        ###########################################################################
        # create dictionary of content that will be used to populate HTML template
        ###########################################################################
        myD = {}
        myD['sessionid'] = sessionId
        myD['depositionid'] = depId
        myD['instanceid'] = instanceId
        myD['related_instanceids'] = relatedInstanceIds
        myD['filesource'] = fileSource
        myD['identifier'] = depId
        myD['instance'] = wfInstId
        myD['pdbid'] = str(self.__reqObj.getValue("pdbid"))
        myD['annotator'] = str(self.__reqObj.getValue("annotator"))
        #
        myD['session_url_prefix'] = os.path.join(self.__rltvSessionPath, "assign", instanceId)
        myD['processing_site'] = self.__cI.get('SITE_NAME').upper()
        rC.setHtmlText(htmlText=self.__processTemplate(fn=os.path.join(self.__pathSnglInstcEditorTmplts, "cc_instnc_edit_tmplt.html"), parameterDict=myD))
        return rC

    def _chopLaunchOp(self):
        """ Launch chemical component chopper

            :Returns:
                Operation output is packaged in a ResponseContent() object.
        """
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._chopLaunchOp() \n")
        #

        sessionId = str(self.__reqObj.getValue("sessionid"))
        depId = str(self.__reqObj.getValue("identifier")).upper()
        instanceId = str(self.__reqObj.getValue("instanceid"))
        fileSource = str(self.__reqObj.getValue("filesource")).lower()
        wfInstId = str(self.__reqObj.getValue("instance")).upper()
        #
        self.__getSession()
        #
        # self.__reqObj.setDefaultReturnFormat(return_format="html")
        self.__reqObj.setReturnFormat(return_format='json')
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #

        ###########################################################################
        # create dictionary of content that will be used to populate HTML template
        ###########################################################################
        myD = {}
        myD['sessionid'] = sessionId
        myD['depositionid'] = depId
        myD['instanceid'] = instanceId
        myD['filesource'] = fileSource
        myD['identifier'] = depId
        myD['instance'] = wfInstId
        myD['pdbid'] = str(self.__reqObj.getValue("pdbid"))
        myD['annotator'] = str(self.__reqObj.getValue("annotator"))
        #
        myD['session_url_prefix'] = os.path.join(self.__rltvSessionPath, "assign", instanceId)
        myD['processing_site'] = self.__cI.get('SITE_NAME').upper()
        rC.setHtmlText(htmlText=self.__processTemplate(fn=os.path.join(self.__pathSnglInstcEditorTmplts, "cc_instnc_chop_tmplt.html"), parameterDict=myD))
        return rC

    def _ccAssign_3dEnvironView(self):
        """ Handle request from instance search view of chem comp assign interface
            for launch of 3D viewer of experimental chem component within
            author's entire structure (in separate browser window/tab)

            :Helpers:
                wwpdb.apps.ccmodule.chem.ChemCompAssignDepict.ChemCompAssignDepict

            :Returns:
                Operation output is packaged in a ResponseContent() object.
        """
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_3dEnvironView() \n")
        # determine if currently operating in Workflow Managed environment
        bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        ccAD = ChemCompAssignDepict(self.__verbose, self.__lfh)
        ccAD.setSessionPaths(self.__reqObj)
        oL = ccAD.doRender_3dEnvironView(self.__reqObj, bIsWorkflow)
        rC.setHtmlText('\n'.join(oL))
        #
        return rC

    def _viewDpstrInfo(self):
        """ Handle request from instance search view of chem comp assign interface
            for launch of separate window to view depositor provided info

            :Helpers:
                wwpdb.apps.ccmodule.chem.ChemCompAssignDepict.ChemCompAssignDepict

            :Returns:
                Operation output is packaged in a ResponseContent() object.
        """
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._viewDpstrInfo() \n")
        # determine if currently operating in Workflow Managed environment
        bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        ccAD = ChemCompAssignDepict(self.__verbose, self.__lfh)
        ccAD.setSessionPaths(self.__reqObj)
        oL = ccAD.doRender_dpstrInfoView(self.__reqObj, bIsWorkflow)
        rC.setHtmlText('\n'.join(oL))
        #
        return rC

    def _ccAssign_BatchSrchSummary(self):
        """ Launch chemical component module first-level interface, i.e. Batch Search Summary of Chem Comp Assignment Results

            :Helpers:
                wwpdb.apps.ccmodule.chem.ChemCompAssignDepict.ChemCompAssignDepict

            :Returns:
                Operation output is packaged in a ResponseContent() object.
                The output consists of a HTML starter container page for quicker return to the client.
                This container page is then populated with content via AJAX calls.
        """
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_BatchSrchSummary() Starting now\n")
        # determine if currently operating in Workflow Managed environment
        bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_BatchSrchSummary() workflow flag is %r\n" % bIsWorkflow)

        if bIsWorkflow:
            # Update WF status database --
            bSuccess = self.__updateWfTrackingDb("open")
            if not bSuccess:
                rC.setError(errMsg="+ChemCompWebAppWorker._ccAssign_BatchSrchSummary() - TRACKING status, update to 'open' failed for session %s \n" % self.__sessionId)
                return rC
            else:
                if (self.__verbose):
                    self.__lfh.write("+ChemCompWebAppWorker._ccAssign_BatchSrchSummary() Tracking status set to open\n")
            pI = PathInfo(siteId=self.__siteId, sessionPath=self.__sessionPath, verbose=self.__verbose, log=self.__lfh)
            self.__modelFilePath = pI.getFilePath(dataSetId=self.__reqObj.getValue('identifier').upper(),
                                                  wfInstanceId=self.__reqObj.getValue('instance'),
                                                  contentType='model', formatType='pdbx',
                                                  fileSource=str(self.__reqObj.getValue("filesource")).lower(),
                                                  versionId='latest', partNumber=1)
        else:
            depId = str(self.__reqObj.getValue('identifier')).upper().strip()
            if depId:
                pI = PathInfo(siteId=self.__siteId, sessionPath=self.__sessionPath, verbose=self.__verbose, log=self.__lfh)
                archiveFilePath = pI.getFilePath(dataSetId=depId, wfInstanceId=None, contentType='model', formatType='pdbx', fileSource="archive")
                if archiveFilePath and os.access(archiveFilePath, os.R_OK):
                    self.__modelFilePath = pI.getFilePath(dataSetId=depId, wfInstanceId=None, contentType='model', formatType='pdbx', fileSource="session")
                    shutil.copyfile(archiveFilePath, self.__modelFilePath)
                    self.__reqObj.setValue("filePath", self.__modelFilePath)
                    self.__reqObj.setValue("identifier", depId)
                else:
                    rC.setError(errMsg='Invalid Deposition ID: ' + depId)
                    return rC
                #
            elif self.__isFileUpload():
                self.__uploadFile()
            else:
                rC.setError(errMsg='No Deposition ID input & file uploaded')
                return rC
            #
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_BatchSrchSummary() Call ChemCompAssignDepict with workflow %r\n" % bIsWorkflow)

        # # Added by ZF
        if self.__modelFilePath and os.access(self.__modelFilePath, os.R_OK):
            cifObj = mmCIFUtil(filePath=self.__modelFilePath)
            dlist = cifObj.GetValue('database_2')
            for dir in dlist:  # pylint: disable=redefined-builtin
                if ('database_id' not in dir) or ('database_code' not in dir):
                    continue
                #
                dbname = dir['database_id'].upper()
                dbcode = dir['database_code'].upper()
                if dbname == 'PDB':
                    self.__reqObj.setValue("pdbid", dbcode)
                    break
                #
            #
            slist = cifObj.GetValue('struct')
            for dir in slist:
                if 'title' not in dir:
                    continue
                #
                entryTitle = dir['title']
                self.__reqObj.setValue("entry_title", entryTitle)
                break
        # # END

        ccAD = ChemCompAssignDepict(self.__verbose, self.__lfh)
        ccAD.setSessionPaths(self.__reqObj)
        oL = ccAD.doRender_BatchSrchSummaryContainer(self.__reqObj, bIsWorkflow)
        rC.setHtmlText('\n'.join(oL))
        #
        return rC

    def _ccAssign_generateBatchData(self):
        """ Generate chem comp summary results for entire deposition data set
            Child process is spawned to allow summary results to be gathered
            while parent process completes simply by returning status of "running"
            to the client.

            :Helpers:
                wwpdb.apps.ccmodule.chem.ChemCompAssign.ChemCompAssign

            :Returns:
                JSON object with status code of "running" returned.

            Re-implemented by ZF
        """
        self.__getSession()
        depId = str(self.__reqObj.getValue("identifier"))
        #
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+%s.%s() starting\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
            self.__lfh.write("+%s.%s() identifier   %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, depId))
            self.__lfh.write("+%s.%s() workflow instance     %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, self.__reqObj.getValue("instance")))
            self.__lfh.write("+%s.%s() file source  %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, self.__reqObj.getValue("filesource")))
            self.__lfh.write("+%s.%s() sessionId  %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, self.__sessionId))
            self.__lfh.flush()
        #
        sph = self.__setSemaphore()
        if (self.__verbose):
            self.__lfh.write("+%s.%s() Just before fork to create child process w/ separate log generated in session directory.\n" %
                             (self.__class__.__name__, inspect.currentframe().f_code.co_name))
        pid = os.fork()
        if pid == 0:
            os.setsid()
            sub_pid = os.fork()
            if sub_pid:
                # Parent of second fork
                os._exit(0)  # pylint: disable=protected-access

            # determine if currently operating in Workflow Managed environment
            bIsWorkflow = self.__isWorkflow()
            #
            if bIsWorkflow:
                depId = depId.upper()
            else:
                depId = depId.lower()
            #
            sys.stdout = RedirectDevice()
            sys.stderr = RedirectDevice()
            os.setpgrp()
            os.umask(0)
            #
            # redirect the logfile
            self.__openSemaphoreLog(sph)
            sys.stdout = self.__lfh
            sys.stderr = self.__lfh
            #
            if (self.__verbose):
                self.__lfh.write("+%s.%s() Child Process: PID# %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, os.getpid()))
            #
            try:
                foundWfSearchResult = False
                foundWfImageResult = False
                ccAssignDataStore = None
                if bIsWorkflow:
                    pI = PathInfo(siteId=self.__siteId, sessionPath=self.__sessionPath, verbose=self.__verbose, log=self.__lfh)
                    WfDirPath = pI.getDirPath(dataSetId=self.__reqObj.getValue('identifier').upper(), wfInstanceId=self.__reqObj.getValue('instance'),
                                              contentType='model', formatType='pdbx', fileSource=str(self.__reqObj.getValue("filesource")).lower(),
                                              versionId='latest', partNumber=1)
                    if WfDirPath is not None:
                        WfccAssignDirPath = os.path.join(WfDirPath, 'assign')
                        ccI = ChemCompDataImport(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
                        WfModelPdbxFilePath = ccI.getModelPdxFilePath()
                        WfccAssignFilePath = ccI.getChemCompAssignFilePath()
                        if WfModelPdbxFilePath is not None and os.access(WfModelPdbxFilePath, os.R_OK) and \
                           WfccAssignFilePath is not None and os.access(WfccAssignFilePath, os.R_OK) and \
                           os.access(WfccAssignDirPath, os.R_OK):
                            # found WFM search result
                            foundWfSearchResult = True
                            #
                            # copy model pdbx file
                            shutil.copyfile(WfModelPdbxFilePath, os.path.join(self.__sessionPath, depId + '-model.cif'))
                            #
                            # copy cc-assign file
                            shutil.copyfile(WfccAssignFilePath, os.path.join(self.__sessionPath, depId + '-cc-assign.cif'))
                            #
                            # make symbolic link to workflow instance assign directory
                            os.symlink(WfccAssignDirPath, os.path.join(self.__sessionPath, 'assign'))
                            #
                            # copy cc-link file if exists
                            WfLinkFilePath = ccI.getChemCompLinkFilePath()
                            if WfLinkFilePath is not None and os.access(WfLinkFilePath, os.R_OK):
                                shutil.copyfile(WfLinkFilePath, os.path.join(self.__sessionPath, depId + '-cc-link.cif'))
                            #
                            # use RcsbDpUtility to create a version of the coordinate data file that can be used for loading into jmol
                            dpCnvrt = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=True)
                            dpCnvrt.setWorkingDir(self.__sessionPath)
                            dpCnvrt.imp(os.path.join(self.__sessionPath, depId + '-model.cif'))
                            dpCnvrt.op("cif2cif-pdbx-skip-process")
                            dpCnvrt.exp(os.path.join(self.__sessionPath, depId + '-jmol-mdl.cif'))
                            #
                            # instantiate a cc assign data store from the pickled file if exists
                            pickleFilePath = os.path.join(self.__sessionPath, 'assign', depId + '-cc-assign-details.pic')
                            if os.access(pickleFilePath, os.R_OK):
                                foundWfImageResult = True
                                ccAssignDataStore = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
                            #
                        #
                    #
                #
                if ccAssignDataStore is None:
                    ccA = ChemCompAssign(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
                    if foundWfSearchResult:
                        # procrss WFM search cc-assign file
                        assignRsltsDict = ccA.processCcAssignFile(os.path.join(self.__sessionPath, depId + '-cc-assign.cif'))
                    else:
                        # run cc-assign search in current session
                        assignRsltsDict = self.__runChemCompSearch(ccA)
                    #
                    ccAssignDataStore = self.__genCcAssignDataStore(assignRsltsDict, ccA)
                    self.__lfh.flush()
                    ccA.updateWithDepositorInfo(ccAssignDataStore)
                    self.__lfh.flush()
                #
                if ccAssignDataStore is not None:
                    # at this point we should have created a ccAssignDataStore either from scratch or based on previous depositor efforts
                    self.__importDepositorFiles(ccAssignDataStore)
                    #
                    # Generate report material that will support 2D,3D renderings.
                    if not foundWfImageResult:
                        # IDG = InstanceDataGenerator(reqObj=self.__reqObj,dataStore=ccAssignDataStore,verbose=self.__verbose,log=self.__lfh)
                        IDG = InstanceDataGenerator(reqObj=self.__reqObj, dataStore=ccAssignDataStore, verbose=True, log=self.__lfh)
                        IDG.run()
                        #
                        ccA = ChemCompAssign(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
                        instIdLst = ccAssignDataStore.getAuthAssignmentKeys()
                        if len(instIdLst) > 0:
                            ccA.getDataForInstncSrch(instIdLst, ccAssignDataStore)
                            ccAssignDataStore.dumpData(self.__lfh)
                            ccAssignDataStore.serialize()
                        #
                    #
                    self.__postSemaphore(sph, "OK")
                else:
                    # we have failed to create a ccAssignDataStore either from scratch or based on previous depositor efforts
                    self.__postSemaphore(sph, "FAIL")
                    self.__lfh.flush()
                #
            except:  # noqa: E722 pylint: disable=bare-except
                traceback.print_exc(file=self.__lfh)
                self.__lfh.write("+%s.%s() Failing for child Process: PID# %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, os.getpid()))
                self.__postSemaphore(sph, "FAIL")
                self.__lfh.flush()
                self.__verbose = False

            self.__verbose = False
            os._exit(0)  # pylint: disable=protected-access
        else:
            # we are in parent process and we will return status code to client to indicate that data processing is "running"
            self.__lfh.write("+%s.%s() Parent Process: PID# %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, os.getpid()))

            # Wait for first fork
            os.waitpid(pid, 0)

            self.__reqObj.setReturnFormat(return_format="json")
            rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            rC.setStatusCode('running')
            self.__lfh.write("+%s.%s() Parent process completed\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
            self.__lfh.flush()
            return rC

    # """
    # def _ccAssign_generateBatchData(self):
    #     ''' Generate chem comp summary results for entire deposition data set
    #         Child process is spawned to allow summary results to be gathered
    #         while parent process completes simply by returning status of "running"
    #         to the client.

    #         :Helpers:
    #             wwpdb.apps.ccmodule.chem.ChemCompAssign.ChemCompAssign

    #         :Returns:
    #             JSON object with status code of "running" returned.
    #     '''
    #     self.__getSession()
    #     depId       =str(self.__reqObj.getValue("identifier"))
    #     #
    #     bReusingPriorDataStore=True
    #     #
    #     if (self.__verbose):
    #         self.__lfh.write("--------------------------------------------\n")
    #         self.__lfh.write("+%s.%s() starting\n"%(self.__class__.__name__, inspect.currentframe().f_code.co_name) )
    #         self.__lfh.write("+%s.%s() identifier   %s\n"%(self.__class__.__name__, inspect.currentframe().f_code.co_name, depId) )
    #         self.__lfh.write("+%s.%s() workflow instance     %s\n" %(self.__class__.__name__, inspect.currentframe().f_code.co_name, self.__reqObj.getValue("instance")) )
    #         self.__lfh.write("+%s.%s() file source  %s\n" %(self.__class__.__name__, inspect.currentframe().f_code.co_name, self.__reqObj.getValue("filesource")) )
    #         self.__lfh.write("+%s.%s() sessionId  %s\n" %(self.__class__.__name__, inspect.currentframe().f_code.co_name, self.__sessionId ) )
    #         self.__lfh.flush()
    #     #
    #     sph=self.__setSemaphore()
    #     if (self.__verbose):
    #             self.__lfh.write("+%s.%s() Just before fork to create child process w/ separate log generated in session directory.\n"%
    #                              (self.__class__.__name__, inspect.currentframe().f_code.co_name) )
    #     pid = os.fork()
    #     if pid == 0:
    #         # if here, means we are in the child process

    #         # determine if currently operating in Workflow Managed environment
    #         bIsWorkflow = self.__isWorkflow()
    #         #
    #         if( bIsWorkflow ):
    #             depId = depId.upper()
    #         else:
    #             depId = depId.lower()
    #         #
    #         sys.stdout = RedirectDevice()
    #         sys.stderr = RedirectDevice()
    #         os.setpgrp()
    #         os.umask(0)
    #         #
    #         # redirect the logfile
    #         self.__openSemaphoreLog(sph)
    #         sys.stdout = self.__lfh
    #         sys.stderr = self.__lfh
    #         #
    #         if (self.__verbose):
    #             self.__lfh.write("+%s.%s() Child Process: PID# %s\n" %(self.__class__.__name__, inspect.currentframe().f_code.co_name, os.getpid()) )
    #         #
    #         try:
    #             # 2013-12-11, RPS: Unfortunately found that currently need to run cc-assign search everytime in order
    #             # to produce instance-level cif files b/c these files are req'd inputs for generating 2D images
    #             # NEED BETTER STRATEGY FOR HANDLING THIS - i.e. have WFE run search before user launch of LigMod
    #             ccA=ChemCompAssign(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
    #             assignRsltsDict = self.__runChemCompSearch(ccA)
    #             # when we are in standalone test context above ligand summary results dict will always be used
    #             # plan to explore strategy where when cc-assign search has been run beforehand, the prior cc-assign cif
    #             # results file will be used to generate the dictionary

    #             # check if there was work already done by depositor in editing chem comp assignments
    #             # if so, we generate a cc-assign data store based on the last saved state contained in previous pickle details file
    #             ccAssignDataStore = self.__checkForExistingCcAssignments()

    #             if ccAssignDataStore is None: # i.e. no work had previously been done and saved by depositor
    #                 # if we don't have any data store then we need to generate a data store from scratch
    #                 # which requires that we fill it with data as parsed from the cc-assign results cif file

    #                 ''' 2013-09-19, RPS: Need to work out with Tom how to improve by having cc-assign search run via WFM before LigMod launch,
    #                     so that can use cc-assign results file instead of running cc-assign search every time.
    #                     When this is possible can do the below:

    #                 # create instance of ChemCompAssign class
    #                 ccA=ChemCompAssign(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)

    #                 # we expect that Dep UI code would have run cc-assign search already
    #                 # so we will attempt to import the already existing cc-assign.cif file into local session directory
    #                 # and parse these for results
    #                 ccI=ChemCompDataImport(self.__reqObj,verbose=self.__verbose,log=self.__lfh)

    #                 ccAssignWfFlPth = ccI.getChemCompAssignFilePath() # the path to copy of the cc-assign results file held by workflow/depUI

    #                 ccAssignLclFlPath = os.path.join(self.__sessionPath,depId+'-cc-assign.cif') # path to local copy of the cc-assign file that we will create
    #                 if ccAssignWfFlPth is not None and os.access(ccAssignWfFlPth,os.R_OK):
    #                     shutil.copyfile(ccAssignWfFlPth, ccAssignLclFlPath)
    #                     if os.access(ccAssignLclFlPath,os.R_OK):
    #                         assignRsltsDict=ccA.processCcAssignFile(ccAssignLclFlPath)
    #                     else:
    #                         # If for some reason there was problem getting pre-existing CC assignment results file, we must then call on ChemCompAssign to generate
    #                         # ligand summary results
    #                         assignRsltsDict = self.__runChemCompSearch(ccA)
    #                     #
    #                 '''

    #                 if (self.__verbose):
    #                     for k,v in assignRsltsDict.items():
    #                         self.__lfh.write("+%s.%s() key %30s\n" %(self.__class__.__name__, inspect.currentframe().f_code.co_name, k) )
    #                         self.__lfh.flush()

    #                 # generate a datastore to serve as representation of chem component assignment results data required/updated by annotator during current session.
    #                 ccAssignDataStore = self.__genCcAssignDataStore(assignRsltsDict,ccA)
    #                 self.__lfh.flush()
    #                 ccA.updateWithDepositorInfo(ccAssignDataStore)
    #                 self.__lfh.flush()
    #                 bReusingPriorDataStore=False
    #             #

    #             if( ccAssignDataStore is not None ): # at this point we should have created a ccAssignDataStore either from scratch or based on previous depositor efforts
    #                 self.__postSemaphore(sph,"OK")
    #                 self.__importDepositorFiles(ccAssignDataStore)
    #                 self.__generateInstanceLevelData(ccAssignDataStore,bReusingPriorDataStore)
    #             else: # we have failed to create a ccAssignDataStore either from scratch or based on previous depositor efforts
    #                 self.__postSemaphore(sph,"FAIL")
    #                 self.__lfh.flush()

    #         except:  # noqa: E722 pylint: disable=bare-except
    #             traceback.print_exc(file=self.__lfh)
    #             self.__lfh.write("+%s.%s() Failing for child Process: PID# %s\n" %(self.__class__.__name__, inspect.currentframe().f_code.co_name,os.getpid()) )
    #             self.__postSemaphore(sph,"FAIL")
    #             self.__lfh.flush()
    #             self.__verbose = False

    #         self.__verbose = False
    #         os._exit(0)

    #     else:
    #         # we are in parent process and we will return status code to client to indicate that data processing is "running"
    #         self.__lfh.write("+%s.%s() Parent Process: PID# %s\n" %(self.__class__.__name__, inspect.currentframe().f_code.co_name,os.getpid()) )
    #         self.__reqObj.setReturnFormat(return_format="json")
    #         rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
    #         rC.setStatusCode('running')
    #         self.__lfh.write("+%s.%s() Parent process completed\n"%(self.__class__.__name__, inspect.currentframe().f_code.co_name) )
    #         self.__lfh.flush()
    #         return rC
    # """

    def _ccAssign_checkForBatchData(self):
        """Performs a check on the contents of a semaphore file and returns the associated status.

           This method currently supports both rcsb and wf filesources.
        """
        #
        self.__getSession()
        sessionId = self.__sessionId
        #
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_checkForBatchData - starting\n")
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_checkForBatchData() sessionId  %s\n" % sessionId)
            self.__lfh.flush()
        #
        sph = self.__reqObj.getSemaphore()
        delayValue = self.__reqObj.getValue("delay")
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_checkForBatchData Checking status of semaphore %s with delay %s\n" % (sph, delayValue))
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        if (self.__semaphoreExists(sph)):
            status = self.__getSemaphore(sph)
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppWorker._ccAssign_checkForBatchData status value for semaphore %s is %s\n" % (sph, str(status)))
            if (status == "OK"):
                rC.setStatusCode('completed')
            else:
                rC.setStatusCode('failed')
        else:
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppWorker._ccAssign_checkForBatchData semaphore %s not posted - waiting %s\n" % (sph, delayValue))
            time.sleep(int(delayValue))
            rC.setStatusCode('running')
        #
        return rC

    def _ccAssign_loadBatchSmmry(self):
        """ Call for loading content displayed in global/batch summary of chem component assignment results

            :Helpers:

                + wwpdb.apps.ccmodule.chem.ChemCompAssignDepict.ChemCompAssignDepict
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                Operation output is packaged in a ResponseContent() object.
                The output consists of the HTML results content that is used to re-populate the
                Batch Search Results container markup that had already been delivered to
                the browser in a prior request.
        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_loadGlblSmmry() starting\n")
        # determine if currently operating in Workflow Managed environment
        self.__getSession()
        # sessionId = self.__sessionId
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
        #
        linkInfoMap = self.__readCovalentBondingInfo()
        ccAD = ChemCompAssignDepict(self.__verbose, self.__lfh)
        oL = ccAD.doRender_BatchSrchSummaryContent(ccADS, linkInfoMap)
        #
        rC.setHtmlText('\n'.join(oL))
        return rC

    def _ccAssign_generateEntityBrowser(self):
        """ Generate "Entity Browser" content for "Instance-Level Searching" view
            This view allows user to navigate ligand instance data via entity CCID groupings

            :Helpers:

                + wwpdb.apps.ccmodule.chem.ChemCompAssign.ChemCompAssign
                + wwpdb.apps.ccmodule.chem.ChemCompAssignDepict.ChemCompAssignDepict
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                Operation output is packaged in a ResponseContent() object.
                The output contains HTML markup that is used to populate the
                HTML container that had already been delivered to the browser
                in the prior request for the Batch Search Summary content.
                This output represents the "Instance-Level" display interface.
        """
        srchIdsL = []
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_generateEntityBrowser() starting\n")
        # determine if currently operating in Workflow Managed environment
        self.__getSession()
        #
        sessionId = self.__sessionId
        depId = str(self.__reqObj.getValue("identifier")).upper()
        srchIds = str(self.__reqObj.getValue("srchids"))
        wfInstId = str(self.__reqObj.getValue("instance")).upper()
        # classId = str(self.__reqObj.getValue("classID")).lower()
        fileSource = str(self.__reqObj.getValue("filesource")).lower()
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_generateEntityBrowser() identifier   %s\n" % depId)
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_generateEntityBrowser() instance     %s\n" % wfInstId)
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_generateEntityBrowser() file source  %s\n" % fileSource)
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_generateEntityBrowser() sessionId  %s\n" % sessionId)
            self.__lfh.flush()

        #
        srchIdsL = srchIds.split(',')
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        #
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        ccA = ChemCompAssign(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        # unpickle assign data from ccAssignDataStore
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_generateEntityBrowser() ----- unpickling ccAssignDataStore\n")
        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
        ccADS.dumpData(self.__lfh)
        #
        ccA.getDataForInstncSrch(srchIdsL, ccADS)
        #
        ccADS.dumpData(self.__lfh)
        ccADS.serialize()
        # call render() methods to generate data unique to this deposition data set
        linkInfoMap = self.__readCovalentBondingInfo()
        ccAD = ChemCompAssignDepict(self.__verbose, self.__lfh)
        ccAD.setSessionPaths(self.__reqObj)
        oL = ccAD.doRender_EntityBrwsr(srchIdsL, ccADS, linkInfoMap, self.__reqObj)
        #
        rC.setHtmlText(''.join(oL))
        return rC

    def _ccAssign_rerunEntityGrpSrch(self):
        """ Call for rerunning chem component assignment search for entity group
            with adjusted parameters for bond and/or link radii.
            Method also performs corresponding rerendering of the display to
            reflect the new cc assignment results.

            :Helpers:

                + wwpdb.apps.ccmodule.chem.ChemCompAssign.ChemCompAssign
                + wwpdb.apps.ccmodule.chem.ChemCompAssignDepict.ChemCompAssignDepict
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                Operation output is packaged in a ResponseContent() object.
                The output consists of the new results content that is used to re-populate the
                instance-level view that had already been delivered to the browser in a prior request.
        """

        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_rerunEntityGrpSrch() starting\n")
        #
        self.__getSession()
        # sessionId = self.__sessionId
        # depId = str(self.__reqObj.getValue("identifier")).lower()
        entityGrp = str(self.__reqObj.getValue("auth_assgnd_grp"))
        instIdLst = str(self.__reqObj.getValue("instidlst"))
        # wfInstId = str(self.__reqObj.getValue("instance")).upper()
        linkRadii = self.__reqObj.getValue("linkradii_" + entityGrp)
        bondRadii = self.__reqObj.getValue("bondradii_" + entityGrp)
        # fileSource = str(self.__reqObj.getValue("filesource")).lower()
        #
        # self.__reqObj.setDefaultReturnFormat(return_format="html")
        #
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        instIdL = instIdLst.split(',')
        #
        ccA = ChemCompAssign(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        for instId in instIdL:
            ccADS = self.__rerunAssgnSrch(ccA, instId, linkRadii, bondRadii)
        ccADS.addGrpToGlblRerunSrchLst(entityGrp, linkRadii, bondRadii)
        ccADS.serialize()
        ccADS.dumpData(self.__lfh)
        #
        # self.__generateReportData(ccADS)
        # call render() methods to generate data unique to this deposition data set
        linkInfoMap = self.__readCovalentBondingInfo()
        ccAD = ChemCompAssignDepict(self.__verbose, self.__lfh)
        ccAD.setSessionPaths(self.__reqObj)
        ccAD.doRender_EntityGrpOnRerunSrch(entityGrp, instIdL, ccADS, linkInfoMap, self.__reqObj)
        #
        return rC

    def _ccAssign_rerunInstncSrch(self):
        """ Call for rerunning chem component assignment search for single ligand
            instance with adjusted parameters for bond and/or link radii.
            Method also performs corresponding rerendering of the display to
            reflect the new cc assignment results.

            :Helpers:

                + wwpdb.apps.ccmodule.chem.ChemCompAssign.ChemCompAssign
                + wwpdb.apps.ccmodule.chem.ChemCompAssignDepict.ChemCompAssignDepict
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                Operation output is packaged in a ResponseContent() object.
                The output consists of the new results content that is used to re-populate the
                instance-level view that had already been delivered to the browser in a prior request.
        """

        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_rerunInstncSrch() starting\n")
        #
        self.__getSession()
        sessionId = self.__sessionId
        depId = str(self.__reqObj.getValue("identifier")).lower()
        instId = str(self.__reqObj.getValue("instanceid"))
        wfInstId = str(self.__reqObj.getValue("instance")).upper()
        fileSource = str(self.__reqObj.getValue("filesource")).lower()
        linkRadii = self.__reqObj.getValue("linkradii_" + instId)
        bondRadii = self.__reqObj.getValue("bondradii_" + instId)
        htmlTmpltPth = self.__reqObj.getValue("TemplatePath")
        #
        #
        hlprDict = {}
        hlprDict['instanceid'] = instId
        hlprDict['sessionid'] = sessionId
        hlprDict['depositionid'] = depId
        hlprDict['identifier'] = depId
        hlprDict['filesource'] = fileSource
        hlprDict['instance'] = wfInstId  # i.e. workflow instance ID
        hlprDict['html_template_path'] = htmlTmpltPth
        #
        #
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        ccA = ChemCompAssign(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        ccADS = self.__rerunAssgnSrch(ccA, instId, linkRadii, bondRadii)
        ccADS.addInstIdToRerunSrchLst(instId)
        ccADS.serialize()
        ccADS.dumpData(self.__lfh)
        #
        # self.__generateReportData(ccADS)
        # call render() methods to generate data unique to this deposition data set
        ccAD = ChemCompAssignDepict(self.__verbose, self.__lfh)
        ccAD.setSessionPaths(self.__reqObj)
        ccAD.doRender_InstanceProfile(ccADS, hlprDict, True)
        #
        return rC

    def _ccAssign_rerunInstncCompSrch(self):
        """ Call for rerunning chem component assignment search for single ligand
            instance with edited chemical component from ChemEditor.
            Method also performs corresponding rerendering of the display to
            reflect the new cc assignment results.

            :Helpers:

                + wwpdb.apps.ccmodule.chem.ChemCompAssign.ChemCompAssign
                + wwpdb.apps.ccmodule.chem.ChemCompAssignDepict.ChemCompAssignDepict
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                Operation output is packaged in a ResponseContent() object.
                The output consists of the new results content that is used to re-populate the
                instance-level view that had already been delivered to the browser in a prior request.
        """

        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_rerunInstncCompSrch() starting\n")
        #
        self.__getSession()
        sessionId = self.__sessionId
        depId = str(self.__reqObj.getValue("identifier")).lower()
        instId = str(self.__reqObj.getValue("instanceid"))
        wfInstId = str(self.__reqObj.getValue("instance")).upper()
        fileSource = str(self.__reqObj.getValue("filesource")).lower()
        htmlTmpltPth = self.__reqObj.getValue("TemplatePath")
        #
        #
        hlprDict = {}
        hlprDict['instanceid'] = instId
        hlprDict['sessionid'] = sessionId
        hlprDict['depositionid'] = depId
        hlprDict['identifier'] = depId
        hlprDict['filesource'] = fileSource
        hlprDict['instance'] = wfInstId  # i.e. workflow instance ID
        hlprDict['html_template_path'] = htmlTmpltPth
        #
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        ccA = ChemCompAssign(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        ccA.setTargetInstanceId(instId)
        rD = ccA.doAssignInstanceComp()  # do comp search
        #
        ccADS = ccA.updateDataStoreForInstnc(instId, rD['dataDict'])   # updating data store with new match results
        # self.__generateReportData(ccADS)
        ccA.getTopHitsDataForInstnc(instId, ccADS, rD['assignDirPath'])
        ccADS.addInstIdToRerunSrchLst(instId)
        ccADS.serialize()
        ccADS.dumpData(self.__lfh)
        #
        # call render() methods to generate data unique to this deposition data set
        ccAD = ChemCompAssignDepict(self.__verbose, self.__lfh)
        ccAD.setSessionPaths(self.__reqObj)
        ccAD.doRender_InstanceProfile(ccADS, hlprDict, True)
        #
        return rC

    def _ccAssign_assignInstnc(self):
        """ Register annotator assignment update for ligand instance with ChemCompAssignDataStore

            :Helpers:
                wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                ResponseContent() object.
                No display output for this method.
        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_assignInstnc() starting\n")
        #
        self.__getSession()
        # sessionId = self.__sessionId
        # depId = str(self.__reqObj.getValue("identifier")).upper()
        instIdList = str(self.__reqObj.getValue("instidlist"))
        assgnCcId = str(self.__reqObj.getValue("ccid"))
        # wfInstId = str(self.__reqObj.getValue("instance")).upper()
        assgnMode = str(self.__reqObj.getValue("assgn_mode"))
        authAssgnGrp = str(self.__reqObj.getValue("auth_assgn_grp"))
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        # unpickle assign data from ccAssignDataStore
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_assignInstnc() ----- unpickling ccAssignDataStore\n")
        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
        #
        instIdL = instIdList.split(',')
        #
        # zk: Add checking if assgnCcId is in HitList
        #
        if (assgnCcId != "Not Assigned"):
            errorMessage = ''
            for instId in instIdL:
                ok = False
                hitList = ccADS.getTopHitsList(instId)
                if hitList:
                    for tup in hitList:
                        if tup[0] == assgnCcId:
                            ok = True
                            break
                        #
                    #
                #
                if not ok:
                    errorMessage += assgnCcId + ' is not in hit list for ' + instId + '\n'
            #
            if errorMessage:
                if (self.__verbose):
                    self.__lfh.write("+ChemCompWebAppWorker._ccAssign_assignInstnc() ----- Error: %s\n" % errorMessage)
                rC.setError(errMsg=errorMessage)
                return rC
        #
        for instId in instIdL:
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_assignInstnc() ----- instId %s\n" % instId)
            hlist = ccADS.getTopHitsList(instId)
            if hlist:
                self.__lfh.write("+ChemCompWebAppWorker._ccAssign_assignInstnc() ----- tuple %s for %s\n" % (hlist, instId))
            else:
                self.__lfh.write("+ChemCompWebAppWorker._ccAssign_assignInstnc() ----- no tuple for %s\n" % instId)
            ccADS.setAnnotAssignment(instId, assgnCcId)
            if assgnMode == 'glbl' and assgnCcId != "Not Assigned":
                ccADS.addGrpToGlbllyAssgndLst(authAssgnGrp, assgnCcId)
            elif assgnMode == 'glbl' and assgnCcId == "Not Assigned":
                ccADS.removeGrpFrmGlbllyAssgndLst(authAssgnGrp)
            ccADS.serialize()
        ccADS.dumpData(self.__lfh)

        return rC

    def _ccAssign_setNewCcDefinedForInstnc(self):
        """ Capture new Chem Comp ID defined for ligand instance via Chem Comp Editor component

            :Helpers:
                wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                ResponseContent() object.
                No display output for this method.
        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_setNewCcDefinedForInstnc() starting\n")
        #
        self.__getSession()
        # sessionId = self.__sessionId
        instId = str(self.__reqObj.getValue("instanceid"))
        newCcId = str(self.__reqObj.getValue("newccid"))
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_setNewCcDefinedForInstnc() ----- new CC id %s defined for instance ID %s \n" % (newCcId, instId))
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        # unpickle assign data from ccAssignDataStore
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_setNewCcDefinedForInstnc() ----- unpickling ccAssignDataStore\n")
        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
        ccADS.setNewCcDefined(instId, newCcId)
        ccADS.serialize()
        ccADS.dumpData(self.__lfh)
        newId = ccADS.getNewCcDefined(instId)
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_setNewCcDefinedForInstnc() ----- value of new ccid from ccAssignDataStore for instance ID %s is %s \n" % (instId, newId))
        return rC

    def _ccAssign_getNewCcIdForInstnc(self):
        """ Obtain newly defined Chem Comp Code for ligand instance

            :Helpers:
                wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                String indicating newly defined chem component ID
                or "NONE" when applicable.
        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_getNewCcIdForInstnc() starting\n")
        #
        self.__getSession()
        # sessionId = self.__sessionId
        instId = str(self.__reqObj.getValue("instanceid"))
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_getNewCcIdForInstnc() ---- requesting new CC ID for instance ID: %s\n" % instId)
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        # unpickle assign data from ccAssignDataStore
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_getNewCcIdForInstnc() ----- unpickling ccAssignDataStore\n")
        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
        newId = ccADS.getNewCcDefined(instId)
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_getNewCcIdForInstnc() ----- value of new ccid from ccAssignDataStore for instance ID %s is %s \n" % (instId, newId))
        #
        statusCode = ''
        if newId is not None and len(newId) > 0:
            statusCode = newId
        else:
            statusCode = "NONE"

        rC.setStatusCode(statusCode)

        return rC

    def _ccAssign_validateCcId(self):
        """ Verify validity of given Chem Comp Code
            Supports two modes of validation:

                + "simple":
                    check that CC ID simply has corresponding directory in server repository of ligand dict data

                + "full":
                    check that CC ID is not obsolete AND
                    would be returned as result of cc-assign match query for the given ligand instance.

            :Helpers:

                + wwpdb.apps.ccmodule.chem.ChemCompAssign.ChemCompAssign
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                if fails return error message
                else return without message
        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_validateCcId() starting\n")
        #
        self.__getSession()
        # sessionId = self.__sessionId
        vldtMode = str(self.__reqObj.getValue("vldtmode"))
        instIdList = str(self.__reqObj.getValue("instidlist"))
        # instncMode = str(self.__reqObj.getValue("instncmode"))
        ccId = str(self.__reqObj.getValue("ccid")).upper()
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        pathPrefix = self.__ccConfig.getPath('chemCompCachePath')
        validationPth = os.path.join(pathPrefix, ccId[:1], ccId, ccId + '.cif')
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_validateCcId() ---- validating CC ID %s against path: %s\n" % (ccId, validationPth))
        if not os.access(validationPth, os.R_OK):
            errorMessage = '"' + ccId + '" is not a valid Code.'
            rC.setError(errMsg=errorMessage)
            return rC
        #
        if vldtMode == 'simple':
            return rC
        #
        if ccId not in ("1CU", "2OF", "3OF", "543", "CD1", "CD3", "CD5", "CO5", "KO4", "MH3",
                        "MN5", "MN6", "MO1", "MO2", "MO3", "MO4", "MO5", "MO6", "MW1", "MW2",
                        "MW3", "NA2", "NA5", "NA6", "NAO", "NAW", "NI1", "NI2", "NI3", "NIK",
                        "O4M", "OC1", "OC2", "OC3", "OC4", "OC5", "OC6", "OC7", "OC8", "OCL",
                        "OCM", "OCN", "OCO", "OF1", "OF3", "YH", "ZH3", "ZN3", "ZNO", "ZO3"):
            cifObj = mmCIFUtil(filePath=validationPth)
            status = cifObj.GetSingleValue('chem_comp', 'pdbx_release_status')
            if status == 'OBS':
                errorMessage = '"' + ccId + '" is an obsolete code.'
                rC.setError(errMsg=errorMessage)
                return rC
            #
            if status == 'REF_ONLY':
                errorMessage = '"' + ccId + '" is an "REF_ONLY" code.'
                rC.setError(errMsg=errorMessage)
                return rC
            #
        #
        # '''    'full' mode includes verification that the given chem comp ID:
        #        = is not obsolete
        #        = would be returned as result of cc-assign match query for the given ligand instance.
        # '''
        ccA = ChemCompAssign(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        ccA.setInstanceIdListForValidation(instIdList)
        ccA.setValidationCcRefFilePath(validationPth)
        returnMessage = ccA.doAssignValidation()
        if returnMessage:
            rC.setError(errMsg=returnMessage)
        #
        return rC

    def _ccAssign_getNewCandidate(self):
        """ Request for new candidate chem component in comparison grid of ligand module.
            If the request is an appropriate one this method invokes generation of files
            of HTML markup corresponding to comparison grid display components for the given candidate.
            The files are stored on the server and depending on the return code returne to the client,
            a corresponding AJAX call is made to have the content load into corresponding sections on the page.
            If the request is not appropriate, no action is taken and corresponding return code sent back.

            :Helpers:

                + wwpdb.apps.ccmodule.chem.ChemCompAssignDepict.ChemCompAssignDepict
                + wwpdb.apps.ccmodule.reports.ChemCompReports.ChemCompReport
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore
                + wwpdb.apps.ccmodule.io.ChemCompIo.ChemCompReader

            :Returns:
                'rtrnCode':
                    0: action will be taken to display new candidate
                    1: no action taken b/c candidate requested is one of the top candidates already presented to the user
                    2: no action taken b/c candidate requested is one of the new candidates already presented/requested by the user
        """

        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_getNewCandidate() starting\n")
        #
        self.__getSession()
        # sessionId = self.__sessionId
        ccId = str(self.__reqObj.getValue("ccid")).upper()
        depId = str(self.__reqObj.getValue("identifier"))
        instId = str(self.__reqObj.getValue("instanceid"))
        # wfInstId = str(self.__reqObj.getValue("instance")).upper()
        # fileSource  = str(self.__reqObj.getValue("filesource")).lower()
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        rtrnCode = -1
        # need to get list of top candidates so that we don't allow user to ask for one of these as new candidate
        candidatesLst = []
        displayhitlist = str(self.__reqObj.getValue("displayhitlist")).upper()
        if displayhitlist:
            candidatesLst = displayhitlist.split(",")
        #
        currentNewCandidates = []
        displaycandidatelist = str(self.__reqObj.getValue("displaycandidatelist")).upper()
        if displaycandidatelist:
            currentNewCandidates = displaycandidatelist.split(",")
        #
        # newCandidatesLst = []
        HitList = candidatesLst
        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
        #       if( ccADS.wasBorn() ):
        #           mtchL = ccADS.getTopHitsList(instId)
        #           for tupL in mtchL:
        #               topHitCcid = tupL[0]
        #               if( not topHitCcid in candidatesLst ):
        #                   candidatesLst.append(topHitCcid)
        #                   HitList.append(topHitCcid)
        #############################################################################################################
        #        Generate report material for requested dictionary reference
        #############################################################################################################
        ccReferncRprt = ChemCompReport(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        if ccId not in candidatesLst:
            # only proceed if ccid is not already one of the top hit candidates displayed to the user
            newCandidatesLst = ccADS.getNewCandidatesList(instId)
            # currentNewCandidates = []
            #
            for tupL in newCandidatesLst:
                newCandidt = tupL[0]
                # currentNewCandidates.append(newCandidt)
                HitList.append(newCandidt)
            #
            if ccId not in currentNewCandidates:
                # only proceed if ccid is not already one of the non candidates presented to the user
                ccReferncRprt.setDefinitionId(definitionId=ccId.lower())
                ccReferncRprt.doReport(type='ref', ccAssignPthMdfier=ccId)
                rD = ccReferncRprt.getReportFilePaths()
                for k, v in rD.items():
                    if self.__verbose:
                        self.__lfh.write("+ChemCompWebAppWorker._getNewCandidate() -- Reference file reporting -- Key %30s value %s\n" % (k, v))
                #
                # 2014-11-03, ZF -- add aligned image
                HitList.append(ccId)
                chemCompFilePathAbs = os.path.join(self.__cI.get('SITE_ARCHIVE_STORAGE_PATH'), 'workflow', depId, 'assign', instId, instId + ".cif")
                if not os.access(chemCompFilePathAbs, os.R_OK):
                    # i.e. if not in Workflow Managed context, must be in standalone dev context where we've run cc-assign search locally
                    # and therefore produced cc-assign results file in local session area
                    chemCompFilePathAbs = os.path.join(self.__sessionPath, 'assign', instId, instId + ".cif")
                #
                ccaig = ChemCompAlignImageGenerator(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
                ccaig.generateImages(instId=instId, instFile=chemCompFilePathAbs, hitList=HitList)
                #
                ##########################################################
                # interrogate report data in order to get name and
                # formula for the chem component reference
                #########################################################
                ccRefFilePath = os.path.join(self.__sessionPath, 'assign', 'rfrnc_reports', ccId, ccId + '.cif')
                #
                if os.access(ccRefFilePath, os.R_OK):
                    ccRefR = ChemCompReader(self.__verbose, self.__lfh)
                    ccRefR.setFilePath(filePath=ccRefFilePath)
                    refD = {}
                    ##################################################################################################
                    #    Getting data contained in "chem_comp" cif category
                    ##################################################################################################
                    #
                    refD = ccRefR.getChemCompDict()
                    #
                    newCandidatesLst.append((ccId, refD['_chem_comp.name'], refD['_chem_comp.formula']))
                    rtrnCode = 0
                    if self.__verbose:
                        self.__lfh.write("+ChemCompWebAppWorker._ccAssign_getNewCandidate() - successfully processing non-candidate %s for instId %s, with name %s and formula %s\n" %
                                         (ccId, instId, refD['_chem_comp.name'], refD['_chem_comp.formula']))

                else:
                    if self.__verbose:
                        self.__lfh.write("+ChemCompWebAppWorker._ccAssign_getNewCandidate() - processing non candidate for %s and NO reference chem comp file found for %s\n" %
                                         (instId, ccRefFilePath))
                #
                ccADS.setNewCandidatesList(instId, newCandidatesLst)
                ccADS.serialize()
                # ccADS.dumpData(self.__lfh)
                #########################################################
                # call render() methods to generate html markup to be supplied for display in comparison grid
                ccAD = ChemCompAssignDepict(self.__verbose, self.__lfh)
                ccAD.setSessionPaths(self.__reqObj)
                ccAD.doRender_InstanceNewCandidate(instId, ccId, ccADS, self.__reqObj)
                #
            else:
                # else ccid is one of the new candidates already presented/requested by the user
                rtrnCode = 2
        else:
            # else ccid is one of the top candidates already presented to the user
            rtrnCode = 1
        if self.__verbose:
            self.__lfh.write("+ChemCompWebAppWorker._ccAssign_getNewCandidate() - return code is %s\n" % str(rtrnCode))

        rC.setStatusCode(str(rtrnCode))
        return rC

    def _searchGraphOp(self):
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._searchGraphOp() starting\n")

        self.__getSession()
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        if self.__isFileUpload():
            # make a copy of the file in the session directory and set 'fileName'
            self.__uploadFile()
        #

        ccE = ChemCompSearch(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        rD = ccE.doGraphIso()
        if (self.__verbose):
            for k, v in rD.items():
                self.__lfh.write("+ChemCompWebApp._searchGraphOp() key %30s   value %s\n" % (k, v))
        if len(rD) > 0:
            ccSD = ChemCompSearchDepict(self.__verbose, self.__lfh)
            oL = ccSD.doRenderGraph(rD)
            rC.setHtmlList(oL)
        else:
            rC.setError(errMsg='No search result')

        return rC

    def _searchIndexOp(self):
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._searchIndexOp() starting\n")
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        ccS = ChemCompSearch(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        rD = ccS.doIndex()
        if len(rD) > 0:
            ccSD = ChemCompSearchDepict(self.__verbose, self.__lfh)
            oL = ccSD.doRenderIndex(rD)
            rC.setHtmlList(oL)
        else:
            rC.setError(errMsg='No search result')

        return rC

    def _searchDbOp(self):
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker._searchDbOp() starting\n")
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        ccS = ChemCompSearchDb(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        rD = ccS.doIdSearch()
        if len(rD) > 0:
            ccSD = ChemCompSearchDbDepict(self.__verbose, self.__lfh)
            oL = ccSD.doRender(rD)
            rC.setHtmlList(oL)
        else:
            rC.setError(errMsg='No search result')

        return rC

    def _ccAssign_exit_Finished(self):
        """ Exiting Ligand Module when annotator has completed all necessary processing
        """
        return self.__exitLigMod(mode='completed')

    def _ccAssign_exit_notFinished(self):
        """ Exiting Ligand Module when annotator has NOT completed all necessary processing
            and user intends to resume use of lig module at another point to continue updating data.
        """
        return self.__exitLigMod(mode='unfinished')

    ################################################################################################################
    # ------------------------------------------------------------------------------------------------------------
    #      Private helper methods
    # ------------------------------------------------------------------------------------------------------------
    #

    def __runChemCompSearch(self, p_ccA):
        #########################################################################################################################################################
        #    If for some reason there was no pre-existing CC assignment results data, we must then call on ChemCompAssign to generate ligand summary results
        #########################################################################################################################################################
        if (self.__verbose):
            now = strftime("%H:%M:%S", localtime())
            self.__lfh.write("+ChemCompWebAppWorker ----TIMECHECK------------------------------------------ time before calling doAssign task is %s\n" % now)

        assignRsltsDict = p_ccA.doAssign()  # NOTE this method generates the "global" cc-assign file *and* creates instance-level directories/chem-component files
        #########################################################################################################################################################
        #    in assignRsltsDict we now have a repository of assignment information for this deposition corresponding to
        #    cif categories: 'pdbx_entry_info','pdbx_instance_assignment','pdbx_match_list','pdbx_atom_mapping','pdbx_missing_atom'
        #########################################################################################################################################################

        if (self.__verbose):
            now = strftime("%H:%M:%S", localtime())
            self.__lfh.write("+ChemCompWebAppWorker ----TIMECHECK------------------------------------------ time after calling doAssign task is %s\n" % now)
        #
        self.__lfh.flush()
        return assignRsltsDict

    def __genCcAssignDataStore(self, p_ccAssignRsltsDict, p_ccAssignObj):
        """ Private method to generate a ChemCompAsssignDataStore object.
            The ChemCompAsssignDataStore serves as a representation of any
            chem component assignment results data required/updated by the
            depositor during the current session.

            :Params:

                + ``p_ccAssignRsltsDict``: Dictionary containing chem comp assignment results
                + ``p_ccAssignObj``: ChemCompAssign object created in calling method

            :Helpers:

                + wwpdb.apps.ccmodule.chem.ChemCompAssign.ChemCompAssign
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                A ChemCompAssignDataStore object.
        """
        # data store for return to calling code
        ccAssignDataStore = None
        #
        # Since no pickled cc assign details file existed previously we must
        # create a DataStore for chem comp assignments
        if (self.__verbose):
            self.__lfh.write("++++%s.%s() ---- creating new datastore because no prior cc-assign-details.pic file existed.\n" % (self.__class__.__name__,
                                                                                                                                 inspect.currentframe().f_code.co_name))
        self.__lfh.flush()
        ccAssignDataStore = p_ccAssignObj.createDataStore(p_ccAssignRsltsDict)

        return ccAssignDataStore

    def __rerunAssgnSrch(self, p_ccA, p_instId, p_linkRadii, p_bondRadii):
        """ Utility method to rerun assignment search for given ligand instance id.

            :Params:

                + ``p_ccA``: ChemCompAssign object created in calling method
                + ``p_instId``: the instance ID
                + ``p_linkRadii``: link radius delta
                + ``p_bondRadii``: bond radius delta

            :Helpers:

                + wwpdb.apps.ccmodule.chem.ChemCompAssign.ChemCompAssign
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                A ChemCompAssignDataStore object reflecting the updated search results.
        """
        if self.__verbose:
            self.__lfh.write("+ChemCompWebAppWorker.__rerunAssgnSrch() starting\n")
        #
        p_ccA.setLinkRadii(p_linkRadii)
        p_ccA.setTargetInstanceId(p_instId)
        p_ccA.setBondRadii(p_bondRadii)
        rD = p_ccA.doAssignInstance()
        #
        ccADS = p_ccA.updateDataStoreForInstnc(p_instId, rD['dataDict'])      # updating data store with new match results
        ccADS.setRerunParam_linkRadii(p_instId, p_linkRadii)     # also remembering what value was used to adjust link radii
        ccADS.setRerunParam_bondRadii(p_instId, p_bondRadii)     # also remembering what value was used to adjust bond radii
        #
        # self.__generateReportData(ccADS)
        p_ccA.getTopHitsDataForInstnc(p_instId, ccADS, rD['assignDirPath'])
        #
        ccADS.serialize()

        return ccADS

    # def __generateInstanceLevelData(self, p_ccAssignDataStore, p_bReusingPriorDataStore):
    #     """ Generate report material that will support 2D,3D renderings.
    #         Also, populate ChemCompAssignDataStore with datapoints required for
    #         instance-level browsing.

    #         Delegates processing to a child process

    #         :Params:
    #             ``p_ccAssignDataStore``: ChemCompAssignDataStore object
    #             ``p_bReusingPriorDataStore``: boolean flag indicating whether there was
    #                                             a pre-existing datastore for us to reuse.

    #         :Helpers:

    #             + wwpdb.apps.ccmodule.reports.ChemCompReports.ChemCompReport
    #             + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore
    #     """
    #     instIdLst = []
    #     depId = str(self.__reqObj.getValue("identifier")).upper()
    #     # wfInstId = str(self.__reqObj.getValue("instance")).upper()
    #     # sessionId = self.__reqObj.getSessionId()
    #     # fileSource = str(self.__reqObj.getValue("filesource")).lower()
    #     #
    #     className = self.__class__.__name__
    #     methodName = inspect.currentframe().f_code.co_name
    #     #
    #     if (self.__verbose):
    #         self.__lfh.write("++%s.%s() Just before fork to create child process w/ separate log generated in session directory.\n" % (className, methodName))
    #     pid = os.fork()
    #     if pid == 0:
    #         #
    #         sys.stdout = RedirectDevice()
    #         sys.stderr = RedirectDevice()
    #         os.setpgrp()
    #         os.umask(0)
    #         #
    #         # redirect the logfile
    #         self.__openChildProcessLog("RPRT_CHLD_PROC")
    #         sys.stdout = self.__lfh
    #         sys.stderr = self.__lfh
    #         #
    #         if (self.__verbose):
    #             self.__lfh.write("+++%s.%s() Child Process: PID# %s\n" % (className, methodName, os.getpid()))
    #         #
    #         try:
    #             ccA = ChemCompAssign(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)

    #             instIdLst = p_ccAssignDataStore.getAuthAssignmentKeys()
    #             if self.__verbose:
    #                 for i in instIdLst:
    #                     if self.__verbose:
    #                         self.__lfh.write("+++%s.%s() -- instIdLst item %30s\n" % (className, methodName, i))

    #             if len(instIdLst) > 0:
    #                 ccIdAlrdySeenLst = []

    #                 for instId in instIdLst:

    #                     #############################################################################################################
    #                     #        First generate report material for top hit dictionary reference(s) to which this lig instance is mapped
    #                     #############################################################################################################
    #                     ccReferncRprt = ChemCompReport(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
    #                     mtchL = p_ccAssignDataStore.getTopHitsList(instId)
    #                     HitList = []
    #                     for tupL in mtchL:
    #                         ccId = tupL[0]
    #                         HitList.append(ccId)
    #                         if ccId not in ccIdAlrdySeenLst:
    #                             ccIdAlrdySeenLst.append(ccId)
    #                             ccReferncRprt.setDefinitionId(definitionId=ccId.lower())
    #                             ccReferncRprt.doReport(type='ref', ccAssignPthMdfier=ccId)
    #                             rD = ccReferncRprt.getReportFilePaths()
    #                             for k, v in rD.items():
    #                                 if self.__verbose:
    #                                     self.__lfh.write("+++%s.%s() -- Reference file reporting -- Key %30s value %s\n" % (className, methodName, k, v))

    #                     #
    #                     #############################################################################################################
    #                     #        Then generate report material for experimental chem comp data of this lig instance
    #                     #############################################################################################################

    #                     chemCompFilePathAbs = os.path.join(self.__cI.get('SITE_ARCHIVE_STORAGE_PATH'), 'workflow', depId, 'assign', instId, instId + ".cif")
    #                     if not os.access(chemCompFilePathAbs, os.R_OK):
    #                         # i.e. if not in Workflow Managed context, must be in standalone dev context where we've run cc-assign search locally
    #                         # and therefore produced cc-assign results file in local session area
    #                         chemCompFilePathAbs = os.path.join(self.__sessionPath, 'assign', instId, instId + ".cif")

    #                     #
    #                     instChemCompRprt = ChemCompReport(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
    #                     instChemCompRprt.setFilePath(chemCompFilePathAbs, instId)
    #                     if self.__verbose:
    #                         self.__lfh.write("+++%s.%s() -- before call to doReport and instId is: %s\n" % (className, methodName, instId))
    #                     instChemCompRprt.doReport(type='exp', ccAssignPthMdfier=instId)
    #                     rDict = instChemCompRprt.getReportFilePaths()
    #                     for k, v in rDict.items():
    #                         if self.__verbose:
    #                             self.__lfh.write("+++%s.%s() -- Checm Comp file reporting -- Key %30s value %s\n" %
    #                                              (className, methodName, k, v))
    #                     #
    #                     # 2014-10-31, ZF -- add aligned image
    #                     ccaig = ChemCompAlignImageGenerator(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
    #                     ccaig.generateImages(instId=instId, instFile=chemCompFilePathAbs, hitList=HitList)

    #                 # 2013-06-26, RPS -- trying this here to see if it introduces improvement in response time
    #                 if p_bReusingPriorDataStore is not True:
    #                     # i.e. if we are spawning a brand new datastore from scratch let's go ahead and
    #                     # parse the instance-level chem-comp cif files and top hit reference chem comp cif files
    #                     # for data needed in instance browser
    #                     ccA.getDataForInstncSrch(instIdLst, p_ccAssignDataStore)
    #                     p_ccAssignDataStore.dumpData(self.__lfh)
    #                     p_ccAssignDataStore.serialize()

    #         except:  # noqa: E722 pylint: disable=bare-except
    #             traceback.print_exc(file=self.__lfh)
    #             self.__lfh.write("+++%s.%s() -- Failing for child Process: PID# %s\n" % (className, methodName, os.getpid()))
    #             self.__lfh.flush()
    #             self.__verbose = False

    #         self.__verbose = False
    #         os._exit(0)

    #     else:
    #         # we are in parent process and we will return status code to client to indicate that data processing is "running"
    #         self.__lfh.write("+++%s.%s() Parent Process Completed: PID# %s\n" % (className, methodName, os.getpid()))
    #     #

    def __importDepositorFiles(self, p_ccAssignDataStore):
        """ Import any files that were previously uploaded/generated by the depositor

            :Params:
                ``p_ccAssgnDataStr``: ChemCompAssignDataStore object

            :Helpers:

                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore
        """
        # instIdLst = []
        # depId = str(self.__reqObj.getValue("identifier")).upper()
        # wfInstId = str(self.__reqObj.getValue("instance")).upper()
        # sessionId = self.__reqObj.getSessionId()
        # fileSource = str(self.__reqObj.getValue("filesource")).lower()
        #
        className = self.__class__.__name__
        methodName = inspect.currentframe().f_code.co_name
        #
        if self.__verbose:
            self.__lfh.write("+%s.%s() ------------------------------ STARTING ------------------------------\n" % (className, methodName))
        #
        assignDirPath = os.path.join(self.__sessionPath, 'assign')
        #
        # contentTypeDict = self.__cI.get('CONTENT_TYPE_DICTIONARY')
        #
        for ligId in p_ccAssignDataStore.getGlbllyRslvdGrpList():
            if self.__verbose:
                self.__lfh.write("+%s.%s() - Inside loop for processing ligand groups for which depositor info was supplied.\n" % (className, methodName))

            try:
                filePthLst = p_ccAssignDataStore.getAllDpstrWfFilePths(ligId)
                if len(filePthLst) < 1:
                    if self.__verbose:
                        self.__lfh.write("+%s.%s() - Empty list of depositor files returned from getAllDpstrWfFilePths.\n" % (className, methodName))
                for wfFlPth in filePthLst:
                    if os.access(wfFlPth, os.R_OK):
                        fileName = os.path.basename(wfFlPth)
                        toLclSessnFlPth = os.path.join(assignDirPath, fileName)
                        shutil.copyfile(wfFlPth, toLclSessnFlPth)
                        if self.__verbose:
                            self.__lfh.write("+%s.%s() - Copied depositor file from workflow path '%s' to session path as '%s'.\n" % (className, methodName, wfFlPth, toLclSessnFlPth))

                        sketchFileLst = p_ccAssignDataStore.getDpstrSketchFile(ligId)
                        if sketchFileLst is not None and fileName in sketchFileLst:
                            toLclSessnSdfInputPth = os.path.join(assignDirPath, ligId + ".sdf")
                            toLclSessnImgPth = os.path.join(assignDirPath, ligId + ".svg")

                            try:
                                shutil.copyfile(toLclSessnFlPth, toLclSessnSdfInputPth)  # just creating copy of file with simple identifier for passing to OeBuildMol
                                oem = OeBuildMol(verbose=self.__verbose, log=self.__lfh)
                                if oem.importFile(toLclSessnSdfInputPth, type='3D'):
                                    self.__lfh.write("Title = %s\n" % oem.getTitle())
                                #
                                oed = OeDepict(verbose=self.__verbose, log=self.__lfh)
                                oed.setMolTitleList([(ligId, oem, "Depiction of SDF submitted for " + ligId)])
                                oed.setDisplayOptions(labelAtomName=True, labelAtomCIPStereo=True, labelAtomIndex=False, labelBondIndex=False, bondDisplayWidth=0.5)
                                oed.setGridOptions(rows=1, cols=1)
                                oed.prepare()
                                oed.write(toLclSessnImgPth)

                                if self.__verbose:
                                    self.__lfh.write("+%s.%s() - Generated image file [%s] from sketch file [%s].\n" % (className, methodName, toLclSessnImgPth, toLclSessnFlPth))
                            except:  # noqa: E722 pylint: disable=bare-except
                                traceback.print_exc(file=self.__lfh)
                        else:
                            if self.__verbose:
                                self.__lfh.write("+%s.%s() - file [%s] is not a sketch file for this ligand ID [%s].\n" % (className, methodName, fileName, ligId))
                    else:
                        if self.__verbose:
                            self.__lfh.write("+%s.%s() - ACCESS PROBLEM when attempting to copy depositor file from workflow path '%s' to session path as '%s'.\n" %
                                             (className, methodName, wfFlPth, toLclSessnFlPth))
                self.__lfh.flush()
            except:  # noqa: E722 pylint: disable=bare-except
                if (self.__verbose):
                    self.__lfh.write("+%s.%s() ----- WARNING ----- processing failed id:  %s\n" % (className, methodName, ligId))
                    traceback.print_exc(file=self.__lfh)
                    self.__lfh.flush()

    def __exitLigMod(self, mode):
        """ Function to accommodate user request to exit lig module task,
            close interface, and return to workflow manager interface.
            Supports different 'modes' = ('completed' | 'unfinished')

            :Params:
                ``mode``:
                    'completed' if annotator has designated all assignments for all ligands and wishes to
                        conclude work in the ligand module.
                    'unfinished' if annotator wishes to leave ligand module but resume work at a later point.

            :Returns:
                ResponseContent object.
        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompWebAppWorker.__exitLigMod() - starting\n")
        #
        if (mode == 'completed'):
            state = "closed(0)"
        elif (mode == 'unfinished'):
            state = "waiting"
        #
        bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        sessionId = self.__sessionId
        depId = self.__reqObj.getValue("identifier")
        instId = self.__reqObj.getValue("instance")
        classId = self.__reqObj.getValue("classID")
        fileSource = str(self.__reqObj.getValue("filesource")).strip().lower()
        #
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompWebAppWorker.__exitLigMod() - depId   %s \n" % depId)
            self.__lfh.write("+ChemCompWebAppWorker.__exitLigMod() - instId  %s \n" % instId)
            self.__lfh.write("+ChemCompWebAppWorker.__exitLigMod() - classID %s \n" % classId)
            self.__lfh.write("+ChemCompWebAppWorker.__exitLigMod() - sessionID %s \n" % sessionId)
            self.__lfh.write("+ChemCompWebAppWorker.__exitLigMod() - filesource %r \n" % fileSource)
            self.__lfh.write("+ChemCompWebAppWorker.__exitLigMod() - bIsWorkflow %r \n" % bIsWorkflow)
        #
        self.__reqObj.setReturnFormat('json')
        #
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        # Update WF status database and persist chem comp assignment states -- ONLY if lig module was running in context of wf-engine
        #
        if bIsWorkflow:
            try:
                bOkay, msg = self.__saveLigModState(mode)
                if bOkay:
                    bSuccess = self.__updateWfTrackingDb(state)
                    if not bSuccess:
                        rC.setError(errMsg="+ChemCompWebAppWorker.__exitLigMod() - TRACKING status, update to '%s' failed for session %s \n" % (state, sessionId))
                    #
                else:
                    if msg != "":
                        rC.setError(errMsg="+ChemCompWebAppWorker.__exitLigMod():\n%s" % msg)
                    else:
                        rC.setError(errMsg="+ChemCompWebAppWorker.__exitLigMod() - problem saving lig module state")
                    #
                #
            except:  # noqa: E722 pylint: disable=bare-except
                if (self.__verbose):
                    self.__lfh.write("+ChemCompWebAppWorker.__exitLigMod() - problem saving lig module state")
                #
                traceback.print_exc(file=self.__lfh)
                rC.setError(errMsg="+ChemCompWebAppWorker.__exitLigMod() - problem saving lig module state:\n%r\n" % traceback.format_exc())
            #
        else:
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppWorker.__exitLigMod() - Not in WF environ so skipping save action of pickle file and status update to TRACKING database for session %s \n" %  # noqa: E501
                                 sessionId)
            #
            if (mode == 'completed'):
                try:
                    if not fileSource:
                        self.__reqObj.setValue("filesource", "session")
                    #
                    bOkay, msg = self.__saveLigModState(mode)
                    if bOkay:
                        rC.setError(errMsg="+ChemCompWebAppWorker.__exitLigMod(): Successfully updated model file.")
                    else:
                        if msg != "":
                            rC.setError(errMsg="+ChemCompWebAppWorker.__exitLigMod():\n%s" % msg)
                        else:
                            rC.setError(errMsg="+ChemCompWebAppWorker.__exitLigMod() - Updating model file failed.")
                        #
                    #
                except:  # noqa: E722 pylint: disable=bare-except
                    if (self.__verbose):
                        self.__lfh.write("+ChemCompWebAppWorker.__exitLigMod() - problem saving lig module state")
                    #
                    traceback.print_exc(file=self.__lfh)
                    rC.setError(errMsg="+ChemCompWebAppWorker.__exitLigMod() - Updating model file failed:\n%r\n" % traceback.format_exc())
                #
            #
        #
        return rC

    def __updateWfTrackingDb(self, p_status):
        """ Private function used to udpate the Workflow Status Tracking Database

            :Params:
                ``p_status``: the new status value to which the deposition data set is being set

            :Helpers:
                wwpdb.apps.ccmodule.utils.WfTracking.WfTracking

            :Returns:
                ``bSuccess``: boolean indicating success/failure of the database update
        """
        #
        bSuccess = False
        #
        sessionId = self.__sessionId
        depId = self.__reqObj.getValue("identifier").upper()
        instId = self.__reqObj.getValue("instance")
        classId = str(self.__reqObj.getValue("classID")).lower()
        #
        try:
            wft = WfTracking(verbose=self.__verbose, log=self.__lfh)
            bSuccess = wft.setInstanceStatus(depId=depId,
                                             instId=instId,
                                             classId=classId,
                                             status=p_status)

            if bSuccess and self.__verbose:
                self.__lfh.write("+ChemCompWebAppWorker.__updateWfTrackingDb() -TRACKING status updated to '%s' for session %s \n" % (p_status, sessionId))
        except:  # noqa: E722 pylint: disable=bare-except
            bSuccess = False
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppWorker.__updateWfTrackingDb() - TRACKING status, update to '%s' failed for session %s \n" % (p_status, sessionId))
            traceback.print_exc(file=self.__lfh)
        #
        return bSuccess

    def __saveLigModState(self, mode):
        """ Persist state of user's chem comp module session which involves capturing updated:
                - ChemCompAssignDataStore pickle file as 'chem-comp-assign-details' file.
                - 'cc-assign-final.cif' file that captures annotator chem comp assignment
                    selections and which is used as input for update of the model file.
                - updated model cif file to reflect current/updated ligand instance assignments

            :Params:
                ``mode``:
                    'completed' if annotator has designated all assignments for all ligands and wishes to
                        conclude work in the ligand module.
                    'unfinished' if annotator wishes to leave ligand module but resume work at a later point.

            :Helpers:
                + wwpdb.wwpdb.io.locator.DataReference.DataFileReference
                + wwpdb.apps.ccmodule.chem.ChemCompAssign

            :Returns:
                ``ok``: boolean indicating success/failure of the save operation
        """
        pathDict = {}
        # ##### updated model file ######
        pathDict['mdlFileDirPth'] = None
        pathDict['mdlFileFlPth'] = None
        # ##### pickle file ######
        pathDict['picFileDirPth'] = None
        pathDict['picFileFlPth'] = None
        # ##### cc-assign-final file ######
        pathDict['ccAssignFinalFileDirPth'] = None
        pathDict['ccAssignFinalFileFlPth'] = None
        #
        fileSource = str(self.__reqObj.getValue("filesource")).strip().lower()
        depId = self.__reqObj.getValue("identifier")
        # instId = self.__reqObj.getValue("instance")
        # classId = self.__reqObj.getValue("classid")
        # sessionId = self.__sessionId
        bSuccess = False

        #
        if fileSource:
            ccE = ChemCompDataExport(self.__reqObj, verbose=self.__verbose, log=self.__lfh)

            # #################################### updated model file #################################################
            if (mode == 'completed'):
                pathDict['mdlFileFlPth'] = ccE.getModelPdxFilePath()

                if pathDict['mdlFileFlPth']:
                    pathDict['mdlFileDirPth'] = (os.path.split(pathDict['mdlFileFlPth']))[0]
                    #
                    if (self.__verbose):
                        self.__lfh.write("+ChemCompWebAppWorker.__saveLigModState() updated model file export directory path: %s\n" % pathDict['mdlFileDirPth'])
                        self.__lfh.write("+ChemCompWebAppWorker.__saveLigModState() updated model file export file      path: %s\n" % pathDict['mdlFileFlPth'])
                else:
                    self.__lfh.write("+ChemCompWebAppWorker.__saveLigModState() ---- WARNING ---- No path obtained for updated model file export file, id %s \n" % depId)

            # #################################### pickle file #################################################

            pathDict['picFileFlPth'] = ccE.getChemCompAssignDetailsFilePath()

            if pathDict['picFileFlPth']:
                pathDict['picFileDirPth'] = (os.path.split(pathDict['picFileFlPth']))[0]

                #
                if (self.__verbose):
                    # self.__lfh.write("+ChemCompWebAppWorker.__saveLigModState() site prefix             : %s\n" % sP)
                    self.__lfh.write("+ChemCompWebAppWorker.__saveLigModState() CC assign details export directory path: %s\n" % pathDict['picFileDirPth'])
                    self.__lfh.write("+ChemCompWebAppWorker.__saveLigModState() CC assign details export file      path: %s\n" % pathDict['picFileFlPth'])
            else:
                self.__lfh.write("+ChemCompWebAppWorker.__saveLigModState() ---- WARNING ---- No path obtained for CC assign details export file, id %s \n" % depId)

            # #################################### cc-assign-final file #################################################
            # i.e. the file that captures the annotator's finalized assignments for chem component IDs

            pathDict['ccAssignFinalFileFlPth'] = ccE.getChemCompAssignFinalFilePath()

            if pathDict['ccAssignFinalFileFlPth']:
                pathDict['ccAssignFinalFileDirPth'] = (os.path.split(pathDict['ccAssignFinalFileFlPth']))[0]

                #
                if (self.__verbose):
                    # self.__lfh.write("+ChemCompWebAppWorker.__saveLigModState() site prefix             : %s\n" % sP)
                    self.__lfh.write("+ChemCompWebAppWorker.__saveLigModState() cc-assign-final file directory path: %s\n" % pathDict['ccAssignFinalFileDirPth'])
                    self.__lfh.write("+ChemCompWebAppWorker.__saveLigModState() cc-assign-final file      path: %s\n" % pathDict['ccAssignFinalFileFlPth'])
            else:
                self.__lfh.write("+ChemCompWebAppWorker.__saveLigModState() ---- WARNING ---- No path obtained for cc-assign-final file, id %s \n" % depId)

        else:
            self.__lfh.write("+ChemCompWebAppWorker.__saveLigModState() - processing undefined | filesource %r \n" % fileSource)

        #########################################################################################################################################################
        #    Call on ChemCompAssign to save current state of ligand assignments
        #########################################################################################################################################################
        ccA = ChemCompAssign(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        bSuccess, msg = ccA.saveState(pathDict)
        #
        return bSuccess, msg

    def __getSession(self):
        """ Join existing session or create new session as required.
        """
        #
        self.__sObj = self.__reqObj.newSessionObj()
        self.__sessionId = self.__sObj.getId()
        self.__sessionPath = self.__sObj.getPath()
        self.__rltvSessionPath = self.__sObj.getRelativePath()
        if (self.__verbose):
            self.__lfh.write("------------------------------------------------------\n")
            self.__lfh.write("+ChemCompWebApp.__getSession() - creating/joining session %s\n" % self.__sessionId)
            # self.__lfh.write("+ChemCompWebApp.__getSession() - workflow storage path    %s\n" % self.__workflowStoragePath)
            self.__lfh.write("+ChemCompWebApp.__getSession() - session path %s\n" % self.__sessionPath)

    def __isFileUpload(self, fileTag='file'):
        """ Generic check for the existence of request paramenter "file".
        """
        # Gracefully exit if no file is provide in the request object -
        try:
            stringtypes = (unicode, str)
        except NameError:
            stringtypes = (str, bytes)

        fs = self.__reqObj.getRawValue(fileTag)
        if (fs is None) or isinstance(fs, stringtypes):
            return False
        return True

    def __uploadFile(self, fileTag='file', fileTypeTag='filetype'):
        #
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebApp.__uploadFile() - file upload starting\n")

        #
        # Copy upload file to session directory -
        try:
            fs = self.__reqObj.getRawValue(fileTag)
            fNameInput = str(fs.filename).lower()
            #
            # Need to deal with some platform issues -
            #
            if fNameInput.find('\\') != -1:
                # likely windows path -
                fName = ntpath.basename(fNameInput)
            else:
                fName = os.path.basename(fNameInput)

            #
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebApp.__loadDataFileStart() - upload file %s\n" % fs.filename)
                self.__lfh.write("+ChemCompWebApp.__loadDataFileStart() - base file   %s\n" % fName)
            #
            # Store upload file in session directory -

            self.__modelFilePath = os.path.join(self.__sessionPath, fName)
            ofh = open(self.__modelFilePath, 'wb')
            ofh.write(fs.file.read())
            ofh.close()
            self.__reqObj.setValue("UploadFileName", fName)
            self.__reqObj.setValue("filePath", self.__modelFilePath)
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebApp.__uploadFile() Uploaded file %s\n" % str(fName))
        except:  # noqa: E722 pylint: disable=bare-except
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebApp.__uploadFile() File upload processing failed for %s\n" % str(fs.filename))
                traceback.print_exc(file=self.__lfh)

            return False
        #
        # Verify file name
        #
        fs = self.__reqObj.getRawValue(fileTag)
        fmt = self.__reqObj.getValue(fileTypeTag)
        fType = fmt.lower()
        fNameInput = str(fs.filename).strip().lower()
        #
        # Need to deal with some platform issues -
        #
        if (fNameInput.find('\\') != -1) :
            # likely windows path -
            fName = ntpath.basename(fNameInput)
        else:
            fName = os.path.basename(fNameInput)
        #
        #
        # if fName.startswith('rcsb'):
        #     fId = fName[:10]
        # elif fName.startswith('d_'):
        #     fId = fName[:8]
        # else:
        #     fId = '000000'
        #     if (self.__verbose):
        #         self.__lfh.write("+ChemCompWebApp.__uploadFile() using default identifier for %s\n" % str(fName))

        # self.__reqObj.setValue("identifier",fId)
        self.__reqObj.setValue("fileName", fName)
        #
        if fType in ['cif', 'cifeps', 'pdb']:
            self.__reqObj.setValue("fileType", fType)
        else:
            self.__reqObj.setValue("fileType", 'unknown')

        if (self.__verbose):
            self.__lfh.write("+ChemCompWebApp.__uploadFile() identifier %s\n" % self.__reqObj.getValue("identifier"))
            self.__lfh.write("+ChemCompWebApp.__uploadFile() UploadFileType  %s\n" % self.__reqObj.getValue("UploadFileType"))
            self.__lfh.write("+ChemCompWebApp.__uploadFile() UploadFileName  %s\n" % self.__reqObj.getValue("UploadFileName"))
        return True

    def __setSemaphore(self):
        sVal = str(time.strftime("TMP_%Y%m%d%H%M%S", time.localtime()))
        self.__reqObj.setValue('semaphore', sVal)
        return sVal

    def __openSemaphoreLog(self, semaphore="TMP_"):
        # sessionId = self.__reqObj.getSessionId()
        fPathAbs = os.path.join(self.__sessionPath, semaphore + '.log')
        self.__lfh = open(fPathAbs, 'w')

    # def __closeSemaphoreLog(self, semaphore="TMP_"):
    #     self.__lfh.flush()
    #     self.__lfh.close()

    def __postSemaphore(self, semaphore='TMP_', value="OK"):
        # sessionId = self.__reqObj.getSessionId()
        fPathAbs = os.path.join(self.__sessionPath, semaphore)
        fp = open(fPathAbs, 'w')
        fp.write("%s\n" % value)
        fp.close()
        return semaphore

    def __semaphoreExists(self, semaphore='TMP_'):
        # sessionId = self.__reqObj.getSessionId()
        fPathAbs = os.path.join(self.__sessionPath, semaphore)
        if (os.access(fPathAbs, os.F_OK)):
            return True
        else:
            return False

    def __getSemaphore(self, semaphore='TMP_'):
        # sessionId = self.__reqObj.getSessionId()
        fPathAbs = os.path.join(self.__sessionPath, semaphore)
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebApp.__getSemaphore() - checking %s in path %s\n" % (semaphore, fPathAbs))
        try:
            fp = open(fPathAbs, 'r')
            lines = fp.readlines()
            fp.close()
            sval = lines[0][:-1]
        except:  # noqa: E722 pylint: disable=bare-except
            sval = "FAIL"
        return sval

    # def __openChildProcessLog(self, label="TMP_"):
    #     # sessionId = self.__reqObj.getSessionId()
    #     fPathAbs = os.path.join(self.__sessionPath, label + '.log')
    #     self.__lfh = open(fPathAbs, 'w')

    def __processTemplate(self, fn, parameterDict=None):
        """ Read the input HTML template data file and perform the key/value substitutions in the
            input parameter dictionary.

            :Params:
                ``parameterDict``: dictionary where
                key = name of subsitution placeholder in the template and
                value = data to be used to substitute information for the placeholder

            :Returns:
                string representing entirety of content with subsitution placeholders now replaced with data
        """
        if parameterDict is None:
            parameterDict = {}
        tPath = self.__reqObj.getValue("TemplatePath")
        fPath = os.path.join(tPath, fn)
        ifh = open(fPath, 'r')
        sIn = ifh.read()
        ifh.close()
        return (sIn % parameterDict)

    def __isWorkflow(self):
        """ Determine if currently operating in Workflow Managed environment

            :Returns:
                boolean indicating whether or not currently operating in Workflow Managed environment
        """
        #
        fileSource = str(self.__reqObj.getValue("filesource")).lower()
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppWorker.__isWorkflow() - filesource is %s\n" % fileSource)
        #
        # add wf_archive to fix PDBe wfm issue -- jdw 2011-06-30
        #
        if fileSource in ['archive', 'wf-archive', 'wf_archive', 'wf-instance', 'wf_instance']:
            # if the file source is any of the above then we are in the workflow manager environment
            return True
        else:
            # else we are in the standalone dev environment
            return False

    def __readCovalentBondingInfo(self):
        """ Read inter-residue covalent bonding information from D_xxxxxxxxxx-cc-link.cif file.
        """
        depId = str(self.__reqObj.getValue("identifier"))
        ccLinkFilePath = os.path.join(self.__sessionPath, depId + '-cc-link.cif')
        if not os.access(ccLinkFilePath, os.F_OK):
            return {}
        #
        try:
            cifObj = mmCIFUtil(filePath=ccLinkFilePath)
            retList = cifObj.GetValue("pdbx_covalent_bonding")
            linkInfoMap = {}
            for retDir in retList:
                if ("inst_id" not in retDir) or ("first_atom_id" not in retDir) or ("second_atom_id" not in retDir) or ("dist" not in retDir):
                    continue
                #
                if retDir["inst_id"] in linkInfoMap:
                    linkInfoMap[retDir["inst_id"]] += "<br />" + retDir["first_atom_id"] + " - " + retDir["second_atom_id"] + " = " + retDir["dist"]
                else:
                    linkInfoMap[retDir["inst_id"]] = "The following atoms are linked together:<br />" + retDir["first_atom_id"] \
                        + " - " + retDir["second_atom_id"] + " = " + retDir["dist"]
                #
            #
            return linkInfoMap
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return {}
        #


class RedirectDevice:
    def write(self, s):
        pass


def testmain():
    sTool = ChemCompWebApp()
    d = sTool.doOp()
    for k, v in d.items():
        sys.stdout.write("Key - %s  value - %r\n" % (k, v))


if __name__ == '__main__':
    testmain()
