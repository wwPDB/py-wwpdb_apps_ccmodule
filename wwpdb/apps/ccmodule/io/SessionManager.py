##
# File:    SessionManager.py
# Date:    14-Dec-2009
#
# Updates:
# 20-Apr-2010 jdw Ported to module seqmodule.
# 05-Aug-2010 jdw Ported to module ccmodule
#                 Replace deprecated sha module with hashlib
# 21-Sep-2010 jdw Remove 'sessions' from internal path used by this module.
#                 topPath now points to the directory containing the hash directory.
##
"""
Provides containment and access for session information.  Methods
are provided to create temporary directories to preserve session files.

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.07"


import sys, hashlib, time, os.path, shutil


class SessionManager(object):
    """
        Utilities for session directory maintenance.
        
    """
    def __init__(self,topPath=".",verbose=False):
        """
             Organization of session directory is -- 
             <topPath>/<sha-hash>/<session_files>
             
             Parameters:
             :topPath: is the path to the directory containing the hash-id sub-directory.

             
        """
        self.__verbose = verbose
        self.__topSessionPath = topPath
        self.__uid=None

    def setId(self,uid):
        self.__uid=uid

    def getId(self):
        return self.__uid
        
    def assignId(self):
        self.__uid = hashlib.sha1(repr(time.time())).hexdigest()
        return self.__uid        

    def getPath(self):
        try:
            pth=os.path.join(self.__topSessionPath,"sessions",self.__uid)
            if (self.__verbose):
                sys.stderr.write("+SessionManager.getPath() path %s\n" % pth)
            if os.access(pth,os.F_OK):
                return pth
            else:
                return None
        except:
            return None

    def getTopPath(self):
        return self.__topSessionPath

    def getRelativePath(self):
        pth=None
        try:
            pth=os.path.join("/sessions",self.__uid)

        except:
            pass
        return pth
    
    def makeSessionPath(self):
        """ If the path to the current session directory does not exist
            create it and return the session path.
        """
        try:
            pth=os.path.join(self.__topSessionPath,"sessions",self.__uid)        
            if (not os.access(pth,os.F_OK)):
                os.makedirs(pth)
            return pth
        except:
            return None

    def remakeSessionPath(self):
        try:
            pth=os.path.join(self.__topSessionPath,"sessions",self.__uid)        
            if (os.access(pth,os.F_OK)):
                shutil.rmtree(pth,True)
            os.makedirs(pth)
            return pth
        except:
            return None

