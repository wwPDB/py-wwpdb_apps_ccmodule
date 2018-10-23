##
# File:    WebRequest.py
# Date:    18-Jan-2010  J. Westbrook
#
# Updated:
# 20-Apr-2010 Ported to seqmodule package
# 25-Jul-2010 Ported to ccmodule package
# 24-Aug-2010 Add dictionary update for content request object.
##
"""
WebRequest provides containers and accessors for managing request parameter information.

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.07"


import sys
from json import loads, dumps

from wwpdb.apps.ccmodule.io.SessionManager import SessionManager

class WebRequest(object):
    """ Base container and accessors for input and output parameters and control information. 
    """
    def __init__(self,paramDict={},verbose=False):
        self.__verbose=verbose
        #
        #  Input and storage model is dictionary of lists (e.g. dict[myKey] = [,,,])
        #  Single values are stored in the leading element of the list (e.g. dict[myKey][0])
        #
        self.__dict=paramDict
        

    def printIt(self,ofh=sys.stdout):
        try:
            ofh.write("\n--------------------------------------------:\n")                         
            ofh.write("\nWebRequest.printIt() Request Dictionary Contents:\n")             
            for k,vL in self.__dict.items():
                ofh.write("  Key: %s  value(s): " % k)
                for v in vL:
                    ofh.write(" %s " % v)
                ofh.write("\n")
            ofh.write("\n--------------------------------------------\n\n")                                         
        except:
            pass


    def dump(self,format='text'):
        oL=[]
        try:
            if (format == 'html'):
                oL.append('<pre>\n')
            oL.append("\n--------------------------------------------:\n")                         
            oL.append("\nWebRequest.dump() Request Dictionary Contents:\n")             
            for k,vL in self.__dict.items():
                oL.append("  Key: %s  value(s): " % k)
                for v in vL:
                    oL.append(" %r " % v)
                oL.append("\n")
            oL.append("\n--------------------------------------------\n\n")
            if (format == 'html'):
                oL.append('</pre>\n')
        except:
            pass
        
        return oL        

    def getJSON(self):
        return dumps(self.__dict)

    def setJSON(self,JSONString):
        self.__dict = loads(JSONString)
                    
    def getValue(self,myKey):
        return(self._getStringValue(myKey))

    def getValueList(self,myKey):
        return(self._getStringList(myKey))

    def getRawValue(self,myKey):
        return(self._getRawValue(myKey))
    
    #
    def setValue(self,myKey,aValue):
        self.__dict[myKey]=[aValue]

    def setValueList(self,myKey,valueList):
        self.__dict[myKey]=valueList        

    
    def exists(self,myKey):
        try:
            return self.__dict.has_key(myKey)
        except:
            return False

    #
    def _getRawValue(self,myKey):
        try:
            return self.__dict[myKey][0]
        except:
            return None
        
    def _getStringValue(self,myKey):
        try:
            return str(self.__dict[myKey][0]).strip()
        except:
            return ''


    def _getIntegerValue(self,myKey):
        try:
            return int(self.__dict[myKey][0])
        except:
            return None

    def _getDoubleValue(self,myKey):
        try:
            return double(self.__dict[myKey][0])
        except:
            return None

    def _getStringList(self,myKey):
        try:
            return self.__dict[myKey]
        except:
            return []
            
class ChemCompInputRequest(WebRequest):
    def __init__(self,paramDict,verbose=False,log=sys.stderr):
        super(ChemCompInputRequest,self).__init__(paramDict,verbose)
        self.__verbose = verbose
        self.__lfh=log
        self.__returnFormatDefault=''

    def setDefaultReturnFormat(self,return_format="html"):
        self.__returnFormatDefault=return_format
        if (not self.exists("return_format")):
            self.setValue('return_format',self.__returnFormatDefault)
        
    def getRequestPath(self):
        return (self._getStringValue('request_path'))

    def getReturnFormat(self):
        if (not self.exists("return_format")):
            self.setValue('return_format',self.__returnFormatDefault)            
        return (self._getStringValue('return_format'))        

    def setReturnFormat(self,return_format='html'):
        return (self.setValue('return_format',return_format))
    
    def getSessionId(self):
        return (self._getStringValue('sessionid'))

    def getTopSessionPath(self):
        return (self._getStringValue('TopSessionPath'))

    def getSemaphore(self):
        return (self._getStringValue('semaphore'))        

    def getSessionObj(self):
        if (self.exists("TopSessionPath")):
            sObj=SessionManager(topPath=self._getStringValue("TopSessionPath"))
        else:
            sObj=SessionManager()
        sObj.setId(uid=self._getStringValue("sessionid"))
        return sObj

    def newSessionObj(self):
        if (self.exists("TopSessionPath")):
            sObj=SessionManager(topPath=self._getStringValue("TopSessionPath"))
        else:
            sObj=SessionManager()

        sessionId = self._getStringValue("sessionid")

        if (len(sessionId) > 0):
            sObj.setId(sessionId)
            sObj.makeSessionPath()
        else:
            sObj.assignId()
            sObj.makeSessionPath()
            self.setValue('sessionid',sObj.getId())
        
        return sObj

#

class ResponseContent(object):

    def __init__(self, reqObj=None, verbose=False,log=sys.stderr):
        """
        Manage content items to be transfered as part of the
        the application response.
        
        """
        self.__verbose=verbose
        self.__lfh=log
        self.__reqObj=reqObj
        #
        self.__cD={}
        self.__setup()
        
    def __setup(self):
        """ Default response content is set here.
        """
        self.__cD['htmlcontent']=''
        self.__cD['textcontent']=''
        self.__cD['errorflag']=False
        self.__cD['errortext']=''
        if self.__reqObj is not None:
            self.__cD['sessionid']=self.__reqObj.getSessionId()
            self.__cD['semaphore']=self.__reqObj.getSemaphore()
        else:
            self.__cD['sessionid']=''
            self.__cD['semaphore']=''


    def setHtmlList(self,htmlList=[]):
        self.__cD['htmlcontent']='\n'.join(htmlList)

    def setHtmlText(self,htmlText=''):
        self.__cD['htmlcontent']=htmlText

    def addDictionaryItems(self,cD={}):
        for k,v in cD.items():
            self.__cD[k]=v

    def setTextFileE(self,filePath):
        try:
            if os.path.exists(filePath):            
                self.__cD['textcontent']=open(filePath).read()            
        except:
            pass

    def setTextFile(self,filePath):
        self.__cD['textcontent']=open(filePath).read()
        
        
    def setError(self,errMsg='',semaphore=''):
        self.__cD['errorflag']=True
        self.__cD['errortext']=errMsg
        self.__cD['semaphore']=semaphore

    def setStatusCode(self,aCode):
        self.__cD['statuscode']=aCode

    def setHtmlContentPath(self,aPath):
        self.__cD['htmlcontentpath']=aPath

    def dump(self):
        retL=[]
        retL.append("+ResponseContent.dump() - response content object\n")
        for k,v in self.__cD.items():
            retL.append(" key = %s " % k)
            retL.append(" value(1-1024): %s\n" %   str(v)[:1024] )
        return retL

    def get(self):
        """Repackage the response for Apache according to the input return_format='html|json|text|...'
        """
        rD={}
        if (self.__reqObj.getReturnFormat() == 'html'):
            if (self.__cD['errorflag']==False):
                rD=self.__initHtmlResponse(self.__cD['htmlcontent'])
            else:
                rD=self.__initHtmlResponse(self.__cD['errortext'])                
        elif (self.__reqObj.getReturnFormat() == 'text'):
            if (self.__cD['errorflag']==False):
                rD=self.__initTextResponse(self.__cD['textcontent'])
            else:
                rD=self.__initHtmlResponse(self.__cD['errortext'])                
        elif (self.__reqObj.getReturnFormat() == 'json'):
            rD=self.__initJsonResponse(self.__cD)
        elif (self.__reqObj.getReturnFormat() == 'jsonText'):
            rD=self.__initJsonResponseInTextArea(self.__cD)            
        else:
            pass
        #
        return rD

    def __initJsonResponse(self,myD={}):
        rspDict={}
        rspDict['CONTENT_TYPE']  = 'application/json'
        rspDict['RETURN_STRING'] = dumps(myD)
        return rspDict

    def __initJsonResponseInTextArea(self,myD={}):
        rspDict={}
        rspDict['CONTENT_TYPE']  = 'text/html'
        rspDict['RETURN_STRING'] = '<textarea>'+dumps(myD)+'</textarea>'
        return rspDict

    def __initHtmlResponse(self,myHtml=''):
        rspDict={}
        rspDict['CONTENT_TYPE']  = 'text/html'
        rspDict['RETURN_STRING'] = myHtml
        return rspDict

    def __initTextResponse(self, myText=''):
        rspDict={}
        rspDict['CONTENT_TYPE']  = 'text/plain'
        rspDict['RETURN_STRING'] = myText
        return rspDict

if __name__ == '__main__':
    rC=ResponseContent()








