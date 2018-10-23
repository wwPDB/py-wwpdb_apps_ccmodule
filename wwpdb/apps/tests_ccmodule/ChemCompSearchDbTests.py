##
# File:    ChemCompSearchDbTests.py
# Date:    10-Aug-2010
#
# Updates:
# 10-Aug-2010 jdw Ported to module ccmodule
##
"""
Test cases chemical component extraction operations.


"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.01"

import time, os, os.path
import sys, unittest, traceback

from wwpdb.apps.ccmodule.webapp.WebRequest             import ChemCompInputRequest
from wwpdb.apps.ccmodule.search.ChemCompSearchDb       import ChemCompSearchDb
from wwpdb.apps.ccmodule.search.ChemCompSearchDbDepict import ChemCompSearchDbDepict
from wwpdb.utils.testing.Features                      import Features


@unittest.skipUnless(Features().haveToolsRuntime(), "Needs OneDep tools for testing")
class ChemCompSearchDbTests(unittest.TestCase): 
        
    def setUp(self):
        self.__verbose=True
        self.__lfh=sys.stderr
        self.__topPath=os.getenv('WWPDB_CCMODULE_TOP_PATH')
        self.__siteId=os.getenv('WWPDB_SITE_ID')        
        #
        # Create a request object and session directories for test cases
        #
        self.__reqObj=ChemCompInputRequest(paramDict={},verbose=self.__verbose,log=self.__lfh)
        self.__reqObj.setValue("WWPDB_SITE_ID",  self.__siteId)        
        self.__reqObj.setValue("TopSessionPath", self.__topPath)
        self.__reqObj.setValue("TopPath",        self.__topPath)
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        self.__sobj=self.__reqObj.newSessionObj()
        self.__sessionPath=self.__sobj.getPath()
        #
        self.__idList=['atp','gtp']
        #
        

    def testSearchDbOne(self): 
        """ 
        """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % sys._getframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        self.__lfh.flush()                
        try:
            self.__lfh.write("+ChemCompSearchDbTests.testSearchOne() Session path is %s\n" % self.__sessionPath)
            self.__reqObj.setValue("operation",  "LIKE")
            self.__reqObj.setValue("targetId",   "atp")                    

            ccS=ChemCompSearchDb(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
            rD=ccS.doIdSearch()
            for row in rD['resultlist']:
                for k,v in row.items():
                    self.__lfh.write(" %s %r\n" % (k,v) )

            ccSD=ChemCompSearchDbDepict(self.__verbose,self.__lfh)
            oL=ccSD.doRender(rD)            
            self.__lfh.write("%s" % "\n".join(oL))                            
        except:
            traceback.print_exc(file=self.__lfh)
            self.__lfh.flush()
            #self.fail()

    def tearDown(self):
        pass
    
def suite():
    return unittest.makeSuite(ChemCompSearchDbTests,'test')

if __name__ == '__main__':
    unittest.main()

