##
# File:  ChemCompViewDepict.py
# Date:  06-Aug-2010
# Updates:
# ---------------------------------------------------------------------------
# 2011-05-12  RPS  Piloting changes to doRender() method for standalone Ligand Editor Tool
# 2011-08-17  RPS  Updated to use inherited methods from ChemCompDepict for establishing absolute and relative paths
#                    used for session data management
# 2011-08-23  RPS  Making use of self.jmolCodeBase as inherited from ChemCompDepict to indicate of location of Jmol applet code
# 2012-03-27  RPS  Updated to reflect improved organization of html template files as stored on server.
##
"""
Create HTML depiction for simple chemical component views

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import os
import sys
from wwpdb.apps.ccmodule.depict.ChemCompDepict import ChemCompDepict


class ChemCompViewDepict(ChemCompDepict):
    """Create HTML depiction for simple views from chemical component definitions.

    """
    def __init__(self, verbose=False, log=sys.stderr):
        """

         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        super(ChemCompViewDepict, self).__init__(verbose, log)
        self.__verbose = verbose
        self.__lfh = log
        # self.__debug = True
        #
        self.__pathDictViewTmplts = "templates/dictionary_ui"

    def doRender(self, p_ccDict, p_reqOb):
        ''' Generates html fragment used for representing chem comp reference in the viz compare grid-->these are written to files on server
        '''
        ccId = p_ccDict['id']
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompViewDepict.doRender_ccRefForViewer() starting for ccid %s\n" % ccId)
        #
        #
        sessionId = p_reqOb.getSessionId()
        htmlTmpltPth = os.path.join(p_reqOb.getValue("TemplatePath"), self.__pathDictViewTmplts)
        #
        checked = ''
        #
        sPathRel = os.path.join(self.rltvSessionPath, ccId)
        sPathAbslt = os.path.join(self.absltSessionPath, ccId)
        #
        p_ccDict['sess_path_rel'] = sPathRel
        p_ccDict['jmol_code_base'] = self.jmolCodeBase
        #
        #####################################################################################################################################
        # using p_ccDict to supply text substitution content for both cc_instnc_match_rslts_tbl_tmplt.html and cc_viz_cmp_li_tmplt.html
        #####################################################################################################################################
        p_ccDict['sessionid'] = sessionId
        #
        p_ccDict['name_displ'] = self.truncateForDisplay(p_ccDict['name'], maxlength=16)
        p_ccDict['synonyms_displ'] = self.truncateForDisplay(p_ccDict['synonyms'], maxlength=16)
        p_ccDict['formula_displ'] = self.truncateForDisplay(p_ccDict['formula'], maxlength=16)
        p_ccDict['replaced_by_displ'] = self.truncateForDisplay(p_ccDict['replaced'], maxlength=16)
        p_ccDict['replaces_displ'] = self.truncateForDisplay(p_ccDict['replaces'], maxlength=16)
        p_ccDict['nstd_parent_displ'] = self.truncateForDisplay(p_ccDict['nstd_parent'], maxlength=16)
        p_ccDict['subcomplist_displ'] = self.truncateForDisplay(p_ccDict['subcomplist'], maxlength=16)
        #
        p_ccDict['checked'] = checked
        p_ccDict['3dpath_ref'] = os.path.join(p_ccDict['sess_path_rel'], 'report', ccId)
        #################################################################################################
        # also populate templates used for displaying chem comp references in viz compare grid
        #################################################################################################
        htmlPathAbs = os.path.join(sPathAbslt)
        jmolPathAbs = os.path.join(sPathAbslt)
        htmlFilePathAbs = os.path.join(htmlPathAbs, ccId + '_viz_cmp_li.html')
        jmolFilePathAbs = os.path.join(jmolPathAbs, ccId + '_ref_jmol.html')
        #
        #################################################################################################
        # populate "cc_viz_cmp_li_tmplt.html"
        #    which contains placeholders for "instanceid", "ccid",and "assgn_sess_path_rel"
        #################################################################################################
        #
        #
        if not os.path.exists(htmlPathAbs):
            os.makedirs(htmlPathAbs)
        fp = open(htmlFilePathAbs, 'w')
        fp.write("%s" % self.processTemplate(tmpltPth=htmlTmpltPth, fn="cc_viz_cmp_li_tmplt_stndalnvw.html", parameterDict=p_ccDict))
        fp.close()
        #
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

        fp.write("%s" % self.processTemplate(tmpltPth=htmlTmpltPth, fn="cc_ref_jmol_tmplt_stndalnvw.html", parameterDict=p_ccDict))
        fp.close()
        #
        #################################################################################################
