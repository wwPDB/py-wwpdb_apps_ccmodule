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
__author__    = "Raul Sala"
__email__     = "rsala@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.01"

import os, sys, time, types, string, traceback, ntpath, threading, signal, shutil
from json import loads, dumps
from time import localtime, strftime

from wwpdb.utils.session.WebRequest              import InputRequest,ResponseContent
#
from wwpdb.apps.ccmodule.chem.ChemCompAssign            import ChemCompAssign
from wwpdb.apps.ccmodule.chem.ChemCompAssignDepictLite  import ChemCompAssignDepictLite
#
from wwpdb.apps.ccmodule.search.ChemCompSearch          import ChemCompSearch
from wwpdb.apps.ccmodule.search.ChemCompSearchDepict    import ChemCompSearchDepict
from wwpdb.apps.ccmodule.search.ChemCompSearchDb        import ChemCompSearchDb
from wwpdb.apps.ccmodule.search.ChemCompSearchDbDepict  import ChemCompSearchDbDepict
#
from wwpdb.apps.ccmodule.reports.ChemCompReports        import ChemCompReport,ChemCompCheckReport
#
from wwpdb.apps.ccmodule.utils.WfTracking               import WfTracking
from wwpdb.apps.ccmodule.utils.ChemCompConfig           import ChemCompConfig
#
from wwpdb.apps.ccmodule.io.ChemCompAssignDataStore     import ChemCompAssignDataStore
from wwpdb.apps.ccmodule.io.ChemCompDataImport          import ChemCompDataImport
from wwpdb.apps.ccmodule.io.ChemCompDataExport          import ChemCompDataExport
from wwpdb.apps.ccmodule.io.ChemCompIo                  import ChemCompReader
#
from wwpdb.wwpdb.utils.wf.DataReference                     import DataFileReference
from wwpdb.utils.config.ConfigInfo                        import ConfigInfo
#
from wwpdb.apps.entity_transform.utils.mmCIFUtil        import mmCIFUtil
#
from oe_util.oedepict.OeAlignDepictUtils                import OeDepictMCSAlignSingle
from oe_util.oedepict.OeDepict                          import OeDepict
from oe_util.build.OeChemCompIoUtils                    import OeChemCompIoUtils
#
import datetime, stat
import socket, shlex
from subprocess import call,Popen,PIPE

