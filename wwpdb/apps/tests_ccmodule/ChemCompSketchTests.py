##
# File:    ChemCompSketchTests.py
# Date:    16-Aug-2010
#
# Updates:
# 16-Aug-2010 jdw Ported to module ccmodule
##
"""
Test cases chemical component sketch launcher

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.01"

import sys, unittest, traceback
import time, os, os.path

from wwpdb.apps.ccmodule.sketch.ChemCompSketch        import ChemCompSketch
from wwpdb.apps.ccmodule.sketch.ChemCompSketchDepict  import ChemCompSketchDepict
from wwpdb.apps.ccmodule.webapp.WebRequest            import ChemCompInputRequest

class ChemCompSketchTests(object):
    # class ChemCompSketchTests(unittest.TestCase):
    def __init__(self):
        self.setUp()
        
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
        self.__fileList=[(os.path.abspath('../data/ATP.cif'),'atp'),(os.path.abspath('../data/GTP.cif'),'gtp')]

        self.__reqObj.setValue("sizexy", '500')        

    def tearDown(self):
        pass
    

    def testSketchtIdOne(self): 
        """ 
        """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % sys._getframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        try:
            self.__lfh.write("Session path is %s\n" % self.__sessionPath)
            ccSk=ChemCompSketch(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
            ccSk.setCcId(ccId='atp')
            rD=ccSk.doSketch()

            for k,v in rD.items():
                self.__lfh.write("Key %30s value %s\n" % (k,v))
            
            ccR=ChemCompSketchDepict(verbose=self.__verbose,log=self.__lfh)
            oL=ccR.doRender(rD)
            self.__lfh.write("%s" % "\n".join(oL))                        
            
        except:
            traceback.print_exc(file=sys.stdout)
            #self.fail()



    def testSketchFileOne(self): 
        """ 
        """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % sys._getframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        try:
            self.__lfh.write("Session path is %s\n" % self.__sessionPath)
            ccSk=ChemCompSketch(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
            ccSk.setFilePath(self.__fileList[0][0],'cif',self.__fileList[0][1])
            rD=ccSk.doSketch()

            for k,v in rD.items():
                self.__lfh.write("Key %30s value %s\n" % (k,v))   

            ccR=ChemCompSketchDepict(verbose=self.__verbose,log=self.__lfh)
            oL=ccR.doRender(rD)
            self.__lfh.write("%s" % "\n".join(oL))
            
        except:
            traceback.print_exc(file=sys.stdout)
            #self.fail()


#def suite():
#    return unittest.makeSuite(ChemCompSketchTests,'test')

if __name__ == '__main__':
    # unittest.main()
    cT=ChemCompSketchTests()
    cT.testSketchtIdOne()
    cT.testSketchFileOne()    

