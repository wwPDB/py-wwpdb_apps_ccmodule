##
# File:  ChemCompWebAppLite.py
# Date:  20-Aug-2012
# Updates:
# 2012-08-20    RPS    Created based on ChemCompWebApp implementation
# 2012-12-18    RPS    Fixed problem with setDpstrUploadFile() method.
# 2013-02-21    RPS    Use of "exact match" searching now replacing "id match" testing and
#                       now exporting chem-comp-depositor-info.cif file to workflow storage
# 2013-02-21    RPS    Call to ChemCompAssignDepictLite.doRender_ResultFilesPage() to facilitate unit testing
# 2013-03-31    RPS    self.__saveLigModState() updated w/ improved checking for proper DataFile references and corrected
#                        for use of "pdbx" file type instead of "cif" for model files.
# 2013-04-08    RPS    Corrected to apply correct version numbers on files persisted to workflow storage.
#                        Introducing use of ChemCompDataExport to manage export of files to workflow storage.
# 2013-04-09    RPS    ChemCompDataExport class now being leverated in self.__saveLigModState() as well.
# 2013-04-10    RPS    Updated to use CCAssignDataStore methods that distinguish generated sketch files from file uploads for "Lite" LigModule
# 2013-04-12    RPS    Added self.__importDepositorFiles().
# 2013-06-11    RPS    Accommodating new 'deposit' filesource/storage type.
# 2013-06-20    RPS    More efficient handling of launch (skipping cc-assign search when previous cc-assign details exist)
# 2013-06-26    RPS    Updates in anticipation of better integration with Deposition UI.
# 2013-07-03    RPS    Added self._validateCcId() to verify any values submitted for "alternate ligand ID".
# 2013-07-18    RPS    Updated for "intermittent" serialization of UI state to "deposit" storage.
#                        Updated handling for depositor file uploads.
# 2013-07-22    RPS    More updates for improved handling of files uploaded by depositor.
# 2013-08-09    RPS    Introduced use of cc-dpstr-progress files
# 2013-09-18    RPS    Corrections needed for stand-alone testing.
# 2013-10-23    RPS    Updates in support of handling data propagation from LigandLite of DepUI to LigandModule of annotation.
# 2013-11-19    RPS    Removed obsolete logic for handling of invalid author-assigned ChemComp IDs. Previously used "invalidLigId" flag
#                        to help determine whether necessary to do ChemComp ref report material generation. But slightly less rigorous matching criteria
#                        used now so can eliminate use of this flag and instead simply check whether there was a best hit or not.
# 2013-12-09    RPS    Updated for display of 2D images that are now aligned.
# 2013-12-16    RPS    _checkForSummaryData() no longer making use of delay interval before returning. Timer mediated interval enforced on front-end instead.
# 2014-01-17    RPS    _checkForUploadedFiles() now supporting requests distinguishing image files from component definition files
# 2014-01-21    RPS    __genAligned2dImages() updated to use subprocess.Popen strategy to eliminate occurrence of runaway process on server
# 2014-01-23    RPS    __runTimeout modified as workaround for permissions problem on executing timeoutscript.sh
#                        _checkForUploadedFiles() now returning datapoints indicating whether any files on record and a list of any files if applicable.
# 2014-01-24    RPS    __genAligned2dImages() corrected to work in case of single instance of ligand which has no top match, and so only one image to generate.
#                        __runTimeout() reverted back to original execution of timeoutscript.sh in sessions directory now that permissions issue resolved.
# 2014-01-31    RPS    _saveNwLgndDscrptn() updated to account for interim implementation whereby no possibility for user to choose sketch over descriptor string.
# 2014-03-11    RPS    __verifyUploadedFiles updated to make allowances for 'jpeg','tiff','svg','bmp' image file types
# 2014-03-19    RPS    parameterized self.__deployPath so as to derive based on ConfigInfoData. Used in __runTimeout() to determine path to runtime env script.
#                        Instituted workaround to allow handling of service URLs with custom prefixes.
# 2014-04-28    RPS    _uploadDpstrFile now enforcing all handling of filetype/extension to be in lowercase
# 2014-05-13    RPS    _uploadDpstrFile fixed for proper handling of fileName when user is on Windows OS
# 2014-06-23    RPS    Updates in support of providing more elaborate choices for choosing an alternate Ligand ID(originally proposed ID vs.
#                        one of the possible exact match IDs for cases where some ligand instances have differing matches).
# 2014-10-31    RPS    Support for providing 2D image of author proposed Ligand ID in "handle mismatch" section of UI, on hover over of the ID.
# 2014-11-15    RPS    bug in self.__generateInstanceLevelData() addressed, so that author proposed ID is first checked for validity before attempt to generate 2D image.
# 2016-02-17    RPS    removing obsolete handling for updated model files in __saveLigModState() (was ultimately decided that LigLite processing would not involve updates to this file).
# 2016-03-02    RPS    updated __genAligned2dImages() with safety measure to guarantee generation of 2D images when original effort to generate aligned images fails silently.
# 2016-04-29    RPS    updated __genAligned2dImages() to accommodate scenarios where use of UNL, UNX, or similar ligand ID are contained in depositor's submission.
# 2016-06-30    RPS    clean up handling of accepted file types for files uploaded by depositor via LigandLite.
# 2017-01-31    EP     DAOTHER-2233 change obsolete runtime-env.sh to site-config
# 2017-02-03    RPS    Updated to support capture of data for ligands as "focus of research"
# 2017-02-13    RPS    Updates to distinguish between ligandIDs that were simply selected as focus of research vs those for which data was actually provided.
#                        Invoking save of state on intermittent saves of research data for a given ligand ID.
# 2017-02-13    RPS    Performing intermittent save to pickle file on calls to updateResearchList()
# 2017-03-27    RPS    Disabling functionality for capturing HOH research data and for capturing ligand binding assay data
#                        Generating cc-dpstr-info file on intermittent saves. Also on startup, now invoking saveLigModState to generate cc-dpstr-prgrss file
#                        for depui monitoring purposes
# 2020-08-27    ZF     Added blocking 'REF_ONLY' status ligands
##
"""
'Lite' Chemical component editor tool web request and response processing modules.
Used in context of the wwPDB common tool deposition UI.

This software was developed as part of the World Wide Protein Data Bank
Common Deposition and Annotation System Project

Copyright (c) 2012 wwPDB

This software is provided under a Creative Commons Attribution 3.0 Unported
License described at http://creativecommons.org/licenses/by/3.0/.

"""
__docformat__ = "restructuredtext en"
__author__ = "Raul Sala"
__email__ = "rsala@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import os
import re
import sys
# import time
import traceback
import ntpath
import shutil
from http import HTTPStatus
from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
from pathlib import Path
import inspect

from wwpdb.apps.ccmodule.utils.Exceptions import InvalidLigandIdError, LigandStateError, InvalidDepositionIdError
from wwpdb.apps.ccmodule.utils.LigandAnalysisState import LigandAnalysisState
from wwpdb.utils.session.WebRequest import InputRequest, ResponseContent
#
from wwpdb.apps.ccmodule.chem.ChemCompAssign import ChemCompAssign
try:
    from wwpdb.apps.ccmodule.chem.ChemCompAssignDepictLite import ChemCompAssignDepictLite
except Exception as e:
    print('++ChemCompWebAppLite -- Error importing ChemCompAssignDepictLite\n%s' % str(e))
#
# from wwpdb.apps.ccmodule.search.ChemCompSearch import ChemCompSearch
# from wwpdb.apps.ccmodule.search.ChemCompSearchDepict import ChemCompSearchDepict
# from wwpdb.apps.ccmodule.search.ChemCompSearchDb import ChemCompSearchDb
# from wwpdb.apps.ccmodule.search.ChemCompSearchDbDepict import ChemCompSearchDbDepict
#
# from wwpdb.utils.wf.dbapi.WfTracking import WfTracking
from wwpdb.apps.ccmodule.utils.ChemCompConfig import ChemCompConfig
#
from wwpdb.apps.ccmodule.io.ChemCompAssignDataStore import ChemCompAssignDataStore
from wwpdb.apps.ccmodule.io.ChemCompDataExport import ChemCompDataExport
#
from wwpdb.utils.config.ConfigInfo import ConfigInfo
from wwpdb.utils.config.ConfigInfoApp import ConfigInfoAppCommon
#
from wwpdb.io.file.mmCIFUtil import mmCIFUtil

from wwpdb.utils.wf.dbapi.WfDbApi import WfDbApi
from wwpdb.utils.wf.dbapi.WFEtime import getTimeNow
from wwpdb.io.locator.PathInfo import PathInfo