class ChemCompWebAppLite(object):
    """Handle request and response object processing for the chemical component lite module application.
    
    """
    def __init__(self,parameterDict={},verbose=False,log=sys.stderr,siteId="WWPDB_DEV"):
        """
        Create an instance of `ChemCompWebAppLite` to manage a ligand editor web request from
        wwPDB Common Tool Deposition UI.

         :param `parameterDict`: dictionary storing parameter information from the web request.
             Storage model for GET and POST parameter data is a dictionary of lists.
         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.
          
        """
        self.__verbose=verbose
        self.__lfh=log
        self.__debug=False
        self.__siteId=siteId
        self.__cI=ConfigInfo(self.__siteId)
        self.__topPath=self.__cI.get('SITE_WEB_APPS_TOP_PATH')
        self.__deployPath=self.__cI.get('SITE_DEPLOY_PATH')
        self.__topSessionPath  = self.__cI.get('SITE_WEB_APPS_TOP_SESSIONS_PATH')
        self.__sessionsPath=self.__cI.get('SITE_WEB_APPS_SESSIONS_PATH')
        self.__templatePath = os.path.join(self.__topPath,"htdocs","ccmodule_lite")
        #

        if type( parameterDict ) == types.DictType:
            self.__myParameterDict=parameterDict
        else:
            self.__myParameterDict={}

        if (self.__verbose):
            self.__lfh.write("+%s.%s() - REQUEST STARTING ------------------------------------\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
            self.__lfh.write("+%s.%s() - dumping input parameter dictionary \n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )                        
            self.__lfh.write("%s" % (''.join(self.__dumpRequest())))
            
        self.__reqObj=InputRequest(self.__myParameterDict,verbose=self.__verbose,log=self.__lfh)
        #
        self.__reqObj.setValue("TopSessionPath", self.__topSessionPath)
        self.__reqObj.setValue("SessionsPath",   self.__sessionsPath)
        self.__reqObj.setValue("TemplatePath",   self.__templatePath)
        self.__reqObj.setValue("TopPath",        self.__topPath)
        self.__reqObj.setValue("WWPDB_SITE_ID",  self.__siteId)
        os.environ["WWPDB_SITE_ID"]=self.__siteId
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        #
        if (self.__verbose):
            self.__lfh.write("-----------------------------------------------------\n")
            self.__lfh.write("+%s.%s() Leaving _init with request contents\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )            
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
        stw=ChemCompWebAppLiteWorker(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        rC=stw.doOp()
        if (self.__debug):
            rqp=self.__reqObj.getRequestPath()
            self.__lfh.write("+%s.%s() operation %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name,rqp) )
            self.__lfh.write("+%s.%s() return format %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, self.__reqObj.getReturnFormat() ) )
            if rC is not None:
                self.__lfh.write("%s" % (''.join(rC.dump())))
            else:
                self.__lfh.write("+%s.%s() return object is empty\n"%( self.__class__.__name__, sys._getframe().f_code.co_name) )
                

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
        retL=[]
        retL.append("\n\-----------------ChemCompWebAppLite().__dumpRequest()-----------------------------\n")
        retL.append("Parameter dictionary length = %d\n" % len(self.__myParameterDict))            
        for k,vL in self.__myParameterDict.items():
            retL.append("Parameter %30s :" % k)
            for v in vL:
                retL.append(" ->  %s\n" % v)
        retL.append("-------------------------------------------------------------\n")                
        return retL
    

class ChemCompWebAppLiteWorker(object):
    def __init__(self, reqObj=None, verbose=False,log=sys.stderr):
        """
         Worker methods for the chemical component editor application

         Performs URL - application mapping and application launching
         for chemical component editor tool.
         
         All operations can be driven from this interface which can
         supplied with control information from web application request
         or from a testing application.
        """
        self.__verbose=verbose
        self.__lfh=log
        self.__reqObj=reqObj
        self.__sObj=None
        self.__sessionId=None
        self.__sessionPath=None
        self.__rltvSessionPath=None
        self.__siteId = str(self.__reqObj.getValue("WWPDB_SITE_ID"))
        self.__cI = ConfigInfo(self.__siteId)
        self.__deployPath = self.__cI.get('SITE_DEPLOY_PATH')
        self.__siteSrvcUrlPathPrefix = self.__cI.get('SITE_SERVICE_URL_PATH_PREFIX')
        self.__siteConfigDir = self.__cI.get('TOP_WWPDB_SITE_CONFIG_DIR')
        self.__siteLoc = self.__cI.get('WWPDB_SITE_LOC')
        self.__ccConfig = ChemCompConfig(reqObj,verbose=self.__verbose,log=self.__lfh)
        #
        self.__pathInstncsVwTmplts="templates/workflow_ui/instances_view"
        self.__pathSnglInstcTmplts=self.__pathInstncsVwTmplts+"/single_instance"
        self.__pathSnglInstcEditorTmplts=self.__pathSnglInstcTmplts+"/editor"
        #
        self.__appPathD={'/service/environment/dump':                       '_dumpOp',
                         '/service/cc_lite/extract':                             '_extractOp',
                         '/service/cc_lite/view':                                '_viewOp',
                         '/service/cc_lite/adminops':                            '_dumpOp',
                         '/service/cc_lite/search/cc-index':                     '_searchIndexOp',
                         '/service/cc_lite/search/cc-db':                        '_searchDbOp',
                         '/service/cc_lite/search/cc-graph':                     '_searchGraphOp',
                         '/service/cc_lite/report':                              '_reportOp',
                         '/service/cc_lite/edit/launch':                         '_editLaunchOp',
                         '/service/cc_lite/testfile':                            '_ligandSrchSummary',
                         '/service/cc_lite/new-session/wf':                      '_ligandSrchSummary',
                         '/service/cc_lite/new_session/wf':                      '_ligandSrchSummary',
                         '/service/cc_lite/save/newligdescr':                    '_saveNwLgndDscrptn',
                         '/service/cc_lite/save/exactmtchid':                     '_saveExactMtchId',
                         '/service/cc_lite/save/rsrchdata':                         '_saveRsrchData',
                         '/service/cc_lite/updatersrchlst':                         '_updateResearchList',
                         '/service/cc_lite/validate_ccid':                          '_validateCcId',
                         '/service/cc_lite/check_uploaded_files':                    '_checkForUploadedFiles',
                         '/service/cc_lite/remove_uploaded_file':                   '_removeUploadedFile',
                         ###############  below are URLs created for WFM/common tool development effort######################
                         #'/service/cc_lite/assign/wf/new_session':                 '_ccAssign_BatchSrchSummary',
                         '/service/cc_lite/wf/new_session':                         '_ligandSrchSummary',
                         '/service/cc_lite/view/ligandsummary':                     '_generateSummaryData',
                         '/service/cc_lite/view/ligandsummary/data_check':          '_checkForSummaryData',
                         '/service/cc_lite/view/ligandsummary/data_load':           '_loadSummaryData',
                         '/service/cc_lite/view/instancebrowser':                   '_generateInstncBrowser',
                         '/service/cc_lite/wf/exit_not_finished':                   '_exit_notFinished',
                         '/service/cc_lite/wf/exit_finished':                       '_exit_Finished'
                         ###################################################################################################
                         }
        
    def doOp(self):
        """Map operation to path and invoke operation.  
        
            :Returns:

            Operation output is packaged in a ResponseContent() object.
        """
        return self.__doOpException()
    
    def __doOpNoException(self):
        """Map operation to path and invoke operation.  No exception handling is performed.
        
            :Returns:

            Operation output is packaged in a ResponseContent() object.
        """
        #
        reqPath=self.__reqObj.getRequestPath()
        self.__lfh.write("+%s.%s() original request path is %r\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, reqPath) )
        reqPath = self.__normalizeReqPath(reqPath)
        self.__lfh.write("+%s.%s() normalized request path is %r\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, reqPath) )
        if not self.__appPathD.has_key(reqPath):
            # bail out if operation is unknown -
            rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
            rC.setError(errMsg='Unknown operation')
            return rC
        else:
            mth=getattr(self,self.__appPathD[reqPath],None)
            rC=mth()
        return rC

    def __doOpException(self):
        """Map operation to path and invoke operation.  Exceptions are caught within this method.
        
            :Returns:

            Operation output is packaged in a ResponseContent() object.
        """
        #
        try:
            reqPath=self.__reqObj.getRequestPath()
            self.__lfh.write("+%s.%s() original request path is %r\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, reqPath) )
            reqPath = self.__normalizeReqPath(reqPath)
            self.__lfh.write("+%s.%s() normalized request path is %r\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, reqPath) )
            if not self.__appPathD.has_key(reqPath):
                # bail out if operation is unknown -
                rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
                rC.setError(errMsg='Unknown operation')
            else:
                mth=getattr(self,self.__appPathD[reqPath],None)
                rC=mth()
            return rC
        except:
            traceback.print_exc(file=self.__lfh)
            rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
            rC.setError(errMsg='Operation failure')
            return rC

    def __normalizeReqPath(self,p_reqPath):
        # special handling required for some sites which have custom prefixes in url request
        if( self.__siteSrvcUrlPathPrefix and len(self.__siteSrvcUrlPathPrefix) > 1 ):
            if( p_reqPath.startswith(self.__siteSrvcUrlPathPrefix) ):
                return p_reqPath.split(self.__siteSrvcUrlPathPrefix)[1]
        else:
            return p_reqPath
        
    ################################################################################################################
    # ------------------------------------------------------------------------------------------------------------
    #      Top-level REST methods
    # ------------------------------------------------------------------------------------------------------------
    #
    def _dumpOp(self):
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        rC.setHtmlList(self.__reqObj.dump(format='html'))
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
            self.__lfh.write("+%s.%s() Starting now\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        # determine if currently operating in Workflow Managed environment
        bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        #
        dataFile = str( self.__reqObj.getValue("datafile") )
        fileSource = str(self.__reqObj.getValue("filesource")).strip().lower()
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")        
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        if (self.__verbose):
            self.__lfh.write("+%s.%s() workflow flag is %r\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, bIsWorkflow) )
        
        if ( bIsWorkflow ):
            # Update WF status database --
            '''
            bSuccess = self.__updateWfTrackingDb("open")
            if( not bSuccess ):
                rC.setError(errMsg="+%s.%s() - TRACKING status, update to 'open' failed for session %s \n" %(self.__class__.__name__, sys._getframe().f_code.co_name, self.__sessionId ) )
            else:
                if (self.__verbose):
                    self.__lfh.write("+%s.%s() Tracking status set to open\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
            '''                
        else:
            if( fileSource and fileSource == "rcsb_dev"):
                if dataFile:
                    sessionFilePath = os.path.join(self.__sessionPath,dataFile)
                    
                    # make copy of file in sessions directory for any access/processing required by front-end
                    devDataExamplePath = os.path.join(self.__deployPath+"/wwpdb_da_test/webapps/htdocs/ccmodule_lite/test_data",dataFile)
                    shutil.copyfile(devDataExamplePath, sessionFilePath)
                    self.__reqObj.setValue("filePath",devDataExamplePath)
                    
            elif( fileSource and fileSource == "upload"):
                if not self.__isFileUpload():
                    rC.setError(errMsg='No file uploaded')            
                    return rC
            #
                self.__uploadFile()
        #
        if (self.__verbose):
            self.__lfh.write("+%s.%s() Called with workflow: %r\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, bIsWorkflow) )
            
        ccAD=ChemCompAssignDepictLite(self.__reqObj,self.__verbose,self.__lfh)
        ccAD.setSessionPaths(self.__reqObj)
        oL = ccAD.doRender_LigSrchSummary(self.__reqObj,bIsWorkflow)
        rC.setHtmlText( '\n'.join(oL) )
        #
        return rC

    def _generateSummaryData(self):
        """ Generate chem comp lite summary results for entire deposition data set
            Child process is spawned to allow summary results to be gathered
            while parent process completes simply by returning status of "running"
            to the client.
            
            :Helpers:
                wwpdb.apps.ccmodule.chem.ChemCompAssign.ChemCompAssign
                
            :Returns:
                JSON object with status code of "running" returned.
        """
        self.__getSession()
        depId       =str(self.__reqObj.getValue("identifier"))
        #
        bReusingPriorDataStore=True
        #
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+%s.%s() starting\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
            self.__lfh.write("+%s.%s() identifier   %s\n"%(self.__class__.__name__, sys._getframe().f_code.co_name, depId) )
            self.__lfh.write("+%s.%s() workflow instance     %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, self.__reqObj.getValue("instance")) )
            self.__lfh.write("+%s.%s() file source  %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, self.__reqObj.getValue("filesource")) )
            self.__lfh.write("+%s.%s() sessionId  %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, self.__sessionId ) )       
            self.__lfh.flush()
        #
        sph=self.__setSemaphore()
        if (self.__verbose):
                self.__lfh.write("+%s.%s() Just before fork to create child process w/ separate log generated in session directory.\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        pid = os.fork()
        if pid == 0:
            # if here, means we are in the child process
            
            # determine if currently operating in Workflow Managed environment
            bIsWorkflow = self.__isWorkflow()
            #
            if( bIsWorkflow ):
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
                self.__lfh.write("+%s.%s() Child Process: PID# %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, os.getpid()) )
            #
            try:
                # check if there was work already done by depositor in editing chem comp assignments
                # if so, we generate a cc-assign data store based on these updates
                ccAssignDataStore = self.__checkForExistingCcAssignments()
                
                if ccAssignDataStore is None: # i.e. no work had previously been done and saved by depositor
                    # if we don't have any data store then we need to generate a data store from scratch
                    # which requires that we fill it with data as parsed from the cc-assign results cif file 
                    
                    # create instance of ChemCompAssign class
                    ccA=ChemCompAssign(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
                    
                    # we expect that Dep UI code would have run cc-assign search already
                    # so we will attempt to import the already existing cc-assign.cif file into local session directory
                    # and parse these for results
                    ccI=ChemCompDataImport(self.__reqObj,verbose=self.__verbose,log=self.__lfh)
                    ccAssignWfFlPth = ccI.getChemCompAssignFilePath() # the path to copy of the cc-assign results file held by workflow/depUI 
                    ccAssignLclFlPath = os.path.join(self.__sessionPath,depId+'-cc-assign.cif') # path to local copy of the cc-assign file that we will create
                    if ccAssignWfFlPth is not None and os.access(ccAssignWfFlPth,os.R_OK):
                        shutil.copyfile(ccAssignWfFlPth, ccAssignLclFlPath)
                        if os.access(ccAssignLclFlPath,os.R_OK):
                            assignRsltsDict=ccA.processCcAssignFile(ccAssignLclFlPath)
                        else:
                            # If for some reason there was problem getting pre-existing CC assignment results file, we must then call on ChemCompAssign to generate ligand summary results 
                            assignRsltsDict = self.__runChemCompSearch(ccA)
                        #
                    else:
                        #########################################################################################################################################################
                        #    if we are in standalone test context then we must then call on ChemCompAssign to generate ligand summary results 
                        #########################################################################################################################################################
                        assignRsltsDict = self.__runChemCompSearch(ccA)
                                                    
                    if (self.__verbose):
                        for k,v in assignRsltsDict.items():
                            self.__lfh.write("+%s.%s() key %30s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, k) )
                    
                    # generate a datastore to serve as representation of chem component assignment results data required/updated by annotator during current session.
                    ccAssignDataStore = self.__genCcAssignDataStore(assignRsltsDict,ccA)
                    bReusingPriorDataStore=False
                
                if( ccAssignDataStore is None ): # if this is true here, then we have failed to create a ccAssignDataStore either from scratch or based on previous depositor efforts
                    self.__postSemaphore(sph,"FAIL")
                    self.__lfh.flush()
                else:
                    self.__generateInstanceLevelData(ccAssignDataStore,bReusingPriorDataStore,sph)
                    #self.__postSemaphore(sph,"OK")
                    self.__importDepositorFiles(ccAssignDataStore)
            except:
                traceback.print_exc(file=self.__lfh)
                self.__lfh.write("+%s.%s() Failing for child Process: PID# %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name,os.getpid()) )    
                self.__postSemaphore(sph,"FAIL")
                self.__lfh.flush()
                self.__verbose = False
            
            self.__saveLigModState("intermittent") # now invoking this on startup to generate cc-dpstr-prgrss file for depui monitoring purposes
            
            self.__lfh.write("+%s.%s() Process: PID# %s completed\n" %(self.__class__.__name__, sys._getframe().f_code.co_name,os.getpid()) )
            self.__lfh.flush()    
            os._exit(0)
            self.__verbose = False
            return
        
        else:
            # we are in parent process and we will return status code to client to indicate that data processing is "running"
            self.__lfh.write("+%s.%s() Parent Process: PID# %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name,os.getpid()) )
            self.__reqObj.setReturnFormat(return_format="json")
            rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
            rC.setStatusCode('running')
            self.__lfh.write("+%s.%s() Parent process completed\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
            return rC
    
    def _checkForSummaryData(self):
        """Performs a check on the contents of a semaphore file and returns the associated status.

           This method currently supports both rcsb and wf filesources.
        """
        #
        self.__getSession()
        sessionId   =self.__sessionId
        #
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")                    
            self.__lfh.write("+%s.%s - starting\n"%(self.__class__.__name__, sys._getframe().f_code.co_name))
            self.__lfh.write("+%s.%s() sessionId  %s\n"%(self.__class__.__name__, sys._getframe().f_code.co_name, sessionId) )       
            self.__lfh.flush()
        #
        try:
            sph=self.__reqObj.getSemaphore()
            #
            if (self.__verbose):
                self.__lfh.write("+%s.%s Checking status of semaphore %s \n" %(self.__class__.__name__, sys._getframe().f_code.co_name, sph))    
            self.__reqObj.setReturnFormat(return_format="json")
            rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
            #
            if (self.__semaphoreExists(sph)):
                status=self.__getSemaphore(sph)
                if (self.__verbose):
                    self.__lfh.write("+%s.%s status value for semaphore %s is %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, sph, str(status)))
                if (status =="OK"):
                    rC.setStatusCode('completed')
                else:
                    rC.setStatusCode('failed')                
            else:
                if (self.__verbose):
                    self.__lfh.write("+%s.%s semaphore %s not posted yet.\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, sph))
                rC.setStatusCode('running')
        except:
            self.__lfh.write("+%s.%s() Exception encountered!!\n" %(self.__class__.__name__, sys._getframe().f_code.co_name ) )
            traceback.print_exc(file=self.__lfh)
            self.__lfh.flush()
            return rC
              
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
            self.__lfh.write("+%s.%s() starting\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        # determine if currently operating in Workflow Managed environment
        self.__getSession()
        sessionId=self.__sessionId
        self.__reqObj.setDefaultReturnFormat(return_format="html")        
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        ccADS=ChemCompAssignDataStore(self.__reqObj,verbose=True,log=self.__lfh)
        #
        ccAD=ChemCompAssignDepictLite(self.__reqObj,self.__verbose,self.__lfh)
        oL=ccAD.doRender_LigSummaryContent(ccADS,self.__reqObj)
        oL.extend(ccAD.doRender_InstanceBrswrLaunchForm(self.__reqObj))
        #oL.extend(ccAD.doRender_WaterRsrchCaptureContent(ccADS,self.__reqObj))
        #
        rC.setHtmlText( '\n'.join(oL) )
        return rC    

    def _generateInstncBrowser(self):
        """ Generate content for "Instance Browser" view
            This view allows user to navigate ligand instance data via entity CCID groupings
            
            :Helpers:
            
                + wwpdb.apps.ccmodule.chem.ChemCompAssign.ChemCompAssign
                + wwpdb.apps.ccmodule.chem.ChemCompAssignDepictLite.ChemCompAssignDepictLite
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore
                
            :Returns:
                Operation output is packaged in a ResponseContent() object.
                The output contains HTML markup that is used to populate the
                HTML container that had already been delivered to the browser
                in the prior request for the Batch Search Summary content.
                This output represents the "Instance-Level" display interface.
        """
        ligIdsL=[]
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+%s.%s() starting\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        # determine if currently operating in Workflow Managed environment
        self.__getSession()
        #
        sessionId   = self.__sessionId
        depId       = str(self.__reqObj.getValue("identifier")).upper()
        ligIds     = str(self.__reqObj.getValue("ligids"))
        ligIdsRsrch = str(self.__reqObj.getValue("ligids_rsrch"))
        wfInstId    = str(self.__reqObj.getValue("instance")).upper()
        classId     = str(self.__reqObj.getValue("classID")).lower()
        fileSource  = str(self.__reqObj.getValue("filesource")).lower()
        #
        if (self.__verbose):
            self.__lfh.write("+%s.%s() identifier   %s\n"%(self.__class__.__name__, sys._getframe().f_code.co_name, depId) )
            self.__lfh.write("+%s.%s() instance     %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, wfInstId) )
            self.__lfh.write("+%s.%s() file source  %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, fileSource) )
            self.__lfh.write("+%s.%s() sessionId  %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, sessionId) )       
            self.__lfh.flush()
 
        #
        ligIdsL = ligIds.split(',')
        ligIdsRsrchL = ligIdsRsrch.split(',')
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        #        
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        ccA=ChemCompAssign(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
        # unpickle assign data from ccAssignDataStore
        if (self.__verbose):
            self.__lfh.write("+%s.%s() ----- unpickling ccAssignDataStore\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        ccADS=ChemCompAssignDataStore(self.__reqObj,verbose=True,log=self.__lfh)
        ccADS.dumpData(self.__lfh);
        #
        instncIdLst=ccADS.getAuthAssignmentKeys()
        srtdInstncLst = sorted(instncIdLst);
        ccA.getDataForInstncSrch(srtdInstncLst,ccADS)
        #
        ccADS.dumpData(self.__lfh);
        ccADS.serialize()
        # call render() methods to generate data unique to this deposition data set
        ccAD=ChemCompAssignDepictLite(self.__reqObj,self.__verbose,self.__lfh)
        ccAD.setSessionPaths(self.__reqObj)
        oL=ccAD.doRender_InstanceBrwsr(ligIdsL,ligIdsRsrchL,ccADS,self.__reqObj)
        #
        rC.setHtmlText( ''.join(oL) )
        return rC
    
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
            self.__lfh.write("+%s.%s() Starting now\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        #
        self.__getSession()
        sessionId   = self.__sessionId
        depId       = str(self.__reqObj.getValue("identifier")).upper()
        wfInstId    = str(self.__reqObj.getValue("instance")).upper()
        authAssgndGrp   = str(self.__reqObj.getValue("auth_assgnd_grp"))
        mode   = str(self.__reqObj.getValue("mode"))
        #
        dpstrExactMtchCcId   = str(self.__reqObj.getValue("exactmatchid"))
        dpstrOrigPrpsdCcId   = str(self.__reqObj.getValue("origproposedid"))
        #
        if (self.__verbose):
            self.__lfh.write("+%s.%s() authAssgndGrp is: %s\n"%(self.__class__.__name__, sys._getframe().f_code.co_name,authAssgndGrp) )
            
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        
        # unpickle assign data from ccAssignDataStore
        if (self.__verbose):
            self.__lfh.write("+%s.%s() unpickling ccAssignDataStore\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        
        ccADS=ChemCompAssignDataStore(self.__reqObj,verbose=True,log=self.__lfh)
        
        if( mode == 'done' ): # mode will be either 'done' or 'undo'
            ccADS.addGrpToGlbllyRslvdLst(authAssgndGrp)
            ccADS.initializeGrpInfo(authAssgndGrp)
            if( dpstrExactMtchCcId and len(dpstrExactMtchCcId) > 1 ):
                ccADS.setDpstrExactMtchCcId(authAssgndGrp,dpstrExactMtchCcId)
            else:
                ccADS.setDpstrAltCcId(authAssgndGrp,dpstrOrigPrpsdCcId)
        else:
            ccADS.removeGrpFrmGlbllyRslvdLst(authAssgndGrp)
            ccADS.setDpstrExactMtchCcId(authAssgndGrp,None)
            ccADS.setDpstrAltCcId(authAssgndGrp,None)
        
        ccADS.serialize()
        ccADS.dumpData(self.__lfh);
        
        if( mode == "done" ): # mode will be either 'done' or 'undo'
            self.__saveLigModState("intermittent")
        
        return rC
    '''
    def _saveMissingLgndDscrptns(self):
        """ Register depositor descriptions of any ligands not found by cc-assign search
        
            :Helpers:
                wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore
                
            :Returns:
                ResponseContent() object.
                No display output for this method.
        """
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+%s.%s() Starting now\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        #
        self.__getSession()
        sessionId   = self.__sessionId
        depId       = str(self.__reqObj.getValue("identifier")).upper()
        wfInstId    = str(self.__reqObj.getValue("instance")).upper()
        mode   = str(self.__reqObj.getValue("mode"))
        #
        if( mode == 'done' ):
            index = 1
            workToDo = True
            dpstrCcId = None
            dpstrCcName = None
            dpstrCcFrmla = None
            #
            ccADS=ChemCompAssignDataStore(self.__reqObj,verbose=True,log=self.__lfh)
        
            while workToDo:
                dpstrCcId   = str(self.__reqObj.getValue("ccid_"+index))
                dpstrCcName   = str(self.__reqObj.getValue("molname_"+index))
                dpstrCcFrmla   = str(self.__reqObj.getValue("frmla_"+index))
                index += 1
                if not dpstrCcId and not dpstrCcName and not dpstrCcFrmla:
                    workToDo = False
                else:
                    ccADS.addToMissingGrpLst(dpstrCcId)
                    ccADS.initializeGrpInfo(dpstrCcId)
                    if( len(dpstrCcName) > 1 ):
                        ccADS.setDpstrCcName(dpstrCcId,dpstrCcName)
                    if( len(dpstrCcFrmla) > 1 ):
                        ccADS.setDpstrCcFrmla(dpstrCcId,dpstrCcFrmla)
        else:
            ccADS.purgeMissingLigandsData()
        #
        if (self.__verbose):
            self.__lfh.write("+%s.%s() \n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
            
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        
        # unpickle assign data from ccAssignDataStore
        if (self.__verbose):
            self.__lfh.write("+%s.%s() unpickling ccAssignDataStore\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        
        
        ccADS.serialize()
        ccADS.dumpData(self.__lfh);
        
        return rC       
   '''
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
            self.__lfh.write("+%s.%s() Starting now\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        #
        self.__getSession()
        sessionId   = self.__sessionId
        depId       = str(self.__reqObj.getValue("identifier")).upper()
        authAssgndGrp   = str(self.__reqObj.getValue("auth_assgnd_grp"))
        mode   = str(self.__reqObj.getValue("mode"))
        
        lstGrps = []
        
        if (self.__verbose):
            self.__lfh.write("+%s.%s() ---------------- STARTING ----------------\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
            self.__lfh.write("+%s.%s() authAssgndGrp is: %s\n"%(self.__class__.__name__, sys._getframe().f_code.co_name,authAssgndGrp) )
            self.__lfh.write("+%s.%s() mode is: %s\n"%(self.__class__.__name__, sys._getframe().f_code.co_name,mode) )
            
        self.__reqObj.setReturnFormat(return_format="json") 
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        
        # unpickle assign data from ccAssignDataStore
        if (self.__verbose):
            self.__lfh.write("+%s.%s() unpickling ccAssignDataStore\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        
        ccADS=ChemCompAssignDataStore(self.__reqObj,verbose=True,log=self.__lfh)
        #
        if( ',' in authAssgndGrp ):
            # presence of comma indicates list of group IDs
            lstGrps = authAssgndGrp.split(',')
                
        if( mode == 'add' ):  # mode will be either 'add' or 'remove'
            if( len(lstGrps) > 0 ):
                for grpId in lstGrps:
                    ccADS.addGrpToRsrchSelectedLst(grpId)
            else:
                ccADS.addGrpToRsrchSelectedLst(authAssgndGrp)
        else:
            if( len(lstGrps) > 0 ):
                for grpId in lstGrps:
                    ccADS.removeGrpFrmRsrchSelectedLst(grpId)
            else:
                ccADS.removeGrpFrmRsrchSelectedLst(authAssgndGrp)
        
        ccADS.serialize()
        ccADS.dumpData(self.__lfh);
        
        self.__saveLigModState("intermittent")
            
        if (self.__verbose):
            self.__lfh.write("+%s.%s() ---------------- DONE ----------------\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        
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
            self.__lfh.write("+%s.%s() Starting now\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        #
        self.__getSession()
        sessionId   = self.__sessionId
        depId       = str(self.__reqObj.getValue("identifier")).upper()
        wfInstId    = str(self.__reqObj.getValue("instance")).upper()
        authAssgndGrp   = str(self.__reqObj.getValue("auth_assgnd_grp"))
        mode   = str(self.__reqObj.getValue("mode"))
        
        
        
        if (self.__verbose):
            self.__lfh.write("+%s.%s() authAssgndGrp is: %s\n"%(self.__class__.__name__, sys._getframe().f_code.co_name,authAssgndGrp) )
            self.__lfh.write("+%s.%s() mode is: %s\n"%(self.__class__.__name__, sys._getframe().f_code.co_name,mode) )
            
        self.__reqObj.setReturnFormat(return_format="json") 
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        
        # unpickle assign data from ccAssignDataStore
        if (self.__verbose):
            self.__lfh.write("+%s.%s() unpickling ccAssignDataStore\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        
        ccADS=ChemCompAssignDataStore(self.__reqObj,verbose=True,log=self.__lfh)
        #
        if( mode == 'done' ):  # mode will be either 'done' or 'undo'

            dataSetDict = {}
            for index in range(10):
                
                if( authAssgndGrp != "HOH" ):
                    assayType = self.__reqObj.getValue("assay_type_"+str(index)+"_")
                    if( assayType is not None and len(assayType) >= 1 ): # i.e. if one param exists for a given index then all params exist for the parameter
                        dataSetDict[index] = {}
                        dataSetDict[index]['assay_type'] = self.__normalizeForCifNull(assayType)
                        dataSetDict[index]['target_sequence'] = self.__normalizeForCifNull(self.__reqObj.getValue("target_sequence_"+str(index)+"_"))
                        dataSetDict[index]['rsrch_dscrptr_type'] = self.__normalizeForCifNull(self.__reqObj.getValue("rsrch_dscrptr_type_"+str(index)+"_"))
                        dataSetDict[index]['rsrch_dscrptr_str'] = self.__normalizeForCifNull(self.__reqObj.getValue("rsrch_dscrptr_str_"+str(index)+"_"))
                        dataSetDict[index]['ph'] = self.__normalizeForCifNull(self.__reqObj.getValue("ph_"+str(index)+"_"))
                        dataSetDict[index]['assay_temp'] = self.__normalizeForCifNull(self.__reqObj.getValue("assay_temp_"+str(index)+"_"))
                        dataSetDict[index]['measurement_type'] = self.__normalizeForCifNull(self.__reqObj.getValue("measurement_type_"+str(index)+"_"))
                        dataSetDict[index]['measured_value'] = self.__normalizeForCifNull(self.__reqObj.getValue("measured_value_"+str(index)+"_"))
                        dataSetDict[index]['details'] = self.__normalizeForCifNull(self.__reqObj.getValue("details_"+str(index)+"_"))
                        
                        for key in dataSetDict[index]:
                            self.__lfh.write("+%s.%s() dataSetDict[%s][%s] is: %s\n"%(self.__class__.__name__, sys._getframe().f_code.co_name, index, key, dataSetDict[index][key]) )
                
                elif( authAssgndGrp == "HOH" ):
                    residueNum = self.__reqObj.getValue("residuenum_"+str(index)+"_")
                    chainId = self.__reqObj.getValue("chain_id_"+str(index)+"_")
                    if( residueNum is not None and len(residueNum) >= 1 ) or ( chainId is not None and len(chainId) >= 1 ): # i.e. if at least one param provided
                        dataSetDict[index] = {}
                        dataSetDict[index]['residuenum'] = self.__normalizeForCifNull(residueNum)
                        dataSetDict[index]['chain_id'] = self.__normalizeForCifNull(chainId)
                    
                        for key in dataSetDict[index]:
                            self.__lfh.write("+%s.%s() dataSetDict[%s][%s] is: %s\n"%(self.__class__.__name__, sys._getframe().f_code.co_name, index, key, dataSetDict[index][key]) )
                
                    
            ccADS.addGrpToRsrchDataAcqurdLst(authAssgndGrp)
            ccADS.initializeGrpRsrchInfo(authAssgndGrp)
            ccADS.setResearchData(authAssgndGrp,dataSetDict)
            #
            
        
        else:
            ccADS.removeGrpFrmRsrchDataAcqurdLst(authAssgndGrp)
        
        ccADS.serialize()
        ccADS.dumpData(self.__lfh)
        
        if( mode == "done" ): # mode will be either 'done' or 'undo'
            self.__saveLigModState("intermittent")
        
        return rC   
    
    def __normalizeForCifNull(self,fieldToEval):
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
            self.__lfh.write("+%s.%s() Starting now\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        #
        self.__getSession()
        sessionId   = self.__sessionId
        depId       = str(self.__reqObj.getValue("identifier")).upper()
        wfInstId    = str(self.__reqObj.getValue("instance")).upper()
        authAssgndGrp   = str(self.__reqObj.getValue("auth_assgnd_grp"))
        mode   = str(self.__reqObj.getValue("mode"))
        
        dpstrCcType   = str(self.__reqObj.getValue("lgnd_type"))
        dpstrAltCcId   = str(self.__reqObj.getValue("alt_ccid"))
        dpstrCcDscptrType   = str(self.__reqObj.getValue("dscrptr_type"))
        dpstrCcDscptrStr   = str(self.__reqObj.getValue("dscrptr_str"))
        dpstrSubmitChoice   = str(self.__reqObj.getValue("submission_choice"))
        dpstrCcName   = str(self.__reqObj.getValue("chem_name"))
        dpstrCcFrmla   = str(self.__reqObj.getValue("chem_frmla"))
        dpstrComments   = str(self.__reqObj.getValue("comments"))
        
        molData = str(self.__reqObj.getValue("moldata"))
        #
        if (self.__verbose):
            self.__lfh.write("+%s.%s() authAssgndGrp is: %s\n"%(self.__class__.__name__, sys._getframe().f_code.co_name,authAssgndGrp) )
            
        self.__reqObj.setReturnFormat(return_format="json") 
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        
        # unpickle assign data from ccAssignDataStore
        if (self.__verbose):
            self.__lfh.write("+%s.%s() unpickling ccAssignDataStore\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        
        ccADS=ChemCompAssignDataStore(self.__reqObj,verbose=True,log=self.__lfh)
        #
        if( mode == 'done' ):  # mode will be either 'done' or 'undo'
            ccADS.addGrpToGlbllyRslvdLst(authAssgndGrp)
            ccADS.initializeGrpInfo(authAssgndGrp)
            ccADS.setDpstrCcType(authAssgndGrp,dpstrCcType)
            if( len(dpstrAltCcId) > 1 ):
                ccADS.setDpstrAltCcId(authAssgndGrp,dpstrAltCcId.upper())
            #ccADS.setDpstrSubmitChoice(authAssgndGrp,dpstrSubmitChoice)
            #if( dpstrSubmitChoice == 'dscrptrstr' and len(dpstrCcDscptrStr) > 1 ):
            if( len(dpstrCcDscptrStr) > 1 ):
                ccADS.setDpstrCcDscrptrStr(authAssgndGrp,dpstrCcDscptrStr)
                ccADS.setDpstrCcDscrptrType(authAssgndGrp,dpstrCcDscptrType)
            if( len(dpstrCcName) > 1 ):
                ccADS.setDpstrCcName(authAssgndGrp,dpstrCcName)
            if( len(dpstrCcFrmla) > 1 ):
                ccADS.setDpstrCcFrmla(authAssgndGrp,dpstrCcFrmla)
            if( len(dpstrComments) > 1 ):
                ccADS.setDpstrComments(authAssgndGrp,dpstrComments)
            #
            for fileTag in ["file_img","file_refdict"]:
                if (self.__verbose):
                    self.__lfh.write("+%s.%s() checking for uploaded files.\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
                if( self.__isFileUpload(fileTag) ):
                    if (self.__verbose):
                        self.__lfh.write("+%s.%s() found uploaded file instance with fileTag: %s.\n"%(self.__class__.__name__, sys._getframe().f_code.co_name, fileTag ) )
                    self._uploadDpstrFile(fileTag,ccADS)
            #
            #rC.addDictionaryItems({'filename':str(fileName)});
            #rC.setHtmlText("%s successfully uploaded!" % fileName)
        
        else:
            ccADS.removeGrpFrmGlbllyRslvdLst(authAssgndGrp)
        
        ccADS.serialize()
        ccADS.dumpData(self.__lfh);
        
        if( molData and len(molData)>0 ):
            #ccADS.setDpstrSketchMolDataStr(authAssgndGrp,molData)
            try:
                fileName = authAssgndGrp+'-sketch.sdf'
                fp=os.path.join(self.__sessionPath,fileName)
                ofh=open(fp,'a')
                if( molData.find("Mrv") == 0 ):
                    ofh.write("%s\n" % authAssgndGrp )                    
                ofh.write("%s\n" % molData)
                ofh.close()
                success = ccADS.setDpstrSketchFile(authAssgndGrp,'sdf',fileName)
                if success:
                    self.__lfh.write("+%s.%s() successfully updated data store for generated sketch file: %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, fileName) )
                    ccADS.serialize()
                    ccADS.dumpData(self.__lfh);
            except:
                traceback.print_exc(file=self.__lfh)            
                rC.setError(errMsg='Save of MarvinSketch sdf file failed')
                
        if( mode == "done" ): # mode will be either 'done' or 'undo'
            self.__saveLigModState("intermittent")
            
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
            self.__lfh.write("+%s.%s() ---- starting.\n"%( self.__class__.__name__, sys._getframe().f_code.co_name ) )
        # 
        self.__getSession()
        vldtMode        = str(self.__reqObj.getValue("vldtmode"))
        ccId            = str(self.__reqObj.getValue("alt_ccid")).upper()
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        pathPrefix = self.__ccConfig.getPath('chemCompCachePath')
        validationPth = os.path.join(pathPrefix,ccId[:1],ccId,ccId+'.cif')
        if (self.__verbose):
            self.__lfh.write("+%s.%s() ---- validating CC ID %s against path: %s\n"%( self.__class__.__name__, sys._getframe().f_code.co_name, ccId, validationPth) )
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
        methodName = sys._getframe().f_code.co_name
        #
        authAssgndGrp   = str(self.__reqObj.getValue("auth_assgnd_grp"))
        contentType   = str(self.__reqObj.getValue("content_type"))
        #
        rtrnDict = {}
        #
        if (self.__verbose):
            self.__lfh.write("+%s.%s() -- Starting.\n" % (className, methodName) )        
        #
        bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        self.__reqObj.setValue("RelativeSessionPath", self.__rltvSessionPath)
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        uploadedFilesLst = self.__verifyUploadedFiles(authAssgndGrp,contentType)
        #
        ccAD=ChemCompAssignDepictLite(self.__reqObj,self.__verbose,self.__lfh)
        ccAD.setSessionPaths(self.__reqObj)
        htmlMrkp = ccAD.doRender_UploadedFilesList(authAssgndGrp,uploadedFilesLst,self.__reqObj)
        #
        rtrnDict['filesonrecord'] = 'true' if len(uploadedFilesLst) > 0 else 'false'
        rtrnDict['htmlmrkup'] = ''.join(htmlMrkp)
        rtrnDict['filelist'] = uploadedFilesLst
        
        if (self.__verbose):
            self.__lfh.write("\n%s.%s() -- rtrnDict['htmlmrkup'] is:%s\n" % (self.__class__.__name__,
                                                       sys._getframe().f_code.co_name,
                                                       rtrnDict['htmlmrkup']) )
            
        rC.addDictionaryItems( rtrnDict )
        
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
        methodName = sys._getframe().f_code.co_name
        #
        rtrnStatus = "FAIL"
        authAssgndGrp   = str(self.__reqObj.getValue("auth_assgnd_grp"))
        fileName   = str(self.__reqObj.getValue("file_name"))
        #
        if (self.__verbose):
            self.__lfh.write("+%s.%s() -- Starting.\n" % (className, methodName) )        
        #
        bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        self.__reqObj.setValue("RelativeSessionPath", self.__rltvSessionPath)
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        bSuccess = self.__removeUploadedFile(authAssgndGrp,fileName)
        #
        if( bSuccess ):
            rtrnStatus = "OK"
        rC.setStatusCode(rtrnStatus)
        return rC            
        
    def _searchGraphOp(self):
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppLiteWorker._searchGraphOp() starting\n")

        self.__getSession()
        self.__reqObj.setDefaultReturnFormat(return_format="html")        
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        
        if self.__isFileUpload():
            # make a copy of the file in the session directory and set 'fileName'
            self.__uploadFile()
        #
        
        ccE=ChemCompSearch(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
        rD=ccE.doGraphIso()
        if (self.__verbose):
            for k,v in rD.items():
                self.__lfh.write("+ChemCompWebAppLite._searchGraphOp() key %30s   value %s\n" % (k,v))
        if len(rD) > 0:
            ccSD=ChemCompSearchDepict(self.__verbose,self.__lfh)
            oL=ccSD.doRenderGraph(rD)                        
            rC.setHtmlList(oL)
        else:
            rC.setError(errMsg='No search result')

        return rC

    def _searchIndexOp(self):
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppLiteWorker._searchIndexOp() starting\n")
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")        
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        ccS=ChemCompSearch(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
        rD=ccS.doIndex()
        if len(rD) > 0:
            ccSD=ChemCompSearchDepict(self.__verbose,self.__lfh)
            oL=ccSD.doRenderIndex(rD)                        
            rC.setHtmlList(oL)
        else:
            rC.setError(errMsg='No search result')

        return rC

    def _searchDbOp(self):
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppLiteWorker._searchDbOp() starting\n")
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")        
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        ccS=ChemCompSearchDb(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
        rD=ccS.doIdSearch()
        if len(rD) > 0:
            ccSD=ChemCompSearchDbDepict(self.__verbose,self.__lfh)
            oL=ccSD.doRender(rD)                        
            rC.setHtmlList(oL)
        else:
            rC.setError(errMsg='No search result')

        return rC

    def _extractOp(self):
        if (self.__verbose):
            self.__lfh.write("+%s.%s() starting\n"%( self.__class__.__name__, sys._getframe().f_code.co_name))

        self.__getSession()
        self.__reqObj.setDefaultReturnFormat(return_format="html")        
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        
        if not self.__isFileUpload():
            rC.setError(errMsg='No file uploaded')            
            return rC
        #
        self.__uploadFile()
        ccE=ChemCompExtract(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
        rD=ccE.doExtract()
        if (self.__verbose):
            for k,v in rD.items():
                self.__lfh.write("+%s.%s() key %30s   value %s\n" %( self.__class__.__name__, sys._getframe().f_code.co_name,k,v) )
        if (rD.has_key('extractlist') and len(rD['extractlist']) > 0):
            ccExD=ChemCompExtractDepict(self.__verbose,self.__lfh)
            oL=ccExD.doRender(rD['extractlist'])
            rC.setHtmlList(oL)
        else:
            rC.setError(errMsg="No components extracted")
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
            self.__lfh.write("+ChemCompWebAppLiteWorker._viewOp() starting\n")
        #
        self.__getSession()
        sessionId   = self.__sessionId
        if (self.__verbose):
            self.__lfh.write("+%s.%s() session ID is: %s\n" %( self.__class__.__name__, sys._getframe().f_code.co_name, sessionId) )
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        ccV=ChemCompView(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
        #
        rtrnCode=ccV.doView()
        #
        if self.__verbose:
            self.__lfh.write("+ChemCompWebAppLiteWorker._viewOp() - return code is %s\n" % str(rtrnCode) )
            
        rC.addDictionaryItems({'sessionid':str(sessionId)});
        rC.setStatusCode(str(rtrnCode))
        
        return rC

    def _editLaunchOp(self):
        """ Launch chemical component editor
            
            :Returns:
                Operation output is packaged in a ResponseContent() object.
        """
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppLiteWorker._editLaunchOp() \n")
        #
        
        sessionId   = str(self.__reqObj.getValue("sessionid"))
        depId       = str(self.__reqObj.getValue("identifier")).upper()
        instanceId  = str(self.__reqObj.getValue("instanceid")).upper()
        fileSource  = str(self.__reqObj.getValue("filesource")).lower()
        wfInstId    = str(self.__reqObj.getValue("instance")).upper()
        #
        self.__getSession()
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")        
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        
        ###########################################################################
        # create dictionary of content that will be used to populate HTML template
        ###########################################################################
        myD={}
        myD['sessionid'] = sessionId
        myD['depositionid'] = depId
        myD['instanceid'] = instanceId
        myD['related_instanceids'] = ''
        myD['filesource'] = fileSource
        myD['identifier'] = depId
        myD['instance'] = wfInstId
        #
        myD['session_url_prefix'] = os.path.join(self.__rltvSessionPath,"assign",instanceId)
        rC.setHtmlText(htmlText=self.__processTemplate(fn=os.path.join(self.__pathSnglInstcEditorTmplts,"cc_instnc_edit_tmplt.html"), parameterDict=myD))
        return rC
        
                                                                               
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
    def __runChemCompSearch(self,p_ccA):
        
        #########################################################################################################################################################
        #    If for some reason there was no pre-existing CC assignment results data, we must then call on ChemCompAssign to generate ligand summary results 
        #########################################################################################################################################################
        if (self.__verbose):
                now = strftime("%H:%M:%S", localtime()) 
                self.__lfh.write("+ChemCompWebAppLiteWorker ----TIMECHECK------------------------------------------ time before calling doAssign task is %s\n" % now)
        
        assignRsltsDict=p_ccA.doAssign(exactMatchOption=True) # NOTE this method generates the "global" cc-assign file *and* creates instance-level directories/chem-component files
        #########################################################################################################################################################
        #    in assignRsltsDict we now have a repository of assignment information for this deposition corresponding to
        #    cif categories: 'pdbx_entry_info','pdbx_instance_assignment','pdbx_match_list','pdbx_atom_mapping','pdbx_missing_atom'
        #########################################################################################################################################################
        
        if (self.__verbose):
                now = strftime("%H:%M:%S", localtime()) 
                self.__lfh.write("+ChemCompWebAppLiteWorker ----TIMECHECK------------------------------------------ time after calling doAssign task is %s\n" % now)
        #
        return assignRsltsDict
    
    
    def __removeUploadedFile(self,p_ccID,p_fileName):
        """
        """
        bSuccess=False
        ccADS=ChemCompAssignDataStore(self.__reqObj,verbose=True,log=self.__lfh)
        bChangeMade=False
        
        dpstrUploadFilesDict = ccADS.getDpstrUploadFilesDict()
        if( p_ccID in dpstrUploadFilesDict ):
            for fileType in dpstrUploadFilesDict[p_ccID]:
                for fileName in dpstrUploadFilesDict[p_ccID][fileType].keys():
                    if( fileName == p_fileName ):
                        try:
                            # delete local copy of file
                            lclFlPth = os.path.join(self.__sessionPath,fileName)
                            if( os.access(lclFlPth,os.R_OK) ):
                                os.remove(lclFlPth)
                                if (self.__verbose):
                                    self.__lfh.write("+%s.%s() ---- removing uploaded file from local storage: %s\n" %( self.__class__.__name__, sys._getframe().f_code.co_name, lclFlPth) )
                            # delete any copy of file in "deposit" storage
                            wfFlPth = ccADS.getDpstrUploadFileWfPath(p_ccID,fileType,p_fileName)
                            if( wfFlPth is not None ):
                                os.remove(wfFlPth)
                                if (self.__verbose):
                                    self.__lfh.write("+%s.%s() ---- removing uploaded file from 'deposit' storage: %s\n" %( self.__class__.__name__, sys._getframe().f_code.co_name, wfFlPth) )
                                
                            # delete record of file in datastore
                            del dpstrUploadFilesDict[p_ccID][fileType][fileName]
                            if( len( dpstrUploadFilesDict[p_ccID][fileType].keys() ) == 0 ):
                                del dpstrUploadFilesDict[p_ccID][fileType]
                            
                            ccADS.dumpData(self.__lfh);
                            ccADS.serialize()
                            bSuccess=True
                            return bSuccess
                        except:
                            traceback.print_exc(file=self.__lfh)
                            self.__lfh.write("+%s.%s() ---- problem encountered when deleting uploaded file from storage.\n" %( self.__class__.__name__, sys._getframe().f_code.co_name) )
                            self.__lfh.flush()
        
        return bSuccess        
    
    def __verifyUploadedFiles(self,p_ccID,p_contentType):
        """
        """
        rtrnFlLst = []
        contentTypeDict = self.__cI.get('CONTENT_TYPE_DICTIONARY')
        ccADS=ChemCompAssignDataStore(self.__reqObj,verbose=True,log=self.__lfh)
        acceptedFileTypes = (contentTypeDict[p_contentType][0])[:]
        if( p_contentType == 'component-definition' ):
            acceptedFileTypes.append('cif')
        if( p_contentType == 'component-image' ):
            acceptedFileTypes.extend(['jpeg','bmp']) # may have accepted these in the past?
        
        dpstrUploadFilesDict = ccADS.getDpstrUploadFilesDict()
        if( p_ccID in dpstrUploadFilesDict ):
            for fileType in dpstrUploadFilesDict[p_ccID]:
                if fileType in acceptedFileTypes:                
                    for fileName in dpstrUploadFilesDict[p_ccID][fileType].keys():
                        lclFlPth = os.path.join(self.__sessionPath,fileName)
                        if( not os.access(lclFlPth,os.R_OK) ):
                            if (self.__verbose):
                                self.__lfh.write("+%s.%s() ---- uploaded file does not exist at path: %s\n" %( self.__class__.__name__, sys._getframe().f_code.co_name, lclFlPth) )
                            # if currently don't have local copy of file then need to obtain copy from "deposit" storage
                            wfFlPth = ccADS.getDpstrUploadFileWfPath(p_ccID,fileType,fileName)
                            if( wfFlPth is not None ):
                                if (self.__verbose):
                                    self.__lfh.write("+%s.%s() ---- copy of uploaded file being obtained from: %s\n" %( self.__class__.__name__, sys._getframe().f_code.co_name, wfFlPth) )
                                shutil.copyfile( wfFlPth, lclFlPth )
                        if( os.access(lclFlPth,os.R_OK) ):
                            rtrnFlLst.append(fileName)
                        else:
                            if (self.__verbose):
                                self.__lfh.write("+%s.%s() ---- unable to obtain working copy of uploaded file: %s\n" %( self.__class__.__name__, sys._getframe().f_code.co_name, fileName) )
                    
        return rtrnFlLst    
                
                        
    def __checkForExistingCcAssignments(self):
        """ Private method to generate a ChemCompAsssignDataStore object from pre-existing assignments already registered by user.
            The ChemCompAsssignDataStore serves as a representation of any 
            chem component assignment results data required/updated by the 
            depositor during the current session.
            
            :Params:
                    
            :Helpers:
            
                + wwpdb.apps.ccmodule.io.ChemCompDataImport.ChemCompDataImport
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore
                
            :Returns:
                A ChemCompAssignDataStore object.
        """
        rtrnCcAssgnDtStr = None
        
        depId = str(self.__reqObj.getValue("identifier")).upper()
        ccI=ChemCompDataImport(self.__reqObj,verbose=self.__verbose,log=self.__lfh)
        fpAssignDtlsWfmArchive =  ccI.getChemCompAssignDetailsFilePath()
        if (self.__verbose):
            self.__lfh.write("+%s.%s() ---- checking for existence of cc-assign-details.pic file in path: %s\n" %( self.__class__.__name__, sys._getframe().f_code.co_name, fpAssignDtlsWfmArchive) )
        if( fpAssignDtlsWfmArchive is not None and os.access(fpAssignDtlsWfmArchive,os.R_OK) ):
                assignDtlsLclPath = os.path.join(self.__sessionPath,'assign')
                if( not os.access(assignDtlsLclPath,os.R_OK)):
                    os.makedirs(assignDtlsLclPath)
                fpAssignDtlsLcl = os.path.join(assignDtlsLclPath,depId+'-cc-assign-details.pic')
                shutil.copyfile(fpAssignDtlsWfmArchive,fpAssignDtlsLcl)
                if( os.access(fpAssignDtlsLcl,os.R_OK) ):
                    #########################################################################################################################################################
                    #    If we have a pickle file of cc assign details this means that the annotator had saved previous ligand assignment work
                    #    with the intention to resume where last left off. So we will instantiate a cc assign data store from the pickled file
                    #    instead of running a batch search to generate a new cc assign data store.
                    #########################################################################################################################################################
                    rtrnCcAssgnDtStr=ChemCompAssignDataStore(self.__reqObj,verbose=True,log=self.__lfh)
                    if (self.__verbose):
                            self.__lfh.write("+%s.%s() prior cc assign details file being used to populate cc data store: %s\n" %( self.__class__.__name__, sys._getframe().f_code.co_name, fpAssignDtlsLcl) )
                            
        return rtrnCcAssgnDtStr      

    def __genCcAssignDataStore(self,p_ccAssignRsltsDict,p_ccAssignObj):
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
            self.__lfh.write("++++%s.%s() ---- creating new datastore because no prior cc-assign-details.pic file existed.\n" %( self.__class__.__name__, sys._getframe().f_code.co_name) )
        ccAssignDataStore=p_ccAssignObj.createDataStore(p_ccAssignRsltsDict,p_exactMatchOption=True)

        return ccAssignDataStore
    

    def __generateInstanceLevelData(self,p_ccAssignDataStore,p_bReusingPriorDataStore,p_semaphore):
        """ Generate report material that will support 2D,3D renderings.
            Also, populate ChemCompAssignDataStore with datapoints required for
            instance-level browsing.
            
            Delegates processing to a child process
            
            :Params:           
                ``p_ccAssignDataStore``: ChemCompAssignDataStore object
                ``p_bReusingPriorDataStore``: boolean flag indicating whether there was
                                                a pre-existing datastore for us to reuse. 
            
            :Helpers:
            
                + wwpdb.apps.ccmodule.reports.ChemCompReports.ChemCompReport
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore
        """
        instIdLst = []
        depId       = str(self.__reqObj.getValue("identifier")).upper()
        wfInstId    = str(self.__reqObj.getValue("instance")).upper()
        sessionId   = self.__reqObj.getSessionId()
        fileSource  = str(self.__reqObj.getValue("filesource")).lower()
        #
        className = self.__class__.__name__
        methodName = sys._getframe().f_code.co_name
        #
        if (self.__verbose):
                self.__lfh.write("++%s.%s() Just before fork to create child process w/ separate log generated in session directory.\n"%(className, methodName) )
                self.__lfh.flush()
        pid = os.fork()
        if pid == 0:
            #
            sys.stdout = RedirectDevice()
            sys.stderr = RedirectDevice()
            os.setpgrp()
            os.umask(0)
            #
            # redirect the logfile
            self.__openChildProcessLog("RPRT_CHLD_PROC")            
            sys.stdout = self.__lfh
            sys.stderr = self.__lfh
            #
            if (self.__verbose):
                self.__lfh.write("+++%s.%s() Child Process: PID# %s\n" %(className, methodName, os.getpid()) )
            #
            try:
                ccA=ChemCompAssign(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
                    
                instIdLst = p_ccAssignDataStore.getAuthAssignmentKeys()
                if( self.__verbose ):
                    for i in instIdLst:
                        if( self.__verbose ):
                            self.__lfh.write("+++%s.%s() -- instIdLst item %30s\n" %(className, methodName, i) )
                        
                if( len(instIdLst) > 0):
                    ccIdAlrdySeenLst=[]
                    fitTuplDict={}
                    
                    for instId in instIdLst:
                        
                        authAssgndId = p_ccAssignDataStore.getAuthAssignment(instId)
                        topHitCcId = p_ccAssignDataStore.getBatchBestHitId(instId)
                        
                        if authAssgndId not in fitTuplDict:
                            fitTuplDict[authAssgndId] = {}
                            fitTuplDict[authAssgndId]["alignList"] = []
                            fitTuplDict[authAssgndId]["masterAlignRef"] = None 
                        
                        instncChemCompFilePth = os.path.join(self.__cI.get('SITE_DEPOSIT_STORAGE_PATH'),'deposit',depId,'assign',instId,instId+".cif")
                        if not os.access(instncChemCompFilePth,os.R_OK):
                            # i.e. if not in Workflow Managed context, must be in standalone dev context where we've run cc-assign search locally
                            # and therefore produced cc-assign results file in local session area
                            instncChemCompFilePth = os.path.join(self.__sessionPath,'assign',instId,instId+".cif")                        
                        #
                        
                        # First generate report material for this experimental lig instance
                        self.__genRprtMaterialForLgndInstance(instId,instncChemCompFilePth)
                        
                        # gather data required for generating 2D images for this experimental lig instance
                        self.__imagingSetupForLgndInstance(instId,authAssgndId,fitTuplDict,instncChemCompFilePth)
                        
                        # gather data required for generating 2D images for *Author Assigned* ID of this lig instance
                        if( not authAssgndId in ccIdAlrdySeenLst ):
                            
                            if( self.__isValid_Simple(authAssgndId) ):
                                self.__genRprtMaterialForTopHit(authAssgndId)
                                self.__imagingSetupForTopHit(authAssgndId,authAssgndId,fitTuplDict)
                                ccIdAlrdySeenLst.append(authAssgndId)
                            
                        if( topHitCcId.lower() != 'none' ) and ( not topHitCcId in ccIdAlrdySeenLst ):
                        
                            # generate report material for TOP HIT dictionary reference to which this lig instance is mapped
                            self.__genRprtMaterialForTopHit(topHitCcId)
                            
                            # gather data required for generating 2D images for TOP HIT of this lig instance
                            self.__imagingSetupForTopHit(authAssgndId,topHitCcId,fitTuplDict)
                            
                            ccIdAlrdySeenLst.append(topHitCcId)
                        
                        
                    # Then generate aligned 2D images using first instance of experimental ligand group as reference orientation
                    self.__genAligned2dImages(fitTuplDict)
                    self.__postSemaphore(p_semaphore,"OK")
                    self.__lfh.flush()
                    
                    # 2013-06-26, RPS -- trying this here to see if it introduces improvement in response time
                    if( p_bReusingPriorDataStore is not True ):
                        # i.e. if we are spawning a brand new datastore from scratch let's go ahead and
                        # parse the instance-level chem-comp cif files and top hit reference chem comp cif files
                        # for data needed in instance browser
                        ccA.getDataForInstncSrch(instIdLst,p_ccAssignDataStore)
                        p_ccAssignDataStore.dumpData(self.__lfh);
                        p_ccAssignDataStore.serialize()
                        
                    self.__lfh.write("+++%s.%s() -- DONE processing for child Process: PID# %s\n" %(className, methodName, os.getpid()) )
                    self.__lfh.flush()
                
            except:
                traceback.print_exc(file=self.__lfh)
                self.__lfh.write("+++%s.%s() -- Failing for child Process: PID# %s\n" %(className, methodName, os.getpid()) )
                self.__lfh.flush()
                self.__postSemaphore(p_semaphore,"FAIL")
                self.__verbose = False
                
            self.__verbose = False
            os.kill(0,signal.SIGTERM)    
            #os._exit(0)

        else:
            # we are in parent process and we will return status code to client to indicate that data processing is "running"
            self.__lfh.write("+++%s.%s() Parent Process Completed: PID# %s\n" %(className, methodName, os.getpid()) )
            self.__lfh.flush()
            return

    def __isValid_Simple(self,ccid):
        #
        className = self.__class__.__name__
        methodName = sys._getframe().f_code.co_name
        #
        pathPrefix = self.__ccConfig.getPath('chemCompCachePath')
        validationPth = os.path.join(pathPrefix,ccid[:1],ccid,ccid+'.cif')
        if (self.__verbose):
            self.__lfh.write("+++%s.%s() ---- validating CC ID %s against path: %s\n" % (className, methodName,ccid,validationPth) )
        if not os.access(validationPth, os.R_OK):
            if (self.__verbose):
                self.__lfh.write("+++%s.%s() ---- INVALID -- CC ID %s has no corresponding dict ref file at %s\n" % (className, methodName,ccid,validationPth) )
            return False
        #
        return True

    def __genRprtMaterialForLgndInstance(self,p_instId,p_chemCompFilePathAbs):
        #
        className = self.__class__.__name__
        methodName = sys._getframe().f_code.co_name
        #
        ccCoordRprt=ChemCompReport(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
        ccCoordRprt.setFilePath(p_chemCompFilePathAbs,p_instId)
        if( self.__verbose ):
            self.__lfh.write("+++%s.%s() -- before call to doReport and p_instId is: %s\n" %(className, methodName, p_instId) )
        ccCoordRprt.doReport(type='exp',ccAssignPthMdfier=p_instId)
        rDict=ccCoordRprt.getReportFilePaths()
        for k,v in rDict.items():
            if( self.__verbose ):
                self.__lfh.write("+++%s.%s() -- Coordinate file reporting -- Key %30s value %s\n" %(className,methodName,k,v) )

    def __imagingSetupForLgndInstance(self,p_instId,p_authAssgndId,p_fitTuplDict,p_chemCompFilePathAbs):
        #
        className = self.__class__.__name__
        methodName = sys._getframe().f_code.co_name
        #
        instImgOutputPth = os.path.join(self.__sessionPath,'assign',p_instId+".svg")
        if p_fitTuplDict[p_authAssgndId]["masterAlignRef"] is None:
            p_fitTuplDict[p_authAssgndId]["masterAlignRef"] = (p_instId,p_chemCompFilePathAbs,instImgOutputPth)
        else:
            p_fitTuplDict[p_authAssgndId]["alignList"].append( (p_instId,p_chemCompFilePathAbs,instImgOutputPth) )

    def __genRprtMaterialForTopHit(self,p_topHitCcId):
        #
        className = self.__class__.__name__
        methodName = sys._getframe().f_code.co_name
        #
        ccReferncRprt=ChemCompReport(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
                        
        ccReferncRprt.setDefinitionId(definitionId=p_topHitCcId.lower())
        ccReferncRprt.doReport(type='ref',ccAssignPthMdfier=p_topHitCcId)
        rD=ccReferncRprt.getReportFilePaths()
        for k,v in rD.items():
            if( self.__verbose ):
                self.__lfh.write("+++%s.%s() -- Reference file reporting -- Key %30s value %s\n" %(className,methodName,k,v) )
                    
    def __imagingSetupForTopHit(self,p_authAssgndId,p_topHitCcId,p_fitTuplDict):
        #
        className = self.__class__.__name__
        methodName = sys._getframe().f_code.co_name
        #
        pathPrefix = self.__ccConfig.getPath('chemCompCachePath')
        chemCompCifPth = os.path.join(pathPrefix,p_topHitCcId[:1],p_topHitCcId,p_topHitCcId+'.cif')
        
        if( os.access(chemCompCifPth, os.R_OK) ):
            defImgOutputPth = os.path.join(self.__sessionPath,'assign',p_topHitCcId+".svg")
            
            if p_authAssgndId not in p_fitTuplDict:
                p_fitTuplDict[p_authAssgndId] = {}
                p_fitTuplDict[p_authAssgndId]["alignList"] = []
                p_fitTuplDict[p_authAssgndId]["masterAlignRef"] = None
            #
            p_fitTuplDict[p_authAssgndId]["alignList"].append( (p_topHitCcId,chemCompCifPth,defImgOutputPth) )
        else:
            self.__lfh.write("+++%s.%s() -- WARNING: PROBLEM accessing chemCompCifPth at: %s\n" %(className,methodName,chemCompCifPth) )
        
    def __genAligned2dImages(self,p_fitTuplDict):
        #
        className = self.__class__.__name__
        methodName = sys._getframe().f_code.co_name
        #
        self.__lfh.write("+++%s.%s() -- STARTING and p_fitTuplDict is %r\n" %(className, methodName, p_fitTuplDict) )
        
        redoCcidLst = []    
        assignPath = os.path.join(self.__sessionPath,'assign')
        
        for ccid in p_fitTuplDict:
            self.__lfh.write("+++%s.%s() -- Top of LOOP iteration through ccids in p_fitTuplDict and current ccid is %s\n" %(className, methodName, ccid) )
            
            try:
                if( p_fitTuplDict[ccid]["alignList"] is not None and len(p_fitTuplDict[ccid]["alignList"]) > 0 ):
                    fileListPath = os.path.join(assignPath,'alignfilelist_'+ccid+'.txt')
                    logPath = os.path.join(assignPath,'alignfile_'+ccid+'.log')
                    ofh=open(fileListPath,'w')
                    ofh.write('ASSIGN_PATH:%s\n'%assignPath)
                    ofh.write('MASTER_ID:%s\nMASTER_DEF_PTH:%s\nMASTER_IMG_PTH:%s\n'%(p_fitTuplDict[ccid]["masterAlignRef"][0],p_fitTuplDict[ccid]["masterAlignRef"][1],p_fitTuplDict[ccid]["masterAlignRef"][2]) )
                        
                    for (thisId,fileDefPath,imgFilePth) in p_fitTuplDict[ccid]["alignList"]:
                        ofh.write('ALIGN_ID:%s\nALIGN_DEF_PTH:%s\nALIGN_IMG_PTH:%s\n'%(thisId,fileDefPath,imgFilePth) )
                        
                    ofh.close()                
                    
                    command = "python -m wwpdb.apps.ccmodule.reports.ChemCompAlignImages -v -i %s -f %s"%(ccid,fileListPath)
                    returnCode = self.__runTimeout(command=command, logPath=logPath)
                    
                    if( returnCode is None or returnCode != 0 ):
                        self.__lfh.write("\n+++%s.%s() -- WARNING: had to revisit image generation for ccid: %s\n\n" %(className, methodName, ccid) )
                        redoCcidLst.append(ccid)
                else:
                    # there is no match for the ccid, no valid auth assigned id, and there is only one instance of the experimental ccid --> i.e. there will only be one image to generate
                    redoCcidLst.append(ccid)
                
            except:
                traceback.print_exc(file=self.__lfh)
                
            # safeguard measure required if above process fails silently
            # so we check to see if the master image was not generated and add the ccid to the redo list
            masterImgPth = p_fitTuplDict[ccid]["masterAlignRef"][2]
            if( not os.access( masterImgPth, os.F_OK ) ):
                self.__lfh.write("\n+++%s.%s() -- WARNING: could not find expected master image file at %s, so had to revisit image generation for ccid: %s\n\n" %(className, methodName, masterImgPth, ccid) )
                redoCcidLst.append(ccid)
        
        # generate non-aligned images for those cases where exception occurred due to timeout/error
        pathList = []
        for ccid in redoCcidLst:
            try:
                imgTupl = p_fitTuplDict[ccid]["masterAlignRef"]
                pathList.append( imgTupl )
                
                for anImgTupl in p_fitTuplDict[ccid]["alignList"]:
                    pathList.append( anImgTupl )
                
                logPath = os.path.join(assignPath,'genimagefile_'+ccid+'.log')
                
                for title,path,imgPth in pathList:
                    
                    command = "python -m wwpdb.apps.ccmodule.reports.ChemCompGenImage -v -i %s -f %s -o %s"%(title,path,imgPth)
                    returnCode = self.__runTimeout(command=command, logPath=logPath)
                    
                    if( returnCode is None or returnCode != 0 ):
                        self.__lfh.write("\n+++%s.%s() -- WARNING: image generation failed for: %s\n\n" %(className, methodName, imgPth) )
                    
            except:
                traceback.print_exc(file=self.__lfh)
        
        return
    
    def __runTimeout(self, command, timeout=10, logPath=None):
        """ Execute the input command string (sh semantics) as a subprocess with a timeout.
    
    
        """
        className = self.__class__.__name__
        methodName = sys._getframe().f_code.co_name
        #
        self.__lfh.write("+++%s.%s() -- STARTING with time out set at %d (seconds)\n" %(className, methodName, timeout) )
        
        start = datetime.datetime.now()
        cmdfile=os.path.join(self.__sessionPath,'assign','timeoutscript.sh')
        # below done when permissions problems arose in attempts to run timeoutscript.sh
        #sVal = str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
        #cmdfile=os.path.join('/tmp','timeoutscript_'+sVal+'.sh')
        ofh=open(cmdfile,'w')
        ofh.write("#!/bin/sh\n")
        ofh.write("source %s/init/env.sh -s %s -l %s\n" % (self.__siteConfigDir, self.__siteId, self.__siteLoc))
        ofh.write(command)
        ofh.write("\n#\n")
        ofh.close()
        st = os.stat(cmdfile)
        os.chmod(cmdfile, 0777)
        
        try:
            self.__lfh.write("+++%s.%s() -- running command %r in cmdfile %s \n" %(className, methodName, command, cmdfile) )
            process = Popen(cmdfile, stdout=PIPE, stderr=PIPE, shell=False,close_fds=True,preexec_fn=os.setsid)
            while process.poll() == None:
                
                time.sleep(0.1)
                now = datetime.datetime.now()
                if (now - start).seconds> timeout:
                    #os.kill(-process.pid, signal.SIGKILL)
                    os.killpg(process.pid, signal.SIGKILL)
                    os.waitpid(-1, os.WNOHANG)
                    self.__lfh.write("+++%s.%s() -- Execution terminated by timeout %d (seconds)\n" %(className, methodName, timeout) )
                    if logPath is not None:
                        ofh=open(logPath,'a')
                        ofh.write("+++%s.%s() -- Execution terminated by timeout %d (seconds)\n" %(className, methodName, timeout) )
                        ofh.close()
                    return None
        except:
            traceback.print_exc(file=self.__lfh)
            
        output = process.communicate()
        self.__lfh.write("+++%s.%s() -- completed with stdout data %r\n" %(className, methodName, output[0]) )
        self.__lfh.write("+++%s.%s() -- completed with stderr data %r\n" %(className, methodName, output[1]) )
        #self.__lfh.write("+++%s.%s() -- completed with return stdout.read() %r\n" %(className, methodName, process.stdout.read()) )
        self.__lfh.write("+++%s.%s() -- completed with return code %r\n" %(className, methodName, process.returncode) )
        
        os.remove(cmdfile)
        
        return process.returncode

        
    def __importDepositorFiles(self,p_ccAssignDataStore):
        """ Import any files that were previously uploaded/generated by the depositor
            
            :Params:           
                ``p_ccAssgnDataStr``: ChemCompAssignDataStore object
            
            :Helpers:
            
                + wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore
        """
        instIdLst = []
        depId       = str(self.__reqObj.getValue("identifier")).upper()
        wfInstId    = str(self.__reqObj.getValue("instance")).upper()
        sessionId   = self.__reqObj.getSessionId()
        fileSource  = str(self.__reqObj.getValue("filesource")).lower()
        #
        className = self.__class__.__name__
        methodName = sys._getframe().f_code.co_name
        #
        if( self.__verbose ):
            self.__lfh.write("+%s.%s() ------------------------------ STARTING ------------------------------\n" %(className, methodName) )
        #
        contentTypeDict = self.__cI.get('CONTENT_TYPE_DICTIONARY')
        #
        for ligId in p_ccAssignDataStore.getGlbllyRslvdGrpList():
            if( self.__verbose ):
                self.__lfh.write("+%s.%s() - Inside loop for processing ligand groups that had been previously addressed.\n" %(className, methodName) )
                
            try:
            
                # technically speaking, sdf files are not "uploaded" but are generated by any
                # sketches created by depositor if using the marvinsketch editor provided in the UI
                # for the time-being the sdf files are being handled as if they were uploaded
                 
                # check if marvinsketch was used to create an sdf file
                sbmttdStrctrData = p_ccAssignDataStore.getDpstrSubmitChoice(ligId)
                if( sbmttdStrctrData is not None and sbmttdStrctrData == 'sketch' ):
                    defntnFlName = ligId+'-sketch.sdf'
                    defntnFlPth = os.path.join(self.__sessionPath,defntnFlName)
                    wfFlPth = p_ccAssignDataStore.getDpstrSketchFileWfPath(ligId,defntnFlName,'sdf')
                    if( wfFlPth is not None and os.access(wfFlPth,os.R_OK) ):
                        shutil.copyfile( wfFlPth, defntnFlPth )
                        if( self.__verbose ):
                            self.__lfh.write("+%s.%s() - Copied depositor sketch file from workflow path '%s' to session path as '%s'.\n" %(className, methodName, wfFlPth, defntnFlPth) )
                    else:
                        if( self.__verbose ):
                            self.__lfh.write("+%s.%s() - ACCESS PROBLEM when attempting to copy depositor sketch file from workflow path '%s' to session path as '%s'.\n" %(className, methodName, wfFlPth, defntnFlPth) )
                
                # then check if any files were uploaded
                dpstrUploadFilesDict = p_ccAssignDataStore.getDpstrUploadFilesDict()
                if( ligId in dpstrUploadFilesDict ):
                    for fileType in dpstrUploadFilesDict[ligId]:
                        if( fileType in contentTypeDict['component-image'][0] ):
                            for fileName in dpstrUploadFilesDict[ligId][fileType].keys():
                                imgFlPth = os.path.join(self.__sessionPath,fileName)
                                wfImgFlPth = p_ccAssignDataStore.getDpstrUploadFileWfPath(ligId,fileType,fileName)
                                if( wfImgFlPth is not None and os.access(wfImgFlPth,os.R_OK) ):
                                    shutil.copyfile( wfImgFlPth, imgFlPth )
                                    if( self.__verbose ):
                                        self.__lfh.write("+%s.%s() - Copied depositor component image file from workflow path '%s' to session path as '%s'.\n" %(className, methodName, wfImgFlPth, imgFlPth ) )
                                else:
                                    if( self.__verbose ):
                                        self.__lfh.write("+%s.%s() - ACCESS PROBLEM when attempting to copy component image file from workflow path '%s' to session path as '%s'.\n" %(className, methodName, wfImgFlPth, imgFlPth) )                                

                        elif( fileType in contentTypeDict['component-definition'][0] ):
                            for fileName in dpstrUploadFilesDict[ligId][fileType].keys():
                                defntnFlPth = os.path.join(self.__sessionPath,fileName)
                                wfDefFlPth = p_ccAssignDataStore.getDpstrUploadFileWfPath(ligId,fileType,fileName)
                                if( wfDefFlPth is not None and os.access(wfDefFlPth,os.R_OK) ):
                                    shutil.copyfile( wfDefFlPth, defntnFlPth )
                                    if( self.__verbose ):
                                        self.__lfh.write("+%s.%s() - Copied depositor component definition file from workflow path '%s' to session path as '%s'.\n" %(className, methodName, wfDefFlPth, defntnFlPth ) )
                                else:
                                    if( self.__verbose ):
                                        self.__lfh.write("+%s.%s() - ACCESS PROBLEM when attempting to copy component definition file from workflow path '%s' to session path as '%s'.\n" %(className, methodName, wfDefFlPth, defntnFlPth) )
                                    
            except:
                if (self.__verbose):
                    self.__lfh.write("+%s.%s() ----- WARNING ----- processing failed id:  %s\n" %(className, methodName) )
                    traceback.print_exc(file=self.__lfh)
                    self.__lfh.flush()                          
    
    def __exitLigMod(self,mode):
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
        if (mode == 'completed'):
            state = "closed(0)"
        elif (mode == 'unfinished'):
            state = "waiting"
        #
        bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        sessionId   = self.__sessionId
        depId  =  self.__reqObj.getValue("identifier")
        instId =  self.__reqObj.getValue("instance")
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
        rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)        
        #
        # Update WF status database and persist chem comp assignment states -- ONLY if lig module was running in context of wf-engine
        #
        if( bIsWorkflow ):
            try:
                bOkay = self.__saveLigModState(mode)
                if( bOkay ):
                    '''
                    bSuccess = self.__updateWfTrackingDb(state)
                    if( not bSuccess ):
                        rC.setError(errMsg="+ChemCompWebAppLiteWorker.__exitLigMod() - TRACKING status, update to '%s' failed for session %s \n" % (state,sessionId) )
                    '''
                else:
                    rC.setError(errMsg="+ChemCompWebAppLiteWorker.__exitLigMod() - problem saving log module state")
                
            except:
                if (self.__verbose):
                    self.__lfh.write("+ChemCompWebAppLiteWorker.__exitLigMod() - problem saving lig module state")
                traceback.print_exc(file=self.__lfh)
                rC.setError(errMsg="+ChemCompWebAppLiteWorker.__exitLigMod() - exception thrown on saving lig module state")                  
        else:
            try:
                bOkay = self.__saveLigModState(mode)
                if( not bOkay ):
                    rC.setError(errMsg="+ChemCompWebAppLiteWorker.__exitLigMod() - problem saving lig module state")
                
            except:
                if (self.__verbose):
                    self.__lfh.write("+ChemCompWebAppLiteWorker.__exitLigMod() - problem saving lig module state")
                traceback.print_exc(file=self.__lfh)
                rC.setError(errMsg="+ChemCompWebAppLiteWorker.__exitLigMod() - exception thrown on saving lig module state")
                             
            if (self.__verbose):
                    self.__lfh.write("+ChemCompWebAppLiteWorker.__exitLigMod() - Not in WF environ so skipping status update to TRACKING database for session %s \n" % sessionId)
        #
        return rC

    def __updateWfTrackingDb(self,p_status):
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
        sessionId   = self.__sessionId
        depId  =  self.__reqObj.getValue("identifier").upper()
        instId =  self.__reqObj.getValue("instance")
        classId=  str(self.__reqObj.getValue("classID")).lower()
        #
        try:
            wft=WfTracking(verbose=self.__verbose,log=self.__lfh)
            wft.setInstanceStatus(depId=depId,
                                  instId=instId,
                                  classId=classId,
                                  status=p_status)
            bSuccess = True
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppLiteWorker.__updateWfTrackingDb() -TRACKING status updated to '%s' for session %s \n" % (p_status,sessionId))
        except:
            bSuccess = False
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppLiteWorker.__updateWfTrackingDb() - TRACKING status, update to '%s' failed for session %s \n" % (p_status,sessionId))
            traceback.print_exc(file=self.__lfh)                    
        #
        return bSuccess

        
    def __saveLigModState(self,mode):
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
                + wwpdb.wwpdb.utils.wf.DataReference.DataFileReference
                + wwpdb.apps.ccmodule.chem.ChemCompAssign
                    
            :Returns:
                ``ok``: boolean indicating success/failure of the save operation
        """
        pathDict={}
        ###### pickle file ######
        pathDict['picFileDirPth'] = None
        pathDict['picFileFlPth'] = None
        ###### depositor info file ######
        pathDict['dpstrInfoFileDirPth']=None
        pathDict['dpstrInfoFileFlPth']=None
        ###### depositor progress file ######
        pathDict['dpstrPrgrssFileDirPth']=None
        pathDict['dpstrPrgrssFileFlPth']=None
        #
        fileSource = str(self.__reqObj.getValue("filesource")).strip().lower()
        depId  =  self.__reqObj.getValue("identifier")
        instId =  self.__reqObj.getValue("instance")
        #classId = self.__reqObj.getValue("classid")
        sessionId=self.__sessionId
        bSuccess = False
        #
        # determine if currently operating in Workflow Managed environment
        bIsWorkflow = self.__isWorkflow()
        #
        if( bIsWorkflow ):
            depId = depId.upper()
        else:
            depId = depId.lower()
        #
        if fileSource:
            ccE=ChemCompDataExport(self.__reqObj,verbose=self.__verbose,log=self.__lfh)
            
            ##################################### chem comp depositor info file #################################################
            pathDict['dpstrInfoFileFlPth'] = ccE.getChemCompDpstrInfoFilePath()
            
            if( pathDict['dpstrInfoFileFlPth'] ):
                pathDict['dpstrInfoFileDirPth'] = ( os.path.split(pathDict['dpstrInfoFileFlPth']) )[0]
                     
                #
                if (self.__verbose):
                    self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() CC depositor info export directory path: %s\n" % pathDict['dpstrInfoFileDirPth'])
                    self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() CC depositor info export file      path: %s\n" % pathDict['dpstrInfoFileFlPth'])
            else:
                self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() ---- WARNING ---- No path obtained for CC depositor info export file, id %s \n" % depId )
            
            
            #######################################################################################################################################
            # Below files are always being updated, i.e. not just on "completed" status but on "intermittent" and "unfinished" states as well.
            #######################################################################################################################################
                
            ##################################### pickle file #################################################
            pathDict['picFileFlPth'] = ccE.getChemCompAssignDetailsFilePath()
            
            if( pathDict['picFileFlPth'] ):
                pathDict['picFileDirPth'] = ( os.path.split(pathDict['picFileFlPth']) )[0]
            
                if (self.__verbose):
                    self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() CC assign details export directory path: %s\n" % pathDict['picFileDirPth'])
                    self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() CC assign details export file      path: %s\n" % pathDict['picFileFlPth'])
            else:
                self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() ---- WARNING ---- No path obtained for CC assign details export file, id %s \n" % depId )
                
            ##################################### chem comp depositor progress file #################################################
            pathDict['dpstrPrgrssFileFlPth']=os.path.join(self.__cI.get('SITE_DEPOSIT_STORAGE_PATH'),'deposit',depId,'cc-dpstr-progress')
            pathDict['dpstrPrgrssFileDirPth'] = ( os.path.split(pathDict['dpstrPrgrssFileFlPth']) )[0]
            
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() CC assign dpstr progress directory path: %s\n" % pathDict['dpstrPrgrssFileDirPth'])
                self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() CC assign dpstr progress file      path: %s\n" % pathDict['dpstrPrgrssFileFlPth'])
                            
        else:
            self.__lfh.write("+ChemCompWebAppLiteWorker.__saveLigModState() - processing undefined | filesource %r \n" % fileSource)                             

        #########################################################################################################################################################
        #    Call on ChemCompAssign to save current state of ligand assignments 
        #########################################################################################################################################################
        ccA=ChemCompAssign(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
        #   
        bSuccess=ccA.saveState( pathDict, context="deposit", mode=mode )
        #
        
        # below added to support convenience of assessing results during unit testing
        if( mode != "intermittent" ):
            bIsWorkflow = self.__isWorkflow()
            ccAD=ChemCompAssignDepictLite(self.__reqObj,self.__verbose,self.__lfh)
            ccAD.setSessionPaths(self.__reqObj)
            ccAD.doRender_ResultFilesPage(self.__reqObj,bIsWorkflow)
        #
        return bSuccess

    def __getSession(self):
        """ Join existing session or create new session as required.
        """
        #
        self.__sObj=self.__reqObj.newSessionObj()
        self.__sessionId=self.__sObj.getId()
        self.__sessionPath=self.__sObj.getPath()
        self.__rltvSessionPath=self.__sObj.getRelativePath()
        if (self.__verbose):
            self.__lfh.write("------------------------------------------------------\n")                    
            self.__lfh.write("+ChemCompWebAppLite.__getSession() - creating/joining session %s\n" % self.__sessionId)
            #self.__lfh.write("+ChemCompWebAppLite.__getSession() - workflow storage path    %s\n" % self.__workflowStoragePath)
            self.__lfh.write("+ChemCompWebAppLite.__getSession() - session path %s\n" % self.__sessionPath)            

    def __isFileUpload(self,fileTag='file'):
        """ Generic check for the existence of request paramenter "file".
        """ 
        # Gracefully exit if no file is provide in the request object - 
        fs=self.__reqObj.getRawValue(fileTag)
        if ( (fs is None) or (type(fs) == types.StringType) or (type(fs) == types.UnicodeType) ):
            return False
        return True

    
    def _uploadDpstrFile(self,p_fileTag,p_ccADS):
        if (self.__verbose):
            self.__lfh.write("+%s.%s() Starting now\n"%(self.__class__.__name__, sys._getframe().f_code.co_name) )
        #
        success = False
        authAssgndGrp   = str(self.__reqObj.getValue("auth_assgnd_grp"))
        #
        ok=self.__uploadFile(p_fileTag)
        #
        if ok:
            fileName = str(self.__reqObj.getValue("UploadFileName"))
            #
            if (self.__verbose):
                self.__lfh.write("+%s.%s() fileName: %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, fileName) )
            
            # when obtaining filetype, we force extension filetype to lowercase so that all handling done consistently in lowercase
            fileType = os.path.splitext(fileName)[1].strip(".").lower() if len( os.path.splitext(fileName)[1] ) > 1 else "n/a" 
            #
            if (self.__verbose):
                self.__lfh.write("+%s.%s() fileType: %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, fileType) )
            
            success = p_ccADS.setDpstrUploadFile(authAssgndGrp,fileType,fileName)
            if success:
                self.__lfh.write("+%s.%s() successfully updated data store for file upload action for %s\n" %(self.__class__.__name__, sys._getframe().f_code.co_name, fileName) )
                p_ccADS.serialize()
                p_ccADS.dumpData(self.__lfh);
        #
        return success

    def __uploadFile(self,fileTag='file'):
        #
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppLite.__uploadFile() - file upload starting\n")
        fs=None
        fNameInput=""
        #
        # Copy upload file to session directory - 
        try:
            fs=self.__reqObj.getRawValue(fileTag)
            fNameInput = str(fs.filename)
            #
            # Need to deal with some platform issues -
            #
            if (fNameInput.find('\\') != -1) :
                # likely windows path -
                fName=ntpath.basename(fNameInput)
            else:
                fName=os.path.basename(fNameInput)
                
            #
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppLite.__loadDataFileStart() - upload file %s\n" % fs.filename)
                self.__lfh.write("+ChemCompWebAppLite.__loadDataFileStart() - base file   %s\n" % fName)                
            #
            # Store upload file in session directory - 

            fPathAbs=os.path.join(self.__sessionPath,fName)
            ofh=open(fPathAbs,'w')
            ofh.write(fs.file.read())
            ofh.close()
            self.__reqObj.setValue("UploadFileName",fName)
            self.__reqObj.setValue("filePath",fPathAbs)
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppLite.__uploadFile() Uploaded file %s\n" % str(fName) )
        except:
            if (self.__verbose):
                self.__lfh.write("+ChemCompWebAppLite.__uploadFile() File upload processing failed for %s\n" % str(fs.filename) )        
                traceback.print_exc(file=self.__lfh)                            

            return False
        #
        # If this is not workflow context then establish depId from filename 
        #
        if not self.__isWorkflow() and fileTag not in ["file_img","file_refdict"]:
            if fName.startswith('rcsb'):
                fId = fName[:10]
            elif fName.startswith('d_'):
                fId = fName[:8]            
            else:
                fId='000000'
                if (self.__verbose):
                    self.__lfh.write("+ChemCompWebAppLite.__uploadFile() using default identifier for %s\n" % str(fName) ) 
    
            self.__reqObj.setValue("identifier",fId)
        #
        self.__reqObj.setValue("fileName",fName)
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppLite.__uploadFile() identifier %s\n" % self.__reqObj.getValue("identifier"))
        return True


    def __setSemaphore(self):
        sVal = str(time.strftime("TMP_%Y%m%d%H%M%S", time.localtime()))
        self.__reqObj.setValue('semaphore',sVal)
        return sVal

    def __openSemaphoreLog(self,semaphore="TMP_"):
        sessionId  =self.__reqObj.getSessionId()
        fPathAbs=os.path.join(self.__sessionPath,semaphore+'.log')
        self.__lfh=open(fPathAbs,'w')

    def __closeSemaphoreLog(self,semaphore="TMP_"):
        self.__lfh.flush()
        self.__lfh.close()
        
    def __postSemaphore(self,semaphore='TMP_',value="OK"):
        sessionId  =self.__reqObj.getSessionId()        
        fPathAbs=os.path.join(self.__sessionPath,semaphore)
        fp=open(fPathAbs,'w')
        fp.write("%s\n" % value)
        fp.close()        
        return semaphore

    def __semaphoreExists(self,semaphore='TMP_'):
        sessionId  =self.__reqObj.getSessionId()        
        fPathAbs=os.path.join(self.__sessionPath,semaphore)
        if (os.access(fPathAbs,os.F_OK)):
            return True
        else:
            return False

    def __getSemaphore(self,semaphore='TMP_'):

        sessionId=self.__reqObj.getSessionId()        
        fPathAbs=os.path.join(self.__sessionPath,semaphore)
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppLite.__getSemaphore() - checking %s in path %s\n" % (semaphore,fPathAbs))
        try:
            fp=open(fPathAbs,'r')
            lines=fp.readlines()
            fp.close()
            sval=lines[0][:-1]
        except:
            sval="FAIL"
        return sval

    def __openChildProcessLog(self,label="TMP_"):
        sessionId  =self.__reqObj.getSessionId()        
        fPathAbs=os.path.join(self.__sessionPath,label+'.log')
        self.__lfh=open(fPathAbs,'w')
        
    def __processTemplate(self,fn,parameterDict={}):
        """ Read the input HTML template data file and perform the key/value substitutions in the
            input parameter dictionary.
            
            :Params:
                ``parameterDict``: dictionary where
                key = name of subsitution placeholder in the template and
                value = data to be used to substitute information for the placeholder
                
            :Returns:
                string representing entirety of content with subsitution placeholders now replaced with data
        """
        tPath =self.__reqObj.getValue("TemplatePath")
        fPath=os.path.join(tPath,fn)
        ifh=open(fPath,'r')
        sIn=ifh.read()
        ifh.close()
        return (  sIn % parameterDict )
    
    def __isWorkflow(self):
        """ Determine if currently operating in Workflow Managed environment
        
            :Returns:
                boolean indicating whether or not currently operating in Workflow Managed environment
        """
        #
        fileSource  = str(self.__reqObj.getValue("filesource")).lower()
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompWebAppLiteWorker.__isWorkflow() - filesource is %s\n" % fileSource)
        #
        # add wf_archive to fix PDBe wfm issue -- jdw 2011-06-30
        #
        if fileSource in ['archive','wf-archive','wf_archive','wf-instance','wf_instance', 'deposit']:
            #if the file source is any of the above then we are in the workflow manager environment
            return True
        else:
            #else we are in the standalone dev environment
            return False

class RedirectDevice:
    def write(self, s):
        pass

if __name__ == '__main__':
    sTool=ChemCompWebAppLite()
    d=sTool.doOp()
    for k,v in d.items():
        sys.stdout.write("Key - %s  value - %r\n" % (k,v))

