##
# File:    ChemCompEditStoreTests.py
# Date:    30-Aug-2010
#
# Updates:
#
# 1-Sep-2010  jdw revise tests and request handling.
##
"""
Test cases for sequence editing operations.

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.01"

import sys, unittest, traceback
import time, os, os.path

from wwpdb.apps.ccmodule.io.ChemCompEditStore   import ChemCompEditStore, ChemCompEdit
from wwpdb.utils.session.WebRequest      import InputRequest


class ChemCompEditStoreTests(unittest.TestCase):
    def setUp(self):
        self.__verbose=True
        self.__lfh=sys.stderr
        #
        # Create a request object and session directories for test cases
        #
        HERE = os.path.abspath(os.path.dirname(__file__))
        sessionPath = os.path.join(HERE, 'test-output')
        self.__topPath = sessionPath
        self.__reqObj=InputRequest(paramDict={},verbose=self.__verbose,log=self.__lfh)
        self.__reqObj.setValue("TopSessionPath", self.__topPath)
        self.__reqObj.setValue("TopPath",        self.__topPath)
        self.__sobj=self.__reqObj.newSessionObj()
        self.__sessionPath=self.__sobj.getPath()
        #


    def tearDown(self):
        pass
    
    def testStoreEdits1(self): 
        """ 
        """
        sys.stdout.write("\n------------------------ ")
        sys.stdout.write("Starting test function  %s" % sys._getframe().f_code.co_name)
        sys.stdout.write(" -------------------------\n")
        try:
            ses=ChemCompEditStore(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
            #
            editOpLast=ses.getLastOpNumber()
            editOpNext=int(editOpLast) + 1                    
            #
            #
            blockId='ATP'
            rowId="chem_comp:0"
            newValue  ='C6N2O2H10'
            priorValue='C6N2O2H12'
            sE=ChemCompEdit(self.__verbose,self.__lfh)
            #
            sE.setBlockId(blockId)
            sE.setTargetRowId(rowId)                                
            sE.setEditType("replace-value")
            sE.setEditOpNumber(editOpNext)            
            #
            sE.setTargetItemName('_chem_comp.formula')
            sE.setValueNew(newValue)        
            sE.setValuePrevious(priorValue)            

            ses.storeEdit(sE)
            editOpNext +=1

            sE=ChemCompEdit(self.__verbose,self.__lfh)            

            #
            sE.setBlockId(blockId)
            sE.setTargetRowId(rowId)                                
            sE.setEditType("replace-value")
            sE.setEditOpNumber(editOpNext)            
            #
            sE.setTargetItemName('_chem_comp.pdbx_release_status')
            sE.setValueNew('REL')
            sE.setValuePrevious('HPUB')            
            #
            ses.storeEdit(sE)
            ses.printIt(self.__lfh)

        except:
            traceback.print_exc(file=self.__lfh)
            self.fail()


def suite():
    return unittest.makeSuite(ChemCompEditStoreTests,'test')

if __name__ == '__main__':
    unittest.main()

