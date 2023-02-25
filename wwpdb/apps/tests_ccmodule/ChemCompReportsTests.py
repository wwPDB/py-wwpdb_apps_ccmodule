##
# File:    ChemCompReportsTests.py
# Date:    04-Aug-2010
#
# Updates:
# 04-Aug-2010 jdw Ported to module ccmodule
##
"""
Test cases chemical component report generation

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import sys
import unittest
import traceback
import os
import os.path

from wwpdb.apps.ccmodule.reports.ChemCompReports import ChemCompReport, ChemCompCheckReport
from wwpdb.utils.session.WebRequest import InputRequest
from wwpdb.utils.testing.Features import Features


@unittest.skipUnless(Features().haveToolsRuntime(), "Needs OneDep tools for testing")
class ChemCompReportsTests(unittest.TestCase):
    def setUp(self):
        self.__verbose = True
        self.__lfh = sys.stderr
        self.__topPath = os.getenv("WWPDB_CCMODULE_TOP_PATH")
        #
        # Create a request object and session directories for test cases
        #
        self.__reqObj = InputRequest(paramDict={}, verbose=self.__verbose, log=self.__lfh)
        self.__reqObj.setValue("TopSessionPath", self.__topPath)
        self.__reqObj.setValue("TopPath", self.__topPath)
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        self.__sobj = self.__reqObj.newSessionObj()
        self.__sessionPath = self.__sobj.getPath()
        self.__fileList = [(os.path.abspath("../data/ATP.cif"), "atp"), (os.path.abspath("../data/GTP.cif"), "gtp")]

    def tearDown(self):
        pass

    def testReportIdOne(self):
        """ """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % sys._getframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        try:
            self.__lfh.write("Session path is %s\n" % self.__sessionPath)
            ccR = ChemCompReport(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            ccR.setDefinitionId(definitionId="atp")
            ccR.doReport()

            htmlText = ccR.getReportHtml()
            self.__lfh.write("%s\n" % htmlText)

            rD = ccR.getReportFilePaths()
            for k, v in rD.items():
                self.__lfh.write("Key %30s value %s\n" % (k, v))

        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=sys.stdout)
            self.fail()

    def testReportFileOne(self):
        """ """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % sys._getframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        try:
            self.__lfh.write("Session path is %s\n" % self.__sessionPath)
            ccR = ChemCompReport(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            ccR.setFilePath(self.__fileList[0][0], self.__fileList[0][1])
            ccR.doReport()

            htmlText = ccR.getReportHtml()
            self.__lfh.write("%s\n" % htmlText)

            rD = ccR.getReportFilePaths()
            for k, v in rD.items():
                self.__lfh.write("Key %30s value %s\n" % (k, v))

        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=sys.stdout)
            self.fail()

    def testCheckReport1(self):
        """ """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % sys._getframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        try:
            self.__lfh.write("Session path is %s\n" % self.__sessionPath)
            ccR = ChemCompCheckReport(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            ccR.setDefinitionId(definitionId="gtp")
            ccR.doReport()

            htmlText = ccR.getReportHtml()
            self.__lfh.write("%s\n" % htmlText)

            rD = ccR.getReportFilePaths()
            for k, v in rD.items():
                self.__lfh.write("Key %30s value %s\n" % (k, v))

        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=sys.stdout)
            self.fail()


def suite():
    return unittest.makeSuite(ChemCompReportsTests, "test")


if __name__ == "__main__":
    unittest.main()
