##
# File:  ChemCompTableEditor.py
# Date:  21-Aug-2010
#
# Updates:
#  1-Sep-2010    jdw   New incremental storage of edits using ChemCompEditStore()
#  2012-10-24    RPS    Updated to reflect reorganization of modules in pdbx packages#
##
"""
Chemical component text edit functions.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import os
import sys
import shutil
import traceback
from wwpdb.apps.ccmodule.utils.ChemCompConfig import ChemCompConfig
from mmcif_utils.chemcomp.PdbxChemCompUtils import PdbxChemCompReader, PdbxChemCompUpdater
#
from wwpdb.apps.ccmodule.io.ChemCompEditStore import ChemCompEditStore, ChemCompEdit
#
# temporary -
# from wwpdb.apps.ccmodule.io.ccIo                 import ccIo


class ChemCompTableEditor(object):
    """Chemical component table/text edit functions.

    """
    def __init__(self, reqObj, verbose=False, log=sys.stderr):
        """Chemical component text edit functions -

         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        self.__verbose = verbose
        self.__lfh = log
        # self.__debug = True
        #
        self.__reqObj = reqObj
        #
        self.__sObj = self.__reqObj.newSessionObj()
        self.__sessionPath = self.__sObj.getPath()
        self.__sessionRelativePath = self.__sObj.getRelativePath()
        self.__sessionId = self.__sObj.getId()
        #
        self.__ccConfig = ChemCompConfig(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        self.__ccId = None
        self.__ccFilePath = None
        self.__ccFileFormat = 'cif'
        #
        #

    def setCcId(self, ccId):
        """Set an existing chemical component identifier in archive collection as
           the edit target
        """
        self.__ccId = str(ccId.upper())
        return self.__getFilePathFromId(self.__ccId)

    def setFilePath(self, ccFilePath, ccFileFormat='cif', ccId=None):
        self.__ccFilePath = ccFilePath
        self.__ccFileFormat = ccFileFormat
        if not os.access(self.__ccFilePath, os.R_OK):
            return False
        if ccId is not None:
            self.__ccId = str(ccId).upper()
        #
        return True

    def getFilePath(self):
        return self.__ccFilePath

    def __getFilePathFromId(self, ccId):
        """
        """
        idUc = str(ccId).upper()
        fileName = idUc + ".cif"
        self.__ccFilePath = os.path.join(self.__ccConfig.getPath('chemCompCachePath'), idUc[0:1], idUc[0:3], fileName)
        #
        if not os.access(self.__ccFilePath, os.R_OK):
            return False
        self.__ccFileFormat = 'cif'
        return True

    def doUndo(self):
        """  Process an undo edit request.
        """
        rD = {}
        #
        # id = self.__reqObj.getValue('id')
        blockId = self.__reqObj.getValue('blockId')
        #
        # edit number controlled from edit store -
        editToUndo = self.__reqObj.getValue('editOpNumber')
        #
        if self.__verbose:
            self.__lfh.write("+ChemCompEdit.doUndo() - Starting doUndo() \n")
            self.__lfh.write("+ChemCompEdit.doUndo() - session id    %s\n" % self.__sessionId)
            self.__lfh.write("+ChemCompEdit.doUndo() - block id      %s\n" % blockId)
            self.__lfh.write("+ChemCompEdit.doUndo() - edit to undo  %r\n" % editToUndo)
            self.__lfh.flush()

        #
        es = ChemCompEditStore(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        editOpLast = es.getLastOpNumber()
        #
        if self.__verbose:
            self.__lfh.write("+ChemCompEdit.doUndo() - last stored edit operation %d\n" % editOpLast)
        #
        edNo = int(editToUndo)
        edList = es.get(edNo)
        undoList = []
        for ed in edList:
            if (ed.getEditType() == "replace-value"):
                targetId = "#" + ed.getTargetId()
                priorValue = ed.getValuePrevious()
                undoList.append({'id' : targetId, 'value' : priorValue})
            else:
                ed.printIt(self.__lfh)

        es.remove(edNo)
        #
        ok = True
        if not ok:
            rD['errortext'] = 'edit failed during update'
            rD['errorflag'] = True
            rD['value'] = None
            rD['editOpNumber'] = edNo - 1
        else:
            rD['editOpNumber'] = edNo - 1
            rD['id'] = None
            rD['value'] = None
            rD['valuelist'] = undoList

        #
        return rD

    def doItemValueUpdate(self):
        """  Process an item value edit.update request.
        """
        rD = {}
        #
        id = self.__reqObj.getValue('id')  # pylint: disable=redefined-builtin
        blockId = self.__reqObj.getValue('blockId')
        value = self.__reqObj.getValue('value')
        priorValue = self.__reqObj.getValue('priorValue')
        localPath = self.__reqObj.getValue('localPath')
        targetRowId = self.__reqObj.getValue('targetRowId')
        #
        # edit number controlled from edit store -
        editNumberReported = self.__reqObj.getValue('editOpNumber')
        #
        if self.__verbose:
            self.__lfh.write("+ChemCompEdit.doItemValueUpdate() - Starting doItemValueUpdate() \n")
            self.__lfh.write("+ChemCompEdit.doItemValueUpdate() - session id    %s\n" % self.__sessionId)
            self.__lfh.write("+ChemCompEdit.doItemValueUpdate() - local path    %s\n" % localPath)
            self.__lfh.write("+ChemCompEdit.doItemValueUpdate() - id            %s\n" % id)
            self.__lfh.write("+ChemCompEdit.doItemValueUpdate() - block id      %s\n" % blockId)
            self.__lfh.write("+ChemCompEdit.doItemValueUpdate() - value         %s\n" % value)
            self.__lfh.write("+ChemCompEdit.doItemValueUpdate() - prior value   %s\n" % priorValue)
            self.__lfh.write("+ChemCompEdit.doItemValueUpdate() - target row id %s\n" % targetRowId)
            self.__lfh.write("+ChemCompEdit.doItemValueUpdate() - editNumber    %r\n" % editNumberReported)
            self.__lfh.flush()

        (catName, attributeName, _sRow, _insertCode, _opNum) = id.split(':')
        # iRow = int(sRow)
        itemName = '_' + catName + '.' + attributeName
        #
        #
        es = ChemCompEditStore(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        editOpLast = es.getLastOpNumber()
        editOpNext = int(editOpLast) + 1

        ccEd = ChemCompEdit(self.__verbose, self.__lfh)
        #
        ccEd.setTargetId(id)
        ccEd.setBlockId(blockId)
        ccEd.setTargetRowId(targetRowId)
        ccEd.setEditType("replace-value")
        ccEd.setEditOpNumber(editOpNext)
        #
        ccEd.setTargetItemName(itemName)
        ccEd.setValueNew(value)
        ccEd.setValuePrevious(priorValue)

        ok = es.storeEdit(ccEd)
        if not ok:
            rD['errortext'] = 'edit failed during update'
            rD['errorflag'] = True
            rD['value'] = priorValue
            rD['editOpNumber'] = editNumberReported
        else:
            rD['editOpNumber'] = editOpNext
            rD['value'] = value
            rD['valuelist'] = [{'id': id, 'value': value}, {'id': id, 'value': value}]

        #
        return rD

    # def __getRowDefault(self, catName):
    #     """ Provide a
    #     """
    #     # rD = {}
    #     pass

    def doRowUpdate(self):
        """  Process a row edit update request -
        """
        rD = {}
        id = self.__reqObj.getValue('id')  # pylint: disable=redefined-builtin
        value = self.__reqObj.getValue('value')
        blockId = self.__reqObj.getValue('blockId')
        priorValue = self.__reqObj.getValue('priorValue')
        localPath = self.__reqObj.getValue('localPath')
        targetRowId = self.__reqObj.getValue('targetRowId')
        editNumberReported = self.__reqObj.getValue('editOpNumber')
        #
        if self.__verbose:
            self.__lfh.write("+ChemCompEdit.doRowUpdate() - Starting doUpdate() \n")
            self.__lfh.write("+ChemCompEdit.doRowUpdate() - session id    %s\n" % self.__sessionId)
            self.__lfh.write("+ChemCompEdit.doRowUpdate() - local path    %s\n" % localPath)
            self.__lfh.write("+ChemCompEdit.doRowUpdate() - id            %s\n" % id)
            self.__lfh.write("+ChemCompEdit.doRowUpdate() - block id      %s\n" % blockId)
            self.__lfh.write("+ChemCompEdit.doRowUpdate() - value         %s\n" % value)
            self.__lfh.write("+ChemCompEdit.doRowUpdate() - prior value   %s\n" % priorValue)
            self.__lfh.write("+ChemCompEdit.doRowUpdate() - target row id %s\n" % targetRowId)
            self.__lfh.write("+ChemCompEdit.doRowUpdate() - editNumber    %r\n" % editNumberReported)
            self.__lfh.flush()

        try:
            rD['editOpNumber'] = int(editOpNumber) + 1  # noqa: F821  XXXX This might be editOpeNumberReported - what are implications?  pylint: disable=undefined-variable
        except:  # noqa: E722 pylint: disable=bare-except
            rD['editOpNumber'] = 1

        rD['value'] = '+/-'
        rD['op'] = value

        (catName, opName, sRow, insertCode, sOpNum) = id.split(':')
        iRow = int(sRow)
        opNum = int(sOpNum)

        rD['id'] = '#%s:%s:%d:%s:%d' % (catName, opName, iRow, insertCode, opNum)

        if True:  # pylint: disable=using-constant-test
            return rD

        ccU = PdbxChemCompUpdater(verbose=self.__verbose, log=self.__lfh)
        ok = ccU.readComp(localPath, compId=None)
        if not ok:
            rD['errortext'] = 'update file not found'
            rD['errorflag'] = True

        ok = ccU.updateItem(itemName, value, iRow)  # noqa: F821  XXXX This code clearly not used as cannot work pylint: disable=undefined-variable
        if not ok:
            rD['errortext'] = 'item update failed'
            rD['errorflag'] = True

        ok = ccU.write()
        if not ok:
            rD['errortext'] = 'write failed during update'
            rD['errorflag'] = True

        #
        return rD

    def doEdit(self):
        """ Return content to launch the chemical component editor -
        """
        #
        oD = {}
        oD['dataDict'] = {}
        filePath = self.__ccFilePath
        fileFormat = self.__ccFileFormat
        blockId = self.__ccId
        #
        editOpNumber = 0
        if self.__verbose:
            self.__lfh.write("+ChemCompEdit.doEdit() - Starting doEdit() \n")
            self.__lfh.write("+ChemCompEdit.doEdit() - file path    %s\n" % filePath)
            self.__lfh.write("+ChemCompEdit.doEdit() - file format  %s\n" % fileFormat)
            self.__lfh.write("+ChemCompEdit.doEdit() - block Id     %s\n" % blockId)
            self.__lfh.flush()
        #
        #
        # make a local copy of the file (if required)
        #
        (_pth, fileName) = os.path.split(filePath)
        dirPath = os.path.join(self.__sessionPath, 'edit')
        localPath = os.path.join(dirPath, fileName)
        localRelativePath = os.path.join(self.__sessionRelativePath, 'edit', fileName)
        if filePath != localPath:
            if not os.access(dirPath, os.F_OK):
                os.makedirs(dirPath)
            shutil.copyfile(filePath, localPath)
            #
            if self.__verbose:
                self.__lfh.write("+ChemCompEdit.doEdit() - Copied input file %s to edit session path %s \n"
                                 % (filePath, localPath))
                self.__lfh.flush()
        #
        # Path context --

        oD['filePath'] = filePath
        oD['localPath'] = localPath
        oD['localRelativePath'] = localRelativePath
        oD['sessionId'] = self.__sessionId
        oD['editOpNumber'] = editOpNumber
        #
        try:
            ccf = PdbxChemCompReader(verbose=self.__verbose, log=self.__lfh)
            ccf.setFilePath(localPath, compId=blockId)
            ccf.getComp()
            oD['blockId'] = ccf.getBlockId()
            for catName in ['chem_comp', 'chem_comp_atom', 'chem_comp_bond']:
                oD['dataDict'][catName] = ccf.getChemCompCategory(catName=catName)
        except:  # noqa: E722 pylint: disable=bare-except
            if (self.__verbose):
                self.__lfh.write("+ChemCompEdit.doEdit() - edit preparation failed for:  %s\n" % fileName)
                traceback.print_exc(file=self.__lfh)
                self.__lfh.flush()
            return oD

        return oD

    def doLiveUpdate(self):
        """  Process an edit update request.
        """
        rD = {}
        id = self.__reqObj.getValue('id')  # pylint: disable=redefined-builtin
        value = self.__reqObj.getValue('value')
        priorValue = self.__reqObj.getValue('priorValue')
        localPath = self.__reqObj.getValue('localPath')
        editOpNumber = self.__reqObj.getValue('editOpNumber')
        if self.__verbose:
            self.__lfh.write("+ChemCompEdit.doUpdate() - Starting doUpdate() \n")
            self.__lfh.write("+ChemCompEdit.doUpdate() - local path    %s\n" % localPath)
            self.__lfh.write("+ChemCompEdit.doUpdate() - id            %s\n" % id)
            self.__lfh.write("+ChemCompEdit.doUpdate() - value         %s\n" % value)
            self.__lfh.write("+ChemCompEdit.doUpdate() - prior value   %s\n" % priorValue)
            self.__lfh.write("+ChemCompEdit.doUpdate() - editOpNumber  %r\n" % editOpNumber)
            self.__lfh.flush()
        try:
            rD['editOpNumber'] = int(editOpNumber) + 1
        except:  # noqa: E722 pylint: disable=bare-except
            rD['editOpNumber'] = 1

        rD['value'] = value
        rD['valuelist'] = [{'id': id, 'value': value}, {'id': id, 'value': value}]
        (catName, attributeName, sRow, _insertCode, _opNum) = id.split(':')
        iRow = int(sRow)
        itemName = '_' + catName + '.' + attributeName

        ccU = PdbxChemCompUpdater(verbose=self.__verbose, log=self.__lfh)
        ok = ccU.readComp(localPath, compId=None)
        if not ok:
            rD['errortext'] = 'update file not found'
            rD['errorflag'] = True

        ok = ccU.updateItem(itemName, value, iRow)
        if not ok:
            rD['errortext'] = 'item update failed'
            rD['errorflag'] = True

        ok = ccU.write()
        if not ok:
            rD['errortext'] = 'write failed during update'
            rD['errorflag'] = True

        #
        return rD


if __name__ == '__main__':
    pass
