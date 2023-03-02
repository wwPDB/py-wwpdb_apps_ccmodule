##
# File:  ChemCompAssignDepictLite.py
# Date:  22-Aug-2012
# Updates:
#
# 2012-08-22    RPS    Created based on ChemCompAssignDepict
# 2013-02-21    RPS    Updates for ChemComp "Lite" processing --> use of "exact match" searching now replacing "id match" testing
# 2013-03-01    RPS    doRender_ResultFilesPage() added for convenience when unit testing
# 2013-03-19    RPS    corrected error in logic in doRender_ResultFilesPage() method
# 2013-04-01    RPS    corrected bug in rendering screen elements in cases where no exact match IDs found.
# 2013-04-02    RPS    Updates for improved provision of visual cues signaling update in state as depositor addresses mismatches in UI.
# 2013-04-03    RPS    Corrected handling of display of warning messages in case of ligand instance vs. case of ligand group
# 2013-04-30    RPS    Updated so that choices to turn on/off 3D and 2D visualization are not provided for ligand instances consisting of only a single atom.
# 2013-06-13    RPS    Updates for improved behavior of "Commit" button when user chooses to accept exact match ID over originally provided ID.
# 2013-06-25    RPS    doRender_InstanceProfile() updated to ensure server-side path exists for generation of instance profile html.
# 2013-07-16    RPS    doRender_HandleLigndMsmtchSection() updated to display empty string instead of default cif value of "?"
# 2013-07-22    RPS    Support for providing confirmation list of files uploaded by depositor.
# 2013-10-10    RPS    Addressed changes in 2D image generation, so that need to reference "noh" version of gif for "no hydrogens" version.
# 2013-10-15    RPS    Improved verbiage for instructions to depositors.
# 2013-11-19    RPS    Removed obsolete logic for handling of invalid author-assigned ChemComp IDs. Previously used "invalidLigId" flag
#                        to help determine how to render UI when there was *perfect* match or not. But slightly less rigorous matching criteria
#                        used now so can eliminate use of this flag and instead simply check whether there was a best hit or not.
# 2013-12-09    RPS    Updated for display of 2D images that are now aligned.
# 2013-11-12    RPS    Introduced changes for non-applet visualization.
# 2014-01-22    RPS    Updated doRender_InstanceBrwsr() to provide navigation buttons at bottom of screen in instance level view
# 2014-03-19    RPS    Instituted workaround to allow handling of service URLs with custom prefixes.
# 2014-05-21    RPS    Fix for confusing use of "exact_match_ccid" when some instances of given Ligand match while others don't
# 2014-06-10    RPS    Updated setting of default for hndle_msmtch_tophit_id.
# 2014-06-23    RPS    Updates in support of providing more elaborate choices for choosing an alternate Ligand ID(originally proposed ID vs.
#                        one of the possible exact match IDs for cases where some ligand instances have differing matches).
# 2014-10-31    RPS    Support for providing 2D image of author proposed Ligand ID in "handle mismatch" section of UI, on hover over of the ID.
# 2016-06-28    RPS    Synchronizing front end with list of accepted file types for uploaded chemical image and definition files.
# 2017-02-03    RPS    Updated to support capture of data for ligands as "focus of research"
# 2017-02-07    RPS    Tweaks to support capture of data for ligands as "focus of research"
# 2017-02-08    RPS    Tweaks to button labels/behavior for ligands as "focus of research"
# 2017-02-13    RPS    Updates to distinguish between ligandIDs that were simply selected as focus of research vs those for which data was actually provided.
#                        Obtaining dropdown options for binding assay measurement type from pdbx_binding_assay.assay_value_type via cif dictionary
# 2017-02-14    RPS    Tweak for behavior of checkbox used to select HOH for research focus
# 2017-02-15    RPS    Removing "Save (and come back later) button which has become obsolete.
# 2017-02-16    RPS    doRender_ResearchDataCapture() updated to support enabling of controls in two phases
# 2017-02-17    RPS    doRender_ResearchDataCapture() updated to remove chem comp ID placeholder in details field. "Undo" replaced with "Edit" for button labels.
# 2017-03-27    RPS    Disabling recent updates related to capturing binding assay data for ligands of research interest (until requirements refined).
# 2017-06-14    RPS    doRender_LigSummaryContent() updated so that no longer generating "All" checkbox used to select all ligands for focus of research.
##
"""
Create HTML depiction chemical component assignment files.

"""
__docformat__ = "restructuredtext en"
__author__ = "Raul Sala"
__email__ = "rsala@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import os
import sys
import inspect

from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
from wwpdb.apps.ccmodule.depict.ChemCompDepict import ChemCompDepict
from wwpdb.apps.ccmodule.chem.ChemCompAssign import ChemCompAssign
# from wwpdb.apps.ccmodule.chem.PdbxChemCompAssign import PdbxCategoryDefinition
from wwpdb.apps.ccmodule.io.ChemCompAssignDataStore import ChemCompAssignDataStore
from wwpdb.utils.config.ConfigInfo import ConfigInfo
from pathlib import Path
from wwpdb.io.locator.PathInfo import PathInfo


