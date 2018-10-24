##
# File:    ChemCompExtractTests.py
# Date:    04-Aug-2010
#
# Updates:
# 04-Aug-2010 jdw Ported to module ccmodule
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

try:
    from wwpdb.utils.session.WebRequest              import InputRequest
    from wwpdb.apps.ccmodule.extract.ChemCompExtract        import ChemCompExtract
    from wwpdb.apps.ccmodule.extract.ChemCompExtractDepict  import ChemCompExtractDepict
    skiptest = False
except ImportError as e:
    skiptest = True

class ChemCompExtractTests(object):
#
#class ChemCompExtractTests(unittest.TestCase):    
# There appears to be some conflict with the unittest class and the Swig packaging of Oechem 1.70
# hence running these as simple test cases - 
#
    def __init__(self):
        self.setup()
        
    def setup(self):
        self.__verbose=True
        self.__lfh=sys.stderr
        self.__topPath=os.getenv('WWPDB_CCMODULE_TOP_PATH')
        #
        # Create a request object and session directories for test cases
        #
        self.__reqObj=InputRequest(paramDict={},verbose=self.__verbose,log=self.__lfh)
        self.__reqObj.setValue("TopSessionPath", self.__topPath)
        self.__reqObj.setValue("TopPath",        self.__topPath)
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        self.__sobj=self.__reqObj.newSessionObj()
        self.__sessionPath=self.__sobj.getPath()
        #
        #self.__rC=ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        #self.__idList=['atp','gtp']
        #
        self.__fileList=[(os.path.abspath('../data/rcsb100135.cif'),'cif'),(os.path.abspath('../data/2fzu.pdb'),'pdb')]
        #self.__reqObj.setValue("filePath", os.path.abspath('../data/rcsb100135.cif'))
        #self.__reqObj.setValue("fileType", 'cif')        
        #
        

    def testCifOne(self): 
        """ 
        """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % sys._getframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        self.__lfh.flush()                
        try:
            self.__lfh.write("+ChemCompExtractTests.testCifOne() Session path is %s\n" % self.__sessionPath)
            self.__reqObj.setValue("filePath", self.__fileList[0][0])
            self.__reqObj.setValue("fileType", self.__fileList[0][1])                    
            ccE=ChemCompExtract(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
            rD=ccE.doExtract()
            for k,v in rD.items():
                self.__lfh.write("+ChemCompExtractTests.testCifOne() key %30s   value %s\n" (k,v))
            ccExD=ChemCompExtractDepict(self.__verbose,self.__lfh)
            oL=ccExD.doRender(rD['extractlist'])
            self.__lfh.write("%s" % "\n".join(oL))                            
        except:
            traceback.print_exc(file=self.__lfh)
            self.__lfh.flush()
            #self.fail()


    def testPdbOne(self): 
        """ 
        """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % sys._getframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        self.__lfh.flush()                
        try:
            self.__lfh.write("+ChemCompExtractTests.testPdbOne() Session path is %s\n" % self.__sessionPath)
            self.__reqObj.setValue("filePath", self.__fileList[1][0])
            self.__reqObj.setValue("fileType", self.__fileList[1][1])                    
            ccE=ChemCompExtract(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
            rD=ccE.doExtract()
            for k,v in rD.items():
                self.__lfh.write("+ChemCompExtractTests.testPdbOne() key %30s   value %s\n" % (k,v))
            ccExD=ChemCompExtractDepict(self.__verbose,self.__lfh)
            oL=ccExD.doRender(rD['extractlist'])
            self.__lfh.write("%s" % "\n".join(oL))            
        except:
            traceback.print_exc(file=self.__lfh)
            self.__lfh.flush()
            #self.fail()

if __name__ == '__main__':
    if not skiptest:
        ex=ChemCompExtractTests()
        ex.testCifOne()
        ex.testPdbOne()
    else:
        print("Test skipped as openeye not available")
