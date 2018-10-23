##
# File:    ChemCompViewTests.py
# Date:    04-Aug-2010
#
# Updates:
# 04-Aug-2010 jdw Ported to module ccmodule
##
"""
Test cases chemical component view report operations

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.01"

import sys, unittest, traceback
import time, os, os.path

from wwpdb.apps.ccmodule.view.ChemCompView  import ChemCompView
from wwpdb.apps.ccmodule.view.ChemCompViewDepict  import ChemCompViewDepict
from wwpdb.apps.ccmodule.webapp.WebRequest        import ChemCompInputRequest
from wwpdb.utils.testing.Features                      import Features


@unittest.skipUnless(Features().haveToolsRuntime(), "Needs OneDep tools for testing")
class ChemCompViewTests(unittest.TestCase):
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
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        self.__sobj=self.__reqObj.newSessionObj()
        self.__sessionPath=self.__sobj.getPath()
        #
        #self.__rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        self.__idList=['atp','gtp']
        #
        
    def tearDown(self):
        pass
    

    def testView1(self): 
        """ 
        """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % sys._getframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        try:
            self.__lfh.write("Session path is %s\n" % self.__sessionPath)
            ccV=ChemCompView(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
            ccV.setIdList(self.__idList)
            ccInfoList=ccV.doView()
            cvD=ChemCompViewDepict(self.__verbose,self.__lfh)
            oL=cvD.doRender(ccInfoList)
            self.__lfh.write("%s" % "\n".join(oL))
            
            #for k,v in rD.items():
            #    self.__lfh.write("Key %30s value %s\n" % (k,v))   
        except:
            traceback.print_exc(file=sys.stdout)
            self.fail()

def suite():
    return unittest.makeSuite(ChemCompViewTests,'test')

if __name__ == '__main__':
    unittest.main()

