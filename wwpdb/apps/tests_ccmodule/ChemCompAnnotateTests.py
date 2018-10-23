##
# File:    ChemCompAnnotateTests.py
# Date:    04-Aug-2010
#
# Updates:
# 04-Aug-2010 jdw Ported to module ccmodule
##
"""
Test cases chemical component annotation -

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.01"

import sys, unittest, traceback
import time, os, os.path

from wwpdb.apps.ccmodule.chem.ChemCompAnnotate     import ChemCompAnnotate
from wwpdb.apps.ccmodule.webapp.WebRequest         import ChemCompInputRequest


class ChemCompAnnotateTests(unittest.TestCase):
    def setUp(self):
        self.__verbose=True
        self.__lfh=sys.stderr
        self.__topPath=os.getenv('WWPDB_CCMODULE_TOP_PATH')
        #
        # Create a request object and session directories for test cases
        #
        self.__reqObj=ChemCompInputRequest(paramDict={},verbose=self.__verbose,log=self.__lfh)
        self.__reqObj.setValue("TopSessionPath", self.__topPath)
        self.__reqObj.setValue("TopPath",        self.__topPath)
        self.__reqObj.setDefaultReturnFormat(return_format="text")
        self.__sobj=self.__reqObj.newSessionObj()
        self.__sessionPath=self.__sobj.getPath()
        self.__fileList=[(os.path.abspath('../data/ATP.cif'),'atp'),(os.path.abspath('../data/GTP.cif'),'gtp')]
        

    def tearDown(self):
        pass
    

    def testAnnotateIdOne(self): 
        """ 
        """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % sys._getframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        try:
            self.__lfh.write("Session path is %s\n" % self.__sessionPath)
            ccR=ChemCompAnnotate(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
            ccR.setDefinitionId(definitionId='atp')
            ccR.doAnnotate()
            textData=ccR.getAnnotatedFileText()
            self.__lfh.write("%s\n" % textData)

        except:
            traceback.print_exc(file=self.__lfh)
            self.fail()


    def testAnnotateFileOne(self): 
        """ 
        """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % sys._getframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        try:
            self.__lfh.write("Session path is %s\n" % self.__sessionPath)
            ccR=ChemCompAnnotate(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
            ccR.setFilePath(self.__fileList[0][0],self.__fileList[0][1])
            ccR.doAnnotate()
            textData=ccR.getAnnotatedFileText()
            self.__lfh.write("%s\n" % textData)

        except:
            traceback.print_exc(file=self.__lfh)
            self.fail()




def suite():
    return unittest.makeSuite(ChemCompAnnotateTests,'test')

if __name__ == '__main__':
    unittest.main()

