##
# File:    ChemCompAssignTests.py
# Date:    13-Sept-2010 jdw
#
# Updates:
#
#  5-Dec-2010  jdw -- remove broken depiction test -
#              jdw -- add example of instance level assignment with parameter adjustment -
#
##
"""
Test cases chemical component batch assignment operations.


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

from wwpdb.utils.testing.Features import Features
from wwpdb.utils.session.WebRequest import InputRequest
from wwpdb.apps.ccmodule.chem.ChemCompAssign import ChemCompAssign

try:
    from wwpdb.apps.ccmodule.chem.ChemCompAssignDepict import ChemCompAssignDepict  # noqa: F401 pylint: disable=unused-import

    skiptest = False
except ImportError as _e:  # noqa: F841
    skiptest = False


@unittest.skipIf(skiptest, "Could not import oedepict")
@unittest.skipUnless(Features().haveToolsRuntime(), "Needs OneDep tools for testing")
class ChemCompAssignTests(unittest.TestCase):
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
        #
        # self.__rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        self.__fileList = [(os.path.abspath("../data/rcsb013067.cifeps"), "cifeps", "1_L_B12_1_"), (os.path.abspath("../data/rcsb057839.cif"), "cif", "")]
        #

    def testBatchAssignAll(self):
        """ """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % inspect.currentframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        self.__lfh.flush()
        try:
            self.__lfh.write("+ChemCompAssignTests.testBatchAssignAll() Session path is %s\n" % self.__sessionPath)
            self.__reqObj.setValue("filePath", self.__fileList[0][0])
            self.__reqObj.setValue("fileType", self.__fileList[0][1])
            ccE = ChemCompAssign(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            # add 0.2 Ang to the search radius
            ccE.setLinkRadii(0.2)
            #
            rD = ccE.doAssign()
            for k, v in rD.items():
                self.__lfh.write("+ChemCompAssignTests.testBatchAssignAll() key %30s   value %r\n" % (k, v))

        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.__lfh.flush()
            # self.fail()

    def testAssignInstance(self):
        """ """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % inspect.currentframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        self.__lfh.flush()
        try:
            # do the full batch assigment first --
            self.__lfh.write("+ChemCompAssignTests.testAssignInstance() Session path is %s\n" % self.__sessionPath)
            self.__reqObj.setValue("filePath", self.__fileList[0][0])
            self.__reqObj.setValue("fileType", self.__fileList[0][1])
            ccE = ChemCompAssign(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            rD = ccE.doAssign()
            #
            #
            # Follow this with a single instance assignment --
            #
            # add 0.4 Ang to the search radius
            ccE.setLinkRadii(0.2)
            ccE.setTargetInstanceId(self.__fileList[0][2])
            ccE.setBondRadii(0.20)
            rD = ccE.doAssignInstance()

            for k, v in rD.items():
                self.__lfh.write("+ChemCompAssignTests.testAssignInstance() key %30s   value %r\n" % (k, v))

        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            self.__lfh.flush()
            # self.fail()


def suite():
    return unittest.makeSuite(ChemCompAssignTests, "test")


if __name__ == "__main__":
    unittest.main()
