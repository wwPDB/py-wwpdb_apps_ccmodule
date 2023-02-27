##
# File:  ChemCompConfig.py
#
# Updated:
#  29-Jul-2010  JDW    - Ported to CC module
#  05-Aug-2010  JDW    - Overhaul constructor integrate with input request class.
#  28-Nov-2011  RPS    - Updated to leverage ConfigInfo class for obtaining site-specific paths to data/binaries
#  08-May-2012  RPS    - self.__shellScriptPath updated to agree with current path used for wwpdb shared deployment.
#                        (Quick change to get things working for now, but may need to revisit to derive this more appropriately from ConfigInfoData?)
#                      - Superseded above change with use of ConfigInfoData module to derive path for 'SITE_CC_SCRIPT_PATH'
#  15-Oct-2015  RPS    - self.__shellScriptPath retired so updated reference to makeReportFromFile.csh to sit under self.__ccAppsBinPath
#  16-Feb-2016  RPS    - removed references to obsolete self.__shellScriptPath
#  01-Mar-2016  RPS    - updated to obtain and provide getter support for OE_DIR and OE_LICENSE environment variables
#
"""
Maintain configuration and path information for chemical component module applications.

"""

import sys
import os
import os.path
from wwpdb.utils.config.ConfigInfoApp import ConfigInfoAppCommon


class ChemCompConfig(object):
    """ Accessors for configuration and path information for chemical component module applications.
    """
#
#    def __init__(self,rootPath,sessionTop,archBinPath,uid, verbose=False,log=sys.stderr):
#
    def __init__(self, reqObj, verbose=False, log=sys.stderr):
        """ Input request object is expected to contain top-level path details.
        """
        self.__verbose = verbose
        self.__lfh = log
        #
        # Information injected from the request object -
        #
        self.__reqObj = reqObj
        self.__topPath = self.__reqObj.getValue("TopPath")
        self.__topSessionPath = self.__reqObj.getValue("TopSessionPath")
        #
        self.__sObj = self.__reqObj.getSessionObj()
        self.__sessionPath = self.__sObj.getPath()
        self.__sessionRelativePath = self.__sObj.getRelativePath()
        self.__sessionId = self.__sObj.getId()
        #
        self.__siteId = str(self.__reqObj.getValue("WWPDB_SITE_ID"))
        self.__cICommon = ConfigInfoAppCommon(self.__siteId)
        #
        # derived from the top path by convention
        #
        # JDW 2011-07-07 --- These are symbolic links in the web application top directory
        # self.__archBinPath      =  os.path.join(self.__topPath,"bin")
        # self.__archDataPath      =  os.path.join(self.__topPath,"data")

        # RPS 2011-11-29 --- use of above symbolic links for archBinPath and archDataPath being superseded by paths determined via calls to ConfigInfo
        self.__ccAppsBinPath = os.path.join(self.__cICommon.get_site_cc_apps_path(), "bin")
        self.__ccDictPath = self.__cICommon.get_site_cc_dict_path()
        self.__ccCvsPath = self.__cICommon.get_site_cc_cvs_path()
        self.__oeLicenseFilePath = self.__cICommon.get_site_cc_oe_licence()
        self.__oeDirPath = self.__cICommon.get_site_cc_oe_dir()

        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompConfig.__init() --------------------------------------------------------------------------\n")
            self.__lfh.write("+ChemCompConfig.__init() ------ self.__ccAppsBinPath is: %s \n" % self.__ccAppsBinPath)
            self.__lfh.write("+ChemCompConfig.__init() ------ self.__ccDictPath is: %s \n" % self.__ccDictPath)
            self.__lfh.write("+ChemCompConfig.__init() ------ self.__ccCvsPath is: %s \n" % self.__ccCvsPath)
            self.__lfh.write("+ChemCompConfig.__init() --------------------------------------------------------------------------\n")
        #
        # Place holders for working path info -
        self.__workingPath = None
        self.__workingRelativePath = None

    def setWorkingPath(self, path):
        self.__workingPath = path

    def setWorkingPathRel(self, path):
        self.__workingRelativePath = path

    def getPath(self, type):  # pylint: disable=redefined-builtin
        #
        # Application paths from the input request
        if (type == "root"):
            return self.__topPath
        elif (type == "binPath"):
            return self.__ccAppsBinPath
        elif (type == "uid"):
            return self.__sessionId
        elif (type == "sessionid"):
            return self.__sessionId
        #
        elif (type == "sessionTop"):
            return self.__topSessionPath

        elif (type == "logFile"):
            return os.path.join(self.__topSessionPath, "debug.log")
        elif (type == "sessionPath"):
            return self.__sessionPath
        elif (type == "sessionPathRel"):
            return self.__sessionRelativePath

        #
        # Special temporation paths -
        elif (type == "workingPath"):
            return self.__workingPath
        elif (type == "workingPathRel"):
            return self.__workingRelativePath
        #
        #
        # Proprietary application paths -- platform
        #
        elif (type == "acdName"):
            return "/apps/acd/namebat"
        elif (type == "mol2gif"):
            return "/opt/openeye/bin/mol2gif"
        #
        # Local binaries --  platform specific --
        elif (type == "maxitApp"):
            return os.path.join("/apps/rcsbapps/bin", "maxit")
        #
        elif (type == "bali"):
            return os.path.join(self.__ccAppsBinPath, "bali")
        elif (type == "babel"):
            return os.path.join(self.__ccAppsBinPath, "babel")
        elif (type == "alignComp"):
            return os.path.join(self.__ccAppsBinPath, "alignComp")
        elif (type == "matchApp"):
            return os.path.join(self.__ccAppsBinPath, "matchComp")
        elif (type == "splitApp"):
            return os.path.join(self.__ccAppsBinPath, "chemCompExtractor")
        elif (type == "buildImportApp"):
            return os.path.join(self.__ccAppsBinPath, "buildImportDefinition")
        elif (type == "cif2sdf"):
            return os.path.join(self.__ccAppsBinPath, "chemComp2Sdf")
        #
        # 15-Oct-2015  RPS self.__shellScriptPath retired so updated reference to makeReportFromFile.csh to sit under self.__ccAppsBinPath
        #
        elif (type == "reportFileScript"):
            return os.path.join(self.__ccAppsBinPath, "makeReportFromFile.csh")

        ##
        #  Data resource files ---
        # elif (type == "sandboxPathV2"):
        #    return os.path.join("/data/components/ligand-dict-v1")
        #
        elif (type == "sandboxPathV3" or type == "chemCompCachePath"):
            return self.__ccCvsPath
        elif (type == "fpPatternPath"):
            return self.__cICommon.get_cc_fp_patterns()
        elif (type == "serializedCcDictPath"):
            return self.__cICommon.get_cc_dict_serial()
        elif (type == "serializedCcIndexPath"):
            return self.__cICommon.get_cc_dict_idx()
        elif (type == "ccIdList"):
            return self.__cICommon.get_cc_id_list()
        elif (type == "oeLicenseFilePath"):
            return self.__oeLicenseFilePath
        elif (type == "oeDirectoryPath"):
            return self.__oeDirPath
        else:
            return "unknown"
