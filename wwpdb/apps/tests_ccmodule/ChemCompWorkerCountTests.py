##
# File: ChemCompWorkerCountTests.py
#
"""Worker-process counts used by the chemical component assignment steps.

Without configuration the pool size is half the CPUs the process may use (at least 1); the assignment validation
uses one worker per instance when the compute cluster is enabled.  The resource allocation file can set a count for
either step.  The tests replace the process pool, the site configuration and the CPU counts, so nothing real is
started.
"""

# pylint: disable=protected-access,unused-argument

import json
import multiprocessing
import os
import tempfile
import unittest
from unittest import mock

import wwpdb.apps.ccmodule.chem.ChemCompAssign as assign_module
import wwpdb.apps.ccmodule.reports.InstanceDataGenerator as generator_module


class _FakePool(object):
    """Stands in for MultiProcUtil and remembers the requested number of processes."""

    requested = []

    def __init__(self, *args, **kwargs):
        pass

    def set(self, **kwargs):
        pass

    def setWorkingDir(self, path):
        pass

    def runMulti(self, dataList=None, numProc=None, numResults=None):
        _FakePool.requested.append(numProc)
        return True, [], [[]], []


class _FakeConfigInfo(object):
    """Site configuration with a resource allocation file and an optional compute-cluster flag."""

    path = None
    cluster = False

    def __init__(self, *args, **kwargs):
        pass

    def get(self, key, default=None):
        if key == "RESOURCE_ALLOCATION_CONFIG_FILE":
            return _FakeConfigInfo.path
        if key == "USE_COMPUTE_CLUSTER":
            return _FakeConfigInfo.cluster
        return default


class _FakeWorker(object):
    """Stands in for the report worker process."""

    created = []

    def __init__(self, *args, **kwargs):
        _FakeWorker.created.append(self)

    def start(self):
        pass

    def terminate(self):
        pass

    def join(self, timeout=None):
        pass


class _FakeQueue(object):
    def put(self, item):
        pass

    def get(self):
        return "OK"


class _Base(unittest.TestCase):
    key = None

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        _FakePool.requested = []
        _FakeWorker.created = []
        _FakeConfigInfo.path = None
        _FakeConfigInfo.cluster = False
        mock.patch("wwpdb.io.misc.ResourceAllocation.ConfigInfo", _FakeConfigInfo).start()
        self.addCleanup(mock.patch.stopall)

    def _configure(self, jobs=None, defaults=None):
        path = os.path.join(self._tmp, "resources.yaml")
        with open(path, "w") as out:
            json.dump({"jobs": jobs or {}, "defaults": defaults or {}}, out)
        _FakeConfigInfo.path = path

    def _cpus(self, available, node=None):
        mock.patch.object(os, "sched_getaffinity", lambda pid: set(range(available)), create=True).start()
        mock.patch.object(multiprocessing, "cpu_count", lambda: available if node is None else node).start()


class InstanceDataGeneratorWorkerCountTests(_Base):
    key = "ccmodule.instance_reports"

    def _pool_size(self, items=40):
        generator = object.__new__(generator_module.InstanceDataGenerator)
        generator._InstanceDataGenerator__verbose = False
        generator._InstanceDataGenerator__lfh = None
        with mock.patch.object(generator_module, "MultiProcWorker", _FakeWorker), mock.patch.object(multiprocessing, "Queue", _FakeQueue):
            generator._InstanceDataGenerator__runMultiprocessing(list(range(items)), mock.Mock(), "run")
        return len(_FakeWorker.created)

    def testUnconfiguredUsesHalfTheCpus(self):
        self._cpus(16)
        self.assertEqual(8, self._pool_size())

    def testUnconfiguredUsesCpusAvailableToTheProcessNotTheNode(self):
        self._cpus(4, node=64)
        self.assertEqual(2, self._pool_size())

    def testOneCpuStillStartsOneWorker(self):
        self._cpus(1)
        self.assertEqual(1, self._pool_size())

    def testNeverMoreWorkersThanItems(self):
        self._cpus(16)
        self.assertEqual(3, self._pool_size(items=3))

    def testConfiguredCountIsUsed(self):
        self._cpus(16)
        self._configure(jobs={self.key: {"cpus": 3}})
        self.assertEqual(3, self._pool_size())

    def testConfiguredCountAboveAvailableCpusIsClamped(self):
        self._cpus(4)
        self._configure(jobs={self.key: {"cpus": 12}})
        self.assertEqual(4, self._pool_size())

    def testConfiguredCountIsStillLimitedByItems(self):
        self._cpus(16)
        self._configure(jobs={self.key: {"cpus": 6}})
        self.assertEqual(2, self._pool_size(items=2))

    def testMalformedConfigurationFallsBackToTheDefault(self):
        self._cpus(16)
        self._configure(jobs={self.key: {"cpus": "lots"}})
        self.assertEqual(8, self._pool_size())


class AssignValidationWorkerCountTests(_Base):
    key = "ccmodule.assign_validation"

    def _pool_size(self, instances="A,B,C,D,E"):
        assign = object.__new__(assign_module.ChemCompAssign)
        assign._ChemCompAssign__ccValidateInstIdList = instances
        assign._ChemCompAssign__reqObj = mock.Mock()
        assign._ChemCompAssign__verbose = False
        assign._ChemCompAssign__lfh = None
        assign._ChemCompAssign__sessionPath = self._tmp
        assign._ChemCompAssign__cI = _FakeConfigInfo()
        _FakePool.requested = []
        with mock.patch.object(assign_module, "MultiProcUtil", _FakePool):
            self.assertEqual("", assign.doAssignValidation())
        self.assertEqual(1, len(_FakePool.requested))
        return _FakePool.requested[0]

    def testWithoutClusterUsesHalfTheCpus(self):
        self._cpus(16)
        self.assertEqual(8, self._pool_size())

    def testWithoutClusterUsesCpusAvailableToTheProcessNotTheNode(self):
        self._cpus(4, node=64)
        self.assertEqual(2, self._pool_size())

    def testOneCpuStillStartsOneWorker(self):
        self._cpus(1)
        self.assertEqual(1, self._pool_size())

    def testClusterUsesOneWorkerPerInstanceEvenAboveTheCpus(self):
        _FakeConfigInfo.cluster = True
        self._cpus(2)
        self.assertEqual(5, self._pool_size())

    def testConfiguredCountIsUsedWithoutCluster(self):
        self._cpus(16)
        self._configure(jobs={self.key: {"cpus": 3}})
        self.assertEqual(3, self._pool_size())

    def testConfiguredCountIsUsedWithCluster(self):
        _FakeConfigInfo.cluster = True
        self._cpus(16)
        self._configure(jobs={self.key: {"cpus": 3}})
        self.assertEqual(3, self._pool_size())

    def testConfiguredCountAboveAvailableCpusIsClamped(self):
        self._cpus(4)
        self._configure(jobs={self.key: {"cpus": 12}})
        self.assertEqual(4, self._pool_size())

    def testMalformedConfigurationFallsBackToTheDefault(self):
        self._cpus(16)
        self._configure(jobs={self.key: {"cpus": "lots"}})
        self.assertEqual(8, self._pool_size())

    def testMalformedConfigurationWithClusterFallsBackToOnePerInstance(self):
        _FakeConfigInfo.cluster = True
        self._cpus(16)
        self._configure(jobs={self.key: {"cpus": "lots"}})
        self.assertEqual(5, self._pool_size())


if __name__ == "__main__":
    unittest.main()
