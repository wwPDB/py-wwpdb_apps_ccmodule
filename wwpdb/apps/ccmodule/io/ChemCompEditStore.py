##
# File:    ChemCompEditStore.py
# Date:    30-Aug-2010
#
# Updates:
# 1-Sep-2010  jdw   revised edit storage model -
#
##
"""
Provide a storage interface for recording incremental edits in chemical component
definition data for use by the chemical component editing tool.

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.01"


import sys, cPickle, time, os.path



class ChemCompEdit(object):
    """ Container for the chemical component data edit records --
        An edit record contains the following:
              Edit Operation number (ordering/grouping identifier),
              Edit operation type ('replace-value','row-insert-after','row-insert-before','row-delete'),
              Data block Id,

           Item value edits -    
              Target item name (for replace value edits).
              New value (for replace value edits),
              Prior value (for replace value edits)
           Row level edits:
              Target row identifier    -
              Inserted row identifier - (for inserts) 

        """
    def __init__(self,verbose=False,log=sys.stderr):
        self.__verbose=verbose
        self.__lfh=log
        self.__reset()

    def __reset(self):
        self.__editOpNumber=0
        self.__targetId=None
        self.__editType=None
        self.__blockId=None
        self.__targetItemName=None
        self.__valueNew=None
        self.__valuePrevious=None
        self.__targetRowId=None
        self.__insertedRowId=None                

    def setTargetId(self,id):
        self.__targetId=id
        return True

    def getTargetId(self):
        return self.__targetId

    def setBlockId(self,blockId):
        if (blockId is not None):
            self.__blockId=blockId
        else:
            return False
        return True
        
    def getBlockId(self):
        return self.__blockId

    def setTargetRowId(self,rowId):
        self.__targetRowId=rowId
        return True

    def getTargetRowId(self):
        return self.__targetRowId

    def setInsertedRowId(self,rowId):
        self.__insertedRowId=rowId
        return True

    def getInsertedRowId(self):
        return self.__insertedRowId
    

    def setValueNew(self,value):
        self.__valueNew=value

    def getValueNew(self):
        return self.__valueNew
    
    def setValuePrevious(self,value):
        self.__valuePrevious=value

    def getValuePrevious(self):
        return self.__valuePrevious


    def setEditType(self,eType):
        if eType in ['replace-value','row-insert-after','row-insert-before','row-delete']:
            self.__editType=eType
        else:
            return False
        return True
        
    def getEditType(self):
        return self.__editType

    def setTargetItemName(self,targetItemName):
        self.__targetItemName=targetItemName
        return True

    def getTargetItemName(self):
        return self.__targetItemName

    def setEditOpNumber(self,opNumber):
        try:
            self.__editOpNumber=int(opNumber)
            if (self.__editOpNumber < 0):
                return False
        except:
            return False
        
        return True

    def getEditOpNumber(self):
        return self.__editOpNumber

    def pack(self):
        return (self.__editOpNumber,self.__editType,self.__targetId,self.__blockId,self.__targetItemName,self.__valueNew,
                self.__valuePrevious,self.__targetRowId,self.__insertedRowId)

    def unpack(self,editTuple):
        #self.__reset()
        try:
            self.__editOpNumber    = int(editTuple[0])
            self.__editType        = editTuple[1]
            self.__targetId        = editTuple[2]            
            self.__blockId         = editTuple[3]
            self.__targetItemName  = editTuple[4]
            self.__valueNew        = editTuple[5]
            self.__valuePrevious   = editTuple[6]
            self.__targetRowId     = editTuple[7]
            self.__insertedRowId   = editTuple[8]             
        except:
            traceback.print_exc(file=self.__lfh)
            return False
        return True

    def printIt(self,ofh):
        ofh.write("\nChemical Component Edit Object Contents:\n")
        ofh.write("  Edit operation no %d\n" % self.__editOpNumber)
        ofh.write("  Edit type         %s\n" % self.__editType)
        ofh.write("  Target Id         %s\n" % self.__targetId)        
        ofh.write("  Block Id          %s\n" % self.__blockId)
        ofh.write("  Target item name  %s\n" % self.__targetItemName)
        ofh.write("  New value         %s\n" % self.__valueNew)
        ofh.write("  Previous value    %s\n" % self.__valuePrevious)
        ofh.write("  Target row Id     %s\n" % self.__targetRowId)
        ofh.write("  Inserted  row Id  %s\n" % self.__insertedRowId)                
        
       
class ChemCompEditStore(object):
    """ Store incremental edits on the chemical component definitions -

    The edit record is defined in class ChemCompEdit().
    ...
    Storage model is a list of tuples where each tuple contains the above attributes.

    """
    def __init__(self,reqObj,fileName='chemCompEditStore.pic',verbose=False,log=sys.stderr):
        """Chemical component edit operations -


         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.
          
        """
        #
        self.__fileName=fileName                
        self.__verbose=verbose
        self.__lfh=log
        self.__debug=True
        #
        self.__reqObj=reqObj
        self.__sessionObj=self.__reqObj.getSessionObj()
        self.__sessionPath=self.__sessionObj.getPath()
        self.__sessionId  =self.__sessionObj.getId()        
        self.__sessionRelativePath=self.__sessionObj.getRelativePath()
        #
        #self.__ccConfig=ChemCompConfig(reqObj, verbose=self.__verbose,log=self.__lfh)        
        #
        # List of ChemCompEdit objects - 
        self.__editList=[]
        #
        self.__editDirPath = os.path.join(self.__sessionPath,'edit')
        self.__filePath = os.path.join(self.__sessionPath,'edit',self.__fileName)        

        #self.__pickleProtocol = cPickle.HIGHEST_PROTOCOL
        self.__pickleProtocol=0        
        
        self.__setup()
        #

    def __setup(self):
        try:
            # create the edit path in the session directory if it does not exist
            #
            if (not os.access(self.__editDirPath,os.F_OK)):
                    os.makedirs(self.__editDirPath)

            if (self.__verbose):
                self.__lfh.write("+ChemCompEditStore.__setup - session id %s  edit store file path%s\n" %
                                 (self.__sessionId,self.__filePath))            
            self.deserialize()
            if (self.__verbose):
                self.__lfh.write("+ChemCompEditStore.__setup - opening store with edit list length %d\n" % len(self.__editList))
                self.printIt(self.__lfh)

        except:
            self.__lfh.write("+ChemCompEditStore.__setup - Failed opening edit store for session id %s  edit store file path%s\n" %
                             (self.__sessionObj.getId(),self.__filePath))                        


    def length(self):
        return (len(self.__editList))
        
    def reset(self):
        self.__editList=[]
        self.serialize()
        
    def serialize(self):
        try:
            fb=open(self.__filePath,'wb')
            cPickle.dump(self.__editList,fb,self.__pickleProtocol)
            fb.close()
        except:
            self.__lfh.write("+ChemCompEditStore.__serialize - failed for session %s edit store file path%s\n" %
                             (self.__sessionObj.getId(),self.__filePath))                                    
            pass
            
    def deserialize(self):
        try:
            fb=open(self.__filePath,'rb')            
            self.__editList=cPickle.load(fb)
            fb.close()
        except:
            pass

    def storeEdit(self,ccEdObj):
        try:
            eTup=ccEdObj.pack()
            self.__editList.append(eTup)
            self.serialize()
            return True
        except:
            return False

    def deleteEdit(self,ccEdObj):
        try:
            eTup=ccEdObj.pack()
            if eTup in self.__editList:
                self.__editList.remove(eTup)
            self.serialize()
            return True
        except:
            return False

    def storeEditList(self,ccEdObjList):
        try:
            for ccEdObj in ccEdObjList:
                eTup=ccEdObj.pack()
                self.__editList.append(eTup)
            self.serialize()
            return True
        except:
            return False

    def deleteEditList(self,ccEdObjList):
        try:
            for ccEdObj in ccEdObjList:
                eTup=ccEdObj.pack()
                if (eTup in self.__editList):
                    self.__editList.remove(eTup)
            self.serialize()
            return True
        except:
            return False

    def printIt(self,ofh):
        ofh.write("\nChemical Component Edit Store Contents\n")
        ofh.write("  Storage path:  %s\n" % self.__filePath)
        ofh.write("  Edit count:    %d\n" % len(self.__editList))        
        for eTup in self.__editList:
            sEd=ChemCompEdit()
            sEd.unpack(eTup)                                 
            sEd.printIt(ofh)

    def getLastOpNumber(self):
        try:
            eTup=self.__editList[-1]
            sEd=ChemCompEdit()
            sEd.unpack(eTup)                     
            return sEd.getEditOpNumber()
        except:
            return 0
    #
    def get(self,opNumber):
        """  Return the list of edit objects corresponding to the edit operation opNumber.
        """
        oL=[]
        for eTup in self.__editList:
            sEd=ChemCompEdit()
            sEd.unpack(eTup)
            if opNumber == sEd.getEditOpNumber():
                oL.append(sEd)
        return oL

    def getList(self):
        """  Return the list of edit objects.
        """
        oL=[]
        for eTup in self.__editList:
            sEd=ChemCompEdit()
            sEd.unpack(eTup)
            oL.append(sEd)
        return oL


    def remove(self,opNumber):
        """ Remove edit objects with the input edit operation Id from the current store
            and save the result.
        """
        newList=[]
        for eTup in self.__editList:
            sEd=ChemCompEdit()
            sEd.unpack(eTup)
            if opNumber != sEd.getEditOpNumber():
                newList.append(eTup)
        self.__editList = newList
        self.serialize()
        
