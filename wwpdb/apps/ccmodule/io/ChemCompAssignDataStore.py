##
# File:    ChemCompAssignDataStore.py
# Date:    23-Nov-2010
#
# Updates:
# 2010-11-29    RPS    Best Hit data updated with more granular getters for score, ccid, and match status info
# 2010-12-02    RPS    Dump of TopHitsList updated to accommodate possibility of more than one item in tuple members
# 2010-12-02    RPS    Updated with admin/convenience features to enable easier tracking of mode/values of assignment actions
# 2010-12-09    RPS    Updated implementation for atom-level mapping.
# 2010-12-17    RPS    Update to __setup() necessary to support proper location of pickle file when in WFM environment.
# 2011-01-11    RPS    Updated with functionality for remembering parameters used for rerunning assignment searches
#                        with adjusted deltas for link and bond radii
# 2011-01-12    RPS    Added call to serialize inside of setAnnotAssignment() to ensure that assignments were not getting lost during concomitant
#                        asynchronous requests for _assgnInstnc() for several instance IDs in context of "All Instance" interface mode.
#                        Built-in intelligence for determining file name of the pickled datastore file based on deposition dataset ID.
# 2011-01-17    RPS    Added doExport() in support of resuming prior work efforts in WFM environ.
# 2011-01-18    RPS    Added support for capturing newly created Chem Comp IDs for given ligand instance.
# 2011-03-23    RPS    Added support for capturing non-candidate Chem Comp IDs requested for comparison with given ligand instances.
# 2011-05-25    RPS    All references to "non-candidate" replaced with "new candidate"
# 2011-06-14    RPS    Support for capturing warning messages relative to instance matching
# 2011-08-05    RPS    Updated with comments in support of generating "restructuredtext" documentation.
#                        Also performed some code cleanup, removed obsolete code.
# 2012-06-11    RPS    Added doExportUserSelections() method to generate export file that captures user assignment selections
#                        for each chem comp instance
# 2012-07-03    RPS    doExportUserSelections() changed to doExportUpdatedCcAssignments(). Creation of "chem-comp-select" file no longer necessary.
#                        Instead generating updated cc-assign cif file that captures annotator chem comp assignment selections and which is used
#                        as input for update of the model file.
# 2012-09-12    RPS    __generateUpdatedCcAssignFile() updated to continue processing in cases where best batch hit may be 'None'.
# 2012-10-10    RPS    Now deriving path of sessions directory by direct interrogation of request object (as opposed to indirectly determining
#                        by obtaining path to directory above 'sessions').
#                      Introducing some attributes intended to support Chem Comp "Lite" implementation.
# 2012-11-28    RPS    Additional updates for ChemComp "Lite" support.
# 2012-12-13    RPS    Additional updates for ChemComp "Lite" support.
# 2012-12-18    RPS    Fixed problem with setDpstrUploadFile() method.
#                       self.__generateUpdatedDepInfoFile() corrected for use of updated method names.
# 2012-12-18    RPS    Added self.__dpstrCcExactMatchId{} to track depositor's decision to use exact match ID for submission
# 2013-02-20    RPS    ChemComp "Lite" updates -- now accommodates capture of depositor's choice to use different cc ID than one originally submitted.
#                        Also corresponding updates to self.__generateUpdatedDepInfoFile() to generate content in form of two cif categories:
#                            =  pdbx_chem_comp_depositor_info
#                            =  pdbx_chem_comp_upload_depositor_info
# 2013-03-01    RPS    Added getDpstrUploadFilesDict()
# 2013-03-31    RPS    Added support for tracking labels applied to depositor uploaded files when copying to workflow storage.
# 2013-04-03    RPS    Added support for tracking whether or not a given ligand instance is single atom.
# 2013-04-10    RPS    Methods added to distinguish generated sketch files from file uploads for "Lite" LigModule
# 2013-04-10    RPS    added setDpstrSketchMolDataStr().
# 2013-05-01    RPS    updated self.__generateUpdatedDepInfoFile() so that pdbx_chem_comp_upload_depositor_info category only output as necessary.
# 2013-05-30    RPS    updated self.__generateUpdatedCcAssignFile() so that atom names in atom mapping content reflect those of the assigned ID
# 2013-06-20    RPS    Accommodating new 'deposit' filesource/storage type.
# 2013-08-12    RPS    Accommodating use of cc-dpstr-prgrss files
# 2013-10-23    RPS    Updates in support of handling data propagation from LigandLite of DepUI to LigandModule of annotation.
# 2014-04-25    RPS    Improving handling of files uploaded via LigandLite UI, so that proper mapping of partition numbers is strictly enforced
#                        throughout all user sessions.
#                      Also, now tracking temporal order in which files are uploaded so that it can be determined
#                        which files have "last word" versioning precedence.
# 2014-06-30    RPS    Updated self.__generateUpdatedDepInfoFile() so that PdbxWriter API is used for generating output in cif format.
# 2014-07-09    RPS    Removed use of any outer double-quotes in self.__generateUpdatedDepInfoFile() --> not necessary now that PdbxWriter API is used
# 2014-10-08    RPS    self.__generateDpstrPrgrssFile() --> strengthened test logic for determining whether depositor has addressed all ligand IDs requiring attention
# 2017-01-31    RPS    Updated to support capture of data for ligands as "focus of research"
# 2017-02-12    RPS    Removing canned text for capture of "details" data for ligands as "focus of research"
# 2017-02-13    RPS    Updates to distinguish between ligandIDs that were simply selected as focus of research vs those for which data was actually provided.
# 2017-02-14    RPS    generateUpdatedDepInfoFile updated --> correcting "auth_sym_id" to "auth_asym_id"
# 2017-02-15    RPS    generateUpdatedDepInfoFile updated --> output complete pdbx_entity_instance_feature category
# 2017-02-17    RPS    generateUpdatedDepInfoFile updated --> accommodating new "auth_comp_id" item for "pdbx_binding_assay category"
# 2017-03-30    RPS    now generating cc-dpstr-prgrss file when there are no ligands requiring attention (in support of depui monitoring at module launch)
# 2017-05-03    RPS    Updates so that LOI tracking can succeed even in cases where annotator reruns ligand search and consequently changes value for "author" assigned CCID
##
'''
Provide a storage interface for recording chemical component
assignment data/state for given deposition data set when
being processed via the common tool ligand module

'''
__docformat__ = "restructuredtext en"
__author__ = "Raul Sala"
__email__ = "rsala@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import sys
import traceback
import shutil
import os.path
try:
    import cPickle as pickle
except ImportError as _e:  # noqa: F841
    import pickle
import inspect

from mmcif.io.PdbxWriter import PdbxWriter
from mmcif.api.PdbxContainers import DataContainer
from mmcif.api.DataCategory import DataCategory
from wwpdb.utils.wf.WfDataObject import WfDataObject


