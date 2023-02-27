##
# File:    ChemCompSearchTests.py
# Date:    10-Aug-2010
#
# Updates:
# 10-Aug-2010 jdw Ported to module ccmodule
##
"""
Test cases chemical component extraction operations.


"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import os
import os.path
import sys
import unittest
import traceback
import inspect

from wwpdb.utils.session.WebRequest import InputRequest
from wwpdb.apps.ccmodule.search.ChemCompSearch import ChemCompSearch
from wwpdb.apps.ccmodule.search.ChemCompSearchDepict import ChemCompSearchDepict
from wwpdb.utils.testing.Features import Features


@unittest.skipUnless(Features().haveToolsRuntime(), "Needs OneDep tools for testing")
class ChemCompSearchTests(unittest.TestCase):
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
        self.__fileList = [(os.path.abspath("../data/ATP.cif"), "cif"), (os.path.abspath("../data/GTP.cif"), "cif")]
        #

    def testGraphSearchOne(self):
        """ """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % inspect.currentframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        self.__lfh.flush()
        try:
            self.__reqObj.setValue("operation", "prefilter-relaxed")
            self.__reqObj.setValue("filePath", self.__fileList[0][0])
            self.__reqObj.setValue("fileType", self.__fileList[0][1])

            ccS = ChemCompSearch(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            rD = ccS.doGraphIso()
            for row in rD["resultlist"]:
                for k, v in row.items():
                    self.__lfh.write(" %s %r\n" % (k, v))

            ccSD = ChemCompSearchDepict(self.__verbose, self.__lfh)
            oL = ccSD.doRenderGraph(rD)
            self.__lfh.write("%s" % "\n".join(oL))
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.__lfh.flush()
            # self.fail()

    def testIndexSearchOne(self):
        """ """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % inspect.currentframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        self.__lfh.flush()
        try:
            self.__lfh.write("+ChemCompSearchTests.testSearchOne() Session path is %s\n" % self.__sessionPath)
            self.__reqObj.setValue("operation", "formula-subset")
            self.__reqObj.setValue("target", "c30o10")

            ccS = ChemCompSearch(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            rD = ccS.doIndex()
            for row in rD["resultlist"]:
                for k, v in row.items():
                    self.__lfh.write(" %s %r\n" % (k, v))

            ccSD = ChemCompSearchDepict(self.__verbose, self.__lfh)
            oL = ccSD.doRenderIndex(rD)
            self.__lfh.write("%s" % "\n".join(oL))
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.__lfh.flush()
            # self.fail()

    def tearDown(self):
        pass


def suite():
    return unittest.makeSuite(ChemCompSearchTests, "test")


if __name__ == "__main__":
    unittest.main()
