import json
import os
import sys
from datetime import datetime, timezone
from logging import DEBUG, INFO, Formatter, StreamHandler, getLogger

from wwpdb.apps.ccmodule.utils.Exceptions import LigandStateError
from wwpdb.utils.config.ConfigInfo import ConfigInfo
from pathlib import Path
from wwpdb.io.locator.PathInfo import PathInfo
from wwpdb.utils.wf.dbapi.WfDbApi import WfDbApi


class LigandAnalysisState:
    """Class to track progress of operations in ligand
    analysis and notify interested modules.
    """
    _CC_STATE_FILE = 'state.json'

    STATE_RUNNING = 'running'
    STATE_STOPPED = 'stopped'
    STATE_UNKNOWN = 'unknown'
    STATE_FINISHED = 'finished'

    def __init__(self, depId, verbose=False, log=sys.stderr):
        self._verbose = verbose
        self._logging = self._setupLog(log)

        self._cI = ConfigInfo()
        self._depId = depId
        self._depositPath = Path(PathInfo().getDepositPath(self._depId)).parent
        self._ccReportPath = os.path.join(self._depositPath, self._depId, 'cc_analysis')
        self._ccStateFilePath = os.path.join(self._ccReportPath, self._CC_STATE_FILE)

        self._progress = 0
        self._state = 'unknown'

    def init(self):
        """Initialize the ligand analysis state for this deposition.

        Raises:
            LigandStateError: in case there is already a state.json file.
        """
        if os.path.exists(self._ccStateFilePath):
            # if there is already a state file, we shouldn't
            # be trying to create a new one
            raise LigandStateError('Trying to create a new ligand state file for deposition {}'.format(self._depId))

        self._progress = 0
        self._state = self.STATE_RUNNING

        if self._verbose:
            self._logging.debug('Creating state file %s for deposition %s', self._ccStateFilePath, self._depId)

        self._saveState()

    def __del__(self):
        if self._state == self.STATE_RUNNING:
            if self._progress < 1.0:
                self._logging.warning('LigandAnalysisState leaving with RUNNING state. Trying to set it to STOPPED.')
                self._state = self.STATE_STOPPED
            else:
                self._state = self.STATE_FINISHED

            try:
                self._saveState()
            except:  # noqa: E722 pylint: disable=bare-except
                pass

    def getProgress(self):
        """Get the current state of the ligand analysis.

        Returns:
            dict: dictionary describing the current state
        """
        currentState = {'state': 'unknown'}

        if not os.access(self._ccStateFilePath, os.R_OK):
            workflowStatus = self._checkRunningWorkflows()

            if workflowStatus is None:
                return currentState

            status = workflowStatus[0]
            classId = workflowStatus[1]

            if status == 'WORKING':
                if classId in ['uploadMod', 'ligandAnalysis']:
                    currentState['state'] = 'preparing'
                else:
                    currentState['state'] = 'busy'
            else:
                currentState['state'] = 'missing_file'

            return currentState

        try:
            with open(self._ccStateFilePath) as fp:
                currentState = json.load(fp)
        except Exception as e:
            self._logging.error('Error trying to read ligand state for %s %s', self._depId, e)
        finally:
            return currentState  # pylint: disable=lost-exception

    def addProgress(self, step, current_ligand=None):
        """Update the current state of the ligand analysis.

        TODO: This should NOT access the file system directly, but
        set the state through an API (as WfDataObject) instead.

        Args:
            step (float): ratio of completion, must be calculated by caller
            current_ligand (str, optional): current ligand being analysed. Defaults to None.

        Raises:
            LigandStateError: in case that it can't access the state.json file
        """
        if not os.access(self._ccStateFilePath, os.R_OK):
            if not self._progress:
                # maybe the caller forgot to call 'init'
                self._logging.warning('Did not find a state.json file. Did you forget to call init()?')
                self.init()
            else:
                raise LigandStateError('Could not find state.json file. Analysis may need to be restarted.')

        if step < 0:
            raise LigandStateError('Step must be positive.')

        if step > 1:
            self._logging.warning('Received a step value greater than 1.0. Check addProgress calls.')

        if self._progress + step > 1.0:
            self._progress = 1.0
        else:
            self._progress += step

        self._saveState(current_ligand=current_ligand)

    def finish(self):
        """Method to inform LiganAnalysisState that the analysis is
        complete.
        """
        if self._progress < 1.0:
            self._logging.warning('Finishing with progress under 1.0.')

        self._state = self.STATE_FINISHED
        self._saveState()

    def abort(self):
        self._state = self.STATE_STOPPED
        self._saveState()

    def reset(self):
        """Remove the progress file to start a new anaysis.

        Raises:
            LigandStateError: if tried to delete the progress file
                while there is an analysis going on
        """
        currentState = self.getProgress()

        if 'state' in currentState and currentState['state'] == self.STATE_RUNNING:
            raise LigandStateError('Tried to delete progress file of running analysis.')

        if os.access(self._ccStateFilePath, os.R_OK):
            os.remove(self._ccStateFilePath)

    def _checkRunningWorkflows(self):
        sqlQuery = "select status, wf_class_id from status.communication " \
            "where dep_set_id = '{}'".format(self._depId)

        wfApi = WfDbApi(verbose=True, log=sys.stderr)

        if wfApi.isConnected():
            nrow = wfApi.runSelectSQL(sqlQuery)

            if len(nrow) > 0:
                return nrow[0]

        return None

    def _saveState(self, current_ligand=None):
        state = self._createStateDescriptor(self._progress, self._state, current_ligand)

        with open(self._ccStateFilePath, 'w') as fp:
            json.dump(state, fp)

    def _createStateDescriptor(self, progress, state, current_ligand=None):
        """Utility to create the ligand state descriptor for the current
        deposition.

        Args:
            progress (float): ratio of completion
            state (str): should be either STATE_RUNNING, STATE_STOPPED, STATE_UNKNOWN or STATE_FINISHED

        Returns:
            dict: dictionary describing the current state
        """
        if progress < 0:
            progress = 0.0

        if progress > 1:
            progress = 1.0

        if state not in [self.STATE_RUNNING, self.STATE_STOPPED, self.STATE_UNKNOWN, self.STATE_FINISHED]:
            raise LigandStateError('Invalid state "{}"'.format(state))

        return {
            'progress': progress,
            'state': state,
            'current_ligand': current_ligand,
            'last_updated': '{}'.format(datetime.utcnow().replace(tzinfo=timezone.utc))
        }

    def _setupLog(self, log_file):
        """Setup a Logger instance to use the same file as provided
        by the 'log' parameters

        Args:
            log_file (IOStream): a file-like object

        Returns:
            Logger: instance of Logger class
        """
        logger = getLogger(__name__)
        handler = StreamHandler(log_file)

        formatter = Formatter('+%(module)s.%(funcName)s() ++ %(message)s\n')
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        if self._verbose:
            logger.setLevel(DEBUG)
        else:
            logger.setLevel(INFO)

        return logger
