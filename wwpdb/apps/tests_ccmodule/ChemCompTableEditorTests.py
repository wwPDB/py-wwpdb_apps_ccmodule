##
# File:    ChemCompTableEditorTests.py
# Date:    23-Aug-2010
#
# Updates:
##
"""
Test cases chemical component table edit operations.

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.01"

import sys, unittest, traceback
import time, os, os.path

from wwpdb.apps.ccmodule.edit.ChemCompTableEditor       import ChemCompTableEditor
from wwpdb.apps.ccmodule.edit.ChemCompTableEditorDepict import ChemCompTableEditorDepict
from wwpdb.apps.ccmodule.webapp.WebRequest              import ChemCompInputRequest


class ChemCompTableEditorTests(unittest.TestCase):
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
    
    def testTableEditorFileOne(self): 
        """ 
        """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % sys._getframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        try:
            ccId=self.__fileList[0][1]
            fileFormat='cif'
            filePath=self.__fileList[0][0]
            #
            self.__lfh.write("Session path is %s\n" % self.__sessionPath)
            ccE=ChemCompTableEditor(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
            ccE.setFilePath(filePath,ccFileFormat=fileFormat,ccId=ccId)
            eD=ccE.doEdit()
            ccED=ChemCompTableEditorDepict(self.__verbose,log=self.__lfh)
            oL=ccED.doRender(eD)
            self.__lfh.write("%s\n" % '\n'.join(oL))
            
        except:
            traceback.print_exc(file=self.__lfh)
            self.fail()




def suite():
    return unittest.makeSuite(ChemCompTableEditorTests,'test')

if __name__ == '__main__':
    unittest.main()

