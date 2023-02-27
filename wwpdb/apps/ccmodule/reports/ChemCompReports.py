##
# File:  ChemCompReports.py
# Date:  29-Jul-2010
# Updates:
# 2010-08-04    jdw    - Refactor -
# 2010-10-05    RPS    doReport() updated to accommodate usage by cc-assign component,
#                      in support of instance searching interface ("Level 2" searching)
# 2010-11-22    RPS    Checkpoint Update: doReport() updated to accommodate more granular dir hierarchy for cc dict reference material
# 2010-12-03    RPS    doReport method updated to accommodate strategy of sharing chem comp reference report material among ligand instances in same entity group.
# 2016-03-01    RPS    updated to set OE_DIR and OE_LICENSE environment variables before calling reportFileScript in doReport()
##
"""
Create web reports and validation/check reports for chemical component definitions.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import os
import sys
import shutil

from wwpdb.apps.ccmodule.utils.ChemCompConfig import ChemCompConfig
# from wwpdb.utils.config.ConfigInfo import ConfigInfo
from pathlib import Path
from wwpdb.io.locator.PathInfo import PathInfo


class ChemCompReport(object):
    """Create web report from chemical component definitions.

    """
    def __init__(self, reqObj, verbose=False, log=sys.stderr):
        """Create web reports from chemical component definitions.

        Using a file system organization like -

            session_path / <definintion_id> / report / [report-files...]

         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        self.__verbose = verbose
        self.__lfh = log
        # self.__debug = True
        #
        self.__reqObj = reqObj
        #
        self.__sObj = self.__reqObj.getSessionObj()
        self.__sessionPath = self.__sObj.getPath()
        # self.__sessionRelativePath = self.__sObj.getRelativePath()
        #
        self.__ccConfig = ChemCompConfig(reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        self.__reportFilePath = None
        self.__reportFileRelativePath = None
        self.__definitionId = None
        self.__definitionFilePath = None
        # self.__siteId = str(self.__reqObj.getValue("WWPDB_SITE_ID"))
        # self.__cI = ConfigInfo(self.__siteId)

        context = self.__getContext()
        if context == 'standalone':
            self.__depId = 'D_0'
            self.__ccReportPath = os.path.join(self.__sessionPath, 'assign')
        elif context == 'workflow' or context == 'unknown':
            self.__ccReportPath = os.path.join(self.__sessionPath, 'assign')
        elif context == 'deposition':
            self.__depId = self.__reqObj.getValue('identifier').upper()
            self.__depositPath = Path(PathInfo().getDepositPath(self.__depId)).parent
            self.__ccReportPath = os.path.join(self.__depositPath, self.__depId, 'cc_analysis')

    def __getContext(self):
        filesource = self.__reqObj.getValue('filesource')
        depid = self.__reqObj.getValue('identifier')

        if depid == 'TMP_ID':
            return 'standalone'

        if filesource == 'deposit':
            return 'deposition'

        if filesource in ['wf-archive', 'wf_archive', 'wf-instance', 'wf_instance']:
            return 'workflow'

        # in case we can't find out the context (as it happens with the standalone
        # ligmod) we fall back to get model files from the sessions path
        return 'unknown'

    def setDefinitionId(self, definitionId):
        """Set an existing chemical component identifier in archive collection as
           the report target
        """
        self.__definitionId = str(definitionId).upper()
        return self.__getFilePathFromId(self.__definitionId)

    def setFilePath(self, definitionFilePath, definitionId="TMP"):
        self.__definitionFilePath = definitionFilePath
        if (not os.access(self.__definitionFilePath, os.R_OK)):
            return False
        self.__definitionId = str(definitionId).upper()

        return True

    def getFilePath(self):
        return self.__definitionFilePath

    def __getFilePathFromId(self, ccId):
        """
        """
        idUc = str(ccId).upper()
        fileName = idUc + ".cif"
        self.__definitionFilePath = os.path.join(self.__ccConfig.getPath('chemCompCachePath'), idUc[0:1], idUc[0:3], fileName)
        #
        if (not os.access(self.__definitionFilePath, os.R_OK)):
            return False
        return True

    def doReport(self, type=None, ccAssignPthMdfier=None):  # pylint: disable=redefined-builtin
        """ Generate report data -
        """
        # Make a local copy of the source definition file -
        #
        rprtPthSuffix = ''
        if type is None:
            reportPath = os.path.join(self.__ccReportPath, self.__definitionId, 'report')
            reportRelativePath = os.path.join(self.__definitionId, 'report')
        else:
            if type == 'exp':
                rprtPthSuffix = os.path.join(ccAssignPthMdfier, 'report')
            elif type == 'ref':
                rprtPthSuffix = os.path.join('rfrnc_reports', ccAssignPthMdfier)

            reportPath = os.path.join(self.__ccReportPath, rprtPthSuffix)
            reportRelativePath = os.path.join(rprtPthSuffix)
        #
        # create the report path in the session directory
        #
        if (not os.access(reportPath, os.F_OK)):
            try:
                os.makedirs(reportPath)
            except:  # noqa: E722 pylint: disable=bare-except
                return False
        #
        # make a local copy of the source definition file
        #
        fileName = self.__definitionId + ".cif"
        filePath = os.path.join(reportPath, fileName)
        shutil.copyfile(self.__definitionFilePath, filePath)

        reportFile = self.__definitionId + "_report.html"
        reportFilePath = os.path.join(reportPath, reportFile)
        reportFileRelativePath = os.path.join(reportRelativePath, reportFile)
        logPath = os.path.join(reportPath, "report.log")

        oeLicenseFilePath = self.__ccConfig.getPath("oeLicenseFilePath")
        oeDirPath = self.__ccConfig.getPath("oeDirectoryPath")
        environVarSetup = "OE_LICENSE=" + oeLicenseFilePath + "; export OE_LICENSE; OE_DIR=" + oeDirPath + "; export OE_DIR;"

        cmd = environVarSetup + " " + self.__ccConfig.getPath("reportFileScript") + " " + \
            self.__ccConfig.getPath("binPath") + " " + reportPath + " " + fileName + \
            " " + reportRelativePath + " " + reportFile + " > " + logPath + " 2>&1"

        if (self.__verbose):
            self.__lfh.write("+ChemCompReports.doReport()\n")
            self.__lfh.write("Report ID                = %s\n" % self.__definitionId)
            self.__lfh.write("Beginning report in path = %s\n" % reportPath)
            self.__lfh.write("Target filename          = %s\n" % fileName)
            self.__lfh.write("Report path              = %s\n" % reportFile)
            self.__lfh.write("Log    path              = %s\n" % logPath)
            self.__lfh.write("Session relative path    = %s\n" % reportRelativePath)
            self.__lfh.write("Report command           = %s\n" % cmd)
            self.__lfh.flush()

        try:
            os.system(cmd)
            if os.path.exists(reportFilePath):
                self.__reportFilePath = reportFilePath
                self.__reportFileRelativePath = reportFileRelativePath
                return True
            else:
                return False
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def getReportPath(self):
        return self.__reportFileRelativePath

    def getReportPathRelative(self):
        return self.__reportFilePath

    def getReportHtml(self):
        #
        htmlData = ""
        try:
            if os.path.exists(self.__reportFilePath):
                htmlData = open(self.__reportFilePath).read()
        except:  # noqa: E722 pylint: disable=bare-except
            pass

        return htmlData

    def getReportFilePaths(self):
        """
            Returns a dictionary containing path information for file produced by report generator.

        The the following keys are used:
        gifPathRel, sdfModelPathRel, sdfIdealPathRel, cifPathRel reportPathRel

        """
        ##
        relPath = os.path.join(self.__definitionId, 'report')
        absPath = os.path.join(self.__ccReportPath, self.__definitionId, 'report')
        ccId = self.__definitionId
        #
        if self.__verbose:
            self.__lfh.write("+ChemCompReports.getReportPathDictionary() - searching files in path %s\n" % str(absPath))
        #
        fD = {}
        try:
            gifPathRel = os.path.join(relPath, ccId + ".gif")
            if os.path.exists(os.path.join(absPath, ccId + ".gif")):
                fD['gifPathRel'] = gifPathRel

            sdfIdealPathRel = os.path.join(relPath, ccId + "_ideal.sdf")
            if os.path.exists(os.path.join(absPath, ccId + "_ideal.sdf")):
                fD['sdfIdealPathRel'] = sdfIdealPathRel

            sdfModelPathRel = os.path.join(relPath, ccId + "_model.sdf")
            if os.path.exists(os.path.join(absPath, ccId + "_model.sdf")):
                fD['sdfModelPathRel'] = sdfModelPathRel

            cifPathRel = os.path.join(relPath, ccId + ".cif")
            if os.path.exists(os.path.join(absPath, ccId + ".cif")):
                fD['cifPathRel'] = cifPathRel

            reportPathRel = os.path.join(relPath, ccId + "_report.html")
            if os.path.exists(os.path.join(absPath, ccId + "_report.html")):
                fD['reportPathRel'] = reportPathRel
        except:  # noqa: E722 pylint: disable=bare-except
            pass

        return fD


class ChemCompCheckReport(object):
    """Create web validation/check reports from chemical component definitions.

    """
    def __init__(self, reqObj, verbose=False, log=sys.stderr):
        """Create web reports from chemical component definitions.
        Using a file system organization like -

            session_path / <definintion_id> / check-report / [report-files...]


         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        self.__verbose = verbose
        self.__lfh = log
        # self.__debug = True
        #
        self.__reqObj = reqObj
        #
        self.__sObj = self.__reqObj.getSessionObj()
        self.__sessionPath = self.__sObj.getPath()
        self.__sessionRelativePath = self.__sObj.getRelativePath()
        #
        self.__ccConfig = ChemCompConfig(reqObj, verbose=self.__verbose, log=self.__lfh)

        #
        self.__reportFilePath = None
        self.__reportFileRelativePath = None
        self.__definitionId = None
        self.__definitionFilePath = None

    def setDefinitionId(self, definitionId):
        """Set an existing chemical component identifier in archive collection as
           the report target
        """
        self.__definitionId = str(definitionId).upper()
        return self.__getFilePathFromId(self.__definitionId)

    def setFilePath(self, definitionFilePath, definitionId="TMP"):
        self.__definitionFilePath = definitionFilePath
        if (not os.access(self.__definitionFilePath, os.R_OK)):
            return False
        self.__definitionId = str(definitionId).upper()

        return True

    def __getFilePathFromId(self, ccId):
        """
        """
        idUc = str(ccId).upper()
        fileName = idUc + ".cif"
        self.__definitionFilePath = os.path.join(self.__ccConfig.getPath('chemCompCachePath'), idUc[0:1], idUc[0:3], fileName)
        #
        if (not os.access(self.__definitionFilePath, os.R_OK)):
            return False
        return True

    def getReportPath(self):
        return self.__reportFileRelativePath

    def getReportPathRelative(self):
        return self.__reportFilePath

    def getReportHtml(self):
        """
        """
        htmlData = ""
        try:
            if os.path.exists(self.__reportFilePath):
                htmlData = open(self.__reportFilePath).read()
        except:  # noqa: E722 pylint: disable=bare-except
            pass

        return htmlData

    def getReportFilePaths(self):
        """
          Returns a dictionary containing path information for file produced by check report generator.

          The the following keys are used:  logfile

        """
        ##
        relPath = os.path.join(self.__sessionRelativePath, self.__definitionId)
        absPath = os.path.join(self.__sessionPath, self.__definitionId)
        # ccId = self.__definitionId
        #
        if self.__verbose:
            self.__lfh.write("+ChemCompReports.getReportPathDictionary() - searching files in path %s\n" % str(absPath))
        #
        fD = {}
        try:
            logfile = os.path.join(relPath, "checkComp.log")
            if os.path.exists(os.path.join(absPath, "checkComp.log")):
                fD['logfile'] = logfile
        except:  # noqa: E722 pylint: disable=bare-except
            pass
        return fD

    def doReport(self):
        """ Need to
        """
        #
        version = "3"
        # Make a local copy of the source definition file -
        #
        reportPath = os.path.join(self.__sessionPath, self.__definitionId, 'check-report')
        reportRelativePath = os.path.join(self.__sessionRelativePath, self.__definitionId, 'check-report')
        #
        # create the report path in the session directory
        #
        if (not os.access(reportPath, os.F_OK)):
            try:
                os.makedirs(reportPath)
            except:  # noqa: E722 pylint: disable=bare-except
                return False
        #
        # make a local copy of the source definition file
        #
        fileName = self.__definitionId + ".cif"
        filePath = os.path.join(reportPath, fileName)
        shutil.copyfile(self.__definitionFilePath, filePath)

        reportFile = self.__definitionId + "_check_report.html"
        reportFilePath = os.path.join(reportPath, reportFile)
        reportFileRelativePath = os.path.join(reportRelativePath, reportFile)
        logPath = os.path.join(reportPath, "report.log")

        cmd = self.__ccConfig.getPath("checkFileScript") + " " + \
            self.__ccConfig.getPath("binPath") + " " + reportPath + " " + fileName + \
            " " + reportFile + " " + version + " > " + logPath + " 2>&1"

        if (self.__verbose):
            self.__lfh.write("+ChemCompReports.doCheckReport()\n")
            self.__lfh.write("Beginning check  in path = %s\n" % reportPath)
            self.__lfh.write("Target filename          = %s\n" % fileName)
            self.__lfh.write("Check report file        = %s\n" % reportFile)
            self.__lfh.write("Log    path              = %s\n" % logPath)
            self.__lfh.write("Check command            = %s\n" % cmd)

        #
        try:
            os.system(cmd)
            if os.path.exists(reportFilePath):
                self.__reportFilePath = reportFilePath
                self.__reportFileRelativePath = reportFileRelativePath
                return True
            else:
                return False
        except:  # noqa: E722 pylint: disable=bare-except
            return False
