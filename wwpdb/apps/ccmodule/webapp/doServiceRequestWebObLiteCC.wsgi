#!/opt/wwpdb/bin/python
#
# File:     doServiceRequestWebObLiteCC.wsgi
# Created:  26-Sep-2018
#
# Updated:
# 26-Sep-2018 EP    Created based on ChemCompWebAppLite implementation of doServiceRequestWebObListCC.fcgi
# 
"""
This top-level responder for requests to /services/.... url for the
wwPDB Lite Chemical Component editor application framework.

This version depends on WSGI and WebOb.

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.07"

import sys
import traceback

from webob import Request, Response

#  - URL mapping and application specific classes are launched from ChemCompLiteWebApp()
from wwpdb.apps.ccmodule.webapp.ChemCompWebAppLite import ChemCompWebAppLite


class MyRequestApp(object):
    """  Handle server interaction using FCGI/WSGI and WebOb Request
         and Response objects.
    """
    def __init__(self,textString="Initialized from contructor",verbose=False,log=sys.stderr):
        """ 
        """
        self.__text=textString
        self.__verbose=verbose
        self.__lfh=log
        self.__siteId=None
        self._myParameterDict={}        
        
    def __dumpEnv(self,request):
        outL=[]
        outL.append("\n------------------doServiceRequest()------------------------------\n")
        outL.append("Web server request data content:\n")                
        outL.append("Text initialization:   %s\n" % self.__text)        
        try:
            outL.append("Host:         %s\n" % request.host)
            outL.append("Path:         %s\n" % request.path)
            outL.append("Method:       %s\n" % request.method)        
            outL.append("Query string: %s\n" % request.query_string)
            outL.append("Parameter List:\n")
            for name,value in request.params.items():
                outL.append("Request parameter:    %s:  %r\n" % (name,value))
        except:
            traceback.print_exc(file=self.__lfh)            

        outL.append("\n------------------------------------------------\n\n")
        return outL

    def __call__(self, environment, responseApplication):
        """          WSGI callable entry point


        """
        myRequest  = Request(environment)
        #
        self._myParameterDict={}   
        try:
            if 'WWPDB_SITE_ID' in environment:
                self.__siteId=environment['WWPDB_SITE_ID']
                self.__lfh.write("+MyRequestApp.__call__() - WWPDB_SITE_ID environ variable captured as %s\n" % self.__siteId)
            for name,value in environment.items():
                self.__lfh.write("+MyRequestApp.__call__() - ENVIRON parameter:    %s:  %r\n" % (name,value))
            for name,value in myRequest.params.items():
                if name not in self._myParameterDict:
                    self._myParameterDict[name]=[]
                self._myParameterDict[name].append(value)
            self._myParameterDict['request_path']=[myRequest.path.lower()]

            # Generate a dictionary for image generation
            # The allowed environment keys to set. Should be more limited over time XXX
            allowedkeys = ['SITE_REFDATA_DB_PASSWORD', 'SITE_REFDATA_DB_USER', 'SITE_REFDATA_CVS_PASSWORD', 'SITE_REFDATA_CVS_USER', 'SITE_REFDATA_DB_SOCKET',
                           'SITE_INSTANCE_DB_USER',
                           'OE_LICENSE', 'OE_DIR', 'PYTHONPATH', 'PATH', 'LD_LIBRARY_PATH',
                           'SITE_DA_INTERNAL_DB_PASSWORD', 'SITE_DA_INTERNAL_DB_USER', 'SITE_INSTANCE_DB_PASSWORD',
                           'WWPDB_SITE_LOC', 'TOP_WWPDB_SITE_CONFIG_DIR', 'WWPDB_SITE_ID',
                           'DJANGO_SETTINGS_MODULE']
            envdict = {}
            for key in allowedkeys:
                if key in environment:
                    envdict[key] = environment[key]
            self._myParameterDict['script_env'] = [envdict]

        except:
            traceback.print_exc(file=self.__lfh)            
            self.__lfh.write("+MyRequestApp.__call__() - contents of request data\n")
            self.__lfh.write("%s" % ("".join(self.__dumpEnv(request=myRequest))))
            
        ###
        ### At this point we have everything needed from the request !
        ###
        myResponse = Response()
        myResponse.status       = '200 OK'
        myResponse.content_type = 'text/html'       
        ###
        ###  Application specific functionality called here --
        ###  Application receives path and parameter info only!
        ###
        ccmodule_lite= ChemCompWebAppLite(parameterDict=self._myParameterDict,verbose=self.__verbose, 
                           log=self.__lfh,siteId=self.__siteId)
        rspD=ccmodule_lite.doOp()
        myResponse.content_type=rspD['CONTENT_TYPE']

        if sys.version_info[0] > 2:
            if isinstance(rspD['RETURN_STRING'], str):
                myResponse.text = rspD['RETURN_STRING']
            else:
                myResponse.body = rspD['RETURN_STRING']
        else:
            myResponse.body = rspD['RETURN_STRING']

        ####
        ###
        return myResponse(environment,responseApplication)
##
##  NOTE -  Path to top of the web application tree and verbose setting are set here ONLY! 
##
application = MyRequestApp(textString="doServiceRequest() - WebOb version",verbose=True,log=sys.stderr)
#