class ChemCompAssignDataStore(object):
    ''' Class serves as data container serving needs for a given user session.
        Records state of chemical component assignment search results and
        annotator assignments for a particular deposition dataset.
        Also serves similar purposes in Deposition UI context / Chem Comp Lite module.
        Usage relies on python pickle protocol for persistence of the
        datastore's contents to a file on server.
    '''
    def __init__(self, reqOb, verbose=False, log=sys.stderr):
        self.__verbose = verbose
        self.__debug = True
        self.__lfh = log
        self.__reqOb = reqOb
        # self.__fileName = None
        self.__fileNameSuffix = "-cc-assign-details.pic"
        # following are set of dictionaries that for each instance ID contain :
        self.__authAssignment = {}            # author-assigned 3-letter code
        self.__batchBestHitAssignment = {}    # tuple of format (<best hit 3-letter code determined by batch search>,<mtchStatus>,<mtchScore>)
        self.__annotAssignment = {}           # 3-letter code assigned by annotator during processing
        self.__topHitsList = {}               # topHitsList is dictionary mapping of instance id to a list of up to 5 tuples representing
        #                                     # the up to 5 top candidates each represented as tuple of form:
        #                                     # (topHitCcId, topHitCcIdScore, matchWarning, ccName, ccFormula) when fully populated
        self.__newCandidatesList = {}         # dictionary mapping of instance id to a list of new candidates user has requested for
        #                                     # comparison with given ligand instance. For given instance ID, list consists of tuples
        #                                     # that take form of: (ccid,name,formula)
        self.__ccNameList = {}                # cc determined name, dictionary of instId-to-name
        self.__ccFormulaList = {}             # cc determined formula, dictionary of instId-to-formula
        self.__ccFormalChrgList = {}          # cc determined formal charge, dictionary of instId-to-charge
        self.__ccAssignmentWarning = {}       # supplemental cc match assignment warnings
        self.__ccSingleAtomFlag = {}          # cc determined flag indicating whether or not instance is a single atom
        self.__annotNotes = {}                # notes input by annotator regarding deposition data
        self.__atomMapDct = {}                # atom level mapping
        #
        self.__drtyGrpCnts = {}               # admin/convenience dict for keeping track of # of instances in each entity groups that have been assigned by annotator
        self.__drtyGrpList = []               # admin/convenience list for keeping track of entity groups that contain annotator assigned instances
        self.__GlbllyAssgndGrpLst = []        # admin/convenience list for keeping track of entity groups that have been globally assigned via "all instances" view
        self.__GlbllyAssgndDict = {}          # admin/convenience dict to track which chem comp IDs have been assigned to globally assigned ligand groups.
        #
        self.__GlblRerunSrchLst = []              # admin/convenience dict to track which entity groups have been subjected to rerun of cc assign search via "all-instances" view.
        self.__GlblRerunSrchDict_lnkRadii = {}    # to store value last used for rerunning group search with adjusted link radii delta
        self.__GlblRerunSrchDict_bndRadii = {}    # to store value last used for rerunning group search with adjusted bond radii delta
        self.__instncRerunSrchLst = []            # admin/convenience dict to track which instance IDs have been subjected to rerun of cc assign search via "singl-instances" view
        self.__rerunParam_linkRadii = {}          # to store value last used for rerunning search with adjusted link radii delta
        self.__rerunParam_bondRadii = {}          # to store value last used for rerunning search with adjusted bond radii delta
        #
        self.__newCcDefined = {}           # tracks new CCid codes created by annotator for a ligand instance during processing
        #
        self.__sessionsPath = self.__reqOb.getValue("SessionsPath")
        self.__filePath = None
        self.__wasBorn = False    # boolean indicating whether or not a datastore for the current deposition dataset had
        #                         #  already been established-->i.e. persisted as pickle file
        #
        # self.__pickleProtocol = pickle.HIGHEST_PROTOCOL
        self.__pickleProtocol = 0
        #

        # Following attributes have been added to meet the needs of the Chem Component "Lite" Module which is used in
        #    context of the Common Tool Deposition UI
        # ###################Chem Comp Lite attributes BEGIN ###############################
        self.__dpstrCcExactMatchId = {}   # dictionary mapping ligand code to exact match cc ID accepted for use by depositor
        self.__dpstrCcAltId = {}   # dictionary mapping ligand code to alternate cc ID proposed for use by depositor
        self.__dpstrCcType = {}   # dictionary mapping ligand code to type of ligand assigned by depositor
        self.__dpstrCcName = {}   # dictionary mapping ligand code to name assigned by depositor
        self.__dpstrCcFrmla = {}   # dictionary mapping ligand code to formula assigned by depositor
        self.__dpstrSubmitChoice = {}  # dictionary mapping ligand code to choice of whether to use sketch or descriptor string for submission
        self.__dpstrCcDscrptrType = {}  # dictionary mapping ligand code to type of descriptor string assigned by depositor (i.e. SMILES vs. InChI)
        self.__dpstrCcDscrptrStr = {}   # dictionary mapping ligand code to descriptor string assigned by depositor
        self.__dpstrComments = {}   # dictionary mapping ligand code to comments by depositor
        self.__dpstrUploadFiles = {}   # dictionary mapping ligand code to file upload(s) by depositor
        self.__dpstrSketchFiles = {}   # dictionary mapping ligand code to sketch file(s) generated by depositor
        self.__dpstrSketchMolStr = {}   # dictionary mapping ligand code to descriptor string assigned by depositor
        self.__dpstrInvalidGrpIdLst = []        # admin/convenience list for keeping track of lig IDs used by depositor but which do not exist in chem comp dictionary
        self.__GlbllyRslvdGrpLst = []        # admin/convenience list for keeping track of entity groups where mismatched instances have been resolved via "all instances" view
        self.__dpstrAttnRqdGrpLst = []        # admin/convenience list for keeping track of entity groups where mismatched instances have been identified
        self.__rslvdPrtnCntr = 1        # admin/convenience counter for tracking current highest partition numbers used to map to resolved Ligand IDs
        self.__rslvdPrtnDict = {}        # admin/convenience dict for keeping track of partition numbers used to map to resolved Ligand IDs
        self.__dpstrUpldFlsOrder = {}     # admin/convenience dict for keeping track of order in which files were uploaded for a given ligid,
        #                                 # so that authoritative precedence given to most recent uploads
        self.__rsrchAcqurdGrpLst = []     # admin/convenience list for keeping track of entity groups for which data was captured for "focus of research" needs.
        self.__dpstrCcRsrchInfo = {}  # dictionary mapping ligand code to research data provied by depositor
        self.__rsrchSlctdGrpLst = []     # admin/convenience list for keeping track of entity groups which were indicated as "focus of research".
        self.__dpstrOrigCcIdMaster = {}  # Authoritative copy of CCID which depositor had originally used to identify the ligand
        # ###################Chem Comp Lite attributes END   ###############################

        self.__setup()

    def __setup(self):
        """ Setup of a given ChemCompAssignDataStore object involves checking for an existing
            serialized pickle file for the current deposition dataset being processed.
            If such a pickle file exists, we use it to populate the object with the last recorded
            state of chemical component search results and annotator assignments.
            If pickle file is not present, then we assume that this is the first time that this
            particular deposition dataset is being processed and leave this object's data attributes
            empty, to be populated by initial processing of chem comp assign results and any annotator
            actions to assign chem component IDs to ligand instances.
        """
        try:
            # the deposition dataset ID
            depId = str(self.__reqOb.getValue("identifier")).upper()
            # the ID uniquely identifying the current user session
            sessionId = self.__reqOb.getSessionId()
            if self.__verbose:
                self.__lfh.write("+ChemCompAssignStore.__setup() - session id %s \n" % sessionId)
            # filesource = whether datafile sourced from Workflow Managed environment or via file upload (i.e. testing)
            fileSource = str(self.__reqOb.getValue("filesource")).lower()
            #
            context = self.__getContext()
            if context in ['standalone', 'unknown', 'workflow']:
                picklePathAbs = os.path.join(self.__sessionsPath, sessionId, 'assign')
                if not os.path.exists(picklePathAbs):
                    os.makedirs(picklePathAbs)

                if context != 'workflow':
                    self.__filePath = os.path.join(picklePathAbs, depId.lower() + self.__fileNameSuffix)
                else:
                    self.__filePath = os.path.join(picklePathAbs, depId.upper() + self.__fileNameSuffix)
            elif context == 'deposition':
                self.__filePath = self.getFileObject(depId, fileSource, 'chem-comp-assign-details', 'pic', wfInstanceId=self.__reqOb.getValue('instance')).getFilePathReference()

            if os.access(self.__filePath, os.R_OK):
                self.deserialize()
                self.__wasBorn = True
                if (self.__verbose):
                    self.__lfh.write("+ChemCompAssignStore.__setup() - pickle file already present at %s\n" % self.__filePath)
            else:
                if (self.__verbose):
                    self.__lfh.write("+ChemCompAssignStore.__setup() - pickle file not found/not yet created at %s\n" % self.__filePath)
        except:  # noqa: E722 pylint: disable=bare-except
            self.__lfh.write("+ChemCompAssignStore.__setup() - Failed to open data store for session id %s data store path %s\n" %
                             (self.__reqOb.getSessionId(), self.__filePath))
            self.__lfh.write("+ChemCompAssignStore.__setup() - Exception info: %s\n" %
                             sys.exc_info()[0])
            traceback.print_exc(file=self.__lfh)

    def __getContext(self):
        filesource = self.__reqOb.getValue('filesource')
        depid = self.__reqOb.getValue('identifier')

        if depid == 'TMP_ID':
            return 'standalone'

        if filesource == 'deposit':
            return 'deposition'

        if filesource in ['archive', 'wf-archive', 'wf_archive', 'wf-instance', 'wf_instance']:
            return 'workflow'

        # in case we can't find out the context (as it happens with the standalone
        # ligmod) we fall back to get model files from the sessions path
        return 'unknown'

    def getFileObject(self, dataSetId, fileSource, contentType, formatType, versionId='latest', mileStone=None, wfInstanceId=None,
                      partNumber=None, sessionDir=None):
        out_file = WfDataObject()
        out_file.setDepositionDataSetId(dataSetId)
        out_file.setWorkflowInstanceId(wfInstanceId)
        out_file.setStorageType(fileSource)

        if mileStone:
            out_file.setContentTypeAndFormat(contentType + '-' + mileStone, formatType)
        else:
            out_file.setContentTypeAndFormat(contentType, formatType)

        if sessionDir:
            out_file.setStorageType('session')
            out_file.setSessionPath(sessionDir)
            out_file.setSessionDataSetId(dataSetId)

        out_file.setVersionId(versionId)
        out_file.setPartitionNumber(partNumber)

        return out_file

    def reset(self):
        """ Purge contents
        """
        self.__authAssignment = {}
        self.__batchBestHitAssignment = {}
        self.__annotAssignment = {}
        self.__topHitsList = {}
        self.__newCandidatesList = {}
        self.__ccNameList = {}
        self.__ccFormulaList = {}
        self.__ccFormalChrgList = {}
        self.__ccAssignmentWarning = {}
        self.__ccSingleAtomFlag = {}
        self.__annotNotes = {}
        self.__rerunParam_linkRadii = {}
        self.__rerunParam_bondRadii = {}
        self.__atomMapDct = {}
        self.__drtyGrpCnts = {}
        self.__drtyGrpList = []
        self.__GlbllyAssgndGrpLst = []
        self.__GlbllyAssgndDict = {}
        self.__GlblRerunSrchLst = []
        self.__GlblRerunSrchDict_lnkRadii = {}
        self.__GlblRerunSrchDict_bndRadii = {}
        self.__instncRerunSrchLst = []
        self.__newCcDefined = {}
        # chem comp lite related attribs below
        self.__dpstrAttnRqdGrpLst = []
        self.__GlbllyRslvdGrpLst = []
        self.__dpstrInvalidGrpIdLst = []
        self.__dpstrCcExactMatchId = {}
        self.__dpstrCcAltId = {}
        self.__dpstrCcType = {}
        self.__dpstrCcName = {}
        self.__dpstrCcFrmla = {}
        self.__dpstrSubmitChoice = {}
        self.__dpstrCcDscrptrType = {}
        self.__dpstrCcDscrptrStr = {}
        self.__dpstrComments = {}
        self.__dpstrUploadFiles = {}
        self.__dpstrSketchFiles = {}
        self.__dpstrSketchMolStr = {}
        self.__rslvdPrtnCntr = 1
        self.__rslvdPrtnDict = {}
        self.__dpstrUpldFlsOrder = {}
        self.__rsrchAcqurdGrpLst = []
        self.__dpstrCcRsrchInfo = {}
        self.__rsrchSlctdGrpLst = []
        self.__dpstrOrigCcIdMaster = {}

    def serialize(self):
        """ Persist data to a pickle file on server so that state can be maintained
            between web requests within a given ligand module session
        """
        if self.__verbose:
            self.__lfh.write("+ChemCompAssignStore.serialize() - starting\n")
        try:
            fb = open(self.__filePath, 'wb')
            pickle.dump(self.__authAssignment, fb, self.__pickleProtocol)
            pickle.dump(self.__batchBestHitAssignment, fb, self.__pickleProtocol)
            pickle.dump(self.__annotAssignment, fb, self.__pickleProtocol)
            pickle.dump(self.__topHitsList, fb, self.__pickleProtocol)
            pickle.dump(self.__newCandidatesList, fb, self.__pickleProtocol)
            pickle.dump(self.__ccNameList, fb, self.__pickleProtocol)
            pickle.dump(self.__ccFormulaList, fb, self.__pickleProtocol)
            pickle.dump(self.__ccFormalChrgList, fb, self.__pickleProtocol)
            pickle.dump(self.__ccAssignmentWarning, fb, self.__pickleProtocol)
            pickle.dump(self.__ccSingleAtomFlag, fb, self.__pickleProtocol)
            pickle.dump(self.__annotNotes, fb, self.__pickleProtocol)
            pickle.dump(self.__rerunParam_linkRadii, fb, self.__pickleProtocol)
            pickle.dump(self.__rerunParam_bondRadii, fb, self.__pickleProtocol)
            pickle.dump(self.__atomMapDct, fb, self.__pickleProtocol)
            pickle.dump(self.__drtyGrpCnts, fb, self.__pickleProtocol)
            pickle.dump(self.__drtyGrpList, fb, self.__pickleProtocol)
            pickle.dump(self.__GlbllyAssgndGrpLst, fb, self.__pickleProtocol)
            pickle.dump(self.__GlbllyAssgndDict, fb, self.__pickleProtocol)
            pickle.dump(self.__GlblRerunSrchDict_lnkRadii, fb, self.__pickleProtocol)
            pickle.dump(self.__GlblRerunSrchDict_bndRadii, fb, self.__pickleProtocol)
            pickle.dump(self.__GlblRerunSrchLst, fb, self.__pickleProtocol)
            pickle.dump(self.__instncRerunSrchLst, fb, self.__pickleProtocol)
            pickle.dump(self.__newCcDefined, fb, self.__pickleProtocol)
            # chem comp lite attribs below
            pickle.dump(self.__GlbllyRslvdGrpLst, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrInvalidGrpIdLst, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrCcExactMatchId, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrCcAltId, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrCcType, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrCcName, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrCcFrmla, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrSubmitChoice, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrCcDscrptrType, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrCcDscrptrStr, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrComments, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrUploadFiles, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrSketchFiles, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrSketchMolStr, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrAttnRqdGrpLst, fb, self.__pickleProtocol)
            pickle.dump(self.__rslvdPrtnCntr, fb, self.__pickleProtocol)
            pickle.dump(self.__rslvdPrtnDict, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrUpldFlsOrder, fb, self.__pickleProtocol)
            pickle.dump(self.__rsrchAcqurdGrpLst, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrCcRsrchInfo, fb, self.__pickleProtocol)
            pickle.dump(self.__rsrchSlctdGrpLst, fb, self.__pickleProtocol)
            pickle.dump(self.__dpstrOrigCcIdMaster, fb, self.__pickleProtocol)
            fb.close()
        except:  # noqa: E722 pylint: disable=bare-except
            self.__lfh.write("+ChemCompAssignStore.serialize() - exception encountered\n")
            traceback.print_exc(file=self.__lfh)

    def deserialize(self):
        """ Pull data from a pickle file on server into memory so that state can be
            restored/maintained between web requests within a given ligand module user session
        """
        try:
            fb = open(self.__filePath, 'rb')
            self.__authAssignment = pickle.load(fb)
            self.__batchBestHitAssignment = pickle.load(fb)
            self.__annotAssignment = pickle.load(fb)
            self.__topHitsList = pickle.load(fb)
            self.__newCandidatesList = pickle.load(fb)
            self.__ccNameList = pickle.load(fb)
            self.__ccFormulaList = pickle.load(fb)
            self.__ccFormalChrgList = pickle.load(fb)
            self.__ccAssignmentWarning = pickle.load(fb)
            self.__ccSingleAtomFlag = pickle.load(fb)
            self.__annotNotes = pickle.load(fb)
            self.__rerunParam_linkRadii = pickle.load(fb)
            self.__rerunParam_bondRadii = pickle.load(fb)
            self.__atomMapDct = pickle.load(fb)
            self.__drtyGrpCnts = pickle.load(fb)
            self.__drtyGrpList = pickle.load(fb)
            self.__GlbllyAssgndGrpLst = pickle.load(fb)
            self.__GlbllyAssgndDict = pickle.load(fb)
            self.__GlblRerunSrchDict_lnkRadii = pickle.load(fb)
            self.__GlblRerunSrchDict_bndRadii = pickle.load(fb)
            self.__GlblRerunSrchLst = pickle.load(fb)
            self.__instncRerunSrchLst = pickle.load(fb)
            self.__newCcDefined = pickle.load(fb)
            # chem comp lite attribs below
            self.__GlbllyRslvdGrpLst = pickle.load(fb)
            self.__dpstrInvalidGrpIdLst = pickle.load(fb)
            self.__dpstrCcExactMatchId = pickle.load(fb)
            self.__dpstrCcAltId = pickle.load(fb)
            self.__dpstrCcType = pickle.load(fb)
            self.__dpstrCcName = pickle.load(fb)
            self.__dpstrCcFrmla = pickle.load(fb)
            self.__dpstrSubmitChoice = pickle.load(fb)
            self.__dpstrCcDscrptrType = pickle.load(fb)
            self.__dpstrCcDscrptrStr = pickle.load(fb)
            self.__dpstrComments = pickle.load(fb)
            self.__dpstrUploadFiles = pickle.load(fb)
            self.__dpstrSketchFiles = pickle.load(fb)
            self.__dpstrSketchMolStr = pickle.load(fb)
            self.__dpstrAttnRqdGrpLst = pickle.load(fb)
            self.__rslvdPrtnCntr = pickle.load(fb)
            self.__rslvdPrtnDict = pickle.load(fb)
            self.__dpstrUpldFlsOrder = pickle.load(fb)
            self.__rsrchAcqurdGrpLst = pickle.load(fb)
            self.__dpstrCcRsrchInfo = pickle.load(fb)
            self.__rsrchSlctdGrpLst = pickle.load(fb)
            self.__dpstrOrigCcIdMaster = pickle.load(fb)

            fb.close()

            # below for loops are defensive measure for backwards compatibility of older pickle files
            # that may have been created prior to introduction of the given dictionary attributes
            for ligId in self.__GlbllyRslvdGrpLst:
                if not (ligId in self.__rslvdPrtnDict):
                    self.__rslvdPrtnDict[ligId] = self._getNextPartitionNumber()

            for ligId in self.__dpstrUploadFiles:
                if ligId not in self.__dpstrUpldFlsOrder:
                    self.__dpstrUpldFlsOrder[ligId] = []

                    for fileType in self.__dpstrUploadFiles[ligId]:
                        for fileName in self.__dpstrUploadFiles[ligId][fileType].keys():
                            self.__dpstrUpldFlsOrder[ligId].append(fileName)

        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def doExport(self, exprtDirPath, exprtFilePath):
        """ Export serialized file for persistence in WFM system

            :Params:

                + ``exprtDirPath``: path indicating directory of WFM storage destination
                + ``exprtFilePath``: path and filename indicating target file for WFM storage
        """
        try:
            if self.__filePath is not None and os.access(exprtDirPath, os.R_OK):
                shutil.copyfile(self.__filePath, exprtFilePath)
                return True
            else:
                return False
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                self.__lfh.write("+ChemCompAssignStore.doExport() - export to %s failed \n" % exprtFilePath)
            traceback.print_exc(file=self.__lfh)

    def doExportUpdatedCcAssignments(self, exprtDirPath, exprtFilePath, depDataSetId):
        """ Generate export file that captures user assignment selections for each chem comp instance

            :Params:

                + ``exprtDirPath``: path indicating directory destination for exported file
                + ``exprtFilePath``: path and filename indicating target export file
        """
        try:
            if os.access(exprtDirPath, os.R_OK):
                self.__generateUpdatedCcAssignFile(exprtFilePath, depDataSetId)
                return True
            else:
                return False
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                self.__lfh.write("+ChemCompAssignStore.doExportUpdatedCcAssignments() - export to %s failed \n" % exprtFilePath)
            traceback.print_exc(file=self.__lfh)

    def doExportUpdatedDepositorInfo(self, p_dpstrInfoDirPath, p_dpstrInfoFilePath, p_depDataSetId):
        """ Generate export file that captures user assignment selections for each chem comp instance

        :Params:

            + ``exprtDirPath``: path indicating directory destination for exported file
            + ``exprtFilePath``: path and filename indicating target export file
        """
        try:
            if os.access(p_dpstrInfoDirPath, os.R_OK):
                self.__generateUpdatedDepInfoFile(p_dpstrInfoFilePath, p_depDataSetId)
                return True
            else:
                return False
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                self.__lfh.write("+ChemCompAssignStore.doExportUpdatedDepositorInfo() - export to %s failed \n" % p_dpstrInfoFilePath)
            traceback.print_exc(file=self.__lfh)

    def doExportDepositorProgress(self, p_dpstrPrgrssDirPath, p_dpstrPrgrssFilePath, p_depDataSetId, p_mode):
        """ Generate export file that captures user assignment selections for each chem comp instance

        :Params:

            + ``p_dpstrPrgrssDirPath``: path indicating directory destination for exported file
            + ``p_dpstrPrgrssFilePath``: path and filename indicating target export file
            + ``p_depDataSetId``: deposition dataset ID
            + ``p_mode``: "unfinished" | "completed" | "intermittent"
        """
        try:
            if os.access(p_dpstrPrgrssDirPath, os.R_OK):
                self.__generateDpstrPrgrssFile(p_dpstrPrgrssFilePath, p_depDataSetId, p_mode)
                return True
            else:
                return False
        except:  # noqa: E722 pylint: disable=bare-except
            if (self.__verbose):
                self.__lfh.write("+ChemCompAssignStore.doExportDepositorProgress() - export to %s failed \n" % p_dpstrPrgrssFilePath)
            traceback.print_exc(file=self.__lfh)

    # def __generateUserSelectionFile(self, exprtFilePath):
    #     outputFile = open(exprtFilePath, "w")
    #     assignedId = ""
    #     for instId in self.getAuthAssignmentKeys():
    #         if self.getBatchBestHitStatus(instId) == 'passed':
    #             # if the assignment search yielded a hit with "passed" status
    #             # we will use the chem comp ID assigned by the batch search
    #             # unless the annotator has for some reason manually assigned
    #             # a chem comp ID to supersede the batch search assignment

    #             if self.__annotAssignment[instId] == 'Not Assigned':
    #                 assignedId = self.getBatchBestHitId(instId)
    #             else:
    #                 assignedId = self.__annotAssignment[instId]
    #         else:
    #             assignedId = self.__annotAssignment[instId]
    #         #
    #         outputFile.write("%s\t%s\n" % (instId, assignedId))

    #     outputFile.close()

    def __generateUpdatedCcAssignFile(self, updtedCcAssignFilePath, depDataSetId):
        '''NOTE: this function is currently being called on save(unfinished) to provide helpful
        representation of state of annotator assignments. BUT on final Save(Done) assuming that
        all assignments have value other than 'None'
        '''
        try:
            outputFile = open(updtedCcAssignFilePath, "w")
            assignedId = ""
            atomMappingInstanceData = []
            atomMappingOutput = []
            outputFile.write("data_%s\n" % depDataSetId)
            outputFile.write("#\nloop_\n_pdbx_instance_assignment.inst_id\n_pdbx_instance_assignment.het_id\n")
            for instId in self.getAuthAssignmentKeys():
                if self.getBatchBestHitStatus(instId) == 'passed':
                    # if the assignment search yielded a hit with "passed" status
                    # we will use the chem comp ID assigned by the batch search
                    # unless the annotator has for some reason manually assigned
                    # a chem comp ID to supersede the batch search assignment

                    if self.__annotAssignment[instId] == 'Not Assigned':
                        assignedId = self.getBatchBestHitId(instId)
                    else:
                        assignedId = self.__annotAssignment[instId]
                else:
                    assignedId = self.__annotAssignment[instId]
                #
                outputFile.write("%s\t%s\n" % (instId, assignedId))
                #
                if self.__atomMapDct[instId][assignedId]:
                    atomMappingInstanceData = self.__atomMapDct[instId][assignedId]  # this gives us a list of tuples of form
                    #                                                                # SW( '_pdbx_atom_mapping.inst_atom_name','_pdbx_atom_mapping.reference_atom_name')

                    for instAtomName, refAtomName in atomMappingInstanceData:
                        atomMappingOutput.append('%s\t%-5s\t%s\t%s\n' % (instId, '"' + instAtomName + '"', assignedId, '"' + refAtomName + '"'))

            outputFile.write("#\n#\n")
            outputFile.write("loop_\n_pdbx_atom_mapping.inst_id\n_pdbx_atom_mapping.inst_atom_name\n_pdbx_atom_mapping.reference_id\n_pdbx_atom_mapping.reference_atom_name\n")

            outputFile.write("".join(atomMappingOutput))
            outputFile.write("#\n")

            outputFile.close()
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                self.__lfh.write("+ChemCompAssignStore.__generateUpdatedCcAssignFile() - generation of updated cc-assign file to %s failed \n" % updtedCcAssignFilePath)
            traceback.print_exc(file=self.__lfh)

    def __generateUpdatedDepInfoFile(self, updtedDpstrInfoFilePath, depDataSetId):
        '''
        '''
        try:
            myDataList = []
            ofh = open(updtedDpstrInfoFilePath, "w")
            curContainer = DataContainer(depDataSetId)
            aCat1 = DataCategory("pdbx_chem_comp_depositor_info")
            aCat1.appendAttribute("ordinal")
            aCat1.appendAttribute("comp_id")
            aCat1.appendAttribute("alt_comp_id")
            aCat1.appendAttribute("type")
            aCat1.appendAttribute("name")
            aCat1.appendAttribute("formula")
            aCat1.appendAttribute("descriptor")
            aCat1.appendAttribute("descriptor_type")
            aCat1.appendAttribute("details")

            for indx, ligId in enumerate(self.getGlbllyRslvdGrpList(), start=1):
                ligType = self.getDpstrCcType(ligId)
                exactMtchId = self.getDpstrExactMtchCcId(ligId)
                altLigId = self.getDpstrAltCcId(ligId) if exactMtchId == '?' else exactMtchId
                chemCompName = self.getDpstrCcName(ligId)
                chemCompFrmla = self.getDpstrCcFrmla(ligId)
                chemCompDescriptor = self.getDpstrCcDscrptrStr(ligId)
                chemCompDescriptorType = self.getDpstrCcDscrptrType(ligId)
                chemCompDetails = self.getDpstrComments(ligId)
                aCat1.append((indx, ligId, altLigId, ligType, chemCompName, chemCompFrmla, chemCompDescriptor, chemCompDescriptorType, chemCompDetails))
                #
            curContainer.append(aCat1)

            if len(self.__dpstrUploadFiles.keys()) > 0 or len(self.__dpstrSketchFiles.keys()) > 0:
                aCat2 = DataCategory("pdbx_chem_comp_upload_depositor_info")
                aCat2.appendAttribute("ordinal")
                aCat2.appendAttribute("comp_id")
                aCat2.appendAttribute("upload_file_name")
                aCat2.appendAttribute("upload_file_type")

                ordinal = 0
                for ligId in self.getGlbllyRslvdGrpList():
                    if ligId in self.__dpstrUploadFiles:
                        for fileType in self.__dpstrUploadFiles[ligId]:
                            for fileName in self.__dpstrUploadFiles[ligId][fileType].keys():
                                wfFlPth = self.getDpstrUploadFileWfPath(ligId, fileType, fileName)
                                if wfFlPth is not None and os.access(wfFlPth, os.R_OK):
                                    outputFileNm = os.path.basename(wfFlPth)
                                else:
                                    outputFileNm = fileName
                                ordinal += 1
                                # outputFile.write( "%s\t%s\t%s\t%s\n" % ( ordinal, ligId, outputFileNm, fileType  ) )
                                aCat2.append((ordinal, ligId, outputFileNm, fileType))
                    #
                    if ligId in self.__dpstrSketchFiles:
                        for fileType in self.__dpstrSketchFiles[ligId]:
                            for fileName in self.__dpstrSketchFiles[ligId][fileType].keys():
                                wfFlPth = self.getDpstrSketchFileWfPath(ligId, fileName, fileType)
                                self.__lfh.write("+ChemCompAssignStore.__generateUpdatedDepInfoFile() - wfFlPth obtained for ligId/filename/fileType, [%s/%s/%s], as [ %s ] \n" %
                                                 (ligId, fileName, fileType, wfFlPth))
                                if wfFlPth is not None and os.access(wfFlPth, os.R_OK):
                                    outputFileNm = os.path.basename(wfFlPth)
                                else:
                                    self.__lfh.write("+ChemCompAssignStore.__generateUpdatedDepInfoFile() - problem accessing wfFlPth of [ %s ] \n" % wfFlPth)
                                    outputFileNm = fileName
                                ordinal += 1
                                # outputFile.write( "%s\t%s\t%s\t%s\n" % ( ordinal, ligId, outputFileNm, fileType  ) )
                                aCat2.append((ordinal, ligId, outputFileNm, fileType))
                    #
                #
                curContainer.append(aCat2)

            if len(self.__rsrchSlctdGrpLst) > 0:

                if len(self.__rsrchAcqurdGrpLst) > 0:

                    aCat3 = DataCategory("pdbx_binding_assay")
                    aCat3.appendAttribute("id")
                    aCat3.appendAttribute("auth_comp_id")
                    aCat3.appendAttribute("target_sequence_one_letter_code")
                    aCat3.appendAttribute("ligand_descriptor_type")
                    aCat3.appendAttribute("ligand_descriptor")
                    aCat3.appendAttribute("assay_type")
                    aCat3.appendAttribute("assay_value_type")
                    aCat3.appendAttribute("assay_value")
                    aCat3.appendAttribute("assay_pH")
                    aCat3.appendAttribute("assay_temperature")
                    aCat3.appendAttribute("details")

                    ordinalCat3 = 1

                aCat4 = DataCategory("pdbx_entity_instance_feature")
                aCat4.appendAttribute("ordinal")
                aCat4.appendAttribute("asym_id")
                aCat4.appendAttribute("auth_asym_id")
                aCat4.appendAttribute("auth_comp_id")
                aCat4.appendAttribute("auth_seq_num")
                aCat4.appendAttribute("comp_id")
                aCat4.appendAttribute("details")
                aCat4.appendAttribute("feature_type")
                aCat4.appendAttribute("seq_num")

                ordinalCat4 = 1

                for ligId in self.__rsrchSlctdGrpLst:

                    if ligId in self.__rsrchAcqurdGrpLst:

                        dataSetDict = self.__dpstrCcRsrchInfo.get(ligId)

                        if dataSetDict:  # dataSetDict for given ligID has integer keys that map to a dictionary representing a single set of binding data

                            if ligId != "HOH" and ligId != "NONE%":
                                for dataSetIndx in range(0, 10):
                                    if dataSetIndx in dataSetDict:
                                        targetSeq = dataSetDict[dataSetIndx]["target_sequence"]
                                        ligDscrptrType = dataSetDict[dataSetIndx]["rsrch_dscrptr_type"]
                                        ligDscrptrStr = dataSetDict[dataSetIndx]["rsrch_dscrptr_str"]
                                        assayType = dataSetDict[dataSetIndx]["assay_type"]
                                        assayValueType = dataSetDict[dataSetIndx]["measurement_type"]
                                        assayValue = dataSetDict[dataSetIndx]["measured_value"]
                                        assayPh = dataSetDict[dataSetIndx]["ph"]
                                        assayTemp = dataSetDict[dataSetIndx]["assay_temp"]
                                        details = dataSetDict[dataSetIndx]["details"]

                                        aCat3.append((ordinalCat3, ligId, targetSeq, ligDscrptrType, ligDscrptrStr, assayType, assayValueType, assayValue, assayPh, assayTemp, details))
                                        ordinalCat3 += 1

                                asymId = "?"
                                authAsymId = "?"
                                authSeqNum = "?"
                                detailsCat4 = "?"
                                featureType = "SUBJECT OF INVESTIGATION"
                                seqNum = "?"

                                aCat4.append((ordinalCat4, asymId, authAsymId, ligId, authSeqNum, ligId, detailsCat4, featureType, seqNum))
                                ordinalCat4 += 1

                            elif ligId == "HOH":
                                for dataSetIndx in range(0, 10):
                                    if dataSetIndx in dataSetDict:
                                        asymId = "?"
                                        authAsymId = dataSetDict[dataSetIndx]["chain_id"]
                                        authSeqNum = dataSetDict[dataSetIndx]["residuenum"]
                                        detailsCat4 = "?"
                                        featureType = "SUBJECT OF INVESTIGATION"
                                        seqNum = "?"

                                        aCat4.append((ordinalCat4, asymId, authAsymId, ligId, authSeqNum, ligId, detailsCat4, featureType, seqNum))
                                        ordinalCat4 += 1

                    elif ligId != "NONE%":  # no data acquired, ligid was simply selected to indicate as focus of research

                        asymId = "?"
                        authAsymId = "?"
                        authSeqNum = "?"
                        detailsCat4 = "?"
                        featureType = "SUBJECT OF INVESTIGATION"
                        seqNum = "?"

                        aCat4.append((ordinalCat4, asymId, authAsymId, ligId, authSeqNum, ligId, detailsCat4, featureType, seqNum))
                        ordinalCat4 += 1
                #
                if len(self.__rsrchAcqurdGrpLst) > 0:
                    curContainer.append(aCat3)
                #
                curContainer.append(aCat4)

            # pdbx_entry_details - only output if we have real info
            if len(self.__rsrchSlctdGrpLst) > 0:
                # LOI - including NONE%
                if "NONE%" in self.__rsrchSlctdGrpLst:
                    val = 'N'
                else:
                    val = 'Y'

                aCat5 = DataCategory("pdbx_entry_details")
                aCat5.appendAttribute("entry_id")
                aCat5.appendAttribute("has_ligand_of_interest")

                aCat5.append((depDataSetId, val))
                curContainer.append(aCat5)

            myDataList.append(curContainer)
            pdbxW = PdbxWriter(ofh)
            pdbxW.write(myDataList)
            ofh.close()

        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                self.__lfh.write("+ChemCompAssignStore.__generateUpdatedDepInfoFile() - generation of updated cc-dpstr-info file to %s failed \n" % updtedDpstrInfoFilePath)
            traceback.print_exc(file=self.__lfh)

        if self.__verbose and self.__debug:
            self.__lfh.write("+ChemCompAssignStore.__generateUpdatedDepInfoFile() ---- DEBUG ---- Dumping DataStore contents right after outputting file.\n")
            self.dumpData(self.__lfh)

    def __generateDpstrPrgrssFile(self, dpstrPrgrssFilePath, depDataSetId, p_mode):
        '''
        '''
        try:
            numGrpsRqurngAttn = len(self.getAttnReqdLst())
            numGrpsAddrsd = len(self.getGlbllyRslvdGrpList())
            numRsrchSelectedLst = len(self.getRsrchSelectedLst())
            numAuthAssignKeys = len(self.getAuthAssignmentKeys())

            # Finished set if one of the following:
            # a) mode = completed and # groups addressed = number needing attention
            # b) # grps rquring attention = 0
            # AND if # AuthAssignKeys != 0 and numRsrchSelectedLst != 0

            loiflag = (numAuthAssignKeys == 0) or (numAuthAssignKeys and numRsrchSelectedLst)
            if loiflag and (((p_mode == "completed") and (int(numGrpsAddrsd) == int(numGrpsRqurngAttn))) or (numGrpsRqurngAttn == 0)):
                doneFlag = "Y"
            else:
                doneFlag = "N"
            outputFile = open(dpstrPrgrssFilePath, "w")
            outputFile.write("deposit_ID\t%s\n" % depDataSetId.upper())
            outputFile.write("num_ligand_ids_requiring_attn\t%s\n" % numGrpsRqurngAttn)
            outputFile.write("num_ligand_ids_addressed\t%s\n" % numGrpsAddrsd)
            outputFile.write("finished\t%s\n" % doneFlag)
            outputFile.close()
        except:  # noqa: E722 pylint: disable=bare-except
            if (self.__verbose):
                self.__lfh.write("+ChemCompAssignStore.__generateDpstrPrgrssFile() - generation of updated cc-dpstr-progress file to %s failed \n" % dpstrPrgrssFilePath)
            traceback.print_exc(file=self.__lfh)

    def wasBorn(self):
        """ Returns boolean indicating whether or not a persistent ChemCompDataStore for this
            particular deposition dataset had been previously established/serialized?
        """
        return self.__wasBorn

    def getFilePath(self):
        return self.__filePath

    def getAuthAssignmentKeys(self):
        try:
            keys = list(self.__authAssignment.keys())
            keys.sort()
            return keys
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setAuthAssignment(self, instId, ccId):
        try:
            self.__authAssignment[instId] = ccId
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getAuthAssignment(self, instId):
        try:
            return self.__authAssignment[instId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setBatchBestHit(self, instId, ccId, mtchStatus, mtchScore):
        try:
            self.__batchBestHitAssignment[instId] = (ccId, mtchStatus, mtchScore)
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getBatchBestHit(self, instId):
        try:
            return self.__batchBestHitAssignment[instId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def getBatchBestHitId(self, instId):
        try:
            return self.__batchBestHitAssignment[instId][0]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def getBatchBestHitStatus(self, instId):
        try:
            return self.__batchBestHitAssignment[instId][1]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def getBatchBestHitScore(self, instId):
        try:
            return self.__batchBestHitAssignment[instId][2]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setAnnotAssignment(self, instId, ccId):
        try:
            self.__annotAssignment[instId] = ccId
            grp = self.getAuthAssignment(instId)
            #
            if ccId != 'Not Assigned':
                # if value of ccId is anything other than 'Not Assigned'
                # then we assume that the ligand instance is being
                # assigned to a valid chem component definition ID
                if grp not in self.__drtyGrpCnts.keys():
                    # group to which ligand instance belongs
                    # will not be a key the drtyGrpCnts dictionary
                    # if this is the first time a ligand in that
                    # group is being assigned an CCID
                    # So create first key/value entry with count of '1'
                    self.__drtyGrpCnts[grp] = 1
                else:
                    self.__drtyGrpCnts[grp] += 1
                if grp not in self.__drtyGrpList:
                    # if this is first time a ligand in the
                    # entity group is being assigned then also
                    # need to add to the drtyGrpList
                    self.__drtyGrpList.append(grp)
            #
            elif ccId == 'Not Assigned':
                # we end up inside this code if
                # ligand instance is actively being
                # de-assigned by annotator from a
                # prior assignment (i.e. user changed their mind)
                self.__drtyGrpCnts[grp] -= 1
                if self.__drtyGrpCnts[grp] == 0:
                    self.__drtyGrpList.remove(grp)
            #
            self.serialize()
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getAnnotAssignment(self, instId):
        try:
            return self.__annotAssignment[instId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setNewCcDefined(self, instId, ccId):
        try:
            self.__newCcDefined[instId] = ccId
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getNewCcDefined(self, instId):
        try:
            return self.__newCcDefined[instId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setTopHitsList(self, instId, topHitsL):
        """ topHitsList is dictionary mapping of instance id to
            a list of tuples representing the top 5 candidate chem comp IDs
            resulting from the cc-assign search.
            When fully populated, each tuple is of form:
            (topHitCcId, topHitCcIdScore, matchWarning, ccName, ccFormula)
        """
        try:
            self.__topHitsList[instId] = topHitsL
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getTopHitsList(self, instId):
        """ topHitsList is dictionary mapping of instance id to
            a list of tuples representing the top 5 candidate chem comp IDs
            resulting from the cc-assign search.
            When fully populated, each tuple is of form:
            (topHitCcId, topHitCcIdScore, matchWarning, ccName, ccFormula)
        """
        try:
            return self.__topHitsList[instId]
        except:  # noqa: E722 pylint: disable=bare-except
            return []

    def setNewCandidatesList(self, instId, newCandidatesL):
        """ NewCandidatesList is dictionary mapping of instance id to
            a list of chem comp IDs that indicate those chem comp
            references that have been requested ad-hoc by user
            for comparison with the experimental ligand instance.
        """
        try:
            self.__newCandidatesList[instId] = newCandidatesL
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getNewCandidatesList(self, instId):
        """ NewCandidatesList is dictionary mapping of instance id to
            a list of chem comp IDs that indicate those chem comp
            references that have been requested ad-hoc by user
            for comparison with the experimental ligand instance.
        """
        try:
            return self.__newCandidatesList[instId]
        except:  # noqa: E722 pylint: disable=bare-except
            return []

    def purgeNewCandidatesLists(self):
        """ Empties the NewCandidatesList.
            NewCandidatesList is dictionary mapping of instance id to
            a list of chem comp IDs that indicate those chem comp
            references that have been requested ad-hoc by user
            for comparison with the experimental ligand instance.

        """
        try:
            self.__newCandidatesList = {}
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def setCcName(self, instId, name):
        try:
            self.__ccName[instId] = name  # pylint: disable=no-member
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getCcName(self, instId):
        try:
            return self.__ccName[instId]  # pylint: disable=no-member
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setCcFormula(self, instId, formula):
        try:
            self.__ccFormulaList[instId] = formula
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getCcFormula(self, instId):
        try:
            return self.__ccFormulaList[instId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setCcFormalChrg(self, instId, frmlChrg):
        try:
            self.__ccFormalChrgList[instId] = frmlChrg
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getCcFormalChrg(self, instId):
        try:
            return self.__ccFormalChrgList[instId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setCcAssgnWarning(self, instId, wrningMsg):
        try:
            self.__ccAssignmentWarning[instId] = wrningMsg
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getCcAssgnWarning(self, instId):
        try:
            return self.__ccAssignmentWarning[instId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setCcSingleAtomFlag(self, instId, singleAtomFlag):
        try:
            self.__ccSingleAtomFlag[instId] = singleAtomFlag
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getCcSingleAtomFlag(self, instId):
        try:
            return self.__ccSingleAtomFlag[instId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setAnnotNotes(self, instId, notes):
        try:
            self.__annotNotes[instId] = notes
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getAnnotNotes(self, instId):
        try:
            return self.__annotNotes[instId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setRerunParam_linkRadii(self, instId, lnkRadii):
        """ Records value of link radius delta last used when
            rerunning cc-assign search for given instance
        """
        try:
            self.__rerunParam_linkRadii[instId] = lnkRadii
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getRerunParam_linkRadii(self, instId):
        """ Returns value of link radius delta last used when
            rerunning cc-assign search for given instance
        """
        try:
            rtrnVal = self.__rerunParam_linkRadii[instId]
            return rtrnVal
        except:  # noqa: E722 pylint: disable=bare-except
            # KeyError exception occurs when search has
            # not yet been run with adjusted param, in which case
            # default value of "0.00" should be returned
            return "0.00"

    def setRerunParam_bondRadii(self, instId, bndRadii):
        """ Records value of bond radius delta last used when
            rerunning cc-assign search for given instance
        """
        try:
            self.__rerunParam_bondRadii[instId] = bndRadii
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getRerunParam_bondRadii(self, instId):
        """ Returns value of bond radius delta last used when
            rerunning cc-assign search for given instance
        """
        try:
            rtrnVal = self.__rerunParam_bondRadii[instId]
            return rtrnVal
        except:  # noqa: E722 pylint: disable=bare-except
            # KeyError exception occurs when search has
            # not yet been run with adjusted param, in which case
            # default value of "0.00" should be returned
            return "0.00"

    def setAtomMapDict(self, instId, atomMapDct):
        try:
            self.__atomMapDct[instId] = atomMapDct
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getAtomMapDict(self, instId):
        try:
            return self.__atomMapDct[instId]
        except:  # noqa: E722 pylint: disable=bare-except
            return []

    def getDrtyGrpList(self):
        try:
            return self.__drtyGrpList
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def getAssgndInstncsCntForGrp(self, grp):
        try:
            return self.__drtyGrpCnts[grp]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def addGrpToGlbllyAssgndLst(self, grp, assgnId):
        try:
            if not (grp in self.__GlbllyAssgndGrpLst):
                self.__GlbllyAssgndGrpLst.append(grp)
            self.__GlbllyAssgndDict[grp] = assgnId
        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def removeGrpFrmGlbllyAssgndLst(self, grp):
        try:
            if grp in self.__GlbllyAssgndGrpLst:
                self.__GlbllyAssgndGrpLst.remove(grp)
            self.__GlbllyAssgndDict[grp] = None
        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def getGlbllyAssgndGrpList(self):
        try:
            return self.__GlbllyAssgndGrpLst
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def getGlblAssgnForGrp(self, grp):
        try:
            return self.__GlbllyAssgndDict[grp]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def addInstIdToRerunSrchLst(self, instId):
        try:
            if not (instId in self.__instncRerunSrchLst):
                self.__instncRerunSrchLst.append(instId)
        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def getInstIdRerunSrchLst(self):
        try:
            return self.__instncRerunSrchLst
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def addGrpToGlblRerunSrchLst(self, grp, lnkRadii, bndRadii):
        try:
            if not (grp in self.__GlblRerunSrchLst):
                self.__GlblRerunSrchLst.append(grp)
            self.__GlblRerunSrchDict_lnkRadii[grp] = lnkRadii
            self.__GlblRerunSrchDict_bndRadii[grp] = bndRadii
        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def removeGrpFrmGlblRerunSrchLst(self, grp):
        try:
            if grp in self.__GlblRerunSrchLst:
                self.__GlblRerunSrchLst.remove(grp)
            self.__GlblRerunSrchDict_lnkRadii[grp] = None
            self.__GlblRerunSrchDict_bndRadii[grp] = None
        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def getGlblRerunSrchLst(self):
        try:
            return self.__GlblRerunSrchLst
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def getGlblRerunSrchParam_lnkRadii(self, grp):
        try:
            rtrnVal = self.__GlblRerunSrchDict_lnkRadii[grp]
            return rtrnVal
        except:  # noqa: E722 pylint: disable=bare-except
            # KeyError exception occurs when search has
            # not yet been run with adjusted param, in which case
            # default value of "0.00" should be returned
            return "0.00"

    def getGlblRerunSrchParam_bndRadii(self, grp):
        try:
            rtrnVal = self.__GlblRerunSrchDict_bndRadii[grp]
            return rtrnVal
        except:  # noqa: E722 pylint: disable=bare-except
            # KeyError exception occurs when search has
            # not yet been run with adjusted param, in which case
            # default value of "0.00" should be returned
            return "0.00"

    # Following "GlbllyRslvd" methods added in support of processing by Chem Comp "Lite" module

    def _getNextPartitionNumber(self):
        returnVal = self.__rslvdPrtnCntr
        self.__rslvdPrtnCntr += 1
        return returnVal

    def getRslvdGrpPartNumber(self, grp):
        return self.__rslvdPrtnDict[grp]

    def addGrpToRsrchDataAcqurdLst(self, grp):
        try:
            if not (grp in self.__rsrchAcqurdGrpLst):
                self.__rsrchAcqurdGrpLst.append(grp)

        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def removeGrpFrmRsrchDataAcqurdLst(self, grp):
        try:
            if grp in self.__rsrchAcqurdGrpLst:
                self.__rsrchAcqurdGrpLst.remove(grp)
                self.initializeGrpRsrchInfo(grp)
        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def getRsrchDataAcqurdLst(self):
        try:
            return self.__rsrchAcqurdGrpLst
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def addGrpToRsrchSelectedLst(self, grp):
        try:
            if not (grp in self.__rsrchSlctdGrpLst):
                self.__rsrchSlctdGrpLst.append(grp)

        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def removeGrpFrmRsrchSelectedLst(self, grp):
        try:
            if grp in self.__rsrchSlctdGrpLst:
                self.__rsrchSlctdGrpLst.remove(grp)
                self.initializeGrpRsrchInfo(grp)
        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def getRsrchSelectedLst(self):
        try:
            return self.__rsrchSlctdGrpLst
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def addGrpToGlbllyRslvdLst(self, grp):
        try:
            if not (grp in self.__GlbllyRslvdGrpLst):
                self.__GlbllyRslvdGrpLst.append(grp)

                if not (grp in self.__rslvdPrtnDict):
                    self.__rslvdPrtnDict[grp] = self._getNextPartitionNumber()

        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def removeGrpFrmGlbllyRslvdLst(self, grp):
        try:
            if grp in self.__GlbllyRslvdGrpLst:
                self.__GlbllyRslvdGrpLst.remove(grp)
                self.initializeGrpInfo(grp)
        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def getGlbllyRslvdGrpList(self):
        try:
            return self.__GlbllyRslvdGrpLst
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def addGrpToAttnReqdLst(self, grp):
        try:
            if not (grp in self.__dpstrAttnRqdGrpLst):
                self.__dpstrAttnRqdGrpLst.append(grp)
        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def removeGrpFromAttnReqdLst(self, grp):
        try:
            if grp in self.__dpstrAttnRqdGrpLst:
                self.__dpstrAttnRqdGrpLst.remove(grp)
        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def getAttnReqdLst(self):
        try:
            return self.__dpstrAttnRqdGrpLst
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def initializeGrpInfo(self, grp):
        self.__dpstrCcExactMatchId[grp] = '?'
        self.__dpstrCcAltId[grp] = '?'
        self.__dpstrCcType[grp] = '?'
        self.__dpstrCcName[grp] = '?'
        self.__dpstrCcFrmla[grp] = '?'
        self.__dpstrSubmitChoice[grp] = ''
        self.__dpstrCcDscrptrType[grp] = '?'
        self.__dpstrCcDscrptrStr[grp] = '?'
        self.__dpstrComments[grp] = '?'
        # self.__dpstrUploadFiles={}   # dictionary mapping ligand code to file upload(s) by depositor

    def initializeGrpRsrchInfo(self, grp):
        try:
            self.__dpstrCcRsrchInfo[grp] = {}
        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def setResearchData(self, grp, dict):  # pylint: disable=redefined-builtin
        try:
            self.__dpstrCcRsrchInfo[grp] = dict.copy()

            if self.__verbose:
                for index in self.__dpstrCcRsrchInfo[grp]:
                    for attr in self.__dpstrCcRsrchInfo[grp][index]:
                        self.__lfh.write("+%s.%s() self.__dpstrCcRsrchInfo[%s][%s][%s] is: %s\n" %
                                         (self.__class__.__name__, inspect.currentframe().f_code.co_name, grp, index, attr, self.__dpstrCcRsrchInfo[grp][index][attr]))
        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def getResearchData(self, grp):
        try:
            if grp in self.__dpstrCcRsrchInfo:
                return self.__dpstrCcRsrchInfo[grp].copy()
            else:
                self.__lfh.write("+%s.%s() -- key '%s' NOT FOUND IN self.__dpstrCcRsrchInfo[]\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, grp))
                return None
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def addLigIdToInvalidLst(self, grp):
        try:
            if not (grp in self.__dpstrInvalidGrpIdLst):
                self.__dpstrInvalidGrpIdLst.append(grp)
        except:  # noqa: E722 pylint: disable=bare-except
            pass

    def getDpstrInvalidLigIdLst(self):
        try:
            return self.__dpstrInvalidGrpIdLst
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setDpstrExactMtchCcId(self, grpId, exactMtchId):
        try:
            if exactMtchId is None:
                del self.__dpstrCcExactMatchId[grpId]
            else:
                self.__dpstrCcExactMatchId[grpId] = exactMtchId
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrExactMtchCcId(self, grpId):
        try:
            return self.__dpstrCcExactMatchId[grpId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None
    #########################################################################
    # 2017-05-03 Notion of "master depositor ccid" to capture permanently
    # what depositor originally denoted as CCID ==> becomes important
    # in cases when annotator reruns ligand module and ends up changing
    # "author assigned CCID"

    def setDpstrOrigCcIdMaster(self, instId, dpstrSbmttdID):
        try:
            self.__dpstrOrigCcIdMaster[instId] = dpstrSbmttdID
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrOrigCcIdMaster(self, instId):
        try:
            return self.__dpstrOrigCcIdMaster[instId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    #########################################################################

    def setDpstrAltCcId(self, grpId, altId):
        try:
            if altId is None:
                del self.__dpstrCcAltId[grpId]
            else:
                self.__dpstrCcAltId[grpId] = altId
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrAltCcId(self, grpId):
        try:
            return self.__dpstrCcAltId[grpId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setDpstrCcType(self, grpId, type):  # pylint: disable=redefined-builtin
        try:
            self.__dpstrCcType[grpId] = type
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrCcType(self, grpId):
        try:
            return self.__dpstrCcType[grpId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setDpstrCcName(self, grpId, name):
        try:
            self.__dpstrCcName[grpId] = name
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrCcName(self, grpId):
        try:
            return self.__dpstrCcName[grpId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setDpstrCcFrmla(self, grpId, frmla):
        try:
            self.__dpstrCcFrmla[grpId] = frmla
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrCcFrmla(self, grpId):
        try:
            return self.__dpstrCcFrmla[grpId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setDpstrSubmitChoice(self, grpId, choice):
        try:
            self.__dpstrSubmitChoice[grpId] = choice
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrSubmitChoice(self, grpId):
        try:
            return self.__dpstrSubmitChoice[grpId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setDpstrCcDscrptrType(self, grpId, dscrptrType):
        try:
            self.__dpstrCcDscrptrType[grpId] = dscrptrType
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrCcDscrptrType(self, grpId):
        try:
            return self.__dpstrCcDscrptrType[grpId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setDpstrCcDscrptrStr(self, grpId, ligStr):
        try:
            self.__dpstrCcDscrptrStr[grpId] = ligStr
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrCcDscrptrStr(self, grpId):
        try:
            return self.__dpstrCcDscrptrStr[grpId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setDpstrUploadFile(self, grpId, fileType, fileName):
        if fileType == 'cif':
            fileType = 'pdbx'
        try:
            if grpId not in self.__dpstrUploadFiles:
                self.__dpstrUploadFiles[grpId] = {}
                if (self.__verbose):
                    self.__lfh.write("+%s.%s() ----- key created in self.__dpstrUploadFiles dict for %s\n" %
                                     (self.__class__.__name__, inspect.currentframe().f_code.co_name, grpId))
            if grpId not in self.__dpstrUpldFlsOrder:
                self.__dpstrUpldFlsOrder[grpId] = []
                if self.__verbose:
                    self.__lfh.write("+%s.%s() ----- key created in self.__dpstrUpldFlsOrder dict for %s\n" %
                                     (self.__class__.__name__, inspect.currentframe().f_code.co_name, grpId))

            if fileType not in self.__dpstrUploadFiles[grpId]:
                self.__dpstrUploadFiles[grpId][fileType] = {}
                if self.__verbose:
                    self.__lfh.write("+%s.%s() ----- key created in self.__dpstrUploadFiles[%s] for %s\n" %
                                     (self.__class__.__name__, inspect.currentframe().f_code.co_name, grpId, fileType))
            if fileName not in self.__dpstrUploadFiles[grpId][fileType]:
                self.__dpstrUploadFiles[grpId][fileType][fileName] = None

            # add to temporally oriented list so that we can track which files were uploaded first-to-last in time, so that we give authoritative precedence to last fileuploaded
            # note that user may choose to upload a file/fileName that has been previously uploaded
            self.__dpstrUpldFlsOrder[grpId].append(fileName)

            if (self.__verbose):
                self.__lfh.write("+%s.%s() ----- filename(s) returned for grpId, %s, and fileType, %s, is: %r\n" %
                                 (self.__class__.__name__, inspect.currentframe().f_code.co_name, grpId, fileType, self.__dpstrUploadFiles[grpId][fileType].keys()))
                self.__lfh.write("+%s.%s() ----- filename(s) in order of upload for grpId, %s, are: %r\n" %
                                 (self.__class__.__name__, inspect.currentframe().f_code.co_name, grpId, self.__dpstrUpldFlsOrder[grpId]))

            return True
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrUploadFile(self, grpId, fileType):
        try:
            return list(self.__dpstrUploadFiles[grpId][fileType].keys())
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setDpstrUploadFileWfPath(self, grpId, fileType, fileName, wfFlPath):
        try:
            if fileName in self.__dpstrUploadFiles[grpId][fileType]:
                self.__dpstrUploadFiles[grpId][fileType][fileName] = wfFlPath
                return True
            else:
                return False
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrUploadFileWfPath(self, grpId, fileType, fileName):
        try:
            return self.__dpstrUploadFiles[grpId][fileType][fileName]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def getDpstrUploadFilesDict(self):
        try:
            return self.__dpstrUploadFiles
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def getDpstrUploadFilesOrder(self, grpId):
        try:
            if grpId in self.__dpstrUpldFlsOrder:
                return self.__dpstrUpldFlsOrder[grpId]
            else:
                return []
        except:  # noqa: E722 pylint: disable=bare-except
            return None

#####################################################################################

    def setDpstrSketchFile(self, grpId, fileType, fileName):
        try:
            if grpId not in self.__dpstrSketchFiles:
                self.__dpstrSketchFiles[grpId] = {}
                if (self.__verbose):
                    self.__lfh.write("+%s.%s() ----- key created in self.__dpstrSketchFiles dict for %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, grpId))
            if fileType not in self.__dpstrSketchFiles[grpId]:
                self.__dpstrSketchFiles[grpId][fileType] = {}
                if (self.__verbose):
                    self.__lfh.write("+%s.%s() ----- key created in self.__dpstrSketchFiles[%s] for %s\n" %
                                     (self.__class__.__name__, inspect.currentframe().f_code.co_name, grpId, fileType))
            if fileName not in self.__dpstrSketchFiles[grpId][fileType]:
                self.__dpstrSketchFiles[grpId][fileType][fileName] = None
            if self.__verbose:
                self.__lfh.write("+%s.%s() ----- filename(s) returned for grpId, %s, and fileType, %s, is: %r\n" %
                                 (self.__class__.__name__, inspect.currentframe().f_code.co_name, grpId, fileType, self.__dpstrSketchFiles[grpId][fileType].keys()))

            return True
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrSketchFile(self, grpId, fileType='sdf'):
        try:
            return list(self.__dpstrSketchFiles[grpId][fileType].keys())
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setDpstrSketchFileWfPath(self, grpId, fileType, fileName, wfFlPath):
        try:
            if fileName in self.__dpstrSketchFiles[grpId][fileType].keys():
                self.__dpstrSketchFiles[grpId][fileType][fileName] = wfFlPath
                return True
            else:
                return False
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrSketchFileWfPath(self, grpId, fileName, fileType='sdf'):
        try:
            return self.__dpstrSketchFiles[grpId][fileType][fileName]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def setDpstrSketchMolDataStr(self, grpId, molDataStr):
        try:
            self.__dpstrSketchMolStr[grpId] = molDataStr
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrSketchMolDataStr(self, grpId):
        try:
            return self.__dpstrSketchMolStr[grpId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def getDpstrSketchFilesDict(self):
        try:
            return self.__dpstrSketchFiles
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    #####################################################################################

    def getAllDpstrWfFilePths(self, grpId):
        rtrnLst = []
        try:
            if grpId in self.__dpstrSketchFiles:
                for fileType in self.__dpstrSketchFiles[grpId]:
                    for fileName in self.__dpstrSketchFiles[grpId][fileType]:
                        rtrnLst.append(self.__dpstrSketchFiles[grpId][fileType][fileName])

            if grpId in self.__dpstrUploadFiles:
                for fileType in self.__dpstrUploadFiles[grpId]:
                    for fileName in self.__dpstrUploadFiles[grpId][fileType]:
                        rtrnLst.append(self.__dpstrUploadFiles[grpId][fileType][fileName])

        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                self.__lfh.write("+%s.%s() ----- WARNING ----- processing failed id:  %s\n" % (self.__class__.__name__, inspect.currentframe().f_code.co_name, grpId))
                traceback.print_exc(file=self.__lfh)
                self.__lfh.flush()
            return []

        return rtrnLst

#####################################################################################

    def setDpstrComments(self, grpId, comments):
        try:
            self.__dpstrComments[grpId] = comments
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getDpstrComments(self, grpId):
        try:
            return self.__dpstrComments[grpId]
        except:  # noqa: E722 pylint: disable=bare-except
            return None

    def minReqsMetForDescrNwLgnd(self, grpId):
        try:
            if (self.__dpstrCcType[grpId] is not None and len(self.__dpstrCcType[grpId]) > 1) and \
               (self.__dpstrCcDscrptrStr[grpId] is not None and len(self.__dpstrCcDscrptrStr[grpId]) > 1):
                return True
            else:
                return False
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def dump(self, ofh):
        """  Dump indexes -

        """
        ofh.write("\nKeys in authAssignment dict ----------------------------- \n")
        # python3 dict_keys cannot be sorted
        keys = list(self.__authAssignment.keys())
        keys.sort()
        for instId in keys:
            ofh.write("Instance id: %s\n" % instId)

        ofh.write("\nKeys in batchBestHitAssignment dict ----------------------------- \n")
        keys = list(self.__batchBestHitAssignment.keys())
        keys.sort()
        for instId in keys:
            ofh.write("Instance id: %s\n" % instId)

        ofh.write("\nKeys in topHitsList dict ----------------------------- \n")
        keys = list(self.__topHitsList.keys())
        keys.sort()
        for instId in keys:
            ofh.write("Instance id: %s\n" % instId)

        ofh.write("\nKeys in annotAssignment dict ----------------------------- \n")
        keys = list(self.__annotAssignment.keys())
        keys.sort()
        for instId in keys:
            ofh.write("Instance id: %s\n" % instId)

    def dumpData(self, ofh):
        ofh.write("+ChemCompAssignStore.dumpData -- starting\n")

        keys = list(self.__dpstrOrigCcIdMaster.keys())
        keys.sort()
        for instId in keys:
            ofh.write("Original depositor ccID for instID, %s, is : %s\n" % (instId, self.__dpstrOrigCcIdMaster[instId]))

        for ligid in self.__rsrchSlctdGrpLst:
            ofh.write("List of IDs selected for research includes: %s \n" % ligid)

        keys = list(self.__dpstrCcRsrchInfo.keys())
        keys.sort()
        for ligid in keys:
            ofh.write("Research data for LigID, %s, is : %r\n" % (ligid, self.__dpstrCcRsrchInfo[ligid]))

        keys = list(self.__authAssignment.keys())
        keys.sort()
        for instId in keys:
            ofh.write("Author assigned ccID for instID, %s, is : %s\n" % (instId, self.__authAssignment[instId]))

        keys = list(self.__batchBestHitAssignment.keys())
        keys.sort()
        for instId in keys:
            ofh.write("Best batch srch hit ccID and hit status for instID, %s, is : %s, %s\n" %
                      (instId, self.__batchBestHitAssignment[instId][0], self.__batchBestHitAssignment[instId][1]))

        keys = list(self.__topHitsList.keys())
        keys.sort()
        for instId in keys:
            for tupl in self.__topHitsList[instId]:
                ofh.write("Top Hits Data contents for instance ID %s is %s\n" % (instId, tupl))

        keys = list(self.__newCandidatesList.keys())
        keys.sort()
        for instId in keys:
            for tupl in self.__newCandidatesList[instId]:
                ofh.write("Non-Candidates contents for instance ID %s is %s\n" % (instId, tupl))

        keys = list(self.__ccNameList.keys())
        keys.sort()
        for instId in keys:
            ofh.write("CC determined name for instID, %s, is : %s\n" % (instId, self.__ccNameList[instId]))

        keys = list(self.__ccFormulaList.keys())
        keys.sort()
        for instId in keys:
            ofh.write("CC determined formula for instID, %s, is : %s\n" % (instId, self.__ccFormulaList[instId]))

        keys = list(self.__ccFormalChrgList.keys())
        keys.sort()
        for instId in keys:
            ofh.write("CC determined formal charge for instID, %s, is : %s\n" % (instId, self.__ccFormalChrgList[instId]))

        keys = list(self.__ccAssignmentWarning.keys())
        keys.sort()
        for instId in keys:
            ofh.write("CC assignment warning for instID, %s, is : %s\n" % (instId, self.__ccAssignmentWarning[instId]))

        keys = list(self.__ccSingleAtomFlag.keys())
        keys.sort()
        for instId in keys:
            ofh.write("CC single atom flag for instID, %s, is : %s\n" % (instId, self.__ccSingleAtomFlag[instId]))

        keys = list(self.__annotAssignment.keys())
        keys.sort()
        for instId in keys:
            ofh.write("Annotator-assigned ccID for instID, %s, is : %s\n" % (instId, self.__annotAssignment[instId]))

        for grp in self.__drtyGrpList:
            ofh.write("drtyGrpList dump: auth-assigned group containing annotator-assigned instance(s): %s\n" % grp)

        for grp in self.__GlbllyAssgndGrpLst:
            ofh.write("glbllyAssgndGrpList dump: group that was assigned via 'All Instances' view: %s\n" % grp)

        keys = list(self.__GlbllyAssgndDict.keys())
        keys.sort()
        for grp in keys:
            ofh.write("GlbllyAssgndDict dump: ccid %s was assigned via 'All Instances' view to authAssgndGrp %s\n" % (self.__GlbllyAssgndDict[grp], grp))
        for grp in self.__GlblRerunSrchLst:
            ofh.write("GlblRerunSrchLst dump: group for which search was rerun via 'All Instances' view: %s\n" % grp)

        keys = list(self.__GlblRerunSrchDict_lnkRadii.keys())
        keys.sort()
        for grp in keys:
            ofh.write("GlblRerunSrchDict_lnkRadii dump: authAssgndGrp %s currently has link radius delta value of %s\n" % (grp, self.__GlblRerunSrchDict_lnkRadii[grp]))

        keys = list(self.__GlblRerunSrchDict_bndRadii.keys())
        keys.sort()
        for grp in keys:
            ofh.write("GlblRerunSrchDict_bndRadii dump: authAssgndGrp %s currently has bond radius delta value of %s\n" % (grp, self.__GlblRerunSrchDict_bndRadii[grp]))

        for instId in self.__instncRerunSrchLst:
            ofh.write("instncRerunSrchLst dump: instId for which search was rerun via 'Single Instance' view: %s\n" % instId)

        keys = list(self.__rerunParam_linkRadii.keys())
        keys.sort()
        for instId in keys:
            ofh.write("rerunParam_linkRadii dump: instId %s currently has link radius delta value of %s\n" % (instId, self.__rerunParam_linkRadii[instId]))

        keys = list(self.__rerunParam_bondRadii.keys())
        keys.sort()
        for instId in keys:
            ofh.write("__rerunParam_bondRadii dump: instId %s currently has bond radius delta value of %s\n" % (instId, self.__rerunParam_bondRadii[instId]))

        keys = list(self.__newCcDefined.keys())
        keys.sort()
        for instId in keys:
            ofh.write("__newCcDefined dump: instId %s currently has new CC ID defined of %s\n" % (instId, self.__newCcDefined[instId]))

        keys = list(self.__dpstrCcExactMatchId.keys())
        keys.sort()
        for grpId in keys:
            ofh.write("Mismatches in grpId '%s' currently have value of '%s' for exact match ID.\n" % (grpId, self.__dpstrCcExactMatchId[grpId]))

        keys = list(self.__dpstrCcType.keys())
        keys.sort()
        for grpId in keys:
            ofh.write("Mismatches in grpId '%s' currently have value of '%s' for auth provided ligand type.\n" % (grpId, self.__dpstrCcType[grpId]))

        keys = list(self.__dpstrCcAltId.keys())
        keys.sort()
        for grpId in keys:
            ofh.write("Mismatches in grpId '%s' currently have value of '%s' for author proposed alternate ID.\n" % (grpId, self.__dpstrCcAltId[grpId]))

        ccIds = list(self.__dpstrCcName.keys())
        ccIds.sort()
        for ccId in ccIds:
            ofh.write("Mismatches in ccId '%s' currently given auth provided ligand descriptor string of '%s'\n" % (ccId, self.__dpstrCcDscrptrStr[ccId]))

        grpIds = list(self.__dpstrUploadFiles.keys())
        grpIds.sort()
        for grpId in grpIds:
            flTypes = list(self.__dpstrUploadFiles[grpId].keys())
            flTypes.sort()
            for flType in flTypes:
                ofh.write("File(s) uploaded for grpId '%s'and fileType '%s': %r \n" % (grpId, flType, self.__dpstrUploadFiles[grpId][flType].items()))

        grpIds = list(self.__dpstrSketchFiles.keys())
        grpIds.sort()
        for grpId in grpIds:
            flTypes = list(self.__dpstrSketchFiles[grpId].keys())
            flTypes.sort()
            for flType in flTypes:
                ofh.write("Sketch file(s) generated for grpId '%s'and fileType '%s': %r \n" % (grpId, flType, self.__dpstrSketchFiles[grpId][flType].items()))

        for ligId in self.__dpstrAttnRqdGrpLst:
            ofh.write("Ligand ID requiring attention: %s\n" % ligId)

        for rid in self.__rslvdPrtnDict:
            ofh.write("Globally resolved Lig Id to Partition Number mapping. ID: '%s' to P#: '%s' \n" % (rid, self.__rslvdPrtnDict[rid]))

        ofh.write("Current next available resolved Lig ID partition number is: %s\n" % self.__rslvdPrtnCntr)

        for ligid in self.__dpstrUpldFlsOrder:
            ofh.write("Dpstr uploaded files sequence for ligID: '%s' is %r \n" % (ligid, self.__dpstrUpldFlsOrder[ligid]))
