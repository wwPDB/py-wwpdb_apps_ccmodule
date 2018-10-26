#!/usr/bin/env python
#
# File:     doServiceRequestWsgi.fcgi
# Created:  10-Mar-2010
#
# Updated:
# 20-Apr-2010 Ported to seqmodule package
# 25-Jul-2010 Ported to ccmodule package
#
"""
This top-level responder for requests to /services/.... url for the
wwPDB application framework.  This version depends only on the FCGI
implementation of the WSGI service.

Adapted from the mod_wsgi version

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.07"

import fcgi
#from flup.server.fcgi import WSGIServer



import sys, os
import cgi
import traceback

#  - Application specific classes - 
from wwpdb.apps.ccmodule.webapp.ChemCompWebApp import ChemCompWebApp

class MyRequestApp(object):
    """  Handle server interaction using FCGI/WSGI.
    """
    def __init__(self,textString="Initialized from contructor",topPath="/www/ccmodule",verbose=True,log=sys.stderr):
        """ 
        """
        self.__text=textString
        self.__topPath=topPath
        self.__verbose=verbose
        self.__lfh=log
        self.__myParameterDict={}
        self.__row_template = "  <tr><td>%s</td><td>%r</td></tr>"
        self.__html_template = """\
        <html>
        <head>
        <title>WSGI Environment Dump</title>
        </head>
        <body>
        <h1>WSGI Environment Dump</h1>
        <table border=1>
        <tr><th colspan=2>System Information</th></tr>
        <tr><td>Python</td><td>%(python_version)s</td></tr>
        <tr><td>Python Path</td><td>%(python_path)s</td></tr>
        <tr><td>Platform</td><td>%(platform)s</td></tr>
        <tr><td>Absolute path of this script</td><td>%(abs_path)s</td></tr>
        <tr><td>Filename</td><td>%(filename)s</td></tr>
        <tr><th colspan=2>WSGI Environment</th></tr>
        %(wsgi_env)s
        </table>
        </body>
        </html>
        """
        
    def __dump(self,op="unknown"):
        retL=[]
        retL.append("\n---------------DoServiceRequestWsgi.__dump()---------------------------\n")
        retL.append("Parameter dictionary length = %d\n" % len(self.__myParameterDict))            
        for k,vL in self.__myParameterDict.items():
            retL.append("Parameter %30s :" % k)
            for v in vL:
                retL.append("        ->  %s\n" % v)
        retL.append("\n----------------------------------------------\n\n")                
        return retL

    def __dumpEnv(self,environ):
        # assemble and return content
        content = self.__html_template % {
            'python_version': sys.version,
            'platform': sys.platform,
            'abs_path': os.path.abspath('.'),
            'filename': __file__,
            'python_path': repr(sys.path),
            'wsgi_env': '\n'.join([self.__row_template % item for item in environ.items()]),
            }
        return content


    def __parseEnvironment(self,environment):
        """ Parse the WSGI environment, and return a dictionary,
            of lists containing POST and GET parameters.  

        """
        fieldstorage = cgi.FieldStorage( fp = environment['wsgi.input']
                                   , environ = environment
                                   , keep_blank_values = True
                                   , strict_parsing = False
                                    )
        d = {}
        for k in fieldstorage:
            fL = fieldstorage.getlist(k)
            oL=[]
            for iS in fL:
                oL.append(cgi.escape(iS.strip()))
            #d[k] = d[k].decode('UTF-8')                
            d[k] = oL
        return d
       
    def __call__(self, environment, responseApplication):
        """          WSGI callable entry point

        """
        self.__myParameterDict={}                        
        try:
            myPath=environment['REQUEST_URI'].split('?')
            #self.__myPathList=myPath[0].upper().split('/')
            self.__myParameterDict=self.__parseEnvironment(environment)
            self.__myParameterDict['request_path']=[myPath[0].lower()]


        except:
            traceback.print_exc(file=self.__lfh)            
            
        if (self.__verbose):
            self.__lfh.write("+MyRequestApp.__call__() - contents of request data\n")
            self.__lfh.write("%s" % ("".join(self.__dump())))
        ###
        ### At this point we have everything needed from the request !
        ###
        
        status       = '200 OK'
        #content_type = 'text/html'       

        ###
        ###  Application specific functionality called here --
        ###  Application receives path and parameter info only!
        ###
        seqT= ChemCompWebApp(parameterDict=self.__myParameterDict,
                            topPath=self.__topPath,verbose=self.__verbose,log=self.__lfh)        
        rspD=seqT.doOp()
        content_type=rspD['CONTENT_TYPE']            
        body=rspD['RETURN_STRING']
        ###
        rspLen=len(body)
        headers = [('Content-Type', content_type), ('Content-Length', str(rspLen)), ]
        responseApplication(status, headers)
           
        return [body]

##
##  NOTE:  Web application path, verbose flag and log stream are set here only... 
##    

fcgi.WSGIServer(MyRequestApp("doServiceRequest - default initialization",topPath="/www/ccmodule",verbose=True,log=sys.stderr)).run()
#WSGIServer(MyRequestApp("doServiceRequest - default initialization",topPath="/www/ccmodule",verbose=True,log=sys.stderr)).run()

