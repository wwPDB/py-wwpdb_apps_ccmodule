##
# File:  ChemCompDepict.py
# Date:  08-Aug-2010
# Updates:
#    2010-08-19  RPS _headerExtrctRslts created with references to stylesheet and js files to support
#                     paginated viewing of chem components in extract depiction.
#    2010-08-24  jdw  fold in changes for editor module
#    2010-09-21  RPS  Piloting support for Level 1 Batch Search Summary display
#    2010-09-24  RPS  Adopted strategy of using HTML template for Batch Search Summary results
#                     which allowed elimination of attributes previously used here.
#    2011-04-26  RPS  isWorkflow(), truncateForDisplay(), and processTemplate() added.
#    2011-05-12  RPS  Piloting changes for standalone Ligand Editor Tool
#    2011-07-07  RPS  Updated check for isWorkflow to check for "wf_instance" and "wf_archive" as valid filesources
#    2011-08-17  RPS  Updated with setSessionPaths() function for establishing absolute and relative paths
#                        used for session data management
#    2011-08-23  RPS  Defined self.jmolCodeBase as centralized definition of location of Jmol applet code, for use
#                        by inheritance in subclasses.
#    2011-11-18  RPS  Interim changes to allow further development of stand alone ligand tool functionality such as cc-extract within the
#                        consolidated common tool setup.
#    2011-12-22, RPS: URL updates to reflect consolidated deployment of js files for all common tool front-end modules.
#    2017-02-03, RPS: updated isWorkflow() to recognize "deposit" as workflow managed filesource.
##
"""
Base class for HTML depictions containing common HTML constructs.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.02"

import os
import sys


class ChemCompDepict(object):
    """Base class for HTML depictions contain definitions of common constructs.

    """
    def __init__(self, verbose=False, log=sys.stderr):  # pylint: disable=unused-argument
        """

         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        # self.__verbose = verbose
        # self.__lfh = log
        # self.__debug = True
        #
        self.absltSessionPath = None
        self.absltAssgnSessionPath = None
        self.rltvSessionPath = None
        self.rltvAssgnSessionPath = None
        #
        self.jmolCodeBase = os.path.join("/applets", "jmol")
        #
        self._pragma = r'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'''
        self._pragmaXhtml = r'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'''
        self._header_ORIG = r'''
<head>
  <title>%s</title>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
  <link rel="stylesheet" type="text/css" href="/ccmodule/styles/general.css" />
  <script type="text/javascript" src="/applets/jmol/Jmol.js"></script>
  <script type="text/javascript" src="/ccmodule/js/cc-tools.js"></script>
</head>
'''

        self._header = r'''
<head>
  <title>%s</title>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
  <link rel="stylesheet" type="text/css" href="/ccmodule/styles/general.css" />
  <link rel="stylesheet" type="text/css" media="all" href="/ccmodule/styles/oneColLiqCtrHdr.css" />
  <link rel="stylesheet" type="text/css" media="all" href="/ccmodule/styles/superfish.css" />
</head>
'''
        self._headerJmol = r'''
<head>
  <title>%s</title>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
  <link rel="stylesheet" type="text/css" href="/ccmodule/styles/general.css" />
  <script type="text/javascript" src="/applets/jmol/Jmol.js"></script>
  <script type="text/javascript" src="/ccmodule/js/cc-tools.js"></script>
</head>
'''
        self._headerExtrctRslts = r'''
<head>
  <title>%s</title>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
  <link rel="stylesheet" type="text/css" href="/ccmodule/styles/general.css" >
  <link rel="stylesheet" type="text/css" href="/ccmodule/styles/jpag.css" >
  <script type="text/javascript" src="/applets/jmol/Jmol.js"></script>
  <script type="text/javascript" src="/ccmodule/styles/cc-tools.js"></script>
  <script type="text/javascript" src="/js/jquery/core/jquery.min.js"></script>
  <script type="text/javascript" src="/ccmodule/js/ligmod_stndaln.js"></script>
</head>
'''
        self._headerMarvin = r'''
<head>
  <title>%s</title>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
  <link rel="stylesheet" type="text/css" href="/ccmodule/styles/general.css" />
  <script type="text/javascript"   src="/applets/marvin/marvin.js"></script>
  <script type="text/javascript"   src="/ccmodule/js/cc-marvin-sketch.js"></script>
</head>
'''
        self._headerMin = r'''
<head>
  <title>%s</title>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
  <link rel="stylesheet" type="text/css" href="/ccmodule/styles/general.css" />
</head>
'''
        self._jQueryTableInclude = r'''
  <script type="text/javascript" src="/ccmodule/js/jquery/plugins/jquery.tablesorter.min.js"></script>
  <script type="text/javascript" src="/ccmodule/js/jquery/plugins/jquery.jeditable.min.js"></script>
  '''

        self._jQueryGenericInclude = r'''
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
<title>Chemical Component Module</title>
<link rel="stylesheet" type="text/css"  media="all" href="/ccmodule/styles/general.css" />
<link rel="stylesheet" type="text/css"  media="all" href="/ccmodule/styles/thrColLiqHdr.css" />
<link rel="stylesheet" type="text/css"  media="all" href="/ccmodule/styles/superfish.css"  />
<link rel="stylesheet" type="text/css"  media="all" href="/styles/themes/south-street/jquery-ui-1.8.2.custom.css" />

<script type="text/javascript" src="/ccmodule/js/jquery/core/jquery.min.js"></script>
<!--[if IE]><script type="text/javascript" src="/ccmodule/js/excanvas.compiled.js" charset="utf-8"></script><![endif]-->
<script type="text/javascript" src="/ccmodule/js/jquery/plugins/jquery.hoverIntent.minified.js"></script>
<script type="text/javascript" src="/ccmodule/js/jquery/plugins/jquery.bgiframe.min.js"></script>
<script type="text/javascript" src="/ccmodule/js/jquery/plugins/superfish.js"></script>
<script type="text/javascript" src="/ccmodule/js/jquery/ui/jquery-ui.custom.min.js"></script>
<script type="text/javascript" src="/ccmodule/js/plugins/jquery.corner.js"></script>
'''

        self._menuCommonInclude_ORIG = r'''
<!--#include virtual="/ccmodule/styles/common/header_cc.txt"-->
'''
        self._menuCommonInclude = r'''
    <!-- begin #header-->
        <div id="header">
            <div id="logo"><img src="/images/wwpdb_logo.gif" width="187" height="58" alt="logo" /> </div>
            <div id="headerCont">
                  <h1>Chemical Component Editor Module</h1>
                  <span id="help_standalone_module" class="ui-icon ui-icon-info fltrgt"></span>
            </div>
            <br class="clearfloat" />
        </div>
    <!-- #header ends above-->
    <!-- begin #menu-->
    <div id="menu">
        <ul class="sf-menu">
            <li class="current"> <a href="/ccmodule/index.html" class="first">Home</a> </li>
            <li> <a href="/ccmodule/cc-view.html">View</a> </li>
            <li> <a href="/ccmodule/editor_beta/chemCifEdit.html">Edit</a> </li>
            <li> <a href="/ccmodule/cc-search.html">Search</a> </li>
            <li> <a href="/ccmodule/help.html">Help</a> </li>
        </ul>
    </div>
    <!-- #menu ends above-->
    <br class="clearfloat" />
    <br />
    <div id="mainContent">

'''

        self._menuCommonIncludeExtrctRslts = r'''
    <!-- begin #header-->
        <div id="header">
            <div id="logo"><img src="/images/wwpdb_logo.gif" width="187" height="58" alt="logo" /> </div>
            <div id="headerCont">
                  <h1>Chemical Component Editor Module</h1>
                  <span id="help_standalone_module" class="ui-icon ui-icon-info fltrgt"></span>
            </div>
            <br class="clearfloat" />
        </div>
    <!-- #header ends above-->
    <br class="clearfloat" />
    <br />
    <div id="mainContent">

'''

        self._jmolInclude = r'''
<script type="text/javascript">
        window.onload = function () { document.appletcontrols.reset(); }
</script>
<script type="text/javascript">
  jmolInitialize("/applets/jmol");
  jmolSetAppletColor("white");
</script>
'''

        self._marvinInclude = r'''
<script type="text/javascript">
   launchSketcher3(%d);
</script>
'''
        self._trailer = r'''
<!-- END TEXT HERE  -->
<!--#include virtual="/styles/common/footer.txt"-->
'''

    def setSessionPaths(self, p_reqObj):
        ''' Establish absolute/relative paths to be used for storing/accessing session-related data

            :Params:
                ``p_reqObj``: Web Request object
        '''
        sessionMgr = p_reqObj.getSessionObj()

        # ### absolute paths ####
        absSessPth = sessionMgr.getPath()
        # absolute path used for referencing session directory content from front end
        self.absltSessionPath = absSessPth
        # absolute path used for generating assign content on server-side
        self.absltAssgnSessionPath = os.path.join(absSessPth, "assign")

        # ### relative paths #####
        rltvSessPth = sessionMgr.getRelativePath()
        # relative path used for referencing session directory content from front end
        self.rltvSessionPath = rltvSessPth
        # relative path used for referencing assign resources from front end
        self.rltvAssgnSessionPath = os.path.join(rltvSessPth, "assign")

    def isWorkflow(self, p_reqObj):
        """ Determine if currently operating in Workflow Managed environment
        """
        #
        fileSource = str(p_reqObj.getValue("filesource")).lower()
        #
        if fileSource in ['archive', 'wf-archive', 'wf_archive', 'wf-instance', 'wf_instance', 'deposit']:
            # if the file source is any of the above then we are in the workflow manager environment
            return True
        else:
            # else we are in the standalone dev environment
            return False

    def processTemplate(self, tmpltPth, fn, parameterDict=None):
        """ Read the input HTML template data file and perform the key/value substitutions in the
            input parameter dictionary.
        """
        if parameterDict is None:
            parameterDict = {}
        fPath = os.path.join(tmpltPth, fn)
        ifh = open(fPath, 'r')
        sIn = ifh.read()
        ifh.close()
        return (sIn % parameterDict)

    def truncateForDisplay(self, content, maxlength=20, suffix='...'):
        """ Obtain truncated version of long identifiers for display purposes (e.g. in comparison panel)
        """
        if not (content is None):
            if len(content) <= maxlength:
                return content
            else:
                return content[:maxlength + 1] + suffix
        else:
            return ''
