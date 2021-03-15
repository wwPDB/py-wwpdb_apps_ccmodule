from wwpdb.utils.config.ConfigInfo import ConfigInfo

class LigandAnalysisState:
    """Class to track progress of operations in ligand
    analysis and notify interested modules.
    """
    def __init__(self):
        self._cI = ConfigInfo()
        print(self._cI.get('SITE_DEPOSIT_STORAGE_PATH'))