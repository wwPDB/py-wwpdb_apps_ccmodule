##
# File:  ChemCompView.py
# Date:  29-Jul-2010
# Updates:
# ---------------------------------------------------------------------------
# 2011-05-12  RPS  Piloting changes to doView() and getChemCompInfo() for standalone Ligand Editor Tool
# 2011-08-05  RPS  Updated with comments in support of generating "restructuredtext" documentation
# 2011-08-17  RPS  Updated so that ChemCompViewDepict uses inherited setSessionPaths() function from ChemCompDepict
#                     for establishing absolute and relative paths used for session data management
# 2012-10-24  RPS  Updated to reflect reorganization of modules in pdbx packages
##
"""
Create simple web views from chemical component definitions.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import os
import sys

from wwpdb.apps.ccmodule.reports.ChemCompReports import ChemCompReport
from wwpdb.apps.ccmodule.view.ChemCompViewDepict import ChemCompViewDepict
from mmcif_utils.chemcomp.PdbxChemCompIo import PdbxChemCompIo


class ChemCompView(object):
    """Create simple web views from chemical component definitions.

    """
    def __init__(self, reqObj, verbose=False, log=sys.stderr):
        """Create simple web views from chemical component definitions.

         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        self.__verbose = verbose
        self.__lfh = log
        self.__debug = True
        #
        self.__reqObj = reqObj
        #
        # self.__sobj=self.__reqObj.newSessionObj()
        #
        # self.__sObj = self.__reqObj.getSessionObj()
        # self.__sessionPath = self.__sObj.getPath()
        # self.__sessionRelativePath = self.__sObj.getRelativePath()

        #
        self.__idList = []  # pylint: disable=unused-private-member
        #

    def setIdList(self, idList):
        self.__idList = idList  # pylint: disable=unused-private-member

    def doView(self):
        """ Call to display data for given chem component in comparison grid of standalone version of chem comp module.

            :Helpers:

                + wwpdb.apps.ccmodule.reports.ChemCompReports.ChemCompReport
                + wwpdb.apps.ccmodule.view.ChemCompViewDepict.ChemCompViewDepict

            :Returns:
                ``rtrnCode``: integer indicating success of this operation
                    -1: failure
                    0: success
        """
        # determine which chem component is to be viewed (i.e. which chem comp ID has been passed in request)
        ccId = str(self.__reqObj.getValue("ccid")).upper()
        # return code indicating failure by default
        rtrnCode = -1
        #############################################################################################################
        #        Generate report material for requested dictionary reference
        #############################################################################################################
        ccReferncRprt = ChemCompReport(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        ccReferncRprt.setDefinitionId(definitionId=ccId)
        ccReferncRprt.doReport()
        rD = ccReferncRprt.getReportFilePaths()
        for k, v in rD.items():
            if self.__verbose:
                self.__lfh.write("+ChemCompView._doView() -- Reference file reporting -- Key %30s value %s\n" % (k, v))
        ##########################################################
        # interrogate report data in order to get name and
        # formula for the chem component reference
        #########################################################
        # ccRefFilePath=os.path.join(self.__sessionPath,ccId,'report',ccId+'.cif')
        ccRefFilePath = ccReferncRprt.getFilePath()
        #
        if os.access(ccRefFilePath, os.R_OK):
            chemCompD = self.getChemCompInfo(ccRefFilePath, ccId)
            rtrnCode = 0
            if self.__verbose:
                self.__lfh.write("+ChemCompView._doView() - successfully processing chem comp ID %s with name %s and formula %s\n" %
                                 (chemCompD['id'], chemCompD['name'], chemCompD['formula']))

        else:
            if self.__verbose:
                self.__lfh.write("+ChemCompView._doView() - NO reference chem comp file found for %s\n" % ccRefFilePath)
        #
        #########################################################
        # call render() methods to generate html markup to be supplied for display in comparison grid
        ccVD = ChemCompViewDepict(self.__verbose, self.__lfh)
        ccVD.setSessionPaths(self.__reqObj)
        # ccVD.doRender_ccRefForViewer(chemCompTupl,self.__reqObj)
        ccVD.doRender(chemCompD, self.__reqObj)
        #

        return rtrnCode

    def getChemCompInfo(self, cifPath, ccId):
        """ Extract data to be displayed for given chem component from cif definition file

            :Params:

                + ``cifPath``: path to cif chem component definition file for the given ccId
                + ``ccId`` : ID for chemical component for which info is being requested

            :Helpers:
                mmcif_utils.chemcomp.PdbxChemCompIo.PdbxChemCompIo

            :Returns:
                ``ccDict``: dictionary of chem comp fields to be displayed for the given ccId
        """
        ccDict = {}
        if os.path.exists(cifPath):
            ccf = PdbxChemCompIo(verbose=self.__verbose, log=self.__lfh)
            ccf.setFilePath(cifPath, compId=ccId)
            ccf.getComp()
            ccDL = ccf.getChemCompDict()
            if (len(ccDL) < 1):
                return ccDict

            ccD = ccDL[0]
            if (self.__verbose):
                for k, v in ccD.items():
                    self.__lfh.write("+ChemCompView.getChemCompInfo() key %20s  value %s\n" % (k, v))

            ccDict['id'] = ccD['_chem_comp.id']
            ccDict['status'] = ccD['_chem_comp.pdbx_release_status']
            ccDict['replaced'] = ccD['_chem_comp.pdbx_replaced_by']
            ccDict['replaces'] = ccD['_chem_comp.pdbx_replaces']
            ccDict['name'] = ccD['_chem_comp.name']
            ccDict['formula'] = ccD['_chem_comp.formula']
            ccDict['formal_charge'] = ccD['_chem_comp.pdbx_formal_charge']
            ccDict['synonyms'] = ccD['_chem_comp.pdbx_synonyms']
            ccDict['subcomplist'] = ccD['_chem_comp.pdbx_subcomponent_list']
            ccDict['creator'] = ccD['_chem_comp.pdbx_processing_site']
            ccDict['mod_date'] = ccD['_chem_comp.pdbx_modified_date']
            ccDict['nstd_parent'] = ccD['_chem_comp.mon_nstd_parent_comp_id']
            ccDict['type'] = ccD['_chem_comp.type']
            ccDict['pdbx_type'] = ccD['_chem_comp.pdbx_type']

        if (self.__debug):
            for k, v in ccDict.items():
                self.__lfh.write("+ChemCompView.getChemCompInfo() key %20s  value %s\n" % (k, v))

        return ccDict

    # def __addWordBreakAtHyphen(self, iString):
    #     oString = ""
    #     for i in iString:
    #         if i == '-':
    #             oString += i
    #             oString += "<wbr />"
    #         else:
    #             oString += i
    #     return oString
