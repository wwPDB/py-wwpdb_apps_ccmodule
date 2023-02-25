import os
import sys
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch, Mock, MagicMock
from wwpdb.apps.ccmodule.utils.Exceptions import LigandStateError

sessionsTopDir = tempfile.mkdtemp()
configInfo = {
    "SITE_ARCHIVE_STORAGE_PATH": tempfile.mkdtemp(),
    "SITE_PREFIX": "PDBE_LOCALHOST",
    "SITE_WEB_APPS_TOP_SESSIONS_PATH": sessionsTopDir,
    "SITE_WEB_APPS_SESSIONS_PATH": os.path.join(sessionsTopDir, "sessions"),
    "SITE_DB_PORT_NUMBER": 10,
}

configInfoMockConfig = {
    "return_value": configInfo,
}

configMock = MagicMock(**configInfoMockConfig)

sys.modules["wwpdb.utils.config.ConfigInfo"] = Mock(ConfigInfo=configMock)

from wwpdb.apps.ccmodule.utils.LigandAnalysisState import LigandAnalysisState  # noqa: E402
from wwpdb.io.locator.PathInfo import PathInfo  # noqa: E402


class ReportFilesRequestTest(unittest.TestCase):
    """This class tests the API for requesting files generated by
    the chemical components report.

    """

    @classmethod
    def setUpClass(cls):
        cls._lfh = sys.stderr
        cls._verbose = False
        cls._depId = "D_0"

        cls._reportDir = os.path.join(Path(PathInfo().getDepositPath(cls._depId)), "cc_analysis")
        os.makedirs(cls._reportDir, exist_ok=True)

        cls._progressFile = os.path.join(cls._reportDir, "state.json")
        cls._ligState = LigandAnalysisState(cls._depId)

    def tearDown(self):
        super().tearDown()

        if os.path.exists(self._progressFile):
            os.remove(self._progressFile)

    @patch("wwpdb.apps.ccmodule.utils.LigandAnalysisState.WfDbApi", autospec=True)
    def testReadProgress(self, mockDbApi):
        mockDbApi.return_value.isConnected.return_value = True

        state = {"state": "running", "progress": 78, "current_ligand": "AAA", "last_updated": ""}

        with open(self._progressFile, "w") as fp:
            json.dump(state, fp)

        self.assertEqual(self._ligState.getProgress(), state)

        # missing file
        os.remove(self._progressFile)
        mockDbApi.return_value.runSelectSQL.return_value = [["WORKING", "ligandAnalysis"]]
        self.assertEqual(self._ligState.getProgress(), {"state": "preparing"})

        mockDbApi.return_value.runSelectSQL.return_value = [["WORKING", "fooBar"]]
        self.assertEqual(self._ligState.getProgress(), {"state": "busy"})

        mockDbApi.return_value.runSelectSQL.return_value = [["FINISHED", "ligandAnalysis"]]
        self.assertEqual(self._ligState.getProgress(), {"state": "missing_file"})

        # missing dir
        os.rmdir(self._reportDir)
        self.assertEqual(self._ligState.getProgress(), {"state": "missing_file"})

        os.makedirs(self._reportDir, exist_ok=True)

    def testInitStateFile(self):
        if os.path.exists(self._progressFile):
            os.remove(self._progressFile)

        self._ligState.init()
        self.assertTrue(os.path.exists(self._progressFile))

        with self.assertRaises(LigandStateError):
            self._ligState.init()

    def testAddProgress(self):
        self._ligState.init()
        self._ligState.addProgress(step=0.13, current_ligand="AAA")
        self._ligState.addProgress(step=0.33, current_ligand="AAA")

        self.assertEqual(self._ligState._progress, 0.46)

        with open(self._progressFile) as fp:
            state = json.load(fp)

            self.assertEqual(state["state"], "running")
            self.assertEqual(state["progress"], 0.46)
            self.assertEqual(state["current_ligand"], "AAA")
            self.assertIsNotNone(state.get("last_updated"))

        self._ligState.addProgress(step=1.3)
        self.assertEqual(self._ligState._progress, 1.0)

        with open(self._progressFile) as fp:
            state = json.load(fp)

            self.assertEqual(state["state"], "running")
            self.assertEqual(state["progress"], 1.0)
            self.assertIsNotNone(state.get("last_updated"))

        os.remove(self._progressFile)
        self._ligState = LigandAnalysisState(self._depId)
        self._ligState.addProgress(step=0.66)

        with self.assertRaises(LigandStateError):
            self._ligState.addProgress(step=-0.17)

        os.remove(self._progressFile)
        with self.assertRaises(LigandStateError):
            self._ligState.addProgress(step=0.5)

    def testReset(self):
        self._ligState = LigandAnalysisState(self._depId)
        self._ligState.init()
        self.assertTrue(os.path.exists(self._progressFile))

        with self.assertRaises(LigandStateError):
            self._ligState.reset()

        self._ligState.abort()
        self._ligState.reset()

        self.assertFalse(os.path.exists(self._progressFile))

    @unittest.skip
    def testGetCurrentTask(self):
        ct = self._ligState._getCurrentTask()
        self.assertEqual(ct, None)

        wfLogsDir = os.path.join(configInfo.get("TOP_WWPDB_SESSIONS_PATH"), "wf-logs", self._depId)

        open(os.path.join(wfLogsDir, "{}_ligandAnalysis_TP31_W_011_TP31_linkFileExist.log".format(self._depId), "w")).close()
        ct = self._ligState._getCurrentTask()
        self.assertEqual(ct, "linkage")

        open(os.path.join(wfLogsDir, "{}_ligandAnalysis_TP6_W_011_TP6_ChemCompReport.log".format(self._depId), "w")).close()
        ct = self._ligState._getCurrentTask()
        self.assertEqual(ct, "report")

        open(os.path.join(wfLogsDir, "{}_ligandAnalysis_TP31_W_012_TP6_linkFileExist.log".format(self._depId), "w")).close()
        ct = self._ligState._getCurrentTask()
        self.assertEqual(ct, "report")

        open(os.path.join(wfLogsDir, "{}_ligandAnalysis_TP3_W_012_TP6_ChemCompLinkCalc.log".format(self._depId), "w")).close()
        ct = self._ligState._getCurrentTask()
        self.assertEqual(ct, "linkage")

        open(os.path.join(wfLogsDir, "{}_ligandAnalysis_TP4_W_012_TP4_bla.log".format(self._depId), "w")).close()
        ct = self._ligState._getCurrentTask()
        self.assertEqual(ct, "assignment")
