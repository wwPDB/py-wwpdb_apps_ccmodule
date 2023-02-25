class InvalidLigandIdError(Exception):
    def __init__(self, lig_id=None):
        if not lig_id or lig_id == '':
            self.message = 'Missing ligand ID'
        else:
            self.message = 'Invalid ligand ID provided ({})'.format(lig_id)

        super().__init__(self.message)


class LigandStateError(Exception):
    def __init__(self, message=''):
        self.message = message
        super().__init__(self.message)


class InvalidDepositionIdError(Exception):
    def __init__(self, message=''):
        self.message = message
        super().__init__(self.message)
