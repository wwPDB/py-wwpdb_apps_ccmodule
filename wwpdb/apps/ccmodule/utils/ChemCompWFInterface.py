import os, sys, traceback
import logging
from wwpdb.apps.ccmodule.utils.ChemCompDpUtility import (
    ChemCompDpUtility,
    ChemCompDpInputs,
    ChemCompContext,
)


class ChemCompWFInterface:
    """This class has the only purpose of serving as an
    inteface between this repository and the WFE.
    """

    def __init__(self, verbose=False, log=sys.stderr):
        self._verbose = verbose
        self._lfh = log

    def chemCompReportOp(self, **kwargs):
        """Performs chemical component analysis from chem comp assign details
        file generated by the ChemCompAssign task.

        Returns:
            bool: status of the task
        """
        try:
            inpObjD = kwargs["inputObjectD"]
            ccAssignFilePath = inpObjD["src"].getFilePathReference()
            depId = inpObjD["src"].getDepositionDataSetId().upper()

            dp = ChemCompDpUtility(
                context=ChemCompContext.CONTEXT_DEPUI,
                depId=depId,
                verbose=self._verbose,
                log=self._lfh,
            )
            dp.addInput(ChemCompDpInputs.FILE_CC_ASSIGN, ccAssignFilePath)
            dp.doAnalysis()

            return True
        except:
            traceback.print_exc(file=self._lfh)
            return False

    def chemCompReportAnnOp(self, **kwargs):
        try:
            inpObjD = kwargs["inputObjectD"]
            wfInstanceId = inpObjD["src"].getWorkflowInstanceId()
            ccAssignFilePath = inpObjD["src"].getFilePathReference()
            depId = inpObjD["src"].getDepositionDataSetId().upper()

            dp = ChemCompDpUtility(
                context=ChemCompContext.CONTEXT_ANNOTATION,
                depId=depId,
                wfInstance=wfInstanceId,
                verbose=self._verbose,
                log=self._lfh,
            )
            dp.addInput(ChemCompDpInputs.FILE_CC_ASSIGN, ccAssignFilePath)
            dp.doAnalysisAnnotation()

            return True
        except:
            traceback.print_exc(file=self._lfh)
            return False
