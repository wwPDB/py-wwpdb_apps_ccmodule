##
# File:  ChemCompAssignDepict.py
# Date:  15-Sept-2010
# Updates:
#
# 2010-09-21    RPS    Piloting support for Level 1 Batch Search Summary display
# 2010-09-24    RPS    Adopted strategy of using of HTML template for Batch Search Summary page
# 2010-09-28    RPS    Supporting pre-selected checkboxes for entries where status != 'passed'
# 2010-10-05    RPS    Added doRender_BatchRslts(), doRender_EntityBrwsr() to support instance searching interface ("Level 2" searching)
# 2010-10-06    RPS    Added doRender_InstanceMatchRslts() to support instance searching interface ("Level 2" searching)
# 2010-11-22    RPS    Checkpoint Update:
#                        Clean up of doRender calls. Added doRender_BatchSrchSummaryContent(). Removed obsolete calls and associated lower-level methods.
#                        Corrected for misuse of pdbx_instance_assignment.het_id which is author assigned and not top hit result from batch search process.
# 2010-11-28    RPS    Removed obsolete methods.
# 2010-11-29    RPS    Updated to utilize ChemCompAssignDataStore as main vehicle for accessing/maintaining assignment data
# 2010-11-30    RPS    Updated to augment use of HTML templates. Template now in place for "all instances" view to mimic strategy used for "single instance" views.
# 2010-12-02    RPS    Updated with creation of assignment table for use in "All Instances" views.
#                      Fetching data needed for display of chem comp reference candidates in comparison grid.
# 2010-12-03    RPS    doRender_EntityBrwsr() and doRender_InstanceMatchRslts() updated to reflect strategy of sharing
#                        chem comp reference report material among ligand instances in same entity group.
# 2010-12-06    RPS    Now when generating HTML markup from templates, applying proper CSS styling depending on state of assignments in progress as captured
#                        in ChemCompAssignDataStore
# 2010-12-09    RPS    Now supporting atom-level mapping feature.
# 2010-12-15    RPS    Introducing support for rerunning instance search with adjusted parameters.
# 2011-01-11    RPS    doRender_EntityGrpOnRerunSrch(), doRender_InstanceProfileOnRerunSrch(), and doRender_EntityBrwsr() now remembering parameters used
#                        for rerunning assignment searches with adjusted deltas for link and bond radii
# 2011-01-25    RPS    doRender_BatchRslts(), doRender_BatchSrchSummaryContent() updated for improving display of top hits
#                      doRender_EntityGrpOnRerunSrch(), doRender_EntityBrwsr() updated to address bug in enabling/disabling rerun search buttons for All Instances section.
# 2011-02-09    RPS    doRender_AtmMpList(), doRender_BatchSrchSummaryContent() and  doRender_BatchRslts() updated to improve handling of cases where no top hits found
#                        for given ligands.
# 2011-02-22    RPS    doRender_BatchSrchSummaryContent() updated as per new strategy of having Batch Search Summary View and Instance Searching View reside on single
#                        web page/browser window.
# 2011-03-04    RPS    doRender_EntityBrwsr() and doRender_EntityGrpOnRerunSrch() updated to support provision of 3D environment view within same webpage as Chem Component Searching UI
# 2011-03-24    RPS    doRender_ccInstanceNonCandidate() added to support ad-hoc viewing of arbitrary non-candidate chem components in comparison grid
#                        self.__isWorkflow() convenience method added
#                        self.__truncateForDisplay() added to generate versions of long identifiers suitable for web page display
# 2011-03-31    RPS    doRender_EntityBrwsr() and doRender_EntityGrpOnRerunSrch() updated to accommodate proper handling of TMP_IDs when files are uploaded for
#                        processing on shared server
# 2011-04-26    RPS    self.__isWorkflow(), self.__truncateForDisplay(), and self.processTemplate() moved out to ChemCompDepict superclass
# 2011-05-17    RPS    doRender_InstanceProfileOnRerunSrch() removed, and doRender_AllInstncsProfile() and doRender_InstanceProfile() created in order to
#                        consolidate redundant blocks of code
#                        serving purpose of building HTML content for "All Instances" and "Single Instance" views.
# 2011-05-26    RPS    Replacing all references to "non"-candidate with "new"-candidate to eliminate confusion.
#                        doRender_InstanceProfile() and doRender_InstanceAssgnRows() updated to accommodate scenarios where there is no Top Hit for given ligand instance.
# 2011-06-03    RPS    doRender_BatchSrchSummaryContent() -- added CSS class for ligand instance checkboxes to support improved behavior of selectall checkbox,
#                        which will now be automatically unchecked when any lig instance in table is unchecked
# 2011-06-07    RPS    doRender_InstanceProfile() updated-->'3dpath" value changed to accommodate use of cif file (instead of pdb file) for loading Jmol viewer
#                        Updated for URLs to new standalone viewer interface for profiling chem component definitions already in dictionary.
# 2011-06-15    RPS    doRender_BatchSrchSummaryContent() updated-->'3dpath" value changed to accommodate use of cif file (instead of pdb file) for loading Jmol viewer
# 2011-06-16    RPS    Support for processing instance matching warning messages for display to user
# 2011-06-21    RPS    More updates for support of processing instance matching warning messages for display to user
# 2011-06-23    RPS    doRender_BatchSrchSummaryContainer() and doRender_3dEnvironView() added (migrated functionality from ChemCompWebApp)
# 2011-06-27    RPS    Corrected dictionary overwriting bug in doRender_AllInstncsProfile()
# 2011-07-01    RPS    doRender_InstanceProfile() updated to generate ready-made html markup for "environment" and "stand-alone" views where necessary
# 2011-07-13    RPS    doRender_EntityBrwsr() updated to generate necessary html div tags (so that can retire "cc_entity_browser_tmplt.html" template)
# 2011-07-19    RPS    doRender_InstanceMatchRslts() renamed to __renderInstanceMatchRslts()
# 2011-07-27    RPS    Updated to improve organization/modularity of code and provide comments in support of generating "restructuredtext" documentation
# 2011-08-01    RPS    More updates to improve organization/modularity of code.
# 2011-08-10    RPS    Updated to accommodate decoupling of directory used for files created/manipulated for given user session from directory used for
#                          Workflow Management data storage
# 2011-08-17    RPS    setSessionPaths() moved to ChemCompDepict class and used via inheritance
# 2011-08-23    RPS    Making use of self.jmolCodeBase as inherited from ChemCompDepict to indicate of location of Jmol applet code
# 2011-09-30    RPS    Corrected doRender_InstanceNewCandidate to make use of self.jmolCodeBase as inherited from ChemCompDepict
# 2011-12-08    RPS    doRender_BatchSrchSummaryContent updated to encode CSS classes in HTML markup necessary for supporting help text tool tips.
# 2012-03-27    RPS    Updated to reflect improved organization of html template files as stored on server.
# 2012-01-31    RPS    Added support for viewing of 2D images with augmented labeling.
# 2013-04-04    RPS    Updated to address bug so that UI behaves as expected when All Instances section is used to establish assignment just
#                        for *selected* instance IDs (i.e. and not entire group of ligands having same author assigned ID).
# 2013-04-16    RPS    Fixed bug with ordering of data when rendering batch results view.
# 2013-05-01    RPS    Updated so that choices to turn on/off 3D and 2D visualization are not provided for ligand instances consisting of only a single atom.
# 2013-10-09    RPS    Fixed bug with __renderInstanceMatchRslts() unexpectedly changing key/values used for top hit in instance profile html.
# 2013-10-10    RPS    Addressed changes in 2D image generation, so that need to reference "noh" version of gif for "no hydrogens" version.
# 2013-10-17    RPS    Updated to accommodate display of data from depositor as entered through LigandLite UI of Deposition site.
# 2013-11-04    ZF     Added pdbid & annotator parameters in doRender_BatchSrchSummaryContainer.
# 2014-05-05    RPS    Updated with feature to allow viewing of 2D rendition of SMILES string supplied by depositor
# 2014-05-22    RPS    Updates to support display of entry title in header of webpage.
# 2014-07-09    RPS        Fix for handling outer double quotes placed on SMILES strings (during CIF persistence) when generating 2D images for depositor info.
# 2014-11-03    ZF     Changed '.gif' to '.svg' for aligned images, added '2dpath' variable to 'cc_viz_cmp_li_tmplt.html' & 'cc_viz_cmp_li_tmplt_newcandidt.html' template
# 2016-07-22    RPS    Added debug trace logging to track file types of files uploaded by depositor via LigandLite.
# 2017-02-10    RPS    Implementing safeguard against crashes of OeBuildMol/OeDepict when problematic SMILES strings encountered
# 2017-04-11    RPS    Updates to accommodate identification of ligands selected by depositor as "ligands of interest"
# 2017-05-03    RPS    Updates so that LOI tracking can succeed even in cases where annotator reruns ligand search and consequently changes value for "author" assigned CCID
##
"""
Create HTML depiction chemical component assignment files.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import os
import sys
import traceback
from operator import itemgetter
import inspect

from wwpdb.apps.ccmodule.depict.ChemCompDepict import ChemCompDepict
# from wwpdb.apps.ccmodule.chem.PdbxChemCompAssign import PdbxCategoryDefinition
from wwpdb.apps.ccmodule.io.ChemCompAssignDataStore import ChemCompAssignDataStore
from wwpdb.utils.config.ConfigInfo import ConfigInfo
from wwpdb.utils.oe_util.oedepict.OeDepict import OeDepict
from wwpdb.utils.oe_util.build.OeBuildMol import OeBuildMol


class ChemCompAssignDepict(ChemCompDepict):
    """ Class responsible for generating HTML depictions of
        chemical component assignment search results.

    """
    def __init__(self, verbose=False, log=sys.stderr):
        """

         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        super(ChemCompAssignDepict, self).__init__(verbose, log)
        self.__verbose = verbose
        self.__lfh = log
        self.__debug = True
        #
        self.__cI = ConfigInfo()
        #
        # self.__cDict = PdbxCategoryDefinition._cDict
        #
        # self.__noDisplayList = ['']
        #
        self.__pathGlblVwTmplts = "templates/workflow_ui/global_view"
        self.__pathInstncsVwTmplts = "templates/workflow_ui/instances_view"
        self.__pathSnglInstcTmplts = self.__pathInstncsVwTmplts + "/single_instance"
        self.__pathSnglInstcCmprTmplts = self.__pathSnglInstcTmplts + "/comparison_view"
        self.__pathSnglInstcJmolTmplts = self.__pathSnglInstcCmprTmplts + "/jmol"
        #
        self.__pathAllInstcs = "templates/workflow_ui/instances_view/all_instances"
        self.__pathAllInstncsCmprTmplts = self.__pathAllInstcs + "/comparison_view"
        self.__pathAllInstncsJmolTmplts = self.__pathAllInstncsCmprTmplts + "/jmol"

        self.__dpstrInfoKeyList = ['dpstr_info_name',
                                   'dpstr_info_alt_comp_id',
                                   'dpstr_info_frmla',
                                   'dpstr_info_defn',
                                   'dpstr_info_defn_lnk',
                                   'dpstr_info_sketch_sdf',
                                   'dpstr_info_sketch_sdf_lnk',
                                   'dpstr_info_sketch_sdf_img_pth',
                                   'dpstr_info_sketch_sdf_img_lnk',
                                   'dpstr_info_image',
                                   'dpstr_info_image_lnk',
                                   'dpstr_info_dscrptr',
                                   'dpstr_info_dscrptr_type',
                                   'dpstr_info_dscrptr_img_pth',
                                   'dpstr_info_type',
                                   'dpstr_info_details']

    ################################################################################################################
    # ------------------------------------------------------------------------------------------------------------
    #      Top-level methods
    # ------------------------------------------------------------------------------------------------------------
    #

    def doRender_BatchSrchSummaryContainer(self, p_reqObj, p_bIsWorkflow):
        ''' Render HTML used as starter page/container for the Batch Search Assignment Results Summary
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
        wfInstId = str(p_reqObj.getValue("instance")).upper()
        depId = str(p_reqObj.getValue("identifier"))
        classId = str(p_reqObj.getValue("classID")).lower()
        fileSource = str(p_reqObj.getValue("filesource")).lower()
        pdbId = str(p_reqObj.getValue("pdbid"))
        annotator = str(p_reqObj.getValue("annotator"))
        entryTitle = str(p_reqObj.getValue("entry_title"))
        tmpltPath = p_reqObj.getValue("TemplatePath")
        #
        # This is wrong - but not correcting depid vs depId
        depid = self.__formatDepositionDataId(depId, p_bIsWorkflow)  # noqa: F841 pylint: disable=unused-variable
        #
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompAssignDepict.doRender_BatchSrchSummaryContainer() starting\n")
            self.__lfh.write("+ChemCompAssignDepict.doRender_BatchSrchSummaryContainer() identifier   %s\n" % depId)
            self.__lfh.write("+ChemCompAssignDepict.doRender_BatchSrchSummaryContainer() instance     %s\n" % wfInstId)
            self.__lfh.write("+ChemCompAssignDepict.doRender_BatchSrchSummaryContainer() file source  %s\n" % fileSource)
            self.__lfh.write("+ChemCompAssignDepict.doRender_BatchSrchSummaryContainer() sessionId  %s\n" % sessionId)
            self.__lfh.flush()
        #
        ############################################################################
        # create dictionary of content that will be used to populate HTML template
        ############################################################################
        myD = {}
        myD['sessionid'] = sessionId
        myD['instance'] = wfInstId
        myD['classid'] = classId
        myD['filesource'] = fileSource
        myD['pdbid'] = pdbId
        myD['entry_title'] = entryTitle
        myD['annotator'] = annotator
        # following params only for rcsb stand-alone version
        myD['caller'] = p_reqObj.getValue("caller")
        myD['filepath'] = p_reqObj.getValue('filePath')
        myD['filetype'] = p_reqObj.getValue('fileType')
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
            if depId:
                myD['identifier'] = depId
            #
        #
        myD['session_url_prefix'] = self.rltvAssgnSessionPath
        #
        # ##############################TIME CHECK TRACE##############################################################################################################################
        # if (self.__verbose):
        #    now = strftime("%H:%M:%S", localtime())
        #    self.__lfh.write("+ChemCompAssignDepict.doRender_BatchSrchSummaryContainer() ----TIMECHECK----------------- time before calling __processTemplate() is %s\n" % now)
        # ############################################################################################################################################################################
        oL.append(self.processTemplate(tmpltPth=os.path.join(tmpltPath, self.__pathGlblVwTmplts), fn="cc_batch_srch_smmry_tmplt.html", parameterDict=myD))
        # ##############################TIME CHECK TRACE#############################################################################################################################
        # if (self.__verbose):
        #    now = strftime("%H:%M:%S", localtime())
        #    self.__lfh.write("+ChemCompAssignDepict.doRender_BatchSrchSummaryContainer() ----TIMECHECK----------------- time after calling __processTemplate() is %s\n" % now)
        # ###########################################################################################################################################################################
        #
        return oL

    def doRender_BatchSrchSummaryContent(self, p_ccAssgnDataStr, p_linkInfoMap):
        ''' Render Summary of Batch Search Results
            Function generates HTML markup used for displaying results of chem comp assign search
            for the deposition data set. The resulting HTML markup is loaded via AJAX into an already
            existing web page "container".

            :Params:
                ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                ``p_linkInfoMap``: inter-residue linkage inforation
            :Returns:
                ``oL``: output list consisting of HTML markup
        '''
        oL = []
        srtdAssignLst = []
        instncIdLst = p_ccAssgnDataStr.getAuthAssignmentKeys()
        rsrchGrpIdsLst = p_ccAssgnDataStr.getRsrchSelectedLst()

        for instId in instncIdLst:
            srtdAssignLst.append((instId, p_ccAssgnDataStr.getAuthAssignment(instId), p_ccAssgnDataStr.getBatchBestHitStatus(instId)))
        #
        srtdAssignLst = sorted(srtdAssignLst, key=itemgetter(1, 2))
        # srtdAssignLst is now ordered by author assigned CCID and then by best hit status
        if self.__verbose and self.__debug:
            self.__lfh.write("+ChemCompAssignDepict.doRender_BatchSrchSummaryContent() srtdAssignLst: %r\n" % srtdAssignLst)
        #
        iRow = 0
        oL.append('<table id="batch_summary_match_tbl">')
        oL.append('<tr><th>Instance</th><th>Top Hit</th><th><span id="match_status" class="target match_status">Match Status</span></th><th>Selection <input id="selectall" name="selectall" type="checkbox" class="selectall"><label for="selectall">All</label></th><th><span id="cmpst_scr" class="target cmpst_scr">Composite Score</span></th><th>Assignment Status</th><th id="loi" title="Ligand of Interest (Research)" >LOI</th>')  # noqa: E501
        for (instId, authAssgndId, topHitStatus) in srtdAssignLst:
            # top candidate hit
            topHitCcId = p_ccAssgnDataStr.getBatchBestHitId(instId)
            # annotation status
            assgnmntStatus = p_ccAssgnDataStr.getAnnotAssignment(instId)
            checked = ''
            if topHitStatus.lower() != 'passed':
                checked = 'checked="checked"'
            if topHitStatus.lower() == 'passed':
                assgnmntStatus = '(' + p_ccAssgnDataStr.getBatchBestHitId(instId) + ')'
            #
            hlprD = self.__processWarningMsg(p_ccAssgnDataStr.getCcAssgnWarning(instId))
            #
            statusWarnClass = hlprD['warn_class']
            statusPrefix = hlprD['prefix']
            statusSuffix = hlprD['suffix']
            #
            topHitStatus = statusPrefix + str(p_ccAssgnDataStr.getBatchBestHitStatus(instId)) + statusSuffix
            #
            scoreWarnClass = ""
            scorePrefix = ''
            scoreSuffix = ''
            #
            if topHitCcId != 'None':
                # when not "None" we capture any existing match warning messages
                topHitTupl = p_ccAssgnDataStr.getTopHitsList(instId)[0]
                if topHitCcId.upper() == topHitTupl[0].upper():
                    wrningMsg = topHitTupl[2]
                    retD = self.__processWarningMsg(wrningMsg)
                    scoreWarnClass = retD['warn_class']
                    scorePrefix = retD['prefix']
                    scoreSuffix = retD['suffix']
                # we also apply required html markup to CCID display field when not "None"
                topHitCcId = '<a href="/ccmodule/cc-view.html?ccid=' + topHitCcId + '" target="_blank" title="Profile in Viewer">' + topHitCcId + '</a>'
            #
            cmpstScore = scorePrefix + str(p_ccAssgnDataStr.getBatchBestHitScore(instId)) + scoreSuffix
            #
            origMasterDpstrCcid = p_ccAssgnDataStr.getDpstrOrigCcIdMaster(instId)
            loiStatus = '&#x2714;' if (origMasterDpstrCcid in rsrchGrpIdsLst) else ''
            #
            oL.append('<tr class="%s c_%s c_%s">' % (self.__rowClass(iRow), instId, authAssgndId))
            #
            bgcolor = ""
            instWarnClass = ""
            processedInstId = instId
            if instId in p_linkInfoMap:
                retD = self.__processWarningMsg(p_linkInfoMap[instId])
                bgcolor = 'style="background-color:#0FF;"'
                instWarnClass = retD["warn_class"]
                processedInstId = retD["prefix"] + instId + retD["suffix"]
            #
            oL.append('<td %s class="%s">%s</td>' % (bgcolor, instWarnClass, processedInstId))
            #
            oL.append('<td>%s</td>' % topHitCcId)
            #
            oL.append('<td class="%s">%s</td>' % (statusWarnClass, topHitStatus))
            oL.append('<td><input name="%s" type="checkbox" class="selectinstnc" %s></td>' % (instId, checked))
            oL.append('<td class="%s">%s</td>' % (scoreWarnClass, cmpstScore))
            oL.append('<td class="assgnmnt_status %s">%s</td>' % (instId, assgnmntStatus))
            oL.append('<td class="loi %s">%s</td>' % (instId, loiStatus))
            oL.append('</tr>')
            #
            iRow += 1
        oL.append('</table>')

        return oL

    def doRender_EntityBrwsr(self, p_instncIdLst, p_ccAssgnDataStr, p_linkInfoMap, p_reqOb):
        ''' Render HTML markup for the Entity (i.e. ligand group) Browser
            The Entity Browser provides navigation of sections devoted to each entity group (one entity group viewed at a time)
            identified within a deposition dataset.
            A given entity group section is further broken down into:
                - an "all-instances" section, providing perspective/actions on all ligand instances within a group
                - a "single-instance" section, providing perspective/actions on a single ligand instance within the group

            :Params:

                + ``p_instncIdLst``: list of instance IDs which had been selected for processing via the Entity Browser
                + ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                + ``p_linkInfoMap``: inter-residue linkage inforation
                + ``p_reqObj``: Web Request object

            :Returns:
                ``oL``: output list consisting of HTML markup
        '''
        bIsWorkflow = self.isWorkflow(p_reqOb)
        depId = str(p_reqOb.getValue("identifier"))
        wfInstId = str(p_reqOb.getValue("instance")).upper()
        sessionId = p_reqOb.getSessionId()
        fileSource = str(p_reqOb.getValue("filesource")).lower()
        htmlTmpltPth = p_reqOb.getValue("TemplatePath")
        #
        depId = self.__formatDepositionDataId(depId, bIsWorkflow)
        #
        # Establish helper dictionary of elements used to populate html templates
        #
        hlprDict = {}
        hlprDict['sessionid'] = sessionId
        hlprDict['depositionid'] = depId
        hlprDict['filesource'] = fileSource
        hlprDict['instance'] = wfInstId  # i.e. workflow instance ID
        hlprDict['identifier'] = depId
        hlprDict['html_template_path'] = htmlTmpltPth
        hlprDict['jmol_code_base'] = self.jmolCodeBase
        #
        oL = []
        #
        oL.append('<div id="cc_entity_browser">\n<h4>Browse Chem Components by Entity Group</h4>\n<div id="pagi" class="noprint fltlft"></div>\n<br class="clearfloat" />\n')
        oL.append('<div id="cc_entity_browse_content">\n')
        i = 0
        # prevGrp and newGrp to keep track of changes in the entity grouping as we move from ligand instance to ligand instance
        prevGrp = ''
        newGrp = False
        #
        # p_instncIdLst.sort(key=lambda k: k.split('_')[2])
        if self.__verbose:
            for k in p_instncIdLst:
                self.__lfh.write("+ChemCompAssignDepict.doRender_EntityBrwsr() instId key in p_instncIdLst: %30s\n" % k)
        index = 0
        for instId in p_instncIdLst:
            ##
            instWarnStyle = ""
            if instId in p_linkInfoMap:
                instWarnStyle = 'style="color:red"'
            #
            hlprDict['inst_warn_style'] = instWarnStyle
            hlprDict['instanceid'] = instId
            authAssignedGrp = p_ccAssgnDataStr.getAuthAssignment(instId)
            hlprDict['2dpath_labld_w_hy'] = os.path.join(self.rltvSessionPath, 'assign', instId, 'image', instId + '_Big.svg')
            # hlprDict['2dpath_labld_w_hy'] = os.path.join(self.rltvSessionPath, 'assign', instId, 'report', authAssignedGrp + '_D3L3.gif')
            hlprDict['2dpath_labld_no_hy'] = os.path.join(self.rltvSessionPath, 'assign', instId, 'image', instId + '_Big.svg')
            # hlprDict['2dpath_labld_no_hy'] = os.path.join(self.rltvSessionPath, 'assign', instId, 'report', authAssignedGrp + '_D3L1.gif')
            # hlprDict['2dpath_labld_no_hy'] = os.path.join(self.rltvSessionPath, 'assign', instId, 'report', authAssignedGrp + '_D3L0.gif')
            ##
            index += 1
            ##
            # following if checks for whether we have arrived at a new ligand grouping
            if authAssignedGrp != prevGrp:
                i += 1
                prevGrp = authAssignedGrp
                newGrp = True
            else:
                newGrp = False
            ##
            tabStyle = "displaynone"
            if i == 1:
                tabStyle = "_current"
            ##
            if newGrp:
                # if this is a new ligand group we create a new "all-instances" section
                if i > 1:
                    oL.append('</div></div>')  # one terminal div for inneraccordion then another terminal div for p<N>

                oL.append('<div id="p%s" class="%s tabscount">' % (str(i), tabStyle))
                oL.append('<div class="cmpnt_grp displaynone">%s</div>' % authAssignedGrp)
                oL.append('<div class="inneraccordion" id="%s_inneraccordion">' % authAssignedGrp)
                # call method to generate html content for "All Instances" profile
                self.doRender_AllInstncsProfile(authAssignedGrp, p_instncIdLst, p_ccAssgnDataStr, p_linkInfoMap, hlprDict, oL)
                #
                #
            ###################################################################################################
            # Call method below to generate html content for "Single Instance" profile, content is in form of html
            # fragments stored in files on the server. The files are then recruited by AJAX calls made by the front end
            ###################################################################################################
            self.doRender_InstanceProfile(p_ccAssgnDataStr, hlprDict, p_bRerun=False)
            ##
            #################################################################################################
            # while we're iterating through the ligand instances, we will
            # also populate "cc_all_instncs_viz_cmp_li_tmplt.html" template used for displaying ligand instances in viz compare grid
            # and which contains placeholders for "auth_assgnd_grp", "name", "instanceid" and "2dpath"
            #################################################################################################
            topHitCcId = p_ccAssgnDataStr.getBatchBestHitId(instId)
            #
            if topHitCcId == "None":
                bHaveTopHit = False
            else:
                bHaveTopHit = True
            #
            if bHaveTopHit:
                vizCmpTmpltName = "cc_all_instncs_viz_cmp_li_tmplt.html"
            else:
                vizCmpTmpltName = "cc_all_instncs_viz_cmp_li_nomatch_tmplt.html"
            #
            htmlPathAbs = os.path.join(self.absltAssgnSessionPath, instId)
            htmlFilePathAbs = os.path.join(htmlPathAbs, instId + '_viz_cmp_li.html')
            fp = open(htmlFilePathAbs, 'w')
            fp.write("%s" % self.processTemplate(tmpltPth=os.path.join(htmlTmpltPth, self.__pathAllInstncsCmprTmplts), fn=vizCmpTmpltName, parameterDict=hlprDict))
            fp.close()
            #
            oL.append(self.processTemplate(tmpltPth=os.path.join(htmlTmpltPth, self.__pathSnglInstcTmplts), fn="cc_instnc_disp_tmplt.html", parameterDict=hlprDict))

        # end of iterating through all chem components
        oL.append('</div>\n')
        # above is end of cc_entity_browse_content div
        oL.append('</div>\n')
        oL.append('</div>\n')
        # above needed to seal off last chem cmpnt_grp div
        oL.append('</div>\n')
        # above is end tag for <div id="cc_entity_browser">
        return oL

    def doRender_AllInstncsProfile(self, p_authAssignedGrp, p_instncIdLst, p_ccAssgnDataStr, p_linkInfoMap, p_hlprDict, p_oL):
        ''' Generate html "all-instances" profile content for given entity group

            :Params:

                + ``p_authAssignedGrp``: Chem Comp ID used by the depositor to the given entity/ligand group
                + ``p_instncIdLst``: list of instance IDs which had been selected for processsing via the Entity Browser
                + ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                + ``p_linkInfoMap``: inter-residue linkage inforation
                + ``p_hlprDict``: dictionary of data to be used for subsitution/population of HTML template(s)
                + ``p_oL``: output list being updated with HTML markup content
        '''
        # we are making a local copy of the p_hlprDict dictionary because while we reuse some of the key/value pairs
        # we redefine some of the key/value pairings differently for specific use in the all-instances view
        lclDict = p_hlprDict.copy()
        #
        htmlTmpltPth = os.path.join(lclDict['html_template_path'], self.__pathAllInstcs)
        #
        if self.__verbose:
            self.__lfh.write("+ChemCompAssignDepict.doRender_AllInstncsProfile() ----- starting for author assigned entityID: %s\n" % p_authAssignedGrp)
        #
        bGrpIsGlbllyAssgnd = (p_authAssignedGrp in p_ccAssgnDataStr.getGlbllyAssgndGrpList())
        bGrpHadSearchRerun = (p_authAssignedGrp in p_ccAssgnDataStr.getGlblRerunSrchLst())
        # ############################# BEGIN creating "all instances" view ##############################
        # ######## Global/vs Instance level assignment handling######
        ##
        grpIsAssgnd = ''
        grpAssgnLbl = 'Assign'
        if p_authAssignedGrp in p_ccAssgnDataStr.getDrtyGrpList():
            if bGrpIsGlbllyAssgnd:
                grpDsplynone = ''
                grpIsAssgnd = 'is_assgnd'
                grpAssgnLbl = 'Un-Assign'
                assgnDisabled = ''
                grpDisabled = 'disabled="disabled"'
                grpAssgnmnt = p_ccAssgnDataStr.getGlblAssgnForGrp(p_authAssignedGrp)
            else:
                grpDsplynone = 'displaynone'
                grpIsAssgnd = ''
                grpAssgnLbl = 'Assign'
                assgnDisabled = 'disabled="disabled"'
                grpDisabled = 'disabled="disabled"'
                grpAssgnmnt = ''
        else:
            grpDisabled = ''
            grpDsplynone = 'displaynone'
            grpAssgnmnt = ''
            assgnDisabled = ''
        ##
        grpAssgnCnt = p_ccAssgnDataStr.getAssgndInstncsCntForGrp(p_authAssignedGrp)
        if grpAssgnCnt is None:
            grpAssgnCnt = 0
        ##
        ############################################################
        #
        # ######## Rerun Search handling ############################
        ##
        lclDict['link_radius_dlta'] = p_ccAssgnDataStr.getGlblRerunSrchParam_lnkRadii(p_authAssignedGrp)
        lclDict['bond_radius_dlta'] = p_ccAssgnDataStr.getGlblRerunSrchParam_bndRadii(p_authAssignedGrp)
        displayClass = ''
        buttonLbl = ''
        if bGrpHadSearchRerun:
            displayClass = ''
            buttonLbl = "Hide Rerun Search Form"
        else:
            displayClass = 'displaynone'
            buttonLbl = "Show Rerun Search Form"
        lclDict['rerun_display_class'] = displayClass
        lclDict['rerun_btn_lbl'] = buttonLbl
        ##
        ############################################################
        #
        dsplyvizopt = "displaynone"
        for instId in p_instncIdLst:

            grp = p_ccAssgnDataStr.getAuthAssignment(instId)
            #
            if grp.upper() == p_authAssignedGrp.upper():
                if str(p_ccAssgnDataStr.getCcSingleAtomFlag(instId)).lower() == 'n':
                    dsplyvizopt = ""
        #
        lclDict['dsplyvizopt'] = dsplyvizopt
        #
        lclDict['ccid_assgnmnt'] = grpAssgnmnt
        lclDict['displaynone'] = grpDsplynone
        lclDict['is_assgnd'] = grpIsAssgnd
        lclDict['assgn_cnt'] = grpAssgnCnt
        lclDict['disabled'] = grpDisabled
        lclDict['assgn_disabled'] = assgnDisabled
        lclDict['assgn_lbl'] = grpAssgnLbl
        lclDict['auth_assgnd_grp'] = p_authAssignedGrp
        lclDict['cc_batch_rslts_tbl'] = ''.join(self.doRender_BatchRslts(p_authAssignedGrp, p_instncIdLst, p_ccAssgnDataStr, p_linkInfoMap, htmlTmpltPth))
        lclDict['instncs_drpdwn_lst'] = ''.join(self.doRender_InstanceAssgnDrpDwn(p_authAssignedGrp, p_instncIdLst, p_ccAssgnDataStr, htmlTmpltPth))
        lclDict['instnc_candidate_rows'] = ''.join(self.doRender_InstanceAssgnRows(p_authAssignedGrp, p_instncIdLst, p_ccAssgnDataStr, htmlTmpltPth))
        # ## dpstr info handling ###
        lclDict['display_dpstr_info'] = "displaynone"
        lclDict['display_dscrptr_vw_btn'] = "displaynone"
        naStr = "n/a"
        #
        for keyName in self.__dpstrInfoKeyList:
            lclDict[keyName] = naStr
        if p_authAssignedGrp in p_ccAssgnDataStr.getGlbllyRslvdGrpList():
            self.__packDpstrViewDict(p_authAssignedGrp, p_ccAssgnDataStr, lclDict)
        for keyName in self.__dpstrInfoKeyList:
            lclDict[keyName + "_displ"] = "displaynone" if lclDict[keyName] == naStr else ""
        ###########################
        lclDict['all_instncs_profile_view'] = self.processTemplate(tmpltPth=htmlTmpltPth, fn="cc_all_instncs_profile_tmplt.html", parameterDict=lclDict)
        p_oL.append(self.processTemplate(tmpltPth=htmlTmpltPth, fn="cc_all_instncs_disp_tmplt.html", parameterDict=lclDict))
        # ############################# END creating "all instances" view ##############################
        if self.__verbose:
            self.__lfh.write("+ChemCompAssignDepict.doRender_AllInstncsProfile() ----- reached end for author assigned entityID: %s\n" % p_authAssignedGrp)

    def doRender_InstanceProfile(self, p_ccAssgnDataStr, p_hlprDict, p_bRerun=False):
        ''' Generate html "single-instance" profile content for given ligand instance

            :Params:

                + ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                + ``p_hlprDict``: dictionary of data to be used for subsitution/population of HTML template(s)
                + ``p_bRerun``: boolean indicating whether or not HTML being generated as result of rerunning cc-assign search for this ligand
        '''
        ##
        instId = p_hlprDict['instanceid']
        # sessionId = p_hlprDict['sessionid']
        # depId = p_hlprDict['depositionid']
        # wfInstId = p_hlprDict['instance']
        htmlTmpltPth = os.path.join(p_hlprDict['html_template_path'], self.__pathSnglInstcTmplts)
        ##
        if self.__verbose:
            self.__lfh.write("+ChemCompAssignDepict.doRender_InstanceProfile() ----- starting for instId: %s\n" % instId)
            self.__lfh.write("+ChemCompAssignDepict.doRender_InstanceProfile() ----- Rerun condition is: %s\n" % p_bRerun)
        ##
        # interrogate ChemCompAssign DataStore for necessary data items
        authAssignedGrp = p_ccAssgnDataStr.getAuthAssignment(instId)
        topHitCcId = p_ccAssgnDataStr.getBatchBestHitId(instId)
        bGrpIsGlbllyAssgnd = (authAssignedGrp in p_ccAssgnDataStr.getGlbllyAssgndGrpList())
        bInstIdHadSearchRerun = (instId in p_ccAssgnDataStr.getInstIdRerunSrchLst())
        # determine whether or not a top candidate hit has been found for this instance
        if topHitCcId == "None":
            bHaveTopHit = False
            if self.__verbose:
                self.__lfh.write("+ChemCompAssignDepict.doRender_InstanceProfile() ----- instId %s has no top hit\n" % instId)
        else:
            bHaveTopHit = True
        #
        #######################################################################################################################################################
        #######################################################################################################################################################
        #
        #    Establish dictionary of elements used to populate html template for instance profile
        #
        #######################################################################################################################################################
        #######################################################################################################################################################
        p_hlprDict['top_hit_ccid'] = topHitCcId
        p_hlprDict['2dpath_labld_w_hy_ref'] = os.path.join(self.rltvSessionPath, 'assign', instId, 'image', topHitCcId + '_Big.svg')
        # p_hlprDict['2dpath_labld_w_hy_ref'] = os.path.join(self.rltvSessionPath, 'assign', 'rfrnc_reports', topHitCcId, topHitCcId + '_D3L3.gif')
        p_hlprDict['2dpath_labld_no_hy_ref'] = os.path.join(self.rltvSessionPath, 'assign', instId, 'image', topHitCcId + '_Big.svg')
        # p_hlprDict['2dpath_labld_no_hy_ref'] = os.path.join(self.rltvSessionPath, 'assign', 'rfrnc_reports', topHitCcId, topHitCcId + '_D3L1.gif')
        # p_hlprDict['2dpath_labld_no_hy_ref'] = os.path.join(self.rltvSessionPath, 'assign', 'rfrnc_reports', topHitCcId, topHitCcId + '_D3L0.gif')
        topHitsList = p_ccAssgnDataStr.getTopHitsList(instId)
        p_hlprDict['top_hit_ccname'] = (len(topHitsList) and [topHitsList[0][3]] or [''])[0]
        p_hlprDict['top_hit_ccname_displ'] = self.truncateForDisplay(p_hlprDict['top_hit_ccname'])
        p_hlprDict['top_hit_ccformula'] = (len(topHitsList) and [topHitsList[0][4]] or [''])[0]
        p_hlprDict['top_hit_ccformula_displ'] = self.truncateForDisplay(p_hlprDict['top_hit_ccformula'])
        p_hlprDict['auth_assgnd_grp'] = p_ccAssgnDataStr.getAuthAssignment(instId)
        p_hlprDict['status'] = p_ccAssgnDataStr.getBatchBestHitStatus(instId)
        p_hlprDict['name'] = p_ccAssgnDataStr.getCcName(instId)
        p_hlprDict['formula'] = p_ccAssgnDataStr.getCcFormula(instId)
        p_hlprDict['formula_displ'] = self.truncateForDisplay(p_hlprDict['formula'])
        p_hlprDict['fmlcharge'] = p_ccAssgnDataStr.getCcFormalChrg(instId)
        #
        if self.__debug:
            self.__lfh.write("+%s.%s() ----- single atomflag for instId '%s' is: '%s'.\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name,
                                                                                             instId, p_ccAssgnDataStr.getCcSingleAtomFlag(instId)))
        p_hlprDict['dsplyvizopt'] = "" if (str(p_ccAssgnDataStr.getCcSingleAtomFlag(instId)).lower() == 'n') else "displaynone"
        #
        ##
        #
        # # setting relative paths to 2D visualization resources that are used by webpage to load on demand via AJAX
        p_hlprDict['2dpath'] = os.path.join(self.rltvAssgnSessionPath, instId, 'image', instId + '.svg')
        # p_hlprDict['2dpath']               = os.path.join(self.rltvAssgnSessionPath, instId, 'report', authAssignedGrp + '-noh.gif')
        # p_hlprDict['2dpath']               = os.path.join(self.rltvAssgnSessionPath, instId, 'report', authAssignedGrp + '_D3L0.gif')
        p_hlprDict['2dpath_top_hit'] = os.path.join(self.rltvAssgnSessionPath, instId, 'image', topHitCcId + '.svg')
        # p_hlprDict['2dpath_top_hit']       = os.path.join(self.rltvAssgnSessionPath, 'rfrnc_reports', topHitCcId, topHitCcId + '-noh.gif')
        # p_hlprDict['2dpath_top_hit']       = os.path.join(self.rltvAssgnSessionPath, 'rfrnc_reports', topHitCcId, topHitCcId + '_D3L0.gif')

        ##
        #
        # added by ZF. It is needed by directly call from ChemCompWebApp._ccAssign_rerunInstncSrch && ChemCompWebApp._ccAssign_rerunInstncCompSrch
        p_hlprDict['jmol_code_base'] = self.jmolCodeBase
        p_hlprDict['2dpath_labld_w_hy'] = os.path.join(self.rltvSessionPath, 'assign', instId, 'image', instId + '_Big.svg')
        # p_hlprDict['2dpath_labld_w_hy'] = os.path.join(self.rltvSessionPath, 'assign', instId,' report', authAssignedGrp + '_D3L3.gif')
        p_hlprDict['2dpath_labld_no_hy'] = os.path.join(self.rltvSessionPath, 'assign', instId, 'image', instId + '_Big.svg')
        # p_hlprDict['2dpath_labld_no_hy'] = os.path.join(self.rltvSessionPath, 'assign', instId, 'report', authAssignedGrp + '_D3L1.gif')
        # p_hlprDict['2dpath_labld_no_hy'] = os.path.join(self.rltvSessionPath, 'assign', instId, 'report', authAssignedGrp + '_D3L0.gif')
        ############################################################################################################################################################
        #################################################################################################################################
        # below we are setting dictionary items that pertain to different display states depending
        # on whether or not given ligand instance has been assigned a CC ID by annotator
        # ------------------------------------------------------------------------------------------------------------------------
        # NOTE: 'ccid_assgnmnt', 'displaynone', and 'is_assgnd', key/value pairs are used in cc_instnc_disp_tmplt.html template
        # which is populated NOT by this by function but by the code calling this function and which reuses the dictionary built here.
        #################################################################################################################################
        ccid = p_ccAssgnDataStr.getAnnotAssignment(instId)
        if ccid != "Not Assigned":
            ##
            p_hlprDict['ccid_assgnmnt'] = ccid
            p_hlprDict['displaynone'] = ''
            p_hlprDict['is_assgnd'] = 'is_assgnd'
            ##
            p_hlprDict['disabled'] = 'disabled="disabled"'
            if not bGrpIsGlbllyAssgnd:
                p_hlprDict['assgn_lbl'] = 'Un-Assign'
                p_hlprDict['assgn_disabled'] = ''
            else:
                p_hlprDict['assgn_lbl'] = 'Assign'
                p_hlprDict['assgn_disabled'] = 'disabled="disabled"'
        else:
            ##
            p_hlprDict['ccid_assgnmnt'] = ''
            p_hlprDict['displaynone'] = 'displaynone'
            p_hlprDict['is_assgnd'] = ''
            ##
            p_hlprDict['disabled'] = ''
            p_hlprDict['assgn_disabled'] = ''
            p_hlprDict['assgn_lbl'] = 'Assign'
        ##

        ############################################################################################################################################################
        # # if the assign search yielded top hit(s) we need to generate tabular display of match results  ###########################################################
        if bHaveTopHit:
            p_hlprDict['assgn_sess_path_rel'] = self.rltvAssgnSessionPath  # this key/value is used in private renderInstanceMatchResults function for cc_viz_cmp_li_tmplt.html
            p_hlprDict['cc_instnc_match_rslts_tbl'] = ''.join(self.__renderInstanceMatchRslts(p_ccAssgnDataStr, p_hlprDict))
        ##
        ############################################################################################################################################################

        ############################################################################################################################################################
        # ######## below we are managing items as relates to rerunning of assignment searches on entity group or instance ###########################################
        ##
        p_hlprDict['link_radius_dlta'] = p_ccAssgnDataStr.getRerunParam_linkRadii(instId)
        p_hlprDict['bond_radius_dlta'] = p_ccAssgnDataStr.getRerunParam_bondRadii(instId)
        ##
        if p_bRerun:
            instncProfileLbl = "rerun_srch_instnc_profile.html"
            instncAtmMpLbl = "rerun_srch_instnc_atm_mp_li.html"
        else:
            instncProfileLbl = "instnc_profile.html"
            instncAtmMpLbl = "instnc_atm_mp_li.html"
        ##
        if bInstIdHadSearchRerun:  # i.e. was rerun called specifically on this single instance as opposed to being called on whole entity group
            p_hlprDict['rerun_display_class'] = ''
            p_hlprDict['rerun_btn_lbl'] = "Hide Rerun Search Form"
        else:
            p_hlprDict['rerun_display_class'] = 'displaynone'
            p_hlprDict['rerun_btn_lbl'] = "Show Rerun Search Form"
        ##
        ############################################################################################################################################################
        ############################################################################################################################################################

        # establishing values for RELATIVE path used by FRONT end for locating file that serves as instance profile markup and is called by front end on-demand
        htmlFilePathRel = os.path.join(self.rltvAssgnSessionPath, instId, instId + instncProfileLbl)
        ############################################################################################################################################################
        # NOTE: 'instnc_profile_path" key/value below is used in cc_instnc_disp_tmplt and cc_all_instncs_disp_tmplt
        # which are populated NOT by this by function but by code that has called this function
        p_hlprDict['instnc_profile_path'] = htmlFilePathRel
        ############################################################################################################################################################

        # establishing value for ABSOLUTE path used by BACK end for writing to file that serves as instance profile markup and is called by front end on-demand
        htmlFilePathAbs = os.path.join(self.absltAssgnSessionPath, instId, instId + instncProfileLbl)
        #
        fp = open(htmlFilePathAbs, 'w')
        #
        if bHaveTopHit:
            instncProfileTmpltName = "cc_instnc_profile_tmplt.html"
        else:
            instncProfileTmpltName = "cc_instnc_profile_nomatch_tmplt.html"
        #
        fp.write("%s" % self.processTemplate(tmpltPth=htmlTmpltPth, fn=instncProfileTmpltName, parameterDict=p_hlprDict))
        fp.close()

        ############################################################################################################################################################
        #    Atom Mapping rendering
        ############################################################################################################################################################
        ##
        if bHaveTopHit:
            # establishing value for ABSOLUTE path used by BACK end for writing to file that serves as atom mapping markup and is called by front end on-demand
            atmMpFilePathAbs = os.path.join(self.absltAssgnSessionPath, instId, instId + instncAtmMpLbl)
            self.doRender_AtmMpList(p_ccAssgnDataStr, p_hlprDict, atmMpFilePathAbs)
        ##
        ############################################################################################################################################################
        ############################################################################################################################################################

        ############################################################################################################################################################
        #  3D JMOL renderings
        ############################################################################################################################################################
        if not p_bRerun:
            self.__renderInstance3dViews(p_ccAssgnDataStr, p_hlprDict)
        ##

        ############################################################################################################################################################
        # ##################################                     END creating "single instance" view                                 ##############################
        ############################################################################################################################################################
        ##
        if self.__verbose:
            self.__lfh.write("+ChemCompAssignDepict.doRender_InstanceProfile() ----- reached end for instId: %s\n" % instId)

    def doRender_BatchRslts(self, p_entityId, p_instncIdLst, p_ccAssgnDataStr, p_linkInfoMap, p_tmpltPth):
        ''' Render "Condensed Batch Search Report"
            An abbreviated version of the Batch Chem Comp Assign search results used for
             display within the "all-instances" profile section of the entity browser.

            :Params:

                + ``p_entityId``: ID of ligand group for which profile is being generated
                + ``p_instncIdLst``: list of instance IDs which had been selected for processsing via the Entity Browser
                + ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                + ``p_linkInfoMap``: inter-residue linkage inforation
                + ``p_tmpltPth``: path to repository of HTML templates on the server

            :Returns:
                ``oL``: output list consisting of HTML markup
        '''
        myD = {}
        oL = []
        #
        # p_instncIdLst.sort(key=lambda k: k.split('_')[2])
        if (self.__verbose):
            for k in p_instncIdLst:
                self.__lfh.write("+ChemCompAssignDepict.doRender_BatchRslts() instId key %30s\n" % k)
        for instId in p_instncIdLst:

            grp = p_ccAssgnDataStr.getAuthAssignment(instId)
            #
            if grp.upper() == p_entityId.upper():
                #
                #    populate dictionary of elements to populate html template
                #
                bgcolor = ""
                instWarnClass = ""
                processedInstId = instId
                if instId in p_linkInfoMap:
                    retD = self.__processWarningMsg(p_linkInfoMap[instId])
                    bgcolor = 'style="background-color:#0FF;"'
                    instWarnClass = retD["warn_class"]
                    processedInstId = retD["prefix"] + instId + retD["suffix"]
                #
                myD['p_instanceid'] = processedInstId
                myD['bgcolor'] = bgcolor
                myD['inst_warn_class'] = instWarnClass
                myD['instanceid'] = instId
                myD['auth_assgnd_grp'] = p_ccAssgnDataStr.getAuthAssignment(instId)
                #
                topHit = p_ccAssgnDataStr.getBatchBestHitId(instId)
                #
                if topHit == 'None':
                    myD['top_hit_ccid'] = topHit
                else:
                    myD['top_hit_ccid'] = '<a href="/ccmodule/cc-view.html?ccid=' + topHit + '" target="_blank" title="Profile in Viewer">' + topHit + '</a>'
                #
                hlprD = self.__processWarningMsg(p_ccAssgnDataStr.getCcAssgnWarning(instId))
                #
                myD['status_warn_class'] = hlprD['warn_class']
                statusPrefix = hlprD['prefix']
                statusSuffix = hlprD['suffix']
                #
                myD['status'] = statusPrefix + str(p_ccAssgnDataStr.getBatchBestHitStatus(instId)) + statusSuffix
                #
                myD['score_warn_class'] = ""
                scorePrefix = ''
                scoreSuffix = ''
                #
                if topHit != 'None':
                    # when not "None" we capture any existing match warning messages
                    topHitTupl = p_ccAssgnDataStr.getTopHitsList(instId)[0]
                    if topHit.upper() == topHitTupl[0].upper():
                        wrningMsg = topHitTupl[2]
                        retD = self.__processWarningMsg(wrningMsg)
                        myD['score_warn_class'] = retD['warn_class']
                        scorePrefix = retD['prefix']
                        scoreSuffix = retD['suffix']
                #
                myD['compositescore'] = scorePrefix + str(p_ccAssgnDataStr.getBatchBestHitScore(instId)) + scoreSuffix
                #
                topHitStatus = p_ccAssgnDataStr.getBatchBestHitStatus(instId)
                annotAssgnmnt = p_ccAssgnDataStr.getAnnotAssignment(instId)
                if topHitStatus.lower() == 'passed':
                    annotAssgnmnt = '<span class="ccid_assgnmnt">(' + topHit + ')</span>'
                else:
                    if annotAssgnmnt != 'Not Assigned':
                        annotAssgnmnt = '<span class="ccid_assgnmnt">' + annotAssgnmnt + '</span>'
                myD['prcssng_status'] = annotAssgnmnt
                #
                #
                oL.append(self.processTemplate(tmpltPth=p_tmpltPth, fn="cc_entity_batch_rslts_tmplt.html", parameterDict=myD))

        # end of iterating through all ligand instances

        return oL

    def doRender_InstanceNewCandidate(self, p_instId, p_ccId, p_ccAssgnDataStr, p_reqOb):
        ''' For given instance id, generates html fragment used for representing new candidate chem comp reference
            (requested ad-hoc by user) in the viz compare grid-->these html files are written to files on server
            for AJAX load into the web-page

            :Params:

                + ``p_instId``: ID of ligand instance for which new candidate is being requested
                + ``p_ccId``: Chem Comp ID of the new reference candidate being requested
                + ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                + ``p_reqOb``:  Web Request object
        '''
        if self.__verbose:
            self.__lfh.write("+ChemCompAssignDepict.doRender_InstanceNewCandidate() starting for instId %s and non-candidate ccid %s\n" % (p_instId, p_ccId))
        #
        bIsWorkflow = self.isWorkflow(p_reqOb)
        #
        depId = str(p_reqOb.getValue("identifier"))
        # wfInstId = str(p_reqOb.getValue("instance")).upper()
        sessionId = p_reqOb.getSessionId()
        # fileSource = str(p_reqOb.getValue("filesource")).lower()
        htmlTmpltPth = p_reqOb.getValue("TemplatePath")
        #
        depId = self.__formatDepositionDataId(depId, bIsWorkflow)
        #
        strReplDict = {}
        checked = ''
        #
        strReplDict['assgn_sess_path_rel'] = self.rltvAssgnSessionPath
        #
        for (ccId, name, formula) in p_ccAssgnDataStr.getNewCandidatesList(p_instId):
            if self.__verbose:
                self.__lfh.write("+ChemCompAssignDepict.doRender_InstanceNewCandidate() looping thru non-candidates. Found entry for %s with name %s and formula %s\n" %
                                 (ccId, name, formula))
            if ccId == p_ccId:
                # using strReplDict to supply text substitution content for both cc_instnc_match_rslts_tbl_tmplt.html and cc_viz_cmp_li_tmplt.html in this loop
                strReplDict['instanceid'] = p_instId
                strReplDict['sessionid'] = sessionId
                strReplDict['ccid'] = ccId
                strReplDict['cc_name'] = name
                strReplDict['cc_name_displ'] = self.truncateForDisplay(name)
                strReplDict['cc_formula'] = formula
                strReplDict['cc_formula_displ'] = self.truncateForDisplay(formula)
                strReplDict['checked'] = checked
                strReplDict['3dpath_ref'] = os.path.join('/', strReplDict['assgn_sess_path_rel'], 'rfrnc_reports', p_ccId, p_ccId)
                strReplDict['2dpath_labld_w_hy_ref'] = os.path.join('/', strReplDict['assgn_sess_path_rel'], p_instId, 'image', p_ccId + '_Big.svg')
                # strReplDict['2dpath_labld_w_hy_ref'] = os.path.join('/',strReplDict['assgn_sess_path_rel'],'rfrnc_reports',p_ccId,p_ccId+'_D3L3.gif')
                strReplDict['2dpath_labld_no_hy_ref'] = os.path.join('/', strReplDict['assgn_sess_path_rel'], p_instId, 'image', p_ccId + '_Big.svg')
                # strReplDict['2dpath_labld_no_hy_ref'] = os.path.join('/',strReplDict['assgn_sess_path_rel'],'rfrnc_reports',p_ccId,p_ccId+'_D3L1.gif')
                strReplDict['jmol_code_base'] = self.jmolCodeBase
                # '''
                # ##########################################################################################################
                # # populate template used for displaying instance match results for this instance and append contents to oL
                # #    this template contains placeholders for "instanceid", "ccid", "score", and "checked"
                # ##########################################################################################################
                # oL.append( self.processTemplate(tmpltPth=p_tmpltPth, fn="cc_instnc_match_rslts_tbl_tmplt.html", parameterDict=strReplDict))
                # #
                # '''
                #################################################################################################
                # also populate templates used for displaying chem comp references in viz compare grid
                #################################################################################################
                htmlPathAbs = os.path.join(self.absltAssgnSessionPath, p_instId)
                jmolPathAbs = os.path.join(self.absltAssgnSessionPath, p_instId)
                htmlFilePathAbs = os.path.join(htmlPathAbs, p_ccId + '_viz_cmp_li.html')
                # atmMpFilePathAbs = os.path.join(htmlPathAbs,p_ccId+'_ref_atm_mp_li.html')
                jmolFilePathAbs = os.path.join(jmolPathAbs, p_ccId + '_ref_jmol.html')
                #
                #################################################################################################
                # populate "cc_viz_cmp_li_tmplt.html"
                #    which contains placeholders for "instanceid", "ccid",and "assgn_sess_path_rel"
                #################################################################################################
                #
                # # added by ZF.
                strReplDict['2dpath'] = os.path.join('/', strReplDict['assgn_sess_path_rel'], p_instId, 'image', p_ccId + '.svg')
                if not os.path.exists(htmlPathAbs):
                    os.makedirs(htmlPathAbs)
                fp = open(htmlFilePathAbs, 'w')
                fp.write("%s" % self.processTemplate(tmpltPth=os.path.join(htmlTmpltPth, self.__pathSnglInstcCmprTmplts),
                                                     fn="cc_viz_cmp_li_tmplt_newcandidt.html", parameterDict=strReplDict))
                fp.close()
                #
                # '''
                # #################################################################################################
                # # call method to populate "cc_ref_atm_mp_li_tmplt.html"
                # #    which contains placeholders for "instanceid", "ccid"
                # #################################################################################################
                # self.doRender_AtmMpList(instId, p_ccAssgnDataStr, p_topSessionPth, p_tmpltPth, atmMpFilePathAbs, ccid)
                # '''
                #################################################################################################
                #
                #################################################################################################
                # populate "cc_ref_jmol_tmplt.html"
                #    which contains placeholders for "pct", "index", "a", and "3dpath_ref"
                #################################################################################################
                #
                #
                if not os.path.exists(jmolPathAbs):
                    os.makedirs(jmolPathAbs)
                fp = open(jmolFilePathAbs, 'w')

                fp.write("%s" % self.processTemplate(tmpltPth=os.path.join(htmlTmpltPth, self.__pathSnglInstcJmolTmplts), fn="cc_ref_jmol_tmplt.html", parameterDict=strReplDict))
                fp.close()
                #
                #################################################################################################
        # DONE

    def doRender_AtmMpList(self, p_ccAssgnDataStr, p_hlprDict, p_atmMpHtmlPathAbs, p_ccId=None):
        ''' Generate file containing html fragment that represents atom listing for the given reference chem component

            :Params:

                + ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                + ``p_hlprDict``: dictionary of data to be used for subsitution/population of HTML template(s)
                + ``p_atmMpHtmlPathAbs``: path to be used for writing out HTML fragment file on the server
                + ``p_ccId``: ChemComp ID, if present indicates that HTML being generated for a dictionary reference

        '''
        ##
        instId = p_hlprDict['instanceid']
        tmpltPth = p_hlprDict['html_template_path']
        ##
        atmMpLst = []
        tmpltFile = ''
        #
        oL = []
        #
        if p_ccId is None:
            # atmMpLst = (p_ccAssgnDataStr.getAtomMapDict(p_instId))[( (p_ccAssgnDataStr.getAtomMapDict(p_instId)).keys() )[0]]
            atomMapDict = p_ccAssgnDataStr.getAtomMapDict(instId)
            if atomMapDict:
                listOfTopHitsForInstId = list((p_ccAssgnDataStr.getAtomMapDict(instId)).keys())
                if len(listOfTopHitsForInstId) > 0:
                    topHitForInstId = listOfTopHitsForInstId[0]
                    atmMpLst = atomMapDict[topHitForInstId]
            tmpltFile = "cc_instnc_atm_mp_li_tmplt.html"
        else:
            atmMpLst = (p_ccAssgnDataStr.getAtomMapDict(instId))[p_ccId]
            tmpltFile = "cc_ref_atm_mp_li_tmplt.html"
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompAssignDepict.doRender_AtmMpList() starting for instId %s and candidate ccid %s\n" % (instId, p_ccId))
        #
        atm = ''
        for instAtm, refAtm in atmMpLst:
            #
            if p_ccId is None:
                atm = instAtm
            else:
                atm = refAtm
            #
            p_hlprDict['atom'] = atm
            #
            oL.append(self.processTemplate(tmpltPth=os.path.join(tmpltPth, self.__pathInstncsVwTmplts), fn=tmpltFile, parameterDict=p_hlprDict))
        # end of iterating through all atm map entries for the ref ccId
        #
        fp = open(p_atmMpHtmlPathAbs, 'w')
        fp.write("%s" % ('\n'.join(oL)))
        fp.close()

    def doRender_InstanceAssgnDrpDwn(self, p_entityId, p_instncIdLst, p_ccAssgnDataStr, p_tmpltPth):
        ''' Generates HTML markup comprising the dropdown list that controls display of content in
            the "All Instances" table used for assigning a given candidate chem comp ID to
            set of all instances currently displayed in the interface.

            :Params:

                + ``p_entityId``: chem comp ID representing ligand group
                + ``p_instncIdLst``: list of instance IDs for ligands currently being processed in the group
                + ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                + ``p_tmpltPth``: path to repository of HTML templates on the server

        '''
        myD = {}
        oL = []
        #
        # p_instncIdLst.sort(key=lambda k: k.split('_')[2])
        # if (self.__verbose):
        #    for k in p_instncIdLst:
        #        self.__lfh.write("+ChemCompAssignDepict.doRender_InstanceAssgnDrpDwn() instId key %30s\n" % k)

        for instId in p_instncIdLst:

            grp = p_ccAssgnDataStr.getAuthAssignment(instId)
            #
            if grp.upper() == p_entityId.upper():
                #
                #    populate dictionary of elements to populate html template
                #
                myD['instanceid'] = instId
                oL.append(self.processTemplate(tmpltPth=p_tmpltPth, fn="cc_all_instncs_assgn_drpdwn_tmplt.html", parameterDict=myD))

        # end of iterating through all instanc IDs

        return oL

    def doRender_InstanceAssgnRows(self, p_entityId, p_instncIdLst, p_ccAssgnDataStr, p_tmpltPth):
        ''' Generates HTML markup comprising the rows that populate the "All Instances" table used for assigning
            a given candidate chem comp ID to set of all instances currently displayed in the interface.

            :Params:

                + ``p_entityId``: chem comp ID representing ligand group
                + ``p_instncIdLst``: list of instance IDs for ligands currently being processed in the group
                + ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                + ``p_tmpltPth``: path to repository of HTML templates on the server
        '''
        myD = {}
        oL = []
        #
        # p_instncIdLst.sort(key=lambda k: k.split('_')[2])
        if self.__verbose:
            for k in p_instncIdLst:
                self.__lfh.write("+ChemCompAssignDepict.doRender_InstanceAssgnRows() instId key %30s\n" % k)
        cnt = 0
        for instId in p_instncIdLst:

            grp = p_ccAssgnDataStr.getAuthAssignment(instId)
            #

            if grp.upper() == p_entityId.upper():
                #
                #    populate dictionary of elements to populate html template
                #
                cnt = cnt + 1
                if cnt == 1:
                    style = ''
                else:
                    style = 'style="display: none;"'  # for every instance after the first instance, hide the row by default
                #
                myD['showstyle'] = style
                myD['instanceid'] = instId
                myD['ligand_grp'] = grp
                #
                if grp in p_ccAssgnDataStr.getDrtyGrpList() or not len(p_ccAssgnDataStr.getTopHitsList(instId)):
                    disabled = 'disabled="disabled"'
                else:
                    disabled = ''
                myD['disabled'] = disabled
                #
                countr = 0
                for tupL in p_ccAssgnDataStr.getTopHitsList(instId):

                    myD['candidate_ccid'] = tupL[0]
                    # template requires "candidate_ccid", "instanceid", and "showstyle" substitution parameters
                    oL.append(self.processTemplate(tmpltPth=p_tmpltPth, fn="cc_all_instncs_assgn_row_tmplt.html", parameterDict=myD))
                    countr += 1

                if countr == 0:
                    myD['candidate_ccid'] = "None"
                    if self.__verbose:
                        self.__lfh.write("+ChemCompAssignDepict.doRender_InstanceAssgnRows() candidate_ccid for %s set to 'None'\n" % instId)
                    # template requires "candidate_ccid", "instanceid", and "showstyle" substitution parameters
                    oL.append(self.processTemplate(tmpltPth=p_tmpltPth, fn="cc_all_instncs_assgn_row_tmplt.html", parameterDict=myD))

        # end of iterating through all instanc IDs

        return oL

    def doRender_EntityGrpOnRerunSrch(self, p_entityGrp, p_instncIdLst, p_ccAssgnDataStr, p_linkInfoMap, p_reqOb):
        ''' Render "Entity Group Profile" for given ligand group for which search was rerun
            A given entity group section consists of the following subsections:
                - an "all-instances" section, providing perspective/actions on all ligand instances within a group
                - a "single-instance" section, providing perspective/actions on a single ligand instance within the group

            :Params:

                + ``p_entityGrp``: Entity group for which chem comp assignment search was rerun
                + ``p_instncIdLst``: list of instance IDs which had been selected for processsing via the Entity Browser
                + ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                + ``p_linkInfoMap``: inter-residue linkage inforation
                + ``p_reqObj``: Web Request object
        '''
        bIsWorkflow = self.isWorkflow(p_reqOb)
        #
        depId = str(p_reqOb.getValue("identifier"))
        wfInstId = str(p_reqOb.getValue("instance")).upper()
        sessionId = p_reqOb.getSessionId()
        fileSource = str(p_reqOb.getValue("filesource")).lower()
        htmlTmpltPth = p_reqOb.getValue("TemplatePath")
        #
        depId = self.__formatDepositionDataId(depId, bIsWorkflow)
        #
        hlprDict = {}
        oL = []
        # establish helper dictionary of data used for populating html templates
        hlprDict['depositionid'] = depId
        hlprDict['instance'] = wfInstId   # i.e. workflow instance ID
        hlprDict['filesource'] = fileSource
        hlprDict['sessionid'] = sessionId
        hlprDict['identifier'] = depId
        hlprDict['html_template_path'] = htmlTmpltPth
        hlprDict['jmol_code_base'] = self.jmolCodeBase
        # call method to generate html content for "All Instances" profile
        self.doRender_AllInstncsProfile(p_entityGrp, p_instncIdLst, p_ccAssgnDataStr, p_linkInfoMap, hlprDict, oL)

        for instId in p_instncIdLst:
            # for each instance in group, call method to generate html content for "Single Instance" profile
            instWarnStyle = ""
            if instId in p_linkInfoMap:
                instWarnStyle = 'style="color:red"'
            #
            hlprDict['inst_warn_style'] = instWarnStyle
            hlprDict['instanceid'] = instId
            self.doRender_InstanceProfile(p_ccAssgnDataStr, hlprDict, True)
            #
            #################################################################################################
            # while we're iterating through the ligand instances, we will
            # also populate "cc_all_instncs_viz_cmp_li_tmplt.html" template used for displaying ligand instances in viz compare grid
            # and which contains placeholders for "instanceid" and "2dpath"
            #################################################################################################
            htmlPathAbs = os.path.join(self.absltAssgnSessionPath, instId)
            htmlFilePathAbs = os.path.join(htmlPathAbs, instId + '_viz_cmp_li.html')
            fp = open(htmlFilePathAbs, 'w')
            fp.write("%s" % self.processTemplate(tmpltPth=htmlTmpltPth, fn="cc_all_instncs_viz_cmp_li_tmplt.html", parameterDict=hlprDict))
            fp.close()
            #
            oL.append(self.processTemplate(tmpltPth=os.path.join(htmlTmpltPth, self.__pathSnglInstcTmplts), fn="cc_instnc_disp_tmplt.html", parameterDict=hlprDict))

        rerunHtmlPathAbs = os.path.join(self.absltAssgnSessionPath, "entity_grp_rerun_srchs", p_entityGrp)
        rerunHtmlFilePathAbs = os.path.join(rerunHtmlPathAbs, p_entityGrp + "_rerun_srch_entitygrp_profile.html")
        if not os.access(rerunHtmlPathAbs, os.F_OK):
            try:
                os.makedirs(rerunHtmlPathAbs)
            except:  # noqa: E722 pylint: disable=bare-except
                if (self.__verbose):
                    self.__lfh.write("+ChemCompAssignDepict.doRender_EntityGrpOnRerunSrch() ----- unable to create directory for grp rerun search html output for %s\n" % p_entityGrp)
                return False
        #
        fp = open(rerunHtmlFilePathAbs, 'w')
        fp.write("%s" % '\n'.join(oL))
        fp.close()
        #
        return True

    def doRender_3dEnvironView(self, p_reqObj, p_bIsWorkflow):
        """ Within instance search view of chem comp assign interface
            launch 3D viewer of experimental chem component within
            author's entire structure (in separate browser window/tab)

            :Params:

                + ``p_reqObj``: Web Request object
                + ``p_bIsWorkflow``: boolean indicating whether or not operating in Workflow Manager environment

            :Returns:
                ``oL``: output list consisting of HTML markup
        """
        #
        sessionId = p_reqObj.getSessionId()
        instId = str(p_reqObj.getValue("instanceid")).upper()
        wfInstnc = str(p_reqObj.getValue("instance")).upper()
        depId = str(p_reqObj.getValue("identifier")).upper()
        fileSource = str(p_reqObj.getValue("filesource")).lower()
        tmpltPath = p_reqObj.getValue("TemplatePath")
        #
        oL = []
        myD = {}
        instIdPieces = instId.split('_')
        chainId = instIdPieces[1]
        residueNum = instIdPieces[3]
        #
        depId = self.__formatDepositionDataId(depId, p_bIsWorkflow)
        #
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompAssignDepict.doRender_3dEnvironView() starting\n")
            self.__lfh.write("+ChemCompAssignDepict.doRender_3dEnvironView() identifier   %s\n" % depId)
            self.__lfh.write("+ChemCompAssignDepict.doRender_3dEnvironView() instance     %s\n" % instId)
            self.__lfh.write("+ChemCompAssignDepict.doRender_3dEnvironView() file source  %s\n" % fileSource)
            self.__lfh.write("+ChemCompAssignDepict.doRender_3dEnvironView() sessionId  %s\n" % sessionId)
            self.__lfh.flush()

        #
        # create dictionary of content that will be used to populate HTML template
        #
        myD['instanceid'] = instId
        myD['sessionid'] = sessionId
        myD['instance'] = wfInstnc
        myD['filesource'] = fileSource
        myD['identifier'] = depId
        myD['3dpath'] = os.path.join(self.rltvSessionPath, depId + '-jmol-mdl')
        myD['residue_num'] = residueNum
        myD['chain_id'] = chainId
        myD['jmol_code_base'] = self.jmolCodeBase
        #
        oL.append(self.processTemplate(tmpltPth=os.path.join(tmpltPath, self.__pathSnglInstcJmolTmplts), fn="cc_instnc_environ_vw_jmol_tmplt.html", parameterDict=myD))

        return oL

    def doRender_dpstrInfoView(self, p_reqObj, p_bIsWorkflow):
        """ Within instance search view of chem comp assign interface
            launch view of depositor provided info in separate browser window/tab)

            :Params:

                + ``p_reqObj``: Web Request object
                + ``p_bIsWorkflow``: boolean indicating whether or not operating in Workflow Manager environment

            :Returns:
                ``oL``: output list consisting of HTML markup
        """
        #
        sessionId = p_reqObj.getSessionId()
        authAssngdGrp = str(p_reqObj.getValue("auth_assgnd_grp")).upper()
        wfInstnc = str(p_reqObj.getValue("instance")).upper()
        depId = str(p_reqObj.getValue("identifier")).upper()
        fileSource = str(p_reqObj.getValue("filesource")).lower()
        tmpltPath = p_reqObj.getValue("TemplatePath")
        #
        oL = []
        lclDict = {}
        #
        depId = self.__formatDepositionDataId(depId, p_bIsWorkflow)
        #
        if (self.__verbose):
            self.__lfh.write("--------------------------------------------\n")
            self.__lfh.write("+ChemCompAssignDepict.doRender_dpstrInfoView() starting\n")
            self.__lfh.write("+ChemCompAssignDepict.doRender_dpstrInfoView() identifier   %s\n" % depId)
            self.__lfh.write("+ChemCompAssignDepict.doRender_dpstrInfoView() authAssngdGrp     %s\n" % authAssngdGrp)
            self.__lfh.write("+ChemCompAssignDepict.doRender_dpstrInfoView() file source  %s\n" % fileSource)
            self.__lfh.write("+ChemCompAssignDepict.doRender_dpstrInfoView() sessionId  %s\n" % sessionId)
            self.__lfh.flush()

        #
        # create dictionary of content that will be used to populate HTML template
        #
        lclDict['auth_assgnd_grp'] = authAssngdGrp
        lclDict['sessionid'] = sessionId
        lclDict['instance'] = wfInstnc
        lclDict['filesource'] = fileSource
        lclDict['identifier'] = depId
        lclDict['display_dpstr_info'] = "displaynone"
        #
        # ## dpstr info handling ###
        lclDict['display_dpstr_info'] = "displaynone"
        lclDict['display_dscrptr_vw_btn'] = "displaynone"
        naStr = "n/a"
        #
        for keyName in self.__dpstrInfoKeyList:
            lclDict[keyName] = naStr
        ccAssgnDataStr = ChemCompAssignDataStore(p_reqObj, verbose=True, log=self.__lfh)
        if authAssngdGrp in ccAssgnDataStr.getGlbllyRslvdGrpList():
            self.__packDpstrViewDict(authAssngdGrp, ccAssgnDataStr, lclDict)
        for keyName in self.__dpstrInfoKeyList:
            lclDict[keyName + "_displ"] = "displaynone" if lclDict[keyName] == naStr else ""
        ###########################

        oL.append(self.processTemplate(tmpltPth=os.path.join(tmpltPath, self.__pathAllInstcs), fn="cc_dpstr_info_vw_tmplt.html", parameterDict=lclDict))

        if self.__verbose and self.__debug:
            self.__lfh.write("+ChemCompAssignDepict.doRender_dpstrInfoView() ----- output HTML %r\n" % oL)

        return oL

    ################################################################################################################
    # ------------------------------------------------------------------------------------------------------------
    #      Private helper methods
    # ------------------------------------------------------------------------------------------------------------
    #
    def __packDpstrViewDict(self, p_grpId, p_dataStore, p_strReplDict):
        className = self.__class__.__name__
        methodName = inspect.currentframe().f_code.co_name
        self.__lfh.write("+%s.%s() ------ STARTING ------\n" % (className, methodName))

        # ## dpstr info handling ###
        naStr = "n/a"
        contentTypeDict = self.__cI.get('CONTENT_TYPE_DICTIONARY')

        ligType = p_dataStore.getDpstrCcType(p_grpId)
        altLigId = p_dataStore.getDpstrAltCcId(p_grpId)
        chemCompName = p_dataStore.getDpstrCcName(p_grpId)
        chemCompFrmla = p_dataStore.getDpstrCcFrmla(p_grpId)
        chemCompDescriptor = p_dataStore.getDpstrCcDscrptrStr(p_grpId)
        chemCompDescriptorType = p_dataStore.getDpstrCcDscrptrType(p_grpId)
        chemCompDetails = p_dataStore.getDpstrComments(p_grpId)
        p_strReplDict['display_dpstr_info'] = ""
        p_strReplDict['dpstr_info_name'] = chemCompName if chemCompName != '?' else naStr
        p_strReplDict['dpstr_info_alt_comp_id'] = altLigId if altLigId != '?' else naStr
        p_strReplDict['dpstr_info_frmla'] = chemCompFrmla if chemCompFrmla != '?' else naStr

        p_strReplDict['dpstr_info_dscrptr'] = chemCompDescriptor if chemCompDescriptor != '?' else naStr
        p_strReplDict['dpstr_info_dscrptr_type'] = chemCompDescriptorType if chemCompDescriptorType != '?' else naStr

        if chemCompDescriptorType and chemCompDescriptorType.lower() == 'smiles':

            try:
                # creating 2D image representation of the SMILES string
                fileName = p_grpId + "_dscrptr_depict.svg"
                toLclSessnImgPth = os.path.join(self.absltAssgnSessionPath, fileName)
                oem = OeBuildMol(verbose=self.__verbose, log=self.__lfh)
                smilesImportOk = oem.importSmiles(chemCompDescriptor.strip('"'))

                if smilesImportOk:
                    oed = OeDepict(verbose=self.__verbose, log=self.__lfh)
                    oed.setMolTitleList([('p_grpId', oem, 'Depiction of Submitted ' + chemCompDescriptorType.upper() + ' String')])
                    oed.setDisplayOptions(labelAtomName=False, labelAtomCIPStereo=True, labelAtomIndex=False, labelBondIndex=False, bondDisplayWidth=1.0)
                    oed.setGridOptions(rows=1, cols=1)
                    oed.prepare()
                    oed.write(toLclSessnImgPth)

                    if self.__verbose :
                        self.__lfh.write("+%s.%s() - Generated image file [%s] from %s string [%s].\n" %
                                         (className, methodName, toLclSessnImgPth, chemCompDescriptorType.upper(), chemCompDescriptor))

                    p_strReplDict['display_dscrptr_vw_btn'] = ""
                    p_strReplDict['dpstr_info_dscrptr_img_pth'] = os.path.join(self.rltvAssgnSessionPath, fileName)

                else:
                    # problem with importing SMILES string
                    p_strReplDict['display_dscrptr_vw_btn'] = "displaynone"
                    p_strReplDict['dpstr_info_dscrptr_img_pth'] = ""
                    if self.__verbose:
                        self.__lfh.write("+%s.%s() - Failed to generate image file [%s] from %s string [%s].\n" %
                                         (className, methodName, toLclSessnImgPth, chemCompDescriptorType.upper(), chemCompDescriptor))
                        traceback.print_exc(file=self.__lfh)
                    #
            except:  # noqa: E722 pylint: disable=bare-except
                # problem with importing SMILES string
                p_strReplDict['display_dscrptr_vw_btn'] = "displaynone"
                p_strReplDict['dpstr_info_dscrptr_img_pth'] = ""
                if self.__verbose:
                    self.__lfh.write("+%s.%s() - Failed to generate image file [%s] from %s string [%s].\n" %
                                     (className, methodName, toLclSessnImgPth, chemCompDescriptorType.upper(), chemCompDescriptor))
                    traceback.print_exc(file=self.__lfh)
                #
        else:
            p_strReplDict['display_dscrptr_vw_btn'] = "displaynone"
            p_strReplDict['dpstr_info_dscrptr_img_pth'] = ""
            if self.__verbose:
                self.__lfh.write("+%s.%s() - no SMILES string submitted for this ligand ID [%s].\n" % (className, methodName, p_grpId))

        p_strReplDict['dpstr_info_type'] = ligType if ligType != '?' else naStr
        p_strReplDict['dpstr_info_details'] = chemCompDetails if chemCompDetails != '?' else naStr

        for contentType in contentTypeDict['component-image'][0]:
            imageFileList = p_dataStore.getDpstrUploadFile(p_grpId, contentType)
            if self.__verbose and self.__debug:
                self.__lfh.write("\n++++ChemCompAssignDepict.__packDpstrViewDict() ----- contentTypeDict['component-image'][0] %r\n" % contentTypeDict['component-image'][0])
                self.__lfh.write("\n++++ChemCompAssignDepict.__packDpstrViewDict() ----- imageFileList %r\n" % imageFileList)

            if imageFileList is not None:
                fileName = imageFileList[0]
                p_strReplDict['dpstr_info_image'] = fileName
                p_strReplDict['dpstr_info_image_lnk'] = '<a href="' + os.path.join(self.rltvAssgnSessionPath, fileName) + '" target="_blank">' + fileName + '</a>'

        # for any component definition files uploaded need to take into account "cif" extensioned files provided by depositor
        # even though "cif" is no longer officially part of 'component-definition' enum in ConfigInfoData
        ccdefTypes = (contentTypeDict['component-definition'][0])[:]
        ccdefTypes.append('cif')
        self.__lfh.write("\n++++ChemCompAssignDepict.__packDpstrViewDict() ----- ccdefTypes %r\n" % ccdefTypes)

        for ccdefType in ccdefTypes:
            defnFileList = p_dataStore.getDpstrUploadFile(p_grpId, ccdefType)
            if defnFileList is not None:
                fileName = defnFileList[0]
                p_strReplDict['dpstr_info_defn'] = fileName
                p_strReplDict['dpstr_info_defn_lnk'] = '<a href="' + os.path.join(self.rltvAssgnSessionPath, fileName) + '" target="_blank">' + fileName + '</a>'

        sketchFileList = p_dataStore.getDpstrSketchFile(p_grpId)
        self.__lfh.write("\n++++ChemCompAssignDepict.__packDpstrViewDict() ----- sketchFileList %r\n" % sketchFileList)
        if sketchFileList is not None:
            fileName = sketchFileList[0]
            p_strReplDict['dpstr_info_sketch_sdf'] = fileName
            p_strReplDict['dpstr_info_sketch_sdf_lnk'] = '<a href="' + os.path.join(self.rltvAssgnSessionPath, fileName) + '" target="_blank">' + fileName + '</a>'
            p_strReplDict['dpstr_info_sketch_sdf_img_pth'] = os.path.join(self.rltvAssgnSessionPath, p_grpId + ".svg")

    def __renderInstance3dViews(self, p_ccAssgnDataStr, p_hlprDict):
        ''' For given ligand instance id, generates html fragments used for 3D jmol viewing in the "single-instance view"
            and "all-instances view" comparison panels-->these are written to files on server to be used on demand

            :Params:

                + ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                + ``p_hlprDict``: dictionary of data to be used for subsitution/population of an HTML template
        '''
        ##
        instId = p_hlprDict['instanceid']
        depId = str(p_hlprDict['depositionid']).upper()
        htmlTmpltPth = p_hlprDict['html_template_path']
        htmlTmpltPth_SnglInstnc = os.path.join(htmlTmpltPth, self.__pathSnglInstcJmolTmplts)
        htmlTmpltPth_AllInstnc = os.path.join(htmlTmpltPth, self.__pathAllInstncsJmolTmplts)
        ##
        #
        # interrogate ChemCompAssign DataStore for necessary data items
        authAssignedGrp = p_ccAssgnDataStr.getAuthAssignment(instId)
        topHitCcId = p_ccAssgnDataStr.getBatchBestHitId(instId)

        # determine whether or not a top candidate hit has been found for this instance
        if topHitCcId == "None":
            bHaveTopHit = False
        else:
            bHaveTopHit = True
        ##
        sPathRel = self.rltvAssgnSessionPath
        s3dpathEnviron = self.rltvSessionPath
        ##
        instIdPieces = instId.split('_')
        chainId = instIdPieces[1]
        residueNum = instIdPieces[3]
        ##
        p_hlprDict['3dpath'] = os.path.join(sPathRel, instId, 'report', authAssignedGrp)
        p_hlprDict['3dpath_environ'] = os.path.join(s3dpathEnviron, depId + '-jmol-mdl')
        p_hlprDict['residue_num'] = residueNum
        p_hlprDict['chain_id'] = chainId
        # establishing values for ABSOLUTE paths used by BACK end for writing to files that serve as additional resources that may be called by front end on-demand
        jmolFilePathAbs_SnglInstVw = os.path.join(self.absltAssgnSessionPath, instId, instId + "instnc_jmol_instVw.html")
        environJmolFilePathAbs_SnglInstVw = os.path.join(self.absltAssgnSessionPath, instId, instId + "instnc_environ_jmol_instVw.html")
        stndalnJmolFilePathAbs_SnglInstVw = os.path.join(self.absltAssgnSessionPath, instId, instId + "instnc_stndaln_jmol_instVw.html")
        jmolFilePathAbs_AllInstVw = os.path.join(self.absltAssgnSessionPath, instId, instId + "instnc_jmol_allInstVw.html")
        environJmolFilePathAbs_AllInstVw = os.path.join(self.absltAssgnSessionPath, instId, instId + "instnc_environ_jmol_allInstVw.html")
        stndalnJmolFilePathAbs_AllInstVw = os.path.join(self.absltAssgnSessionPath, instId, instId + "instnc_stndaln_jmol_allInstVw.html")
        #
        if bHaveTopHit:
            # set default templates to be used
            instncJmolTmplt = "cc_instnc_jmol_tmplt.html"
            instncJmolAivwTmplt = "cc_instnc_jmol_aivw_tmplt.html"
            ################################################################################
            # when there is a top hit, we also need to generate "ready-made" html markup
            # for option to view author's instance within the structure environment (because default mode in presence of top hit is in "stand-alone")
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
        else:
            # set default templates to be used
            instncJmolTmplt = "cc_instnc_jmol_nomatch_tmplt.html"
            instncJmolAivwTmplt = "cc_instnc_jmol_aivw_nomatch_tmplt.html"
            ################################################################################
            # when there is no top hit, we also need to generate "ready-made" html markup
            # for option to view author's instance in "standalone" mode (because default mode in absence of top hit is "in environment") if the user so chooses
            # (this was found necessary due to Java security access
            # restrictions encountered in Mac/Firefox scenarios)
            #    ===    single instance stndaln view    ===
            fp = open(stndalnJmolFilePathAbs_SnglInstVw, 'w')
            fp.write("%s" % self.processTemplate(tmpltPth=htmlTmpltPth_SnglInstnc, fn="cc_instnc_stndaln_jmol_nomatch_tmplt.html", parameterDict=p_hlprDict))
            fp.close()
            #    ===    all instance stndaln view    ===
            fp = open(stndalnJmolFilePathAbs_AllInstVw, 'w')
            fp.write("%s" % self.processTemplate(tmpltPth=htmlTmpltPth_AllInstnc, fn="cc_instnc_stndaln_jmol_aivw_nomatch_tmplt.html", parameterDict=p_hlprDict))
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

    def __renderInstanceMatchRslts(self, p_ccAssgnDataStr, p_hlprDict):
        ''' For given ligand instance id, generates:

                + html markup for "Instance Match Results Table" showing top candidate hits--> this is returned to caller of the function
                + html fragments used for representing top chem comp reference hits in the viz compare grid-->these are written to files on server to be used on demand

            :Params:

                + ``p_ccAssgnDataStr``: ChemCompAssignDataStore object representing current state of ligand matches/assignments
                + ``p_hlprDict``: dictionary of data to be used for subsitution/population of an HTML template

            :Helpers:
                wwpdb.apps.ccmodule.io.ChemCompAssignDataStore.ChemCompAssignDataStore

            :Returns:
                ``oL``: output list representing HTMl markup
        '''
        oL = []
        instId = p_hlprDict['instanceid']
        htmlTmpltPth = p_hlprDict['html_template_path']
        #
        cnt = 0
        checked = ''
        assgnChecked = ''
        assgndCcId = p_ccAssgnDataStr.getAnnotAssignment(instId)
        #

        # we are making a local copy of the p_hlprDict dictionary because while we reuse some of the key/value pairs
        # we redefine some of the key/value pairings differently for specific use in the individual reference comparison templates
        lclDict = p_hlprDict.copy()

        for ccid, cmpstscore, matchWarning, name, formula in p_ccAssgnDataStr.getTopHitsList(instId):
            cnt = cnt + 1
            if cnt == 1:
                checked = 'checked="checked"'
            else:
                checked = ''
            #
            if ccid == assgndCcId:
                assgnChecked = 'checked="checked"'
            else:
                assgnChecked = ''
            #
            # using lclDict to supply text substitution content for both cc_instnc_match_rslts_tbl_tmplt.html and cc_viz_cmp_li_tmplt.html in this loop
            lclDict['assgn_checked'] = assgnChecked
            #
            retD = self.__processWarningMsg(matchWarning)
            lclDict['score_warn_class'] = retD['warn_class']
            scorePrefix = retD['prefix']
            scoreSuffix = retD['suffix']
            #
            lclDict['score'] = scorePrefix + cmpstscore + scoreSuffix
            lclDict['ccid'] = ccid
            lclDict['cc_name'] = name
            lclDict['cc_name_displ'] = self.truncateForDisplay(name)
            lclDict['cc_formula'] = formula
            lclDict['cc_formula_displ'] = self.truncateForDisplay(formula)
            lclDict['checked'] = checked
            lclDict['index'] = cnt
            lclDict['3dpath_ref'] = os.path.join(self.rltvAssgnSessionPath, 'rfrnc_reports', ccid, ccid)
            lclDict['2dpath_labld_w_hy_ref'] = os.path.join(self.rltvSessionPath, 'assign', instId, 'image', ccid + '_Big.svg')
            # lclDict['2dpath_labld_w_hy_ref'] = os.path.join(self.rltvSessionPath, 'assign', 'rfrnc_reports', ccid,ccid + '_D3L3.gif')
            lclDict['2dpath_labld_no_hy_ref'] = os.path.join(self.rltvSessionPath, 'assign', instId, 'image', ccid + '_Big.svg')
            # lclDict['2dpath_labld_no_hy_ref'] = os.path.join(self.rltvSessionPath, 'assign', 'rfrnc_reports', ccid, ccid + '_D3L1.gif')
            #
            lclDict['a'] = '%a'
            #
            ##########################################################################################################
            # populate template used for displaying instance match results for this instance and append contents to oL
            #    this template contains placeholders for "instanceid", "ccid", "score", and "checked"
            ##########################################################################################################
            oL.append(self.processTemplate(tmpltPth=os.path.join(htmlTmpltPth, self.__pathSnglInstcTmplts), fn="cc_instnc_match_rslts_row_tmplt.html", parameterDict=lclDict))
            #
            #################################################################################################
            # while we're iterating through the candidate assignments for the given instance, we will
            # also populate templates used for displaying chem comp references in viz compare grid
            #################################################################################################
            htmlPathAbs = os.path.join(self.absltAssgnSessionPath, instId)
            jmolPathAbs = os.path.join(self.absltAssgnSessionPath, instId)
            htmlFilePathAbs = os.path.join(htmlPathAbs, ccid + '_viz_cmp_li.html')
            atmMpFilePathAbs = os.path.join(htmlPathAbs, ccid + '_ref_atm_mp_li.html')
            jmolFilePathAbs = os.path.join(jmolPathAbs, ccid + '_ref_jmol.html')
            #
            #################################################################################################
            # populate "cc_viz_cmp_li_tmplt.html"
            #    which contains placeholders for "instanceid", "ccid",and "assgn_sess_path_rel"
            #################################################################################################
            #
            #
            # added by ZF.
            lclDict['2dpath'] = os.path.join(self.rltvSessionPath, 'assign', instId, 'image', ccid + '.svg')
            #
            if not os.path.exists(htmlPathAbs):
                os.makedirs(htmlPathAbs)
            fp = open(htmlFilePathAbs, 'w')
            fp.write("%s" % self.processTemplate(tmpltPth=os.path.join(htmlTmpltPth, self.__pathSnglInstcCmprTmplts), fn="cc_viz_cmp_li_tmplt.html", parameterDict=lclDict))
            fp.close()
            #
            #################################################################################################
            # call method to populate "cc_ref_atm_mp_li_tmplt.html"
            #    which contains placeholders for "instanceid", "ccid"
            #################################################################################################
            self.doRender_AtmMpList(p_ccAssgnDataStr, lclDict, atmMpFilePathAbs, ccid)

            #################################################################################################
            #
            #################################################################################################
            # populate "cc_ref_jmol_tmplt.html"
            #    which contains placeholders for "pct", "index", "a", and "3dpath_ref"
            #################################################################################################
            #
            #
            if not os.path.exists(jmolPathAbs):
                os.makedirs(jmolPathAbs)
            fp = open(jmolFilePathAbs, 'w')

            fp.write("%s" % self.processTemplate(tmpltPth=os.path.join(htmlTmpltPth, self.__pathSnglInstcJmolTmplts), fn="cc_ref_jmol_tmplt.html", parameterDict=lclDict))
            fp.close()
            #
            #################################################################################################

        # end of iterating through all chem components

        return oL

    def __processWarningMsg(self, p_wrningMsg):
        rtrnD = {}
        rtrnD['warn_class'] = ""
        rtrnD['prefix'] = ""
        rtrnD['suffix'] = ""
        #
        if p_wrningMsg != 'n.a.' and p_wrningMsg is not None:
            rtrnD['warn_class'] = "warninfo"
            rtrnD['prefix'] = '<a href="#" title="SUPPLEMENTAL INFO:<br />' + p_wrningMsg + '" onclick="return false">'
            rtrnD['suffix'] = '</a>'
        #
        return rtrnD

    def __formatDepositionDataId(self, p_depid, p_bIsWorkflow):  # pylint: disable=unused-argument
        #       if( p_bIsWorkflow or ( p_depid.upper() == 'TMP_ID' ) ):
        #           depId = p_depid.upper()
        #       else:
        #           depId = p_depid.lower()
        depId = p_depid.upper()
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