class ChemCompAssignDepictLite(ChemCompDepict):
    """ Class responsible for generating HTML depictions of
        chemical component search results for the Common Tool Deposition UI.

    """
    _CC_REPORT_DIR = 'cc_analysis'
    _CC_ASSIGN_DIR = 'assign'
    _CC_HTML_FILES_DIR = 'html'

    def __init__(self, p_reqObj, verbose=False, log=sys.stderr):
        """

         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        super(ChemCompAssignDepictLite, self).__init__(verbose, log)
        self.__verbose = verbose
        self.__lfh = log
        self.__debug = False
        self.__reqObj = p_reqObj
        self.__depId = "D_0" if self.__reqObj.getValue("identifier") in [None, 'TMP_ID'] else str(self.__reqObj.getValue("identifier")).upper()
        #
        # self.__cDict = PdbxCategoryDefinition._cDict
        #
        # self.__noDisplayList = ['']
        #
        # self.__pathGlblVwTmplts = "templates/workflow_ui/global_view"
        # self.__pathInstncsVwTmplts = " templates/workflow_ui/instances_view"
        # self.__pathSnglInstcTmplts = self.__pathInstncsVwTmplts + "/single_instance"
        # self.__pathSnglInstcCmprTmplts = self.__pathSnglInstcTmplts + "/comparison_view"
        # self.__pathSnglInstcJmolTmplts = self.__pathSnglInstcCmprTmplts + "/jmol"
        #
        # self.__pathAllInstcs = "templates/workflow_ui/instances_view/all_instances"
        # self.__pathAllInstncsCmprTmplts = self.__pathAllInstcs + "/comparison_view"
        # self.__pathAllInstncsJmolTmplts = self.__pathAllInstncsCmprTmplts + "/jmol"
        # paths to templates used for the ccmodule_lite UI
        self.__pathCCliteGlblVwTmplts = "templates/workflow_ui/global_view"
        self.__pathCCliteInstncsVwTmplts = "templates/workflow_ui/instances_view"
        self.__pathCCliteSnglInstcTmplts = self.__pathCCliteInstncsVwTmplts + "/single_instance"
        self.__pathCCliteSnglInstcCmprTmplts = self.__pathCCliteSnglInstcTmplts + "/comparison_view"
        self.__pathCCliteSnglInstcJmolTmplts = self.__pathCCliteSnglInstcCmprTmplts + "/jmol"
        #
        self.__pathCCliteAllInstcs = "templates/workflow_ui/instances_view/all_instances"
        self.__pathCCliteAllInstncsCmprTmplts = self.__pathCCliteAllInstcs + "/comparison_view"
        self.__pathCCliteAllInstncsJmolTmplts = self.__pathCCliteAllInstncsCmprTmplts + "/jmol"
        #
        self.__siteId = str(self.__reqObj.getValue("WWPDB_SITE_ID"))
        self.__cI = ConfigInfo(self.__siteId)
        # self.__deployPath = self.__cI.get('SITE_DEPLOY_PATH')
        self.__siteSrvcUrlPathPrefix = self.__cI.get('SITE_SERVICE_URL_PATH_PREFIX', '')
        self.__workingRltvAssgnSessionPath = ''

        self.__alternateTopHitMarkup = '''<input id="use_exact_mtch_id_%(auth_assgnd_grp)s_%(tophit_id)s" class="c_%(auth_assgnd_grp)s addrss_msmtch use_exact_mtch_id" type="radio" name="addrss_msmtch_chc" value="use_exact_mtch_id" %(use_exact_mtch_id_checked)s %(disabled)s /><label for="use_exact_mtch_id_%(auth_assgnd_grp)s_%(tophit_id)s">Use exact match ID of <span name="%(tophit_id)s" style="color: #F00;" class="strong tophit">%(tophit_id)s</span> (<a href="http://ligand-expo.rcsb.org/pyapps/ldHandler.py?formid=cc-index-search&target=%(tophit_id)s&operation=ccid" target="_blank">See Definition</a>) instead of originally proposed ID</label><br />'''  # noqa: E501

        self.__depositPath = Path(PathInfo().getDepositPath(self.__depId)).parent
        self.__ccReportPath = os.path.join(self.__depositPath, self.__depId, self._CC_REPORT_DIR)
        # self.__depositAssignPath = os.path.join(self.__depositPath, self.__depId, self._CC_ASSIGN_DIR)
        self.__logger = self._setupLog(log)

    ################################################################################################################
    # ------------------------------------------------------------------------------------------------------------
    #      Top-level methods
    # ------------------------------------------------------------------------------------------------------------
    #

    def doRender_LigSrchSummary(self, p_reqObj, p_bIsWorkflow):
        ''' Render HTML used as starter page/container for the Deposition UI's Ligand Search Results Summary
            Once this content is in the browser, an AJAX call is made to populate the page
            with the actual assignment results content.

            :Params:

                + ``p_reqObj``: Web Request object
                + ``p_bIsWorkflow``: boolean indicating whether or not operating in Workflow Manager environment

            :Returns:
                ``oL``: output list consisting of HTML markup
        '''
        oL = []
        #
        sessionId = p_reqObj.getSessionId()
        siteId = str(p_reqObj.getValue("WWPDB_SITE_ID"))
        wfInstId = str(p_reqObj.getValue("instance")).upper()
        depId = str(p_reqObj.getValue("identifier"))
        classId = str(p_reqObj.getValue("classID")).lower()
        fileSource = str(p_reqObj.getValue("filesource")).lower()
        dataFile = str(p_reqObj.getValue("datafile"))
        tmpltPath = p_reqObj.getValue("TemplatePath")
        #
        # This is wrong - but not correcting depid vs depId
        depid = self.__formatDepositionDataId(depId, p_bIsWorkflow)  # noqa: F841 pylint: disable=unused-variable
        #
        self.__workingRltvAssgnSessionPath = self.__siteSrvcUrlPathPrefix + self.rltvAssgnSessionPath
        #
        if self.__verbose:
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+%s.%s() starting\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
            self.__lfh.write("+%s.%s() identifier   %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, depId))
            self.__lfh.write("+%s.%s() instance     %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, wfInstId))
            self.__lfh.write("+%s.%s() file source  %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, fileSource))
            self.__lfh.write("+%s.%s() sessionId  %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, sessionId))
            self.__lfh.write("+%s.%s() self.__siteSrvcUrlPathPrefix  %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, self.__siteSrvcUrlPathPrefix))
            self.__lfh.write("+%s.%s() self.__workingRltvAssgnSessionPath  %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, self.__workingRltvAssgnSessionPath))
            self.__lfh.flush()
        #
        ############################################################################
        # create dictionary of content that will be used to populate HTML template
        ############################################################################
        myD = {}
        myD['siteid'] = siteId
        myD['sessionid'] = sessionId
        myD['instance'] = wfInstId
        myD['classid'] = classId
        myD['filesource'] = fileSource
        # following params only for rcsb stand-alone version
        myD['caller'] = p_reqObj.getValue("caller")
        myD['filepath'] = p_reqObj.getValue('filePath')
        myD['filetype'] = p_reqObj.getValue('fileType')
        myD['datafile'] = dataFile
        #
        if p_bIsWorkflow:
            myD['identifier'] = depId

        else:
            (_pth, fileName) = os.path.split(p_reqObj.getValue('filePath'))
            (fN, _fileExt) = os.path.splitext(fileName)
            if (fN.upper().startswith("D_")):
                depDataSetId = fN.upper()
            elif (fN.lower().startswith("rcsb")):
                depDataSetId = fN.lower()
            else:
                depDataSetId = "TMP_ID"
            myD['identifier'] = depDataSetId
        #
        myD['session_url_prefix'] = self.__workingRltvAssgnSessionPath
        myD['service_url_prefix'] = self.__siteSrvcUrlPathPrefix
        #
        contentTypeDict = self.__cI.get('CONTENT_TYPE_DICTIONARY')
        acceptedImgFileTypes = (contentTypeDict['component-image'][0])[:]
        acceptedDefFileTypes = (contentTypeDict['component-definition'][0])[:]
        acceptedDefFileTypes.append('cif')  # appending "cif" as a possible extension that is equivalent to "pdbx"
        myD['accepted_img_file_types'] = "['" + "','".join(acceptedImgFileTypes) + "']"
        myD['accepted_def_file_types'] = "['" + "','".join(acceptedDefFileTypes) + "']"

        # ##############################TIME CHECK TRACE###########################################################################################################################
        # if (self.__verbose):
        #    now = strftime("%H:%M:%S", localtime())
        #    self.__lfh.write("+%s.%s() ----TIMECHECK------------------------------------------ time before calling __processTemplate() is %s\n" % now)
        ##########################################################################################################################################################################
        oL.append(self.processTemplate(tmpltPth=os.path.join(tmpltPath, self.__pathCCliteGlblVwTmplts), fn="cc_lite_ligand_smmry_tmplt.html", parameterDict=myD))
        # ##############################TIME CHECK TRACE###########################################################################################################################
        # if (self.__verbose):
        #    now = strftime("%H:%M:%S", localtime())
        #    self.__lfh.write("+%s.%s() ----TIMECHECK------------------------------------------ time after calling __processTemplate() is %s\n" % now)
        ##########################################################################################################################################################################
        #
        return oL

    def doRender_LigSummaryContent(self, p_ccAssgnDataStr, p_reqObj):
        ''' Render Summary of Ligand Inventory Results
            Function generates HTML markup used for displaying results of chem comp assign inventory
            for the deposition data set. The resulting HTML markup is loaded via AJAX into an already
            existing web page "container".

            :Params:
                ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments

            :Returns:
                ``oL``: output list consisting of HTML markup
        '''
        self.__reqObj = p_reqObj
        #
        oL = []
        grpLst = []
        srtdGrpLst = []
        msmtchlist = ''
        rslvdlist = ''
        separator_m = ''
        separator_r = ''
        #
        ligGrpDict = self.__generateLigGroupSummaryDict(p_ccAssgnDataStr)
        grpLst = ligGrpDict.keys()
        srtdGrpLst = sorted(grpLst)
        #
        iRow = 0
        oL.append('<table id="ligand_inventory_tbl" class="">')
        oL.append('<tr><th>Ligand ID</th><th>Number of Instances</th><th><span id="resolve_status" class="target resolve_status">Status</span></th><th>Select for Inspection<input id="selectall" name="selectall" type="checkbox" class="selectall" ><label for="selectall">All</label></th><th id="hdrfcsrsrch">Ligand of Interest (LOI)?</th>')  # noqa: E501
        #
        grpsSelectedForResearch = p_ccAssgnDataStr.getRsrchSelectedLst()
        grpsHavingRsrchDataSubmitted = p_ccAssgnDataStr.getRsrchDataAcqurdLst()

        if "NONE%" in grpsSelectedForResearch:
            None_checked = 'checked="checked"'
            None_check_disabled = ''
        else:
            None_checked = ''
            None_check_disabled = ''

        # if( "HOH" in grpsSelectedForResearch):
        #     HOH_checked = 'checked="checked"'
        #     HOH_check_disabled = 'disabled="disabled"' if "HOH" in grpsHavingRsrchDataSubmitted else ''
        # else:
        #     HOH_checked = ''
        #     HOH_check_disabled = ''

        for ccId in srtdGrpLst:
            checked = ''
            checked_rsrch = ''
            check_rsrch_disabled = ''
            cssHighlightClass = ''
            if ligGrpDict[ccId]['bGrpRequiresAttention'] is True:
                checked = 'checked="checked"'
                # check to see if ccId represents group that has been resolved by user in previous session
                if ligGrpDict[ccId]['bGrpMismatchAddressed'] is True:
                    resolveStatus = 'Mismatch(es) Addressed'
                    cssHighlightClass = 'beenrslved'
                    if len(rslvdlist) > 0:
                        separator_r = ','
                    rslvdlist += separator_r + ccId
                else:
                    resolveStatus = 'Mismatch(es) Require Attention'
                    cssHighlightClass = 'warn'
                    if len(msmtchlist) > 0:
                        separator_m = ','
                    msmtchlist += separator_m + ccId
            else:
                resolveStatus = 'OK'
            #
            if ccId in grpsSelectedForResearch:
                check_rsrch_disabled = 'disabled="disabled"' if ccId in grpsHavingRsrchDataSubmitted else ''
                checked_rsrch = 'checked="checked"'
                # DISABLING UNTIL BINDING ASSAY DATA CAPTURE REQUIREMENTS ARE SORTED OUT:   checked = 'checked="checked"'
            #
            oL.append('<tr class="%s c_%s">' % (self.__rowClass(iRow), ccId))
            #
            oL.append('<td>%s</td>' % ccId)
            #
            oL.append('<td>%s</td>' % ligGrpDict[ccId]['totlInstncsInGrp'])
            #
            oL.append('<td class="resolve_status ' + cssHighlightClass + '">%s</td>' % (resolveStatus))
            #
            oL.append('<td><input name="%s" type="checkbox" class="selectinstnc" %s></td>' % (ccId, checked))
            #
            oL.append('<td class="selectinstnc_td"><input name="%s_rsrch" id="%s_rsrch" type="checkbox" class="selectinstnc_rsrch selectinst_stdgrp" %s %s></td>' %
                      (ccId, ccId, checked_rsrch, check_rsrch_disabled))
            #
            oL.append('</tr>')
            #
            iRow += 1

        # Artifical row to select "none" as "focus of research
        oL.append('<tr class="%s c_NONE_special">' % self.__rowClass(iRow))
        oL.append('<td class="" colspan=4>No ligand of interest</td>')
        oL.append('<td class="selectinstnc_td"><input name="NONE%%" id="NONE_rsrch" type="checkbox" class="selectinstnc_rsrch selectinst_none" %s %s></td>' %
                  (None_checked, None_check_disabled))
        oL.append('</tr>')
        iRow += 1

        oL.append('</table>')
        oL.append('<span id="mismatchlist" class="displaynone">' + msmtchlist + '</span>')
        oL.append('<span id="rslvdlist" class="displaynone">' + rslvdlist + '</span>')

        return oL

    def doRender_InstanceBrswrLaunchForm(self, p_reqObj):
        ''' Generate html for instance browser button and form in deposition UI

            :Params:

                + ``p_reqObj``: Web Request Object
        '''
        bIsWorkflow = self.isWorkflow(self.__reqObj)
        sessionId = p_reqObj.getSessionId()
        siteId = str(p_reqObj.getValue("WWPDB_SITE_ID"))
        wfInstId = str(p_reqObj.getValue("instance")).upper()
        depId = str(p_reqObj.getValue("identifier"))
        classId = str(p_reqObj.getValue("classID")).lower()
        fileSource = str(p_reqObj.getValue("filesource")).lower()
        # dataFile = str(p_reqObj.getValue("datafile"))
        tmpltPath = p_reqObj.getValue("TemplatePath")
        #
        depId = self.__formatDepositionDataId(depId, bIsWorkflow)

        rtrnLst = []

        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+%s.%s() starting\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
            self.__lfh.write("+%s.%s() identifier   %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, depId))
            self.__lfh.write("+%s.%s() instance     %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, wfInstId))
            self.__lfh.write("+%s.%s() file source  %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, fileSource))
            self.__lfh.write("+%s.%s() sessionId  %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, sessionId))
            self.__lfh.flush()
        #
        ############################################################################
        # create dictionary of content that will be used to populate HTML template
        ############################################################################
        myD = {}
        myD['siteid'] = siteId
        myD['sessionid'] = sessionId
        myD['instance'] = wfInstId
        myD['classid'] = classId
        myD['filesource'] = fileSource
        #
        if bIsWorkflow:
            myD['identifier'] = depId

        else:
            (_pth, fileName) = os.path.split(p_reqObj.getValue('filePath'))
            (fN, _fileExt) = os.path.splitext(fileName)
            if fN.upper().startswith("D_"):
                depDataSetId = fN.upper()
            elif fN.lower().startswith("rcsb"):
                depDataSetId = fN.lower()
            else:
                depDataSetId = "TMP_ID"
            myD['identifier'] = depDataSetId
        #

        rtrnLst.append(self.processTemplate(tmpltPth=os.path.join(tmpltPath, self.__pathCCliteGlblVwTmplts), fn="cc_lite_launch_instnc_brwsr_frm_tmplt.html", parameterDict=myD))
        return rtrnLst

    def getInstanceList(self, ligIdList, ccAssignDataStore):
        ligSubgroupDict = {}

        self.__logger.info('Getting instances for ligId %s', ligIdList)

        ligGrpDict = self.__generateLigGroupSummaryDict(ccAssignDataStore)

        self.__logger.debug('Result %s', ligGrpDict)

        for ligId in ligIdList:
            if ligId in ligGrpDict:
                ligSubgroupDict[ligId] = ligGrpDict[ligId]

        return ligSubgroupDict

    def __getNormalizedCifValue(self, fieldToEval):
        return fieldToEval if fieldToEval != "?" else ""

    def doRender_WaterRsrchCaptureContent(self, p_ccAssgnDataStr, p_reqObj):
        ''' Generate html "Provide data for HOH as focus of research" content for deposition UI

            :Params:

                + ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                + ``p_reqObj``: Web Request Object
        '''
        bIsWorkflow = self.isWorkflow(self.__reqObj)
        sessionId = p_reqObj.getSessionId()
        siteId = str(p_reqObj.getValue("WWPDB_SITE_ID"))
        wfInstId = str(p_reqObj.getValue("instance")).upper()
        depId = str(p_reqObj.getValue("identifier"))
        classId = str(p_reqObj.getValue("classID")).lower()
        fileSource = str(p_reqObj.getValue("filesource")).lower()
        dataFile = str(p_reqObj.getValue("datafile"))
        tmpltPath = p_reqObj.getValue("TemplatePath")
        #
        depId = self.__formatDepositionDataId(depId, bIsWorkflow)

        rtrnLst = []

        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+%s.%s() starting\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name))
            self.__lfh.write("+%s.%s() identifier   %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, depId))
            self.__lfh.write("+%s.%s() instance     %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, wfInstId))
            self.__lfh.write("+%s.%s() file source  %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, fileSource))
            self.__lfh.write("+%s.%s() sessionId  %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, sessionId))
            self.__lfh.flush()
        #
        ############################################################################
        # create dictionary of content that will be used to populate HTML template
        ############################################################################
        myD = {}
        myD['siteid'] = siteId
        myD['sessionid'] = sessionId
        myD['instance'] = wfInstId
        myD['classid'] = classId
        myD['filesource'] = fileSource
        # following params only for rcsb stand-alone version
        myD['caller'] = p_reqObj.getValue("caller")
        myD['filepath'] = p_reqObj.getValue('filePath')
        myD['filetype'] = p_reqObj.getValue('fileType')
        myD['datafile'] = dataFile
        #
        if bIsWorkflow:
            myD['identifier'] = depId

        else:
            (_pth, fileName) = os.path.split(p_reqObj.getValue('filePath'))
            (fN, _fileExt) = os.path.splitext(fileName)
            if fN.upper().startswith("D_"):
                depDataSetId = fN.upper()
            elif fN.lower().startswith("rcsb"):
                depDataSetId = fN.lower()
            else:
                depDataSetId = "TMP_ID"
            myD['identifier'] = depDataSetId
        #
        p_ccAssgnDataStr.dumpData(self.__lfh)

        bWaterInfoProvided = ("HOH" in p_ccAssgnDataStr.getRsrchDataAcqurdLst())

        # ############################# BEGIN creating "capture HOH research data" view ##############################
        if not bWaterInfoProvided:
            # allow depositor to provide data
            inputDisabled = ''
            doneBtnLabel = 'Save'
            doneBtnDisabled = 'disabled="disabled"'  # locked until valid data entered into input feild(s)

        else:
            # data already saved so display in locked state (they can undo if desired)
            inputDisabled = 'disabled="disabled"'
            doneBtnLabel = 'Edit'
            doneBtnDisabled = ''  # undo button is enabled to allow them to undo

        #
        myD['disabled'] = inputDisabled
        myD['donebtnlabel'] = doneBtnLabel
        myD['donebtndisabled'] = doneBtnDisabled
        #
        markedForResearchLst = p_ccAssgnDataStr.getRsrchSelectedLst()
        bHOHmarkedForResearch = True if "HOH" in markedForResearchLst else False

        if bHOHmarkedForResearch:
            myD['hide_HOH_section'] = ''
        else:
            myD['hide_HOH_section'] = 'displaynone'

        rsrchDataDict = p_ccAssgnDataStr.getResearchData("HOH")

        if rsrchDataDict is None or (len(rsrchDataDict.keys()) < 1):
            # no data stored for the HOH yet
            # so just supply default non-values for dataset 0
            myD['residuenum_0_'] = ''
            myD['chain_id_0_'] = ''
            myD['multi_datasets'] = ''
            #
            myD['data_acqurd'] = 'no_data_acqurd'
            myD['datasubmitted_display'] = 'displaynone'
            myD['no_datasubmitted_display'] = ''

        else:
            myD['residuenum_0_'] = self.__getNormalizedCifValue(rsrchDataDict[0]['residuenum'])
            myD['chain_id_0_'] = self.__getNormalizedCifValue(rsrchDataDict[0]['chain_id'])
            #
            myD['data_acqurd'] = 'data_acqurd'
            myD['datasubmitted_display'] = ''
            myD['no_datasubmitted_display'] = 'displaynone'

            oL = []
            strSubstDict = myD.copy()
            for key in rsrchDataDict:
                self.__lfh.write("+%s.%s() rsrchDataDict[%s] is: %r\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, key, rsrchDataDict[key]))

            for index in range(1, 10):
                if index in rsrchDataDict:
                    strSubstDict['index'] = index
                    strSubstDict['dataset_disply_index'] = str(index + 1)
                    #
                    strSubstDict['residuenum'] = self.__getNormalizedCifValue(rsrchDataDict[index]['residuenum'])
                    strSubstDict['chain_id'] = self.__getNormalizedCifValue(rsrchDataDict[index]['chain_id'])

                    oL.append(self.processTemplate(tmpltPth=os.path.join(tmpltPath, self.__pathCCliteGlblVwTmplts), fn="cc_lite_hoh_rsrch_data_clone_tmplt.html",
                                                   parameterDict=strSubstDict))

            myD['multi_datasets'] = '\n'.join(oL)

        rtrnLst.append(self.processTemplate(tmpltPth=os.path.join(tmpltPath, self.__pathCCliteGlblVwTmplts), fn="cc_lite_hoh_rsrch_data_init_tmplt.html", parameterDict=myD))
        return rtrnLst

    def _generateLigandMismatchSectionHtml(self, p_authAssignedGrp, p_ccAssgnDataStr, p_ligGrpDict, p_hlprDict):
        # we are making a local copy of the p_hlprDict dictionary because while we reuse some of the key/value pairs
        # we redefine some of the key/value pairings differently for specific use in the describe-new-ligand view
        lclDict = p_hlprDict.copy()

        htmlTmpltPth = os.path.join(lclDict['html_template_path'], self.__pathCCliteAllInstcs)

        if self.__verbose:
            self.__logger.debug('----- starting for author assigned entityID: %s', p_authAssignedGrp)

        if lclDict['browser'] == "noApplets":
            useApplet = False
        else:
            useApplet = True

        bGrpHasBeenResolved = p_authAssignedGrp in p_ccAssgnDataStr.getGlbllyRslvdGrpList()

        # begin creating "handle ligand mismatch" view
        grpInstIdCnt = p_ligGrpDict[p_authAssignedGrp]['totlInstncsInGrp']
        grpIsResolved = ''

        if not bGrpHasBeenResolved:
            grpMismtchRslvdDsply = 'displaynone'
            grpIsResolved = ''
            grpDisabled = ''
            doneBtnLabel = 'Save Verification for Ligand Mismatch'
            exctMtchBtnDisabled = 'disabled="disabled"'
            if p_ccAssgnDataStr.minReqsMetForDescrNwLgnd(p_authAssignedGrp) is True:
                doneBtnDisabled = ''
            else:
                doneBtnDisabled = 'disabled="disabled"'
        else:
            grpMismtchRslvdDsply = ''
            grpIsResolved = 'is_rslvd'
            grpDisabled = 'disabled="disabled"'
            doneBtnLabel = 'Edit Verification for Ligand Mismatch'
            doneBtnDisabled = ''
            exctMtchBtnDisabled = ''

        lclDict['inst_cnt'] = grpInstIdCnt
        lclDict['mismtch_rslvd_display'] = grpMismtchRslvdDsply
        lclDict['disabled'] = grpDisabled
        lclDict['donebtnlabel'] = doneBtnLabel
        lclDict['donebtndisabled'] = doneBtnDisabled
        lclDict['is_rslvd'] = grpIsResolved

        lclDict['dsply_addrss_msmtch_opts'] = 'displaynone'
        lclDict['dsply_no_match_instrctns'] = 'displaynone'
        lclDict['dsply_dscrnwlgnd'] = 'displaynone'
        lclDict['displaynextreqdset'] = 'displaynone'

        lclDict['dsply_exct_mtch_sv_btn'] = ''
        lclDict['exct_mtch_sv_btn_label'] = 'Save Verification for Ligand Mismatch'
        lclDict['exct_mtch_btn_disabled'] = exctMtchBtnDisabled
        lclDict['use_exact_mtch_id_checked'] = ''
        lclDict['use_orig_proposed_id_checked'] = ''
        lclDict['dscr_nw_lgnd_checked'] = ''

        lclDict['peptide_like_checked'] = ''
        lclDict['carbohydrate_checked'] = ''
        lclDict['lipid_checked'] = ''
        lclDict['heterogen_checked'] = ''
        lclDict['none_of_abv_checked'] = ''

        lclDict['alt_ccid'] = ''
        lclDict['dscrptr_type'] = ''
        lclDict['dscrptr_str'] = ''
        lclDict['inchi_selected'] = ''
        lclDict['smiles_selected'] = ''
        lclDict['sbmt_choice_dscrptrstr_slctd'] = 'selected="selected"'
        lclDict['sbmt_choice_sketch_slctd'] = ''

        lclDict['chem_name'] = ''
        lclDict['chem_frmla'] = ''
        lclDict['comments'] = ''

        exactMatchId = p_ccAssgnDataStr.getDpstrExactMtchCcId(p_authAssignedGrp)

        ligType = p_ccAssgnDataStr.getDpstrCcType(p_authAssignedGrp)
        ligAltId = p_ccAssgnDataStr.getDpstrAltCcId(p_authAssignedGrp) if p_ccAssgnDataStr.getDpstrAltCcId(p_authAssignedGrp) != '?' else ""
        ligDscrptrType = p_ccAssgnDataStr.getDpstrCcDscrptrType(p_authAssignedGrp)
        ligDscrptrStr = p_ccAssgnDataStr.getDpstrCcDscrptrStr(p_authAssignedGrp) if p_ccAssgnDataStr.getDpstrCcDscrptrStr(p_authAssignedGrp) != '?' else ""
        dpstrSubmitChoice = p_ccAssgnDataStr.getDpstrSubmitChoice(p_authAssignedGrp)
        ligName = p_ccAssgnDataStr.getDpstrCcName(p_authAssignedGrp) if p_ccAssgnDataStr.getDpstrCcName(p_authAssignedGrp) != '?' else ""
        ligFrmla = p_ccAssgnDataStr.getDpstrCcFrmla(p_authAssignedGrp) if p_ccAssgnDataStr.getDpstrCcFrmla(p_authAssignedGrp) != '?' else ""
        ligComments = p_ccAssgnDataStr.getDpstrComments(p_authAssignedGrp) if p_ccAssgnDataStr.getDpstrComments(p_authAssignedGrp) != '?' else ""

        if p_authAssignedGrp in p_hlprDict['hndle_msmtch_tophit_id_list'] and len(p_hlprDict['hndle_msmtch_tophit_id_list'][p_authAssignedGrp]) > 0:
            lclDict['dsply_addrss_msmtch_opts'] = ''
        else:
            lclDict['dsply_no_match_instrctns'] = ''
            lclDict['dsply_dscrnwlgnd'] = ''

        if self.__verbose and self.__debug:
            self.__logger.debug('----- ligComments: %s', ligComments)

        if ligType is not None and len(ligType) > 1:
            # if ligType is specified then indicates that user had chosen to open describe new ligand section
            lclDict[ligType + '_checked'] = 'checked="checked"'
            lclDict['displaynextreqdset'] = ''
            lclDict['use_exact_mtch_id_checked'] = ''  # uncheck opposing radio button options
            lclDict['use_orig_proposed_id_checked'] = ''  # uncheck opposing radio button options
            lclDict['dscr_nw_lgnd_checked'] = 'checked="checked"'  # show radio button as clicked
            lclDict['dsply_exct_mtch_sv_btn'] = 'displaynone'
            lclDict['dsply_dscrnwlgnd'] = ''  # display sections on describing a ligand

            if ligDscrptrType is not None and len(ligDscrptrType) > 0:
                if ligDscrptrType == 'smiles':
                    lclDict['smiles_selected'] = 'selected="selected"'
                    lclDict['inchi_selected'] = ''
                elif ligDscrptrType == 'inchi':
                    lclDict['smiles_selected'] = ''
                    lclDict['inchi_selected'] = 'selected="selected"'

            if ligAltId is not None and len(ligAltId) > 0:
                lclDict['alt_ccid'] = ligAltId  # repopulate chosen value
            if ligDscrptrStr is not None and len(ligDscrptrStr) > 0:
                lclDict['dscrptr_str'] = ligDscrptrStr
            if dpstrSubmitChoice is not None and len(dpstrSubmitChoice) > 0:
                if dpstrSubmitChoice == 'sketch':
                    lclDict['sbmt_choice_sketch_slctd'] = 'selected="selected"'
                    lclDict['sbmt_choice_dscrptrstr_slctd'] = ''
            if ligName is not None and len(ligName) > 0:
                lclDict['chem_name'] = ligName
            if ligFrmla is not None and len(ligFrmla) > 0:
                lclDict['chem_frmla'] = ligFrmla
            if ligComments is not None and len(ligComments) > 0:
                lclDict['comments'] = ligComments

        else:
            if bGrpHasBeenResolved:
                lclDict['dsply_exct_mtch_sv_btn'] = ''
                lclDict['exct_mtch_btn_disabled'] = ''
                lclDict['exct_mtch_sv_btn_label'] = 'Edit Verification for Ligand Mismatch'
                lclDict['dscr_nw_lgnd_checked'] = ''  # uncheck opposite radio button option
                lclDict['dsply_dscrnwlgnd'] = 'displaynone'  # don't display sections on describing a ligand

                if exactMatchId is not None and len(exactMatchId) > 1 :
                    if self.__verbose and self.__debug:
                        self.__logger.debug('----- DEBUG ----- exactMatchId is: %s', exactMatchId)

                    # if exactMatchId is specified then indicates that user had chosen to just use the chem comp ID that our software found as an exact match
                    lclDict['use_exact_mtch_id_checked'] = 'checked="checked"'  # show radio button as clicked
                else:
                    # else user chose to use originally proposed ligand ID
                    lclDict['use_orig_proposed_id_checked'] = 'checked="checked"'  # show radio button as clicked

        path2dAuthAssgndImg = '/service/cc_lite/report/file?identifier={}&source=author&file={}'.format(p_hlprDict["depositionid"].upper(), p_authAssignedGrp + '.svg')

        if self.__verbose and self.__debug:
            self.__logger.debug('----- so setting path2dAuthAssgndImg to: %s', path2dAuthAssgndImg)

        lclDict['2dpath_auth_assgnd_id'] = path2dAuthAssgndImg
        lclDict['use_exact_match_id_list'] = self.__generateExactMatchAssignMarkup(lclDict, exactMatchId)

        contentTypeDict = self.__cI.get('CONTENT_TYPE_DICTIONARY')
        acceptedImgFileTypes = (contentTypeDict['component-image'][0])[:]
        acceptedDefFileTypes = (contentTypeDict['component-definition'][0])[:]
        acceptedDefFileTypes.append('cif')  # appending "cif" as a possible extension that is equivalent to "pdbx"
        lclDict['accepted_img_file_types'] = "'" + "','".join(acceptedImgFileTypes) + "'"
        lclDict['accepted_def_file_types'] = "'" + "','".join(acceptedDefFileTypes) + "'"

        if useApplet:
            templateFile = "cc_lite_handle_lgnd_msmtch_tmplt.html"
        else:
            templateFile = "cc_lite_handle_lgnd_msmtch_noapplet_tmplt.html"

        instIdLst = p_ligGrpDict[p_authAssignedGrp]['instIdLst']
        lclDict['cc_lite_srch_rslts_tbl'] = ''.join(self.doRender_BatchRslts(p_authAssignedGrp, p_ccAssgnDataStr, instIdLst, htmlTmpltPth))
        lclDict['marvin_sketch'] = ''

        if self.__verbose:
            self.__logger.debug('----- reached end for author assigned entityID: %s', p_authAssignedGrp)

        htmlDirPathAbs = os.path.join(self.__ccReportPath, 'html', p_authAssignedGrp)
        if not os.path.exists(htmlDirPathAbs):
            os.makedirs(htmlDirPathAbs)

        htmlFilePathAbs = os.path.join(htmlDirPathAbs, p_authAssignedGrp + '_mismatch.html')
        with open(htmlFilePathAbs, 'w') as fp:
            fp.write('%s' % self.processTemplate(tmpltPth=htmlTmpltPth, fn=templateFile, parameterDict=lclDict))

    def __generateExactMatchAssignMarkup(self, p_hlprDict, p_exactMatchId):
        markup = []
        authAssgndGrp = p_hlprDict['auth_assgnd_grp']
        if authAssgndGrp in p_hlprDict['hndle_msmtch_tophit_id_list']:
            for ccId in p_hlprDict['hndle_msmtch_tophit_id_list'][authAssgndGrp]:
                p_hlprDict['tophit_id'] = ccId
                if p_exactMatchId is not None and ccId == p_exactMatchId:
                    p_hlprDict['use_exact_mtch_id_checked'] = 'checked="checked"'
                else:
                    p_hlprDict['use_exact_mtch_id_checked'] = ''
                markup.append(self.__alternateTopHitMarkup % p_hlprDict)

        return '\n'.join(markup) if len(markup) > 0 else ""

    def doRender_MarvinSketch(self, p_authAssignedGrp, p_htmlTmpltPth):
        if self.__verbose:
            self.__lfh.write("+%s.%s() ----- STARTING FOR : %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, p_authAssignedGrp))
        oL = []
        rD = {}
        rD['ccid'] = p_authAssignedGrp
        oL.append(self.processTemplate(tmpltPth=p_htmlTmpltPth, fn="marvin_sketch_tmplt.html", parameterDict=rD))

        # exporting html to file for debug purposes
        fp = open(os.path.join(self.__ccReportPath, 'html', 'debug' + p_authAssignedGrp + '_mrvnsktch.html'), 'w')
        fp.write("%s" % '\n'.join(oL))
        fp.close()

        return oL

    def generateInstancesMainHtml(self, ccAssignDataStore, ligList):
        """Render HTML markup for the ccmodule_lite UI Instance Browser
            The Instance Browser provides navigation of sections devoted to each ligand group (one ligand group viewed at a time)
            identified within a deposition dataset.
            A given ligand group section is itself broken down into:
                - a "single-instance" section, providing perspective/actions on a single ligand instance within the group

            This method generates HTML sections right after the chem comp analysis.
        Args:
            ccAssignDataStore (ChemCompAssignDataStore): object representing current state of ligand matches/assignments
            ligList (list): list of ligand ids associated with the current deposition
        """
        bIsWorkflow = self.isWorkflow(self.__reqObj)
        wfInstId = str(self.__reqObj.getValue("instance")).upper()
        sessionId = self.__reqObj.getSessionId()
        fileSource = str(self.__reqObj.getValue("filesource")).lower()
        htmlTmpltPth = self.__reqObj.getValue("TemplatePath")
        browser = self.__reqObj.getValue("browser")

        depId = self.__formatDepositionDataId(self.__depId, bIsWorkflow)

        # establish helper dictionary of elements used to populate html templates
        helperDict = {}
        helperDict['sessionid'] = sessionId
        helperDict['depositionid'] = depId
        helperDict['filesource'] = fileSource
        helperDict['instance'] = wfInstId  # i.e. workflow instance ID
        helperDict['identifier'] = depId
        helperDict['html_template_path'] = htmlTmpltPth
        helperDict['jmol_code_base'] = self.jmolCodeBase
        helperDict['browser'] = browser
        helperDict['service_url_prefix'] = self.__siteSrvcUrlPathPrefix
        helperDict['hndle_msmtch_tophit_id'] = ''
        helperDict['hndle_msmtch_tophit_id_list'] = {}

        ligGrpDict = self.__generateLigGroupSummaryDict(ccAssignDataStore)

        for _grpIndx, ligId in enumerate(ligList, start=1):
            if ligId is None:
                continue

            # first determine some data items about the current ligand ID/group
            # that we need to know for display purposes
            totlInstncsInGrp = 0
            bGrpRequiresAttention = False

            totlInstncsInGrp = ligGrpDict[ligId]['totlInstncsInGrp']
            bGrpRequiresAttention = ligGrpDict[ligId]['bGrpRequiresAttention']
            bGrpMsmtchsAddressed = ligGrpDict[ligId]['bGrpMismatchAddressed']

            helperDict['auth_assgnd_grp'] = ligId
            ccName = ligGrpDict[ligId]['ccName']
            helperDict['auth_assgnd_ccname'] = (ccName and len(ccName) or [''])[0]
            helperDict['auth_assgnd_ccname_displ'] = self.truncateForDisplay(helperDict['auth_assgnd_ccname'])
            helperDict['auth_assgnd_ccformula'] = ligGrpDict[ligId]['ccFormula']
            helperDict['auth_assgnd_ccformula_displ'] = self.truncateForDisplay(helperDict['auth_assgnd_ccformula'])
            helperDict['tot_inst_cnt'] = totlInstncsInGrp

            # then render html markup that serves as search result content for those instances in the current ligand group
            for instId in ligGrpDict[ligId]['instIdLst']:
                # rendering markup for chem component instances in the current group
                helperDict['instanceid'] = instId

                # if this particular instance is NOT one of the instances with mismatch issue, then can hide "attention required" notice
                if instId not in ligGrpDict[ligId]['mismatchLst']:
                    helperDict['attn_reqd_display'] = 'displaynone'
                else:
                    # else this instId does have mismatch issue but we show "attention required" notice only if depositor has yet to address the issue
                    if bGrpMsmtchsAddressed:
                        helperDict['attn_reqd_display'] = 'displaynone'
                    else:
                        helperDict['attn_reqd_display'] = ''

                self._generateInstanceProfileHtml(helperDict, ccAssignDataStore)

            # if necessary generate "describe new ligand for all-instances" section
            if bGrpRequiresAttention:
                self._generateLigandMismatchSectionHtml(ligId, ccAssignDataStore, ligGrpDict, helperDict)

    def _generateInstanceProfileHtml(self, helperDict, ccAssignDataStore):
        """Generate html "single-instance" profile content for given ligand instance

        Args:
            helperDict (dict): dictionary of data to be used for subsitution/population of HTML template(s)
            ccAssignDataStore (ChemCompAssignDataStore): ChemCompAssignDataStore object representing current state of ligand matches/assignments
        """
        instId = helperDict['instanceid']
        # sessionId = helperDict['sessionid']
        depId = helperDict['depositionid']
        # wfInstId = helperDict['instance']
        browser = helperDict['browser']
        htmlTmpltPth = os.path.join(helperDict['html_template_path'], self.__pathCCliteSnglInstcTmplts)

        self.__logger.info("Generating instance profile HTML for instId: %s", instId)

        # interrogate ChemCompAssign DataStore for necessary data items
        authAssignedGroup = ccAssignDataStore.getAuthAssignment(instId)
        topHitCcId = ccAssignDataStore.getBatchBestHitId(instId)
        isGroupResolved = (authAssignedGroup in ccAssignDataStore.getGlbllyRslvdGrpList())

        # determine whether or not a top candidate hit has been found for this instance
        if topHitCcId.lower() == 'none':
            hasTopHit = False
            helperDict['have_top_hit'] = False

            if self.__verbose:
                self.__logger.debug('instId %s has no top hit', instId)
        else:
            hasTopHit = True
            helperDict['have_top_hit'] = True

        # determine whether or not to use applets based on browser detected
        if browser == 'noApplets':
            useApplet = False
        else:
            useApplet = True

        # establish dictionary of elements used to populate html template for instance profile
        if authAssignedGroup.upper() != topHitCcId.upper():
            helperDict['attn_reqd'] = 'attn_reqd'
        else:
            helperDict['attn_reqd'] = ''

        if isGroupResolved:
            helperDict['is_rslvd'] = 'is_rslvd'
        else:
            helperDict['is_rslvd'] = 'not_rslvd'

        helperDict['auth_assgnd_grp'] = authAssignedGroup
        helperDict['status'] = ccAssignDataStore.getBatchBestHitStatus(instId)
        helperDict['name'] = ccAssignDataStore.getCcName(instId)
        helperDict['formula'] = ccAssignDataStore.getCcFormula(instId)
        helperDict['formula_displ'] = self.truncateForDisplay(helperDict['formula'])
        helperDict['fmlcharge'] = ccAssignDataStore.getCcFormalChrg(instId)
        helperDict['exact_match_ccid'] = ''

        if self.__debug:
            self.__logger.debug('----- single atomflag for instId %s is: %s', instId, ccAssignDataStore.getCcSingleAtomFlag(instId))

        helperDict['dsplyvizopt'] = '' if str(ccAssignDataStore.getCcSingleAtomFlag(instId)).lower() == 'n' else 'displaynone'

        if hasTopHit:
            helperDict['exact_match_ccid'] = topHitCcId
            topHitsList = ccAssignDataStore.getTopHitsList(instId)
            helperDict['exact_match_ccname'] = (len(topHitsList) and [topHitsList[0][3]] or [''])[0]
            helperDict['exact_match_ccname_displ'] = self.truncateForDisplay(helperDict['exact_match_ccname'])
            helperDict['exact_match_ccformula'] = (len(topHitsList) and [topHitsList[0][4]] or [''])[0]
            helperDict['exact_match_ccformula_displ'] = self.truncateForDisplay(helperDict['exact_match_ccformula'])

            if topHitCcId.lower() != authAssignedGroup.lower():
                helperDict['msmtch_explain'] = 'There is a discrepancy between your coordinates of <span class="strong">{}</span> and the match found in the CCD: <span style="color: #F00;">{}</span>'.format(authAssignedGroup, topHitCcId)  # noqa: E501
                helperDict['hndle_msmtch_tophit_id'] = topHitCcId
                if authAssignedGroup not in helperDict['hndle_msmtch_tophit_id_list']:
                    helperDict['hndle_msmtch_tophit_id_list'][authAssignedGroup] = []
                if topHitCcId not in helperDict['hndle_msmtch_tophit_id_list'][authAssignedGroup]:
                    helperDict['hndle_msmtch_tophit_id_list'][authAssignedGroup].append(topHitCcId)
            else:
                helperDict['msmtch_explain'] = ''

        # setting relative paths to 2D visualization resources that are used by webpage to load on demand via AJAX
        helperDict['2dpath'] = '/service/cc_lite/report/file?identifier={}&source=author&file={}.svg'.format(depId, instId)

        if hasTopHit:
            # if the assign search yielded top hit(s) we need to generate tabular display of match results
            helperDict['2dpath_top_hit'] = '/service/cc_lite/report/file?identifier={}&source=ccd&ligid={}&file={}.svg'.format(depId, topHitCcId, topHitCcId)  # noqa: E501 pylint: disable=duplicate-string-formatting-argument
            helperDict['assgn_sess_path_rel'] = self.__workingRltvAssgnSessionPath  # this key/value is used in private renderInstanceMatchResults function for cc_viz_cmp_li_tmplt.html
            helperDict['cc_instnc_match_rslts_tbl'] = ''.join(self._generateMatchResultsTable(ccAssignDataStore, helperDict))

        instanceProfileLabel = 'instnc_profile.html'

        # establishing values for RELATIVE path used by FRONT end for locating file that serves as instance profile markup and is called by front end on-demand
        htmlFilePathRel = '/service/cc_lite/report/file?identifier={}&source=report&ligid={}&file={}'.format(depId.upper(), instId, instId + instanceProfileLabel)
        helperDict['instnc_profile_path'] = htmlFilePathRel

        # establishing value for ABSOLUTE path used by BACK end for writing to file that serves as instance profile markup and is called by front end on-demand
        htmlDirPathAbs = os.path.join(self.__ccReportPath, 'html', instId)
        if not os.path.exists(htmlDirPathAbs):
            os.makedirs(htmlDirPathAbs)

        htmlFilePathAbs = os.path.join(htmlDirPathAbs, instId + instanceProfileLabel)

        with open(htmlFilePathAbs, 'w') as fp:
            if hasTopHit:
                if useApplet:
                    instncProfileTmpltName = 'cc_lite_instnc_profile_tmplt.html'
                else:
                    instncProfileTmpltName = 'cc_lite_instnc_profile_noapplet_tmplt.html'
            else:
                helperDict['msmtch_explain'] = 'No match was found in the CCD.'

                if useApplet:
                    instncProfileTmpltName = 'cc_lite_instnc_profile_nomatch_tmplt.html'
                else:
                    instncProfileTmpltName = 'cc_lite_instnc_profile_nomatch_noapplet_tmplt.html'

            fp.write('%s' % self.processTemplate(tmpltPth=htmlTmpltPth, fn=instncProfileTmpltName, parameterDict=helperDict))

        # 3D JMOL renderings
        if useApplet:
            self.__renderInstance3dViews(ccAssignDataStore, helperDict)

    def _generateMatchResultsTable(self, ccAssignDataStore, helperDict):
        oL = []
        # depId = helperDict['depositionid']
        instId = helperDict['instanceid']
        htmlTemplatePath = helperDict['html_template_path']

        ccid = ccAssignDataStore.getBatchBestHitId(instId)
        helperDict['ccid'] = ccid
        helperDict['3dpath_ref'] = '/service/cc_lite/report/file?identifier={}&source=ccd&ligid={}&file='

        # ################OBSOLETE?############################
        #
        #
        cnt = 0
        checked = ''
        assgnChecked = ''
        # assgndCcId = ccAssignDataStore.getAnnotAssignment(instId)  # XXXXX Any side effects if removed?
        assgnChecked = 'checked="checked"'
        #
        # using p_hlprDict to supply text substitution content for both cc_instnc_match_rslts_tbl_tmplt.html and cc_viz_cmp_li_tmplt.html in this loop
        helperDict['assgn_checked'] = assgnChecked
        #
        matchWarning = ''
        retD = self.__processWarningMsg(matchWarning)
        helperDict['score_warn_class'] = retD['warn_class']
        # scorePrefix = retD['prefix']
        # scoreSuffix = retD['suffix']
        #
        # p_hlprDict['score'] = scorePrefix+cmpstscore+scoreSuffix
        helperDict['score'] = ''
        helperDict['cc_name'] = ccAssignDataStore.getCcName(instId)
        helperDict['cc_name_displ'] = self.truncateForDisplay(helperDict['cc_name'])
        helperDict['cc_formula'] = ccAssignDataStore.getCcFormula(instId)
        helperDict['cc_formula_displ'] = self.truncateForDisplay(helperDict['cc_formula'])
        helperDict['checked'] = checked
        helperDict['index'] = cnt
        #
        helperDict['a'] = '%a'
        #
        ################################################

        # while we're iterating through the candidate assignments for the given instance, we will
        # also populate templates used for displaying chem comp references in viz compare grid
        htmlPathAbs = os.path.join(self.__ccReportPath, 'html', instId)
        jmolPathAbs = os.path.join(self.__ccReportPath, 'html', instId)
        htmlFilePathAbs = os.path.join(htmlPathAbs, ccid + '_viz_cmp_li.html')
        # atmMpFilePathAbs = os.path.join(htmlPathAbs, ccid + '_ref_atm_mp_li.html')
        jmolFilePathAbs = os.path.join(jmolPathAbs, ccid + '_ref_jmol.html')

        # populate "cc_viz_cmp_li_tmplt.html" which contains placeholders for "instanceid", "ccid",and "assgn_sess_path_rel"
        if not os.path.exists(htmlPathAbs):
            os.makedirs(htmlPathAbs)

        with open(htmlFilePathAbs, 'w') as fp:
            fp.write('%s' % self.processTemplate(tmpltPth=os.path.join(htmlTemplatePath, self.__pathCCliteSnglInstcCmprTmplts),
                                                 fn='cc_lite_viz_cmp_li_tmplt.html', parameterDict=helperDict))

        # populate "cc_ref_jmol_tmplt.html" which contains placeholders for "pct", "index", "a", and "3dpath_ref"
        if not os.path.exists(jmolPathAbs):
            os.makedirs(jmolPathAbs)

        with open(jmolFilePathAbs, 'w') as fp:
            fp.write('%s' % self.processTemplate(tmpltPth=os.path.join(htmlTemplatePath, self.__pathCCliteSnglInstcJmolTmplts),
                                                 fn='cc_lite_ref_jmol_tmplt.html', parameterDict=helperDict))

        return oL

    def doRender_BatchRslts(self, p_entityId, p_ccAssgnDataStr, p_instIdLst, p_tmpltPth):
        ''' Render "Condensed Batch Search Report"
            An abbreviated version of the Batch Chem Comp Assign search results used for
             display within the "describe new ligand" section of the entity browser.

            :Params:

                + ``p_entityId``: ID of ligand group for which profile is being generated
                + ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                + ``p_tmpltPth``: path to repository of HTML templates on the server

            :Returns:
                ``oL``: output list consisting of HTML markup
        '''
        myD = {}
        oL = []
        matchStatus = ''
        #
        for instId in p_instIdLst:
            #
            #    populate dictionary of elements to populate html template
            #
            matchStatus = p_ccAssgnDataStr.getBatchBestHitStatus(instId)
            if matchStatus != 'passed' and matchStatus != 'close match':
                myD['instanceid'] = instId
                myD['auth_assgnd_grp'] = p_entityId
                myD['status'] = matchStatus
                #
                oL.append(self.processTemplate(tmpltPth=p_tmpltPth, fn="cc_lite_entity_batch_rslts_tmplt.html", parameterDict=myD))

        # end of iterating through all ligand instances

        return oL

    def doRender_UploadedFilesList(self, p_ccid, p_filesLst, p_reqObj):
        """
        """
        #
        sessionId = p_reqObj.getSessionId()
        # tmpltPath = p_reqObj.getValue("TemplatePath")
        #
        replDict = {}
        fileUpldsMrkp = []
        #
        if self.__verbose:
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompAssignDepictLite.doRender_UploadedFilesList() starting\n")
            self.__lfh.write("+ChemCompAssignDepictLite.doRender_UploadedFilesList() sessionId  %s\n" % sessionId)
            self.__lfh.flush()

        #
        replDict['sessionid'] = sessionId
        #
        if len(p_filesLst) > 0:
            fileUpldsMrkp.append('<div id="upload_inventory" ><br /><p>Each item listed links to respective file.</p><ul>')
            replDict['ccid'] = p_ccid
            for fileName in p_filesLst:
                if (self.__verbose):
                    self.__lfh.write("+ChemCompAssignDepictLite.doRender_UploadedFilesList() listing includes file: %s\n" % fileName)
                replDict['filename'] = fileName
                fileListing = ('<li><a href="/sessions/%(sessionid)s/%(filename)s" target="_blank">%(filename)s</a><input id="%(ccid)s" name="%(filename)s" type="button" value="Remove" title="Remove file from deposition dataset" class="remove_file" style="margin-left:10px;"/></li>' % replDict)  # noqa: E501
                fileUpldsMrkp.append(fileListing)
            fileUpldsMrkp.append("</ul></div>")
        else:
            fileUpldsMrkp = '<div id="upload_inventory" ><br /><span>Currently no files on record.</span></div>'

        return fileUpldsMrkp

    def doRender_ResultFilesPage(self, p_reqObj, p_bIsWorkflow):
        """
        """
        #
        sessionId = p_reqObj.getSessionId()
        depId = str(p_reqObj.getValue("identifier")).upper()
        fileSource = str(p_reqObj.getValue("filesource")).lower()
        tmpltPath = p_reqObj.getValue("TemplatePath")
        #
        myD = {}
        #
        depId = self.__formatDepositionDataId(depId, p_bIsWorkflow)
        #

        #
        # Local path details - i.e. for processing within given session
        #
        #
        # dpstrInfoDirPath = os.path.join(self.__sessionPath, 'assign')
        dpstrInfoFile = depId + '-cc-dpstr-info.cif'
        dpstrUpdtdPdbxFile = depId + '-cc-model-w-dpstr-info.cif'
        #
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompAssignDepictLite.doRender_ResultFilesPage() starting\n")
            self.__lfh.write("+ChemCompAssignDepictLite.doRender_ResultFilesPage() identifier   %s\n" % depId)
            self.__lfh.write("+ChemCompAssignDepictLite.doRender_ResultFilesPage() file source  %s\n" % fileSource)
            self.__lfh.write("+ChemCompAssignDepictLite.doRender_ResultFilesPage() sessionId  %s\n" % sessionId)
            self.__lfh.flush()

        #
        # create dictionary of content that will be used to populate HTML template
        #
        myD['sessionid'] = sessionId
        myD['identifier'] = depId
        myD['dpstrInfoFile'] = dpstrInfoFile
        myD['dpstrUpdtdPdbxFile'] = dpstrUpdtdPdbxFile
        #
        fileUpldsLst = []
        fileListing = ''
        replDict = {}
        replDict['sessionid'] = sessionId

        ccADS = ChemCompAssignDataStore(p_reqObj, verbose=True, log=self.__lfh)
        for ligId in ccADS.getGlbllyRslvdGrpList():
            replDict['ligid'] = ligId
            dpstrUploadFilesDict = ccADS.getDpstrUploadFilesDict()

            if ligId in dpstrUploadFilesDict:

                for fileType in dpstrUploadFilesDict[ligId]:
                    for fileName in dpstrUploadFilesDict[ligId][fileType].keys():

                        replDict['filename'] = fileName

                        fileListing = ('<li><a href="/sessions/%(sessionid)s/%(filename)s">%(filename)s uploaded for %(ligid)s</a></li>' % replDict)
                        fileUpldsLst.append(fileListing)

            sbmttdStrctrData = ccADS.getDpstrSubmitChoice(ligId)
            if self.__verbose:
                self.__lfh.write("+%s.%s() sbmttdStrctrData is: %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, sbmttdStrctrData))
            if sbmttdStrctrData is not None and sbmttdStrctrData == 'sketch':
                replDict['filename'] = ligId + '-sketch.sdf'
                fileListing = ('<li><a href="/sessions/%(sessionid)s/assign/%(filename)s">%(filename)s structure sketch data submitted for %(ligid)s</a></li>' % replDict)
                fileUpldsLst.append(fileListing)

        myD['fileuploadslist'] = '\n'.join(fileUpldsLst)

        resultFilePathaAbs = os.path.join(self.absltSessionPath, "results.html")
        #
        fp = open(resultFilePathaAbs, 'w')
        fp.write("%s" % self.processTemplate(tmpltPth=os.path.join(tmpltPath, "templates"), fn="cc_lite_result_files_tmplt.html", parameterDict=myD))
        fp.close()

        if os.access(resultFilePathaAbs, os.R_OK):
            if self.__verbose:
                self.__lfh.write("+%s.%s() - results.html file created at: %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, resultFilePathaAbs))
        else:
            if self.__verbose:
                self.__lfh.write("+%s.%s() - NO results.html file created at: %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, resultFilePathaAbs))

    ################################################################################################################
    # ------------------------------------------------------------------------------------------------------------
    #      Private helper methods
    # ------------------------------------------------------------------------------------------------------------
    #
    def __generateLigGroupSummaryDict(self, p_ccAssgnDataStr):
        ''' generate utility dictionary to hold info for chem comp groups indicated in depositor's data

            :Returns:
            Currently returning two-tier dictionary with primary key of chem comp ID and following secondary keys:

                ``totlInstncsInGrp``:  total number of chem component instances with same ligand ID as given ID
                ``bGrpRequiresAttention``:  boolean indicating whether or not the given ligand ID group has any instances
                                        for which top hit does not match author provided ligand ID
                ``grpMismatchCnt``:  total number of chem component instances where mismatch detected
                ``instidLst``:  list of instanceIds for all instances of the chem component found in the depositor data
        '''
        rtrnDict = {}
        instncIdLst = p_ccAssgnDataStr.getAuthAssignmentKeys()
        ccA = ChemCompAssign(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        for _indx, instnc in enumerate(instncIdLst):
            authAssgndLigID = p_ccAssgnDataStr.getAuthAssignment(instnc)
            if authAssgndLigID not in rtrnDict:
                rtrnDict[authAssgndLigID] = {}
                rtrnDict[authAssgndLigID]['totlInstncsInGrp'] = 0
                rtrnDict[authAssgndLigID]['bGrpRequiresAttention'] = False
                rtrnDict[authAssgndLigID]['bGrpMismatchAddressed'] = False
                rtrnDict[authAssgndLigID]['grpMismatchCnt'] = 0
                rtrnDict[authAssgndLigID]['mismatchLst'] = []
                rtrnDict[authAssgndLigID]['instIdLst'] = []
                rtrnDict[authAssgndLigID]['ccName'] = p_ccAssgnDataStr.getCcName(instnc)  # assuming can use chem comp name for first instance for purposes of the group
                rtrnDict[authAssgndLigID]['ccFormula'] = p_ccAssgnDataStr.getCcFormula(instnc)  # assuming can use chem comp formula for first instance for purposes of the group

                if ccA.validCcId(authAssgndLigID) == 1:
                    p_ccAssgnDataStr.addLigIdToInvalidLst(authAssgndLigID)

            rtrnDict[authAssgndLigID]['totlInstncsInGrp'] += 1
            rtrnDict[authAssgndLigID]['instIdLst'].append(instnc)
            rtrnDict[authAssgndLigID]['instIdLst'].sort  # pylint: disable=pointless-statement
            curTopHitId = p_ccAssgnDataStr.getBatchBestHitId(instnc)
            if curTopHitId.upper() != authAssgndLigID.upper():  # i.e. mismatch detected
                rtrnDict[authAssgndLigID]['bGrpRequiresAttention'] = True
                rtrnDict[authAssgndLigID]['grpMismatchCnt'] += 1
                rtrnDict[authAssgndLigID]['mismatchLst'].append(instnc)
                rtrnDict[authAssgndLigID]['mismatchLst'].sort  # pylint: disable=pointless-statement
            if authAssgndLigID in p_ccAssgnDataStr.getGlbllyRslvdGrpList():
                rtrnDict[authAssgndLigID]['bGrpMismatchAddressed'] = True

        return rtrnDict

    def __renderInstance3dViews(self, p_ccAssgnDataStr, p_hlprDict):
        ''' For given ligand instance id, generates html fragments used for 3D jmol viewing in the "single-instance view"
            comparison panels-->these are written to files on server to be used on demand

            :Params:

                + ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                + ``p_hlprDict``: dictionary of data to be used for subsitution/population of an HTML template
        '''
        ##
        instId = p_hlprDict['instanceid']
        depId = p_hlprDict['depositionid']
        htmlTmpltPth = p_hlprDict['html_template_path']
        htmlTmpltPth_SnglInstnc = os.path.join(htmlTmpltPth, self.__pathCCliteSnglInstcJmolTmplts)
        htmlTmpltPth_AllInstnc = os.path.join(htmlTmpltPth, self.__pathCCliteAllInstncsJmolTmplts)
        ##
        #
        # # interrogate ChemCompAssign DataStore for necessary data items
        authAssignedGrp = p_ccAssgnDataStr.getAuthAssignment(instId)
        _topHitCcId = p_ccAssgnDataStr.getBatchBestHitId(instId)  # noqa: F841

        # ## determine whether or not a top candidate hit has been found for this instance
        # if topHitCcId == "None":
        #     bHaveTopHit = False
        # else:
        #     bHaveTopHit = True
        ##
        # sPathRel = self.__ccReportPath
        # s3dpathEnviron = self.rltvSessionPath
        ##
        instIdPieces = instId.split('_')
        chainId = instIdPieces[1]
        residueNum = instIdPieces[3]
        ##
        # p_hlprDict['3dpath'] = os.path.join(sPathRel,instId,'report',authAssignedGrp)
        p_hlprDict['3dpath'] = '/service/cc_lite/report/file?identifier={}&source=report&ligid={}&file='.format(depId.upper(), authAssignedGrp)
        # p_hlprDict['3dpath_environ'] = os.path.join(s3dpathEnviron,depId+'-jmol-mdl')
        p_hlprDict['3dpath_environ'] = '/service/cc_lite/report/file?identifier={}&source=report&ligid={}&file='.format(depId.upper(), instId)
        p_hlprDict['residue_num'] = residueNum
        p_hlprDict['chain_id'] = chainId
        # establishing values for ABSOLUTE paths used by BACK end for writing to files that serve as additional resources that may be called by front end on-demand
        jmolFilePathAbs_SnglInstVw = os.path.join(self.__ccReportPath, 'html', instId, instId + "instnc_jmol_instVw.html")
        environJmolFilePathAbs_SnglInstVw = os.path.join(self.__ccReportPath, 'html', instId, instId + "instnc_environ_jmol_instVw.html")
        # stndalnJmolFilePathAbs_SnglInstVw = os.path.join(self.__ccReportPath, 'html', instId, instId + "instnc_stndaln_jmol_instVw.html")
        jmolFilePathAbs_AllInstVw = os.path.join(self.__ccReportPath, 'html', instId, instId + "instnc_jmol_allInstVw.html")
        environJmolFilePathAbs_AllInstVw = os.path.join(self.__ccReportPath, 'html', instId, instId + "instnc_environ_jmol_allInstVw.html")
        # stndalnJmolFilePathAbs_AllInstVw = os.path.join(self.__ccReportPath, 'html', instId, instId+"instnc_stndaln_jmol_allInstVw.html")
        #
        # set default templates to be used
        instncJmolTmplt = "cc_instnc_jmol_tmplt.html"
        instncJmolAivwTmplt = "cc_instnc_jmol_aivw_tmplt.html"
        ################################################################################
        # when there is a top hit, we also need to generate "ready-made" html markup
        # for option to view author's instance within the structure environment
        # (this was found necessary due to Java security access
        # restrictions encountered in Mac/Firefox scenarios)
        #    ===    single instance environ view    ===
        fp = open(environJmolFilePathAbs_SnglInstVw, 'w')
        fp.write("%s" % self.processTemplate(tmpltPth=htmlTmpltPth_SnglInstnc, fn="cc_instnc_environ_jmol_tmplt.html", parameterDict=p_hlprDict))
        fp.close()
        #    ===    all instance environ view    ===
        fp = open(environJmolFilePathAbs_AllInstVw, 'w')
        fp.write("%s" % self.processTemplate(tmpltPth=htmlTmpltPth_AllInstnc, fn="cc_instnc_environ_jmol_aivw_tmplt.html", parameterDict=p_hlprDict))
        fp.close()
        ################################################################################
        #
        ####################################################################################################
        # generate default "single-instance view"
        ####################################################################################################
        fp = open(jmolFilePathAbs_SnglInstVw, 'w')
        fp.write("%s" % self.processTemplate(tmpltPth=htmlTmpltPth_SnglInstnc, fn=instncJmolTmplt, parameterDict=p_hlprDict))
        fp.close()
        #
        #####################################################################################################
        # generate default html fragment file for 3D jmol viewing in the "all-instances view" comparison panel
        #####################################################################################################
        fp = open(jmolFilePathAbs_AllInstVw, 'w')
        fp.write("%s" % self.processTemplate(tmpltPth=htmlTmpltPth_AllInstnc, fn=instncJmolAivwTmplt, parameterDict=p_hlprDict))
        fp.close()
        #

    def __processWarningMsg(self, p_wrningMsg):
        rtrnD = {}
        rtrnD['warn_class'] = ""
        rtrnD['prefix'] = ""
        rtrnD['suffix'] = ""
        #
        if p_wrningMsg != 'n.a.':
            rtrnD['warn_class'] = "warninfo"
            rtrnD['prefix'] = '<a href="#" title="SUPPLEMENTAL INFO:<br />' + p_wrningMsg + '" onclick="return false">'
            rtrnD['suffix'] = '</a>'
        #
        return rtrnD

    def __formatDepositionDataId(self, p_depid, p_bIsWorkflow):
        if p_bIsWorkflow or (p_depid.upper() == 'TMP_ID'):
            depId = p_depid.upper()
        else:
            depId = p_depid.lower()
        return depId

    def __rowClass(self, iRow):
        return (iRow % 2 and "odd" or 'even')

    # def __categoryPart(self, name):
    #     tname = ""
    #     if name.startswith("_"):
    #         tname = name[1:]
    #     else:
    #         tname = name

    #     i = tname.find(".")
    #     if i == -1:
    #         return tname
    #     else:
    #         return tname[:i]

    # def __attributePart(self, name):
    #     i = name.find(".")
    #     if i == -1:
    #         return None
    #     else:
    #         return name[i + 1:]

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