class ChemCompWebAppLite(object):
    """Handle request and response object processing for the chemical component lite module application.

    """
    def __init__(self, parameterDict=None, verbose=False, log=sys.stderr, siteId="WWPDB_DEV"):
        """
        Create an instance of `ChemCompWebAppLite` to manage a ligand editor web request from
        wwPDB Common Tool Deposition UI.

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
        # self.__deployPath = self.__cI.get('SITE_DEPLOY_PATH')
        self.__topSessionPath = self.__cICommon.get_site_web_apps_top_sessions_path()
        self.__sessionsPath = self.__cICommon.get_site_web_apps_sessions_path()
        self.__templatePath = os.path.join(self.__topPath, "htdocs", "ccmodule_lite")
        #

        if isinstance(parameterDict, dict):
            self.__myParameterDict = parameterDict
        else:
            self.__myParameterDict = {}

        if (self.__verbose):
            self.__lfh.write("+%s.%s() - REQUEST STARTING ------------------------------------\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
            self.__lfh.write("+%s.%s() - dumping input parameter dictionary \n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
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
        if (self.__verbose):
            self.__lfh.write("-----------------------------------------------------\n")
            self.__lfh.write("+%s.%s() Leaving _init with request contents\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
            self.__reqObj.printIt(ofh=self.__lfh)
            self.__lfh.write("---------------ChemCompWebAppLite - done -------------------------------\n")
            self.__lfh.flush()

    def doOp(self):
        """ Execute request and package results in response dictionary.

        :Returns:
             A dictionary containing response data for the input request.
             Minimally, the content of this dictionary will include the
             keys: CONTENT_TYPE and REQUEST_STRING.
        """
        stw = ChemCompWebAppLiteWorker(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        rC = stw.doOp()
        if self.__debug:
            rqp = self.__reqObj.getRequestPath()
            self.__lfh.write("+%s.%s() operation %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, rqp))
            self.__lfh.write("+%s.%s() return format %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, self.__reqObj.getReturnFormat()))
            if rC is not None:
                self.__lfh.write("%s" % (''.join(rC.dump())))
            else:
                self.__lfh.write("+%s.%s() return object is empty\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))

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
        retL.append("\n-----------------ChemCompWebAppLite().__dumpRequest()-----------------------------\n")
        retL.append("Parameter dictionary length = %d\n" % len(self.__myParameterDict))
        for k, vL in self.__myParameterDict.items():
            retL.append("Parameter %30s :" % k)
            for v in vL:
                retL.append(" ->  %s\n" % v)
        retL.append("-------------------------------------------------------------\n")
        return retL


class ChemCompWebAppLiteWorker(object):
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
        self.__depId = "D_0" if self.__reqObj.getValue("identifier") in [None, 'TMP_ID'] else self.__reqObj.getValue("identifier").upper()
        self.__siteId = str(self.__reqObj.getValue("WWPDB_SITE_ID"))
        self.__cI = ConfigInfo(self.__siteId)
        self.__deployPath = self.__cI.get('SITE_DEPLOY_PATH')
        self.__siteSrvcUrlPathPrefix = self.__cI.get('SITE_SERVICE_URL_PATH_PREFIX', '')
        # self.__siteConfigDir = self.__cI.get('TOP_WWPDB_SITE_CONFIG_DIR')
        # self.__siteLoc = self.__cI.get('WWPDB_SITE_LOC')
        self.__ccConfig = ChemCompConfig(reqObj, verbose=self.__verbose, log=self.__lfh)
        self.__pathInfo = PathInfo()
        self.__depositPath = Path(self.__pathInfo.getDepositPath(self.__depId)).parent
        # self.__depositAssignPath = os.path.join(self.__depositPath, self.__depId, 'assign')
        # self.__ccReportPath = os.path.join(self.__depositPath, self.__depId, 'cc_analysis')  # should we add 'cc_analysis' in a variable in site-config?
        self.__logger = self._setupLog(log)

        #
        # self.__pathInstncsVwTmplts = "templates/workflow_ui/instances_view"
        # self.__pathSnglInstcTmplts = self.__pathInstncsVwTmplts + "/single_instance"
        # self.__pathSnglInstcEditorTmplts = self.__pathSnglInstcTmplts + "/editor"
        #
        self.__appPathD = {'/service/environment/dump': '_dumpOp',
                           '/service/cc_lite/testfile': '_ligandSrchSummary',
                           '/service/cc_lite/save/newligdescr': '_saveNwLgndDscrptn',
                           '/service/cc_lite/save/exactmtchid': '_saveExactMtchId',
                           '/service/cc_lite/save/rsrchdata': '_saveRsrchData',
                           '/service/cc_lite/updatersrchlst': '_updateResearchList',
                           '/service/cc_lite/validate_ccid': '_validateCcId',
                           '/service/cc_lite/check_uploaded_files': '_checkForUploadedFiles',
                           '/service/cc_lite/remove_uploaded_file': '_removeUploadedFile',
                           # ##############  below are URLs created for WFM/common tool development effort######################
                           '/service/cc_lite/wf/new_session': '_ligandSrchSummary',
                           '/service/cc_lite/view/ligandsummary': '_loadSummaryData',
                           '/service/cc_lite/view/ligandsummary/data_check': '_checkForSummaryData',
                           '/service/cc_lite/view/ligandsummary/data_load': '_loadSummaryData',
                           '/service/cc_lite/view/instancebrowser': '_generateInstncBrowser',
                           '/service/cc_lite/wf/exit_not_finished': '_exit_notFinished',
                           '/service/cc_lite/wf/exit_finished': '_exit_Finished',
                           # report endpoints
                           '/service/cc_lite/report/create': '_runAnalysis',
                           '/service/cc_lite/report/file': '_getReportFile',
                           '/service/cc_lite/report/summary': '_getLigandInstancesData',
                           '/service/cc_lite/report/status': '_getLigandAnalysisStatus',
                           ###################################################################################################
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
        self.__lfh.write("+%s.%s() original request path is %r\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, reqPath))
        reqPath = self.__normalizeReqPath(reqPath)
        self.__lfh.write("+%s.%s() normalized request path is %r\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, reqPath))
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
        reqPath = ''
        try:
            reqPath = self.__reqObj.getRequestPath()
            self.__lfh.write("+%s.%s() original request path is %r\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, reqPath))
            reqPath = self.__normalizeReqPath(reqPath)
            self.__lfh.write("+%s.%s() normalized request path is %r\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, reqPath))
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

    def __normalizeReqPath(self, p_reqPath):
        # special handling required for some sites which have custom prefixes in url request
        if self.__siteSrvcUrlPathPrefix and len(self.__siteSrvcUrlPathPrefix) > 1:
            if p_reqPath.startswith(self.__siteSrvcUrlPathPrefix):
                return p_reqPath.split(self.__siteSrvcUrlPathPrefix)[1]
        else:
            return p_reqPath

    ################################################################################################################
    # ------------------------------------------------------------------------------------------------------------
    #      Top-level REST methods
    # ------------------------------------------------------------------------------------------------------------
    #
    def _dumpOp(self):
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        rC.setHtmlList(self.__reqObj.dump(format='html'))
        return rC

    def _getReportFile(self):
        """ Get files generated by the report operation.

            :Helpers:
                wwpdb.apps.ccmodule.

            :Returns:
                Operation output is packaged in a ResponseContent() object.
                The output will vary depending on the type of requested file, which
                will affect the Content-Type HTTP header. For now it supports getting
                svg, gif and cif files.
        """
        supportedSources = ["ccd", "author", "report"]  # this will tell from where we should get the file
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        # sessionId = self.__reqObj.getValue("sessionid")
        depId = self.__reqObj.getValue("identifier").upper()
        source = self.__reqObj.getValue("source").lower()
        ligandId = self.__reqObj.getValue("ligid")
        filename = self.__reqObj.getValue("file")

        ccReportPath = os.path.join(self.__depositPath, depId, "cc_analysis")
        fileType = filename.split(".")[-1]
        filePath = None

        if (self.__verbose):
            self.__lfh.write("+%s.%s() Requesting file '%s' from '%s' for deposition '%s'\n" % (
                self.__class__.__name__, inspect.currentframe().f_code.co_name, filename, source, depId
            ))

        # allowing only alphanum, _ and . characters
        filename = re.sub('[^a-zA-Z0-9_.-]+', '', filename)

        if source not in supportedSources:
            rC.setError(errMsg="Source should be either 'ccd', 'author' or 'report'")
            rC.setStatusCode(HTTPStatus.BAD_REQUEST)
            return rC

        if source == "ccd" and ligandId == "":
            rC.setError(errMsg="You must pass a valid ligand ID")
            rC.setStatusCode(HTTPStatus.BAD_REQUEST)
            return rC

        if fileType == "svg":
            # all svgs, afaik, are located in the root folder of reports
            filePath = os.path.join(ccReportPath, filename)

            # even though svg can be considered a text file, we set as binary
            # so ResponseContent can set the correct Content-Type header
            # Someday: test for possible encoding issues
            rC.setReturnFormat("binary")
            rC.setBinaryFile(filePath)
        elif fileType == "cif":
            if source == "ccd":
                filePath = os.path.join(ccReportPath, "rfrnc_reports", ligandId, filename)
            elif source == "author":
                filePath = os.path.join(ccReportPath, ligandId, "report", filename)

            rC.setReturnFormat("text")
            rC.setTextFile(filePath)
        elif fileType == "gif":
            if source == "ccd":
                filePath = os.path.join(ccReportPath, "rfrnc_reports", ligandId, filename)

            rC.setReturnFormat("binary")
            rC.setBinaryFile(filePath)
        elif fileType == "html":
            filePath = os.path.join(ccReportPath, "html", ligandId, filename)

            rC.setReturnFormat("html")
            rC.setTextFile(filePath)
            # Someday: Should add access for textcontent return
            rC.setHtmlText(rC._cD["textcontent"])  # pylint: disable=protected-access
        else:
            rC.setReturnFormat("text")

        if not filePath or not os.path.exists(filePath):
            rC.setError(errMsg="File not found")
            rC.setStatusCode(HTTPStatus.NOT_FOUND)

        return rC

    def _ligandSrchSummary(self):
        """ Launch chemical component "lite" module interface

            :Helpers:
                wwpdb.apps.ccmodule.

            :Returns:
                Operation output is packaged in a ResponseContent() object.
                The output consists of a HTML starter container page for quicker return to the client.
                This container page is then populated with content via AJAX calls.
        """
        if (self.__verbose):
            self.__lfh.write("+%s.%s() Starting now\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
        # determine if currently operating in Workflow Managed environment
        bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        #
        dataFile = str(self.__reqObj.getValue("datafile"))
        fileSource = str(self.__reqObj.getValue("filesource")).strip().lower()
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        if (self.__verbose):
            self.__lfh.write("+%s.%s() workflow flag is %r\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, bIsWorkflow))

        if bIsWorkflow:
            # Update WF status database --
            # '''
            # bSuccess = self.__updateWfTrackingDb("open")
            # if not bSuccess:
            #     rC.setError(errMsg="+%s.%s() - TRACKING status, update to 'open' failed for session %s \n" %
            #        (self.__class__.__name__, inspect.currentframe().f_code.co_name, self.__sessionId ) )
            # else:
            #     if (self.__verbose):
            #         self.__lfh.write("+%s.%s() Tracking status set to open\n"%(self.__class__.__name__, inspect.currentframe().f_code.co_name) )
            # '''
            pass
        else:
            if fileSource and fileSource == "rcsb_dev":
                if dataFile:
                    sessionFilePath = os.path.join(self.__sessionPath, dataFile)

                    # make copy of file in sessions directory for any access/processing required by front-end
                    devDataExamplePath = os.path.join(self.__deployPath + "/wwpdb_da_test/webapps/htdocs/ccmodule_lite/test_data", dataFile)
                    shutil.copyfile(devDataExamplePath, sessionFilePath)
                    self.__reqObj.setValue("filePath", devDataExamplePath)

            elif fileSource and fileSource == "upload":
                if not self.__isFileUpload():
                    rC.setError(errMsg='No file uploaded')
                    return rC
            #
                self.__uploadFile()
        #
        if (self.__verbose):
            self.__lfh.write("+%s.%s() Called with workflow: %r\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, bIsWorkflow))

        ccAD = ChemCompAssignDepictLite(self.__reqObj, self.__verbose, self.__lfh)
        ccAD.setSessionPaths(self.__reqObj)
        oL = ccAD.doRender_LigSrchSummary(self.__reqObj, bIsWorkflow)
        rC.setHtmlText('\n'.join(oL))
        #
        return rC

    def _loadSummaryData(self):
        """ Call for loading content displayed in summary of chem component inventory results

            :Helpers:

                + wwpdb.apps.ccmodule.chem.ChemCompAssignDepictLite.ChemCompAssignDepictLite
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                Operation output is packaged in a ResponseContent() object.
                The output consists of the HTML results content that is used to re-populate the
                Batch Search Results container markup that had already been delivered to
                the browser in a prior request.
        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+%s.%s() starting\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
        # determine if currently operating in Workflow Managed environment
        self.__getSession()
        # sessionId = self.__sessionId
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
        #
        ccAD = ChemCompAssignDepictLite(self.__reqObj, self.__verbose, self.__lfh)
        oL = ccAD.doRender_LigSummaryContent(ccADS, self.__reqObj)
        oL.extend(ccAD.doRender_InstanceBrswrLaunchForm(self.__reqObj))
        # oL.extend(ccAD.doRender_WaterRsrchCaptureContent(ccADS, self.__reqObj))
        #
        rC.setHtmlText('\n'.join(oL))
        return rC

    def _runAnalysis(self):
        """Run ligand analysis workflow.

        Raises:
            InvalidDepositionIdError: in case an invalid dep id was provided

        Returns:
            ResponseContent: ResponseContent object
        """
        now = getTimeNow()
        wfApi = WfDbApi(verbose=True, log=self.__lfh)
        status = 'success'

        if not self.__depId or not re.fullmatch('D_[0-9]+', self.__depId):
            raise InvalidDepositionIdError('Invalid deposition ID')

        analysisState = LigandAnalysisState(self.__depId)
        progress = analysisState.getProgress()

        if progress['state'] in ['busy', 'preparing']:
            raise LigandStateError('Ligand analysis already running or system busy')

        query = "update status.communication set " \
            "  sender = 'DEP' " \
            ", receiver = 'WFE' " \
            ", wf_class_file = 'wf_op_ligand_analysis.xml' " \
            ", wf_class_id = 'ligandAnalysis' " \
            ", command = 'runWF' " \
            ", status = 'PENDING' " \
            ", actual_timestamp = '{}' " \
            ", parent_dep_set_id = '{}' " \
            ", parent_wf_class_id = 'DepUpload' " \
            ", parent_wf_inst_id = 'W_001' " \
            "where dep_set_id = '{}'".format(now, self.__depId, self.__depId)

        if self.__verbose:
            self.__logger.debug('Running sql query %s', query)

        nrow = wfApi.runUpdateSQL(query)

        self.__logger.info('Result %d', nrow)

        analysisState.reset()

        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        rC.setReturnFormat('jsonData')
        rC.setData({'status': status})

        return rC

    def _getLigandAnalysisStatus(self):
        """Get the state of ligand analysis for this deposition.

        Returns:
            ResponseContent: response object with state in json
        """
        depId = str(self.__reqObj.getValue('identifier')).upper()
        ligState = LigandAnalysisState(depId, self.__verbose, self.__lfh)
        state = ligState.getProgress()

        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        rC.setReturnFormat('jsonData')
        rC.setData(state)

        return rC

    def _getLigandInstancesData(self):
        """Endpoint to get a summary dictionary for requested
        ligand ids. See _generateLigGroupSummaryDict() below for
        the info provided.

        Raises:
            InvalidLigandId: raised when an empty lig id is
                provided

        Returns:
            ResponseContent: ResponseContent object with format "jsonData"
        """
        ccAssignDataStore = ChemCompAssignDataStore(self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        ligIds = str(self.__reqObj.getValue('ligids'))

        if not ligIds or ligIds == '':
            raise InvalidLigandIdError()

        # allowing only alphanum, ",", and _ chars
        ligIds = re.sub('[^a-zA-Z0-9_,]+', '', ligIds)
        ligIdsList = ligIds.split(',')

        if self.__verbose:
            self.__logger.debug('Getting summary data for ligands %s', ligIds)

        ligandInstancesData = self._generateLigGroupSummaryDict(ccAssignDataStore, ligIdsList)

        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        rC.setReturnFormat('jsonData')
        rC.setData(ligandInstancesData)

        return rC

    def _generateLigGroupSummaryDict(self, ccAssignDataStore, ligIdList):
        """Generate utility dictionary to hold info for chem comp
        groups indicated in depositor's data. I copied this method
        to this class because I intend to remove any dependency of
        ChemCompWebAppLite on ChemCompAssignDepictLite.

        Args:
            ccAssignDataStore (ChemCompAssignDataStore): assign data
                store with latest version of cc assign details file

        Returns:
            dict: Currently returning two-tier dictionary with primary
                key of chem comp ID and following secondary keys:

                totlInstncsInGrp: total number of chem component
                    instances with same ligand ID as given ID
                bGrpRequiresAttention: boolean indicating whether
                    or not the given ligand ID group has any instances
                    for which top hit does not match author provided ligand ID
                grpMismatchCnt: total number of chem component instances
                    where mismatch detected
                instidLst: list of instanceIds for all instances of the
                    chem component found in the depositor data
        """
        returnDict = {}
        instanceIdList = ccAssignDataStore.getAuthAssignmentKeys()
        ccA = ChemCompAssign(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        for inst in instanceIdList:
            authorAssignedId = ccAssignDataStore.getAuthAssignment(inst)

            if authorAssignedId not in ligIdList:
                continue

            if not authorAssignedId:
                # this should never happen
                continue

            if authorAssignedId not in returnDict:
                returnDict[authorAssignedId] = {
                    'totlInstncsInGrp': 0,
                    'bGrpRequiresAttention': False,
                    'bGrpMismatchAddressed': False,
                    'grpMismatchCnt': 0,
                    'mismatchLst': [],
                    'instIdLst': [],
                    'ccName': ccAssignDataStore.getCcName(inst),
                    'ccFormula': ccAssignDataStore.getCcFormula(inst),
                }

                if ccA.validCcId(authorAssignedId) == 1:
                    ccAssignDataStore.addLigIdToInvalidLst(authorAssignedId)

            returnDict[authorAssignedId]['totlInstncsInGrp'] += 1
            returnDict[authorAssignedId]['instIdLst'].append(inst)
            returnDict[authorAssignedId]['instIdLst'].sort  # pylint: disable=pointless-statement
            topHitCcId = ccAssignDataStore.getBatchBestHitId(inst)

            if topHitCcId.upper() != authorAssignedId.upper():
                returnDict[authorAssignedId]['bGrpRequiresAttention'] = True
                returnDict[authorAssignedId]['grpMismatchCnt'] += 1
                returnDict[authorAssignedId]['mismatchLst'].append(inst)
                returnDict[authorAssignedId]['mismatchLst'].sort  # pylint: disable=pointless-statement

            isResolved = authorAssignedId in ccAssignDataStore.getGlbllyRslvdGrpList()
            returnDict[authorAssignedId]['bGrpMismatchAddressed'] = isResolved
            returnDict[authorAssignedId]['isResolved'] = isResolved

        return returnDict

    def _saveExactMtchId(self):
        """ Register depositor's choice to use exact match CC ID instead of original lig ID with ChemCompAssignDataStore

            :Helpers:
                wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                ResponseContent() object.
                No display output for this method.
        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+%s.%s() Starting now\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
        #
        self.__getSession()
        # sessionId = self.__sessionId
        # depId = str(self.__reqObj.getValue("identifier")).upper()
        # wfInstId = str(self.__reqObj.getValue("instance")).upper()
        authAssgndGrp = str(self.__reqObj.getValue("auth_assgnd_grp"))
        mode = str(self.__reqObj.getValue("mode"))
        #
        dpstrExactMtchCcId = str(self.__reqObj.getValue("exactmatchid"))
        dpstrOrigPrpsdCcId = str(self.__reqObj.getValue("origproposedid"))
        #
        if (self.__verbose):
            self.__lfh.write("+%s.%s() authAssgndGrp is: %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, authAssgndGrp))

        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        # unpickle assign data from ccAssignDataStore
        if (self.__verbose):
            self.__lfh.write("+%s.%s() unpickling ccAssignDataStore\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))

        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)

        if mode == 'done':  # mode will be either 'done' or 'undo'
            ccADS.addGrpToGlbllyRslvdLst(authAssgndGrp)
            ccADS.initializeGrpInfo(authAssgndGrp)
            if dpstrExactMtchCcId and len(dpstrExactMtchCcId) > 1:
                ccADS.setDpstrExactMtchCcId(authAssgndGrp, dpstrExactMtchCcId)
            else:
                ccADS.setDpstrAltCcId(authAssgndGrp, dpstrOrigPrpsdCcId)
        else:
            ccADS.removeGrpFrmGlbllyRslvdLst(authAssgndGrp)
            ccADS.setDpstrExactMtchCcId(authAssgndGrp, None)
            ccADS.setDpstrAltCcId(authAssgndGrp, None)

        ccADS.serialize()
        ccADS.dumpData(self.__lfh)

        if mode == "done":  # mode will be either 'done' or 'undo'
            self.__saveLigModState("intermittent")

        ccAD = ChemCompAssignDepictLite(self.__reqObj, self.__verbose, self.__lfh)
        ccAD.setSessionPaths(self.__reqObj)
        ccAD.generateInstancesMainHtml(ccADS, [authAssgndGrp])

        return rC
    #  '''
    #  def _saveMissingLgndDscrptns(self):
    #      """ Register depositor descriptions of any ligands not found by cc-assign search

    #          :Helpers:
    #              wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

    #          :Returns:
    #              ResponseContent() object.
    #              No display output for this method.
    #      """
    #      if (self.__verbose):
    #          self.__lfh.write("--------------------------------------------\n")
    #          self.__lfh.write("+%s.%s() Starting now\n"%(self.__class__.__name__, inspect.currentframe().f_code.co_name) )
    #      #
    #      self.__getSession()
    #      sessionId   = self.__sessionId
    #      depId       = str(self.__reqObj.getValue("identifier")).upper()
    #      wfInstId    = str(self.__reqObj.getValue("instance")).upper()
    #      mode   = str(self.__reqObj.getValue("mode"))
    #      #
    #      if( mode == 'done' ):
    #          index = 1
    #          workToDo = True
    #          dpstrCcId = None
    #          dpstrCcName = None
    #          dpstrCcFrmla = None
    #          #
    #          ccADS=ChemCompAssignDataStore(self.__reqObj,verbose=True,log=self.__lfh)

    #          while workToDo:
    #              dpstrCcId   = str(self.__reqObj.getValue("ccid_"+index))
    #              dpstrCcName   = str(self.__reqObj.getValue("molname_"+index))
    #              dpstrCcFrmla   = str(self.__reqObj.getValue("frmla_"+index))
    #              index += 1
    #              if not dpstrCcId and not dpstrCcName and not dpstrCcFrmla:
    #                  workToDo = False
    #              else:
    #                  ccADS.addToMissingGrpLst(dpstrCcId)
    #                  ccADS.initializeGrpInfo(dpstrCcId)
    #                  if( len(dpstrCcName) > 1 ):
    #                      ccADS.setDpstrCcName(dpstrCcId,dpstrCcName)
    #                  if( len(dpstrCcFrmla) > 1 ):
    #                      ccADS.setDpstrCcFrmla(dpstrCcId,dpstrCcFrmla)
    #      else:
    #          ccADS.purgeMissingLigandsData()
    #      #
    #      if (self.__verbose):
    #          self.__lfh.write("+%s.%s() \n"%(self.__class__.__name__, inspect.currentframe().f_code.co_name) )

    #      rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)

    #      # unpickle assign data from ccAssignDataStore
    #      if (self.__verbose):
    #          self.__lfh.write("+%s.%s() unpickling ccAssignDataStore\n"%(self.__class__.__name__, inspect.currentframe().f_code.co_name) )

    #      ccADS.serialize()
    #      ccADS.dumpData(self.__lfh);

    #      return rC
    # '''

    def _updateResearchList(self):
        """ Register/remove ligand ID for ligand as focus of research with ChemCompAssignDataStore

            This is called whenever user chooses to select a ligand as a "focus of research"

            :Helpers:
                wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                ResponseContent() object.
                No display output for this method.
        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+%s.%s() Starting now\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
        #
        self.__getSession()
        # sessionId = self.__sessionId
        # depId = str(self.__reqObj.getValue("identifier")).upper()
        authAssgndGrp = str(self.__reqObj.getValue("auth_assgnd_grp"))
        mode = str(self.__reqObj.getValue("mode"))

        lstGrps = []

        if (self.__verbose):
            self.__lfh.write("+%s.%s() ---------------- STARTING ----------------\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
            self.__lfh.write("+%s.%s() authAssgndGrp is: %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, authAssgndGrp))
            self.__lfh.write("+%s.%s() mode is: %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, mode))

        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        # unpickle assign data from ccAssignDataStore
        if (self.__verbose):
            self.__lfh.write("+%s.%s() unpickling ccAssignDataStore\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))

        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
        #
        if ',' in authAssgndGrp:
            # presence of comma indicates list of group IDs
            lstGrps = authAssgndGrp.split(',')

        if mode == 'add':  # mode will be either 'add' or 'remove'
            if len(lstGrps) > 0:
                for grpId in lstGrps:
                    ccADS.addGrpToRsrchSelectedLst(grpId)
            else:
                ccADS.addGrpToRsrchSelectedLst(authAssgndGrp)
        else:
            if len(lstGrps) > 0:
                for grpId in lstGrps:
                    ccADS.removeGrpFrmRsrchSelectedLst(grpId)
            else:
                ccADS.removeGrpFrmRsrchSelectedLst(authAssgndGrp)

        ccADS.serialize()
        ccADS.dumpData(self.__lfh)

        self.__saveLigModState("intermittent")

        if (self.__verbose):
            self.__lfh.write("+%s.%s() ---------------- DONE ----------------\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))

        return rC

    def _saveRsrchData(self):
        """ Register depositor data for ligand as focus of research with ChemCompAssignDataStore

            This is called whenever user chooses to update information submitted
            to describe a ligand as a "focus of research"

            It is invoked for a particular ligand ID, and NOT for the entire dataset of ligand in the deposition.

            :Helpers:
                wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                ResponseContent() object.
                No display output for this method.
        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+%s.%s() Starting now\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
        #
        self.__getSession()
        # sessionId = self.__sessionId
        # depId = str(self.__reqObj.getValue("identifier")).upper()
        # wfInstId = str(self.__reqObj.getValue("instance")).upper()
        authAssgndGrp = str(self.__reqObj.getValue("auth_assgnd_grp"))
        mode = str(self.__reqObj.getValue("mode"))

        if (self.__verbose):
            self.__lfh.write("+%s.%s() authAssgndGrp is: %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, authAssgndGrp))
            self.__lfh.write("+%s.%s() mode is: %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, mode))

        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        # unpickle assign data from ccAssignDataStore
        if (self.__verbose):
            self.__lfh.write("+%s.%s() unpickling ccAssignDataStore\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))

        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
        #
        if mode == 'done':  # mode will be either 'done' or 'undo'

            dataSetDict = {}
            for index in range(10):

                if authAssgndGrp != "HOH":
                    assayType = self.__reqObj.getValue("assay_type_" + str(index) + "_")
                    if assayType is not None and len(assayType) >= 1:  # i.e. if one param exists for a given index then all params exist for the parameter
                        dataSetDict[index] = {}
                        dataSetDict[index]['assay_type'] = self.__normalizeForCifNull(assayType)
                        dataSetDict[index]['target_sequence'] = self.__normalizeForCifNull(self.__reqObj.getValue("target_sequence_" + str(index) + "_"))
                        dataSetDict[index]['rsrch_dscrptr_type'] = self.__normalizeForCifNull(self.__reqObj.getValue("rsrch_dscrptr_type_" + str(index) + "_"))
                        dataSetDict[index]['rsrch_dscrptr_str'] = self.__normalizeForCifNull(self.__reqObj.getValue("rsrch_dscrptr_str_" + str(index) + "_"))
                        dataSetDict[index]['ph'] = self.__normalizeForCifNull(self.__reqObj.getValue("ph_" + str(index) + "_"))
                        dataSetDict[index]['assay_temp'] = self.__normalizeForCifNull(self.__reqObj.getValue("assay_temp_" + str(index) + "_"))
                        dataSetDict[index]['measurement_type'] = self.__normalizeForCifNull(self.__reqObj.getValue("measurement_type_" + str(index) + "_"))
                        dataSetDict[index]['measured_value'] = self.__normalizeForCifNull(self.__reqObj.getValue("measured_value_" + str(index) + "_"))
                        dataSetDict[index]['details'] = self.__normalizeForCifNull(self.__reqObj.getValue("details_" + str(index) + "_"))

                        for key in dataSetDict[index]:
                            self.__lfh.write("+%s.%s() dataSetDict[%s][%s] is: %s\n" %
                                             (self.__class__.__name__, inspect.currentframe().f_code.co_name, index, key, dataSetDict[index][key]))

                elif authAssgndGrp == "HOH":
                    residueNum = self.__reqObj.getValue("residuenum_" + str(index) + "_")
                    chainId = self.__reqObj.getValue("chain_id_" + str(index) + "_")
                    if (residueNum is not None and len(residueNum) >= 1) or (chainId is not None and len(chainId) >= 1):  # i.e. if at least one param provided
                        dataSetDict[index] = {}
                        dataSetDict[index]['residuenum'] = self.__normalizeForCifNull(residueNum)
                        dataSetDict[index]['chain_id'] = self.__normalizeForCifNull(chainId)

                        for key in dataSetDict[index]:
                            self.__lfh.write("+%s.%s() dataSetDict[%s][%s] is: %s\n" %
                                             (self.__class__.__name__, inspect.currentframe().f_code.co_name, index, key, dataSetDict[index][key]))

            ccADS.addGrpToRsrchDataAcqurdLst(authAssgndGrp)
            ccADS.initializeGrpRsrchInfo(authAssgndGrp)
            ccADS.setResearchData(authAssgndGrp, dataSetDict)
            #

        else:
            ccADS.removeGrpFrmRsrchDataAcqurdLst(authAssgndGrp)

        ccADS.serialize()
        ccADS.dumpData(self.__lfh)

        if mode == "done":  # mode will be either 'done' or 'undo'
            self.__saveLigModState("intermittent")

        return rC

    def __normalizeForCifNull(self, fieldToEval):
        value = str(fieldToEval)
        return value if len(value) > 0 else '?'

    def _saveNwLgndDscrptn(self):
        """ Register depositor description of new ligand with ChemCompAssignDataStore

            This is called whenever user chooses to update information submitted
            to describe a ligand in his/her data that was found to have no match in the ligand
            dictionary.

            It is invoked for a particular ligand ID, and NOT for the entire dataset of ligand in the deposition.

            :Helpers:
                wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                ResponseContent() object.
                No display output for this method.
        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+%s.%s() Starting now\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
        #
        self.__getSession()
        # sessionId = self.__sessionId
        # depId = str(self.__reqObj.getValue("identifier")).upper()
        # wfInstId = str(self.__reqObj.getValue("instance")).upper()
        authAssgndGrp = str(self.__reqObj.getValue("auth_assgnd_grp"))
        mode = str(self.__reqObj.getValue("mode"))

        dpstrCcType = str(self.__reqObj.getValue("lgnd_type"))
        dpstrAltCcId = str(self.__reqObj.getValue("alt_ccid"))
        dpstrCcDscptrType = str(self.__reqObj.getValue("dscrptr_type"))
        dpstrCcDscptrStr = str(self.__reqObj.getValue("dscrptr_str"))
        # dpstrSubmitChoice = str(self.__reqObj.getValue("submission_choice"))
        dpstrCcName = str(self.__reqObj.getValue("chem_name"))
        dpstrCcFrmla = str(self.__reqObj.getValue("chem_frmla"))
        dpstrComments = str(self.__reqObj.getValue("comments"))

        molData = str(self.__reqObj.getValue("moldata"))
        #
        if (self.__verbose):
            self.__lfh.write("+%s.%s() authAssgndGrp is: %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, authAssgndGrp))

        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        # unpickle assign data from ccAssignDataStore
        if (self.__verbose):
            self.__lfh.write("+%s.%s() unpickling ccAssignDataStore\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))

        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
        #
        if mode == 'done':  # mode will be either 'done' or 'undo'
            ccADS.addGrpToGlbllyRslvdLst(authAssgndGrp)
            ccADS.initializeGrpInfo(authAssgndGrp)
            ccADS.setDpstrCcType(authAssgndGrp, dpstrCcType)
            if len(dpstrAltCcId) > 1:
                ccADS.setDpstrAltCcId(authAssgndGrp, dpstrAltCcId.upper())
            # ccADS.setDpstrSubmitChoice(authAssgndGrp, dpstrSubmitChoice)
            # if( dpstrSubmitChoice == 'dscrptrstr' and len(dpstrCcDscptrStr) > 1 ):
            if len(dpstrCcDscptrStr) > 1:
                ccADS.setDpstrCcDscrptrStr(authAssgndGrp, dpstrCcDscptrStr)
                ccADS.setDpstrCcDscrptrType(authAssgndGrp, dpstrCcDscptrType)
            if len(dpstrCcName) > 1:
                ccADS.setDpstrCcName(authAssgndGrp, dpstrCcName)
            if len(dpstrCcFrmla) > 1:
                ccADS.setDpstrCcFrmla(authAssgndGrp, dpstrCcFrmla)
            if len(dpstrComments) > 1:
                ccADS.setDpstrComments(authAssgndGrp, dpstrComments)
            #
            for fileTag in ["file_img", "file_refdict"]:
                if (self.__verbose):
                    self.__lfh.write("+%s.%s() checking for uploaded files.\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
                if self.__isFileUpload(fileTag):
                    if (self.__verbose):
                        self.__lfh.write("+%s.%s() found uploaded file instance with fileTag: %s.\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, fileTag))
                    self._uploadDpstrFile(fileTag, ccADS)
            #
            # rC.addDictionaryItems({'filename':str(fileName)});
            # rC.setHtmlText("%s successfully uploaded!" % fileName)

        else:
            ccADS.removeGrpFrmGlbllyRslvdLst(authAssgndGrp)

        ccADS.serialize()
        ccADS.dumpData(self.__lfh)

        if molData and len(molData) > 0:
            # ccADS.setDpstrSketchMolDataStr(authAssgndGrp,molData)
            try:
                fileName = authAssgndGrp + '-sketch.sdf'
                fp = os.path.join(self.__sessionPath, fileName)
                ofh = open(fp, 'a')
                if molData.find("Mrv") == 0:
                    ofh.write("%s\n" % authAssgndGrp)
                ofh.write("%s\n" % molData)
                ofh.close()
                success = ccADS.setDpstrSketchFile(authAssgndGrp, 'sdf', fileName)
                if success:
                    self.__lfh.write("+%s.%s() successfully updated data store for generated sketch file: %s\n" %
                                     (self.__class__.__name__, inspect.currentframe().f_code.co_name, fileName))
                    ccADS.serialize()
                    ccADS.dumpData(self.__lfh)
            except:  # noqa: E722 pylint: disable=bare-except
                traceback.print_exc(file=self.__lfh)
                rC.setError(errMsg='Save of MarvinSketch sdf file failed')

        if mode == "done":  # mode will be either 'done' or 'undo'
            self.__saveLigModState("intermittent")

        ccAD = ChemCompAssignDepictLite(self.__reqObj, self.__verbose, self.__lfh)
        ccAD.setSessionPaths(self.__reqObj)
        ccAD.generateInstancesMainHtml(ccADS, [authAssgndGrp])

        return rC

    def _validateCcId(self):
        """ Verify validity of given Chem Comp Code
            Supports two modes of validation:

                + "simple":
                    check that CC ID simply has corresponding directory in server repository of ligand dict data

                + "full":
                    in addition to simple, also check that CC ID is not obsolete

            :Helpers:

                + wwpdb.apps.ccmodule.chem.ChemCompAssign.ChemCompAssign
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                if fails return error message
                else return without message
        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+%s.%s() ---- starting.\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
        #
        self.__getSession()
        vldtMode = str(self.__reqObj.getValue("vldtmode"))
        ccId = str(self.__reqObj.getValue("alt_ccid")).upper()
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        pathPrefix = self.__ccConfig.getPath('chemCompCachePath')
        validationPth = os.path.join(pathPrefix, ccId[:1], ccId, ccId + '.cif')
        if (self.__verbose):
            self.__lfh.write("+%s.%s() ---- validating CC ID %s against path: %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, ccId, validationPth))
        if not os.access(validationPth, os.R_OK):
            errorMessage = '"' + ccId + '" is not a valid Code.'
            rC.setError(errMsg=errorMessage)
            return rC
        #
        if vldtMode == 'simple':
            return rC
        #
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
        return rC

    def _checkForUploadedFiles(self):
        """
            :Helpers:
                wwpdb.apps.ccmodule.depict.ChemCompAssignDepictLite

            :Returns:
                Operation output is packaged in a ResponseContent() object.
                The output consists of JSON object with property(ies):
                    'htmlmrkup' --> markup representing Jmol object element
        """
        className = self.__class__.__name__
        methodName = inspect.currentframe().f_code.co_name
        #
        authAssgndGrp = str(self.__reqObj.getValue("auth_assgnd_grp"))
        contentType = str(self.__reqObj.getValue("content_type"))
        #
        rtrnDict = {}
        #
        if (self.__verbose):
            self.__lfh.write("+%s.%s() -- Starting.\n" % (className, methodName))
        #
        # bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        self.__reqObj.setValue("RelativeSessionPath", self.__rltvSessionPath)
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        uploadedFilesLst = self.__verifyUploadedFiles(authAssgndGrp, contentType)
        #
        ccAD = ChemCompAssignDepictLite(self.__reqObj, self.__verbose, self.__lfh)
        ccAD.setSessionPaths(self.__reqObj)
        htmlMrkp = ccAD.doRender_UploadedFilesList(authAssgndGrp, uploadedFilesLst, self.__reqObj)
        #
        rtrnDict['filesonrecord'] = 'true' if len(uploadedFilesLst) > 0 else 'false'
        rtrnDict['htmlmrkup'] = ''.join(htmlMrkp)
        rtrnDict['filelist'] = uploadedFilesLst

        if (self.__verbose):
            self.__lfh.write("\n%s.%s() -- rtrnDict['htmlmrkup'] is:%s\n" % (self.__class__.__name__,
                                                                             inspect.currentframe().f_code.co_name,
                                                                             rtrnDict['htmlmrkup']))

        rC.addDictionaryItems(rtrnDict)

        return rC

    def _removeUploadedFile(self):
        """
            :Helpers:
                wwpdb.apps.ccmodule.io.ChemCompAssignDataStore

            :Returns:
                Operation output is packaged in a ResponseContent() object.
                The output consists of JSON object with property(ies):
                    'statuscode'
        """
        className = self.__class__.__name__
        methodName = inspect.currentframe().f_code.co_name
        #
        rtrnStatus = "FAIL"
        authAssgndGrp = str(self.__reqObj.getValue("auth_assgnd_grp"))
        fileName = str(self.__reqObj.getValue("file_name"))
        #
        if (self.__verbose):
            self.__lfh.write("+%s.%s() -- Starting.\n" % (className, methodName))
        #
        # bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        self.__reqObj.setValue("RelativeSessionPath", self.__rltvSessionPath)
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        bSuccess = self.__removeUploadedFile(authAssgndGrp, fileName)
        #
        if bSuccess:
            rtrnStatus = "OK"
        rC.setStatusCode(rtrnStatus)
        return rC

    # def _searchGraphOp(self):
    #     if (self.__verbose):
    #         self.__lfh.write("+ChemCompWebAppLiteWorker._searchGraphOp() starting\n")

    #     self.__getSession()
    #     self.__reqObj.setDefaultReturnFormat(return_format="html")
    #     rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)

    #     if self.__isFileUpload():
    #         # make a copy of the file in the session directory and set 'fileName'
    #         self.__uploadFile()
    #     #

    #     ccE=ChemCompSearch(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
    #     rD=ccE.doGraphIso()
    #     if (self.__verbose):
    #         for k,v in rD.items():
    #             self.__lfh.write("+ChemCompWebAppLite._searchGraphOp() key %30s   value %s\n" % (k,v))
    #     if len(rD) > 0:
    #         ccSD=ChemCompSearchDepict(self.__verbose,self.__lfh)
    #         oL=ccSD.doRenderGraph(rD)
    #         rC.setHtmlList(oL)
    #     else:
    #         rC.setError(errMsg='No search result')

    #     return rC

    # def _searchIndexOp(self):
    #     if (self.__verbose):
    #         self.__lfh.write("+ChemCompWebAppLiteWorker._searchIndexOp() starting\n")
    #     #
    #     self.__reqObj.setDefaultReturnFormat(return_format="html")
    #     rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
    #     #
    #     ccS=ChemCompSearch(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
    #     rD=ccS.doIndex()
    #     if len(rD) > 0:
    #         ccSD=ChemCompSearchDepict(self.__verbose,self.__lfh)
    #         oL=ccSD.doRenderIndex(rD)
    #         rC.setHtmlList(oL)
    #     else:
    #         rC.setError(errMsg='No search result')

    #     return rC

    # def _searchDbOp(self):
    #     if (self.__verbose):
    #         self.__lfh.write("+ChemCompWebAppLiteWorker._searchDbOp() starting\n")
    #     #
    #     self.__reqObj.setDefaultReturnFormat(return_format="html")
    #     rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
    #     #
    #     ccS=ChemCompSearchDb(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
    #     rD=ccS.doIdSearch()
    #     if len(rD) > 0:
    #         ccSD=ChemCompSearchDbDepict(self.__verbose,self.__lfh)
    #         oL=ccSD.doRender(rD)
    #         rC.setHtmlList(oL)
    #     else:
    #         rC.setError(errMsg='No search result')

    #     return rC

    # def _extractOp(self):
    #     if (self.__verbose):
    #         self.__lfh.write("+%s.%s() starting\n"%( self.__class__.__name__, inspect.currentframe().f_code.co_name))

    #     self.__getSession()
    #     self.__reqObj.setDefaultReturnFormat(return_format="html")
    #     rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)

    #     if not self.__isFileUpload():
    #         rC.setError(errMsg='No file uploaded')
    #         return rC
    #     #
    #     self.__uploadFile()
    #     ccE=ChemCompExtract(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
    #     rD=ccE.doExtract()
    #     if (self.__verbose):
    #         for k,v in rD.items():
    #             self.__lfh.write("+%s.%s() key %30s   value %s\n" %( self.__class__.__name__, inspect.currentframe().f_code.co_name,k,v) )
    #     if ('extractlist' in rD and len(rD['extractlist']) > 0):
    #         ccExD=ChemCompExtractDepict(self.__verbose,self.__lfh)
    #         oL=ccExD.doRender(rD['extractlist'])
    #         rC.setHtmlList(oL)
    #     else:
    #         rC.setError(errMsg="No components extracted")
    #     return rC

    # def _viewOp(self):
    #     """ Call to display data for given chem component in comparison grid of standalone version of chem comp module.
    #         Delegates primary processing to ChemCompView class.

    #         :Helpers:
    #             wwpdb.apps.ccmodule.view.ChemCompView.ChemCompViewe

    #         :Returns:
    #             Operation output is packaged in a ResponseContent() object.
    #     """
    #     if (self.__verbose):
    #         self.__lfh.write("--------------------------------------------\n")
    #         self.__lfh.write("+ChemCompWebAppLiteWorker._viewOp() starting\n")
    #     #
    #     self.__getSession()
    #     sessionId   = self.__sessionId
    #     if (self.__verbose):
    #         self.__lfh.write("+%s.%s() session ID is: %s\n" %( self.__class__.__name__, inspect.currentframe().f_code.co_name, sessionId) )
    #     #
    #     self.__reqObj.setReturnFormat(return_format="json")
    #     rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
    #     #
    #     ccV=ChemCompView(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
    #     #
    #     rtrnCode=ccV.doView()
    #     #
    #     if self.__verbose:
    #         self.__lfh.write("+ChemCompWebAppLiteWorker._viewOp() - return code is %s\n" % str(rtrnCode) )

    #     rC.addDictionaryItems({'sessionid':str(sessionId)});
    #     rC.setStatusCode(str(rtrnCode))

    #     return rC

    # def _editLaunchOp(self):
    #     """ Launch chemical component editor

    #         :Returns:
    #             Operation output is packaged in a ResponseContent() object.
    #     """
    #     if (self.__verbose):
    #         self.__lfh.write("+ChemCompWebAppLiteWorker._editLaunchOp() \n")
    #     #

    #     sessionId   = str(self.__reqObj.getValue("sessionid"))
    #     depId       = str(self.__reqObj.getValue("identifier")).upper()
    #     instanceId  = str(self.__reqObj.getValue("instanceid")).upper()
    #     fileSource  = str(self.__reqObj.getValue("filesource")).lower()
    #     wfInstId    = str(self.__reqObj.getValue("instance")).upper()
    #     #
    #     self.__getSession()
    #     #
    #     self.__reqObj.setDefaultReturnFormat(return_format="html")
    #     rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
    #     #

    #     ###########################################################################
    #     # create dictionary of content that will be used to populate HTML template
    #     ###########################################################################
    #     myD={}
    #     myD['sessionid'] = sessionId
    #     myD['depositionid'] = depId
    #     myD['instanceid'] = instanceId
    #     myD['related_instanceids'] = ''
    #     myD['filesource'] = fileSource
    #     myD['identifier'] = depId
    #     myD['instance'] = wfInstId
    #     #
    #     myD['session_url_prefix'] = os.path.join(self.__rltvSessionPath,"assign",instanceId)
    #     myD['processing_site'] = self.__cI.get('SITE_NAME').upper()
    #     rC.setHtmlText(htmlText=self.__processTemplate(fn=os.path.join(self.__pathSnglInstcEditorTmplts,"cc_instnc_edit_tmplt.html"), parameterDict=myD))
    #     return rC

    def _exit_Finished(self):
        """ Exiting Ligand Module when annotator has completed all necessary processing
        """
        return self.__exitLigMod(mode='completed')

    def _exit_notFinished(self):
        """ Exiting Ligand Module when annotator has NOT completed all necessary processing
            and user intends to resume use of lig module at another point to continue updating data.
        """
        return self.__exitLigMod(mode='unfinished')

    ################################################################################################################
    # ------------------------------------------------------------------------------------------------------------
    #      Private helper methods
    # ------------------------------------------------------------------------------------------------------------
    #

    def __removeUploadedFile(self, p_ccID, p_fileName):
        """
        """
        bSuccess = False
        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
        # bChangeMade = False

        dpstrUploadFilesDict = ccADS.getDpstrUploadFilesDict()
        if p_ccID in dpstrUploadFilesDict:
            for fileType in dpstrUploadFilesDict[p_ccID]:
                for fileName in dpstrUploadFilesDict[p_ccID][fileType].keys():
                    if fileName == p_fileName:
                        try:
                            # delete local copy of file
                            lclFlPth = os.path.join(self.__sessionPath, fileName)
                            if os.access(lclFlPth, os.R_OK):
                                os.remove(lclFlPth)
                                if (self.__verbose):
                                    self.__lfh.write("+%s.%s() ---- removing uploaded file from local storage: %s\n" %
                                                     (self.__class__.__name__, inspect.currentframe().f_code.co_name, lclFlPth))
                            # delete any copy of file in "deposit" storage
                            wfFlPth = ccADS.getDpstrUploadFileWfPath(p_ccID, fileType, p_fileName)
                            if wfFlPth is not None:
                                os.remove(wfFlPth)
                                if (self.__verbose):
                                    self.__lfh.write("+%s.%s() ---- removing uploaded file from 'deposit' storage: %s\n" %
                                                     (self.__class__.__name__, inspect.currentframe().f_code.co_name, wfFlPth))

                            # delete record of file in datastore
                            del dpstrUploadFilesDict[p_ccID][fileType][fileName]
                            if len(dpstrUploadFilesDict[p_ccID][fileType].keys()) == 0:
                                del dpstrUploadFilesDict[p_ccID][fileType]

                            ccADS.dumpData(self.__lfh)
                            ccADS.serialize()
                            bSuccess = True
                            return bSuccess
                        except:  # noqa: E722 pylint: disable=bare-except
                            traceback.print_exc(file=self.__lfh)
                            self.__lfh.write("+%s.%s() ---- problem encountered when deleting uploaded file from storage.\n" %
                                             (self.__class__.__name__, inspect.currentframe().f_code.co_name))
                            self.__lfh.flush()

        return bSuccess

    def __verifyUploadedFiles(self, p_ccID, p_contentType):
        """
        """
        rtrnFlLst = []
        contentTypeDict = self.__cI.get('CONTENT_TYPE_DICTIONARY')
        ccADS = ChemCompAssignDataStore(self.__reqObj, verbose=True, log=self.__lfh)
        acceptedFileTypes = (contentTypeDict[p_contentType][0])[:]
        if p_contentType == 'component-definition':
            acceptedFileTypes.append('cif')
        if p_contentType == 'component-image':
            acceptedFileTypes.extend(['jpeg', 'bmp'])  # may have accepted these in the past?

        dpstrUploadFilesDict = ccADS.getDpstrUploadFilesDict()
        if p_ccID in dpstrUploadFilesDict:
            for fileType in dpstrUploadFilesDict[p_ccID]:
                if fileType in acceptedFileTypes:
                    for fileName in dpstrUploadFilesDict[p_ccID][fileType].keys():
                        lclFlPth = os.path.join(self.__sessionPath, fileName)
                        if not os.access(lclFlPth, os.R_OK):
                            if (self.__verbose):
                                self.__lfh.write("+%s.%s() ---- uploaded file does not exist at path: %s\n" %
                                                 (self.__class__.__name__, inspect.currentframe().f_code.co_name, lclFlPth))
                            # if currently don't have local copy of file then need to obtain copy from "deposit" storage
                            wfFlPth = ccADS.getDpstrUploadFileWfPath(p_ccID, fileType, fileName)
                            if wfFlPth is not None:
                                if (self.__verbose):
                                    self.__lfh.write("+%s.%s() ---- copy of uploaded file being obtained from: %s\n" %
                                                     (self.__class__.__name__, inspect.currentframe().f_code.co_name, wfFlPth))
                                shutil.copyfile(wfFlPth, lclFlPth)
                        if os.access(lclFlPth, os.R_OK):
                            rtrnFlLst.append(fileName)
                        else:
                            if (self.__verbose):
                                self.__lfh.write("+%s.%s() ---- unable to obtain working copy of uploaded file: %s\n" %
                                                 (self.__class__.__name__, inspect.currentframe().f_code.co_name, fileName))

        return rtrnFlLst

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
            self.__lfh.write("+ChemCompWebAppLiteWorker.__exitLigMod() - starting\n")
        #
        # if (mode == 'completed'):
        #     state = "closed(0)"
        # elif (mode == 'unfinished'):
        #     state = "waiting"
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
            self.__lfh.write("+ChemCompWebAppLiteWorker.__exitLigMod() - depId   %s \n" % depId)
            self.__lfh.write("+ChemCompWebAppLiteWorker.__exitLigMod() - instId  %s \n" % instId)
            self.__lfh.write("+ChemCompWebAppLiteWorker.__exitLigMod() - classID %s \n" % classId)
            self.__lfh.write("+ChemCompWebAppLiteWorker.__exitLigMod() - sessionID %s \n" % sessionId)
            self.__lfh.write("+ChemCompWebAppLiteWorker.__exitLigMod() - filesource %r \n" % fileSource)

        #
        self.__reqObj.setReturnFormat('json')
        #
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        # Update WF status database and persist chem comp assignment states -- ONLY if lig module was running in context of wf-engine
        #
        if bIsWorkflow:
            try:
                bOkay = self.__saveLigModState(mode)
                if bOkay:
                    # '''
                    # bSuccess = self.__updateWfTrackingDb(state)
                    # if( not bSuccess ):
                    #     rC.setError(errMsg="+ChemCompWebAppLiteWorker.__exitLigMod() - TRACKING status, update to '%s' failed for session %s \n" % (state,sessionId) )
                    # '''
                    pass
                else:
                    rC.setError(errMsg="+ChemCompWebAppLiteWorker.__exitLigMod() - problem saving log module state")

            except:  # noqa: E722 pylint: disable=bare-except
                if (self.__verbose):
                    self.__lfh.write("+ChemCompWebAppLiteWorker.__exitLigMod() - problem saving lig module state")
                traceback.print_exc(file=self.__lfh)
                rC.setError(errMsg="+ChemCompWebAppLiteWorker.__exitLigMod() - exception thrown on saving lig module state")
        else:
            try:
                bOkay = self.__saveLigModState(mode)
                if not bOkay:
                    rC.setError(errMsg="+ChemCompWebAppLiteWorker.__exitLigMod() - problem saving lig module state")

            except:  # noqa: E722 pylint: disable=bare-except
                if (self.__verbose):
                    self.__lfh.write("+ChemCompWebAppLiteWorker.__exitLigMod() - problem saving lig module state")
                traceback.print_exc(file=self.__lfh)
                rC.setError(errMsg="+ChemCompWebAppLiteWorker.__exitLigMod() - exception thrown on saving lig module state")

            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppLiteWorker.__exitLigMod() - Not in WF environ so skipping status update to TRACKING database for session %s \n" % sessionId)
        #
        return rC

    # def __updateWfTrackingDb(self, p_status):
    #     """ Private function used to udpate the Workflow Status Tracking Database

    #         :Params:
    #             ``p_status``: the new status value to which the deposition data set is being set

    #         :Helpers:
    #             wwpdb.apps.ccmodule.utils.WfTracking.WfTracking

    #         :Returns:
    #             ``bSuccess``: boolean indicating success/failure of the database update
    #     """
    #     #
    #     bSuccess = False
    #     #
    #     sessionId = self.__sessionId
    #     depId = self.__reqObj.getValue("identifier").upper()
    #     instId = self.__reqObj.getValue("instance")
    #     classId = str(self.__reqObj.getValue("classID")).lower()
    #     #
    #     try:
    #         wft = WfTracking(verbose=self.__verbose, log=self.__lfh)
    #         wft.setInstanceStatus(depId=depId,
    #                               instId=instId,
    #                               classId=classId,
    #                               status=p_status)
    #         bSuccess = True
    #         if (self.__verbose):
    #             self.__lfh.write("+ChemCompWebAppLiteWorker.__updateWfTrackingDb() -TRACKING status updated to '%s' for session %s \n" % (p_status, sessionId))
    #     except:  # noqa: E722 pylint: disable=bare-except
    #         bSuccess = False
    #         if (self.__verbose):
    #             self.__lfh.write("+ChemCompWebAppLiteWorker.__updateWfTrackingDb() - TRACKING status, update to '%s' failed for session %s \n" % (p_status, sessionId))
    #         traceback.print_exc(file=self.__lfh)
    #     #
    #     return bSuccess

    def __saveLigModState(self, mode):
        """ Persist state of user's chem comp module session which involves capturing updated:
                - ChemCompAssignDataStore pickle file as 'chem-comp-assign-details' file.
                - cc depositor info file is generated if user is has completed Ligand Lite submission -- this file is used to propagate
                    the relevant depositor provided info to the annotation pipeline

            :Params:
                ``mode``:
                    'completed' if annotator has designated all assignments for all ligands and wishes to
                        conclude work in the ligand module.
                    'unfinished' if annotator wishes to leave ligand module but resume work at a later point.
                    'intermittent' save of state on intermittent commits of ligand description data for an
                                    *individual* ligand ID (i.e. not for entire dataset of ligands)
                                    this mode is used when user chooses to update information
                                    being submitted for an individual ligand ID.

            :Helpers:
                + wwpdb.wwpdb.io.locator.DataReference.DataFileReference
                + wwpdb.apps.ccmodule.chem.ChemCompAssign

            :Returns:
                ``ok``: boolean indicating success/failure of the save operation
        """
        pathDict = {}
        # ##### pickle file ######
        pathDict['picFileDirPth'] = None
        pathDict['picFileFlPth'] = None
        # ##### depositor info file ######
        pathDict['dpstrInfoFileDirPth'] = None
        pathDict['dpstrInfoFileFlPth'] = None
        # ##### depositor progress file ######
        pathDict['dpstrPrgrssFileDirPth'] = None
        pathDict['dpstrPrgrssFileFlPth'] = None
        #
        fileSource = str(self.__reqObj.getValue("filesource")).strip().lower()
        depId = "D_0" if self.__reqObj.getValue("identifier") in [None, 'TMP_ID'] else self.__reqObj.getValue("identifier")
        # instId = self.__reqObj.getValue("instance")
        # classId = self.__reqObj.getValue("classid")
        # sessionId = self.__sessionId
        bSuccess = False
        #
        # determine if currently operating in Workflow Managed environment
        bIsWorkflow = self.__isWorkflow()
        #
        if bIsWorkflow:
            depId = depId.upper()
        else:
            depId = depId.lower()
        #
        if fileSource:
            ccE = ChemCompDataExport(self.__reqObj, verbose=self.__verbose, log=self.__lfh)

            # #################################### chem comp depositor info file #################################################
            pathDict['dpstrInfoFileFlPth'] = ccE.getChemCompDpstrInfoFilePath()

            if pathDict['dpstrInfoFileFlPth']:
                pathDict['dpstrInfoFileDirPth'] = (os.path.split(pathDict['dpstrInfoFileFlPth']))[0]

                #
                if (self.__verbose):
                    self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() CC depositor info export directory path: %s\n" % pathDict['dpstrInfoFileDirPth'])
                    self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() CC depositor info export file      path: %s\n" % pathDict['dpstrInfoFileFlPth'])
            else:
                self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() ---- WARNING ---- No path obtained for CC depositor info export file, id %s \n" % depId)

            #######################################################################################################################################
            # Below files are always being updated, i.e. not just on "completed" status but on "intermittent" and "unfinished" states as well.
            #######################################################################################################################################

            # #################################### pickle file #################################################
            pathDict['picFileFlPth'] = ccE.getChemCompAssignDetailsFilePath()

            if pathDict['picFileFlPth']:
                pathDict['picFileDirPth'] = (os.path.split(pathDict['picFileFlPth']))[0]

                if (self.__verbose):
                    self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() CC assign details export directory path: %s\n" % pathDict['picFileDirPth'])
                    self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() CC assign details export file      path: %s\n" % pathDict['picFileFlPth'])
            else:
                self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() ---- WARNING ---- No path obtained for CC assign details export file, id %s \n" % depId)

            # #################################### chem comp depositor progress file #################################################
            pathDict['dpstrPrgrssFileFlPth'] = os.path.join(Path(self.__pathInfo.getDepositPath(depId)), 'cc-dpstr-progress')
            pathDict['dpstrPrgrssFileDirPth'] = (os.path.split(pathDict['dpstrPrgrssFileFlPth']))[0]

            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() CC assign dpstr progress directory path: %s\n" % pathDict['dpstrPrgrssFileDirPth'])
                self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() CC assign dpstr progress file      path: %s\n" % pathDict['dpstrPrgrssFileFlPth'])

        else:
            self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() - processing undefined | filesource %r \n" % fileSource)

        #########################################################################################################################################################
        #    Call on ChemCompAssign to save current state of ligand assignments
        #########################################################################################################################################################
        ccA = ChemCompAssign(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        bSuccess, _msg = ccA.saveState(pathDict, context="deposit", mode=mode)
        #

        # below added to support convenience of assessing results during unit testing
        if mode != "intermittent":
            bIsWorkflow = self.__isWorkflow()
            ccAD = ChemCompAssignDepictLite(self.__reqObj, self.__verbose, self.__lfh)
            ccAD.setSessionPaths(self.__reqObj)
            ccAD.doRender_ResultFilesPage(self.__reqObj, bIsWorkflow)
        #
        return bSuccess

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
            self.__lfh.write("+ChemCompWebAppLite.__getSession() - creating/joining session %s\n" % self.__sessionId)
            # self.__lfh.write("+ChemCompWebAppLite.__getSession() - workflow storage path    %s\n" % self.__workflowStoragePath)
            self.__lfh.write("+ChemCompWebAppLite.__getSession() - session path %s\n" % self.__sessionPath)

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

    def _uploadDpstrFile(self, p_fileTag, p_ccADS):
        if (self.__verbose):
            self.__lfh.write("+%s.%s() Starting now\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
        #
        success = False
        authAssgndGrp = str(self.__reqObj.getValue("auth_assgnd_grp"))
        #
        ok = self.__uploadFile(p_fileTag)
        #
        if ok:
            fileName = str(self.__reqObj.getValue("UploadFileName"))
            #
            if (self.__verbose):
                self.__lfh.write("+%s.%s() fileName: %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, fileName))

            # when obtaining filetype, we force extension filetype to lowercase so that all handling done consistently in lowercase
            fileType = os.path.splitext(fileName)[1].strip(".").lower() if len(os.path.splitext(fileName)[1]) > 1 else "n/a"
            #
            if (self.__verbose):
                self.__lfh.write("+%s.%s() fileType: %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, fileType))

            success = p_ccADS.setDpstrUploadFile(authAssgndGrp, fileType, fileName)
            if success:
                self.__lfh.write("+%s.%s() successfully updated data store for file upload action for %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, fileName))
                p_ccADS.serialize()
                p_ccADS.dumpData(self.__lfh)
        #
        return success

    def __uploadFile(self, fileTag='file'):
        #
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppLite.__uploadFile() - file upload starting\n")
        fs = None
        fNameInput = ""
        #
        # Copy upload file to session directory -
        try:
            fs = self.__reqObj.getRawValue(fileTag)
            fNameInput = str(fs.filename)
            #
            # Need to deal with some platform issues -
            #
            if (fNameInput.find('\\') != -1) :
                # likely windows path -
                fName = ntpath.basename(fNameInput)
            else:
                fName = os.path.basename(fNameInput)

            #
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppLite.__loadDataFileStart() - upload file %s\n" % fs.filename)
                self.__lfh.write("+ChemCompWebAppLite.__loadDataFileStart() - base file   %s\n" % fName)
            #
            # Store upload file in session directory -

            fPathAbs = os.path.join(self.__sessionPath, fName)
            ofh = open(fPathAbs, 'wb')
            ofh.write(fs.file.read())
            ofh.close()
            self.__reqObj.setValue("UploadFileName", fName)
            self.__reqObj.setValue("filePath", fPathAbs)
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppLite.__uploadFile() Uploaded file %s\n" % str(fName))
        except:  # noqa: E722 pylint: disable=bare-except
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppLite.__uploadFile() File upload processing failed for %s\n" % str(fs.filename))
                traceback.print_exc(file=self.__lfh)

            return False
        #
        # If this is not workflow context then establish depId from filename
        #
        if not self.__isWorkflow() and fileTag not in ["file_img", "file_refdict"]:
            if fName.startswith('rcsb'):
                fId = fName[:10]
            elif fName.startswith('d_'):
                fId = fName[:8]
            else:
                fId = '000000'
                if (self.__verbose):
                    self.__lfh.write("+ChemCompWebAppLite.__uploadFile() using default identifier for %s\n" % str(fName))

            self.__reqObj.setValue("identifier", fId)
        #
        self.__reqObj.setValue("fileName", fName)
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppLite.__uploadFile() identifier %s\n" % self.__reqObj.getValue("identifier"))
        return True

    # def __setSemaphore(self):
    #     sVal = str(time.strftime("TMP_%Y%m%d%H%M%S", time.localtime()))
    #     self.__reqObj.setValue('semaphore', sVal)
    #     return sVal

    # def __openSemaphoreLog(self, semaphore="TMP_"):
    #     # sessionId = self.__reqObj.getSessionId()
    #     fPathAbs = os.path.join(self.__sessionPath, semaphore + '.log')
    #     self.__lfh = open(fPathAbs, 'w')

    # def __closeSemaphoreLog(self, semaphore="TMP_"):
    #     self.__lfh.flush()
    #     self.__lfh.close()

    # def __postSemaphore(self, semaphore='TMP_', value="OK"):
    #     # sessionId = self.__reqObj.getSessionId()
    #     fPathAbs = os.path.join(self.__sessionPath, semaphore)
    #     fp = open(fPathAbs, 'w')
    #     fp.write("%s\n" % value)
    #     fp.close()
    #     return semaphore

    # def __semaphoreExists(self, semaphore='TMP_'):
    #     # sessionId = self.__reqObj.getSessionId()
    #     fPathAbs = os.path.join(self.__sessionPath, semaphore)
    #     if (os.access(fPathAbs, os.F_OK)):
    #         return True
    #     else:
    #         return False

    # def __getSemaphore(self, semaphore='TMP_'):

    #     # sessionId = self.__reqObj.getSessionId()
    #     fPathAbs = os.path.join(self.__sessionPath, semaphore)
    #     if (self.__verbose):
    #         self.__lfh.write("+ChemCompWebAppLite.__getSemaphore() - checking %s in path %s\n" % (semaphore, fPathAbs))
    #     try:
    #         fp = open(fPathAbs, 'r')
    #         lines = fp.readlines()
    #         fp.close()
    #         sval = lines[0][:-1]
    #     except:  # noqa: E722 pylint: disable=bare-except
    #         sval = "FAIL"
    #     return sval

    # def __openChildProcessLog(self, label="TMP_"):
    #     _sessionId = self.__reqObj.getSessionId()  # noqa: F841
    #     fPathAbs = os.path.join(self.__sessionPath, label + '.log')
    #     self.__lfh = open(fPathAbs, 'w')

    # def __processTemplate(self, fn, parameterDict={}):
    #     """ Read the input HTML template data file and perform the key/value substitutions in the
    #         input parameter dictionary.

    #         :Params:
    #             ``parameterDict``: dictionary where
    #             key = name of subsitution placeholder in the template and
    #             value = data to be used to substitute information for the placeholder

    #         :Returns:
    #             string representing entirety of content with subsitution placeholders now replaced with data
    #     """
    #     tPath = self.__reqObj.getValue("TemplatePath")
    #     fPath = os.path.join(tPath, fn)
    #     ifh = open(fPath, 'r')
    #     sIn = ifh.read()
    #     ifh.close()
    #     return (sIn % parameterDict)

    def __isWorkflow(self):
        """ Determine if currently operating in Workflow Managed environment

            :Returns:
                boolean indicating whether or not currently operating in Workflow Managed environment
        """
        #
        fileSource = str(self.__reqObj.getValue("filesource")).lower()
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppLiteWorker.__isWorkflow() - filesource is %s\n" % fileSource)
        #
        # add wf_archive to fix PDBe wfm issue -- jdw 2011-06-30
        #
        if fileSource in ['archive', 'wf-archive', 'wf_archive', 'wf-instance', 'wf_instance', 'deposit']:
            # if the file source is any of the above then we are in the workflow manager environment
            return True
        else:
            # else we are in the standalone dev environment
            return False

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

        if self.__verbose:
            logger.setLevel(DEBUG)
        else:
            logger.setLevel(INFO)

        return logger


# Might not be needed here
class RedirectDevice:
    def write(self, s):
        pass


def maintest():
    sTool = ChemCompWebAppLite()
    d = sTool.doOp()
    for k, v in d.items():
        sys.stdout.write("Key - %s  value - %r\n" % (k, v))


if __name__ == '__main__':
    maintest()
