##
# File: PdbxChemCompAssign.py
# Date: 15-Sep-2010
#
# Updates:
#
# 2011-06-14    RPS    Updated for addition of following items as per update to data models:
#                            _pdbx_instance_assignment.warning_message
#                            _pdbx_instance_assignment.parameter
#                            and
#                            _pdbx_match_list.warning_message
# 2011-06-20    RPS    Updated for update to _pdbx_match_list category definition
# 2012-10-24    RPS    Updated to reflect reorganization of modules in pdbx packages
##
"""
A collection of classes supporting chemical component assignment data files.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"


import sys
import os
import traceback
from mmcif.io.PdbxReader import PdbxReader
# ??? unused?
# from mmcif.api.PdbxContainers import *  # noqa: F401, F402, F403


class PdbxCategoryDefinition:

    _categoryInfo = [('pdbx_entry_info',           'key-value'),  # noqa: E241
                     ('pdbx_instance_assignment',  'table'),  # noqa: E241
                     ('pdbx_match_list',           'table'),  # noqa: E241
                     ('pdbx_atom_mapping',         'table'),  # noqa: E241
                     ('pdbx_missing_atom',         'table')]  # noqa: E241
    _cDict = {
        'pdbx_entry_info': [
            ('_pdbx_entry_info.file', '%s', 'str', ''),
            ('_pdbx_entry_info.format', '%s', 'str', ''),
            ('_pdbx_entry_info.number_of_total', '%s', 'str', ''),
            ('_pdbx_entry_info.number_of_passed', '%s', 'str', ''),
            ('_pdbx_entry_info.number_of_match', '%s', 'str', ''),
            ('_pdbx_entry_info.number_of_close_match', '%s', 'str', ''),
            ('_pdbx_entry_info.number_of_no_match', '%s', 'str', ''),
            ('_pdbx_entry_info.status', '%s', 'str', '')],
        'pdbx_instance_assignment': [
            ('_pdbx_instance_assignment.inst_id', '%s', 'str', ''),
            ('_pdbx_instance_assignment.het_id', '%s', 'str', ''),
            ('_pdbx_instance_assignment.single_atom_flag', '%s', 'str', ''),
            ('_pdbx_instance_assignment.status', '%s', 'str', ''),
            ('_pdbx_instance_assignment.warning_message', '%s', 'str', ''),
            ('_pdbx_instance_assignment.parameter', '%s', 'str', '')
        ],
        'pdbx_match_list': [
            ('_pdbx_match_list.inst_id', '%s', 'str', ''),
            ('_pdbx_match_list.reference_id', '%s', 'str', ''),
            ('_pdbx_match_list.match_type', '%s', 'str', ''),
            ('_pdbx_match_list.number_of_atoms_instance', '%s', 'str', ''),
            ('_pdbx_match_list.number_of_chiral_centers_instance', '%s', 'str', ''),
            ('_pdbx_match_list.number_of_atoms_reference', '%s', 'str', ''),
            ('_pdbx_match_list.number_of_chiral_centers_reference', '%s', 'str', ''),
            ('_pdbx_match_list.number_of_chiral_centers_combined', '%s', 'str', ''),
            ('_pdbx_match_list.number_of_aromatic_bonds', '%s', 'str', ''),
            ('_pdbx_match_list.number_of_total_bonds', '%s', 'str', ''),
            ('_pdbx_match_list.number_of_atoms_match', '%s', 'str', ''),
            ('_pdbx_match_list.number_of_chiral_centers_match_combined', '%s', 'str', ''),
            ('_pdbx_match_list.number_of_chiral_centers_match', '%s', 'str', ''),
            ('_pdbx_match_list.number_of_aromatic_bonds_match', '%s', 'str', ''),
            ('_pdbx_match_list.number_of_total_bonds_match', '%s', 'str', ''),
            ('_pdbx_match_list.heavy_atom_match_percent', '%s', 'str', ''),
            ('_pdbx_match_list.chiral_center_match_percent', '%s', 'str', ''),
            ('_pdbx_match_list.chiral_center_match_with_handness_percent', '%s', 'str', ''),
            ('_pdbx_match_list.aromatic_match_flag', '%s', 'str', ''),
            ('_pdbx_match_list.bond_order_match_percent', '%s', 'str', ''),
            ('_pdbx_match_list.warning_message', '%s', 'str', '')
        ],
        'pdbx_atom_mapping': [
            ('_pdbx_atom_mapping.inst_id', '%s', 'str', ''),
            ('_pdbx_atom_mapping.inst_atom_name', '%s', 'str', ''),
            ('_pdbx_atom_mapping.reference_id', '%s', 'str', ''),
            ('_pdbx_atom_mapping.reference_atom_name', '%s', 'str', '')
        ],
        'pdbx_missing_atom': [
            ('_pdbx_missing_atom.inst_id', '%s', 'str', ''),
            ('_pdbx_missing_atom.reference_id', '%s', 'str', ''),
            ('_pdbx_missing_atom.reference_atom_name', '%s', 'str', '')
        ]
    }


class PdbxChemCompAssignReader(object):
    ''' Accessor methods chemical component assignment data files.

        Currently supporting bond data data for the WWF format converter.
    '''
    def __init__(self, verbose=True, log=sys.stderr):
        self.__verbose = verbose
        self.__debug = False
        self.__lfh = log
        self.__dBlock = None
        self.__filePath = None
        #

    def getBlockId(self):
        try:
            if self.__dBlock is not None:
                return self.__dBlock.getName()
            else:
                return False
        except:  # noqa: E722 pylint: disable=bare-except
            return False

    def categoryExists(self, catName):
        return self.__dBlock.exists(catName)

    def setFilePath(self, filePath):
        """ Specify the file path for the target component and optionally provide an identifier
            for component data section within the file.
        """
        try:
            self.__filePath = filePath
            if (not os.access(self.__filePath, os.R_OK)):
                if self.__verbose:
                    self.__lfh.write("+ERROR- PdbxChemCompAssignReader.setFilePath() Missing file %s\n" % filePath)
                return False
            else:
                if self.__verbose:
                    self.__lfh.write("+PdbxChemCompAssignReader.setFilePath() file path %s\n" % self.__filePath)
            return True
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                self.__lfh.write("+ERROR- PdbxChemCompAssignReader.setFilePath() Missing file %s\n" % filePath)
            return False

    def getBlock(self):
        """ Load the first data block in the file.

            Returns True for success or False otherwise.
        """
        try:
            block = self.__getDataBlock(self.__filePath, None)
            return self.__setDataBlock(block)

        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return False

    def getCategory(self, catName='pdbx_instance_assignment'):
        return self.__getDictList(catName=catName)

    def __getDataBlock(self, filePath, blockId=None):
        """ Worker method to read the data file and set the target datablock
            corresponding to the target chemical component.   If no blockId is provided return the
            first data block.
        """
        try:
            ifh = open(filePath, 'r')
            myBlockList = []
            pRd = PdbxReader(ifh)
            pRd.read(myBlockList)
            ifh.close()
            if blockId is not None:
                for block in myBlockList:
                    if block.getType() == 'data' and block.getName() == blockId:
                        if (self.__debug):
                            block.printIt(self.__lfh)
                        return block
            else:
                for block in myBlockList:
                    if block.getType() == 'data':
                        if self.__debug:
                            block.printIt(self.__lfh)
                        return block

            return None
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=self.__lfh)
            return None

    def __setDataBlock(self, dataBlock=None):
        """ Assigns the input data block as the active internal data block containing the
            target chemical component definition.
        """
        ok = False
        try:
            if dataBlock.getType() == 'data':
                self.__dBlock = dataBlock
                ok = True
            else:
                self.__dBlock = None
        except:  # noqa: E722 pylint: disable=bare-except
            pass

        return ok

    def __getDictList(self, catName='chem_comp'):
        """Return a list of dictionaries of the input category where the dictionaries
           represent the row with full item names as dictionary keys.
        """
        #
        # Get category object - from current data block
        #
        itTupList = PdbxCategoryDefinition._cDict[catName]  # pylint: disable=protected-access
        catObj = self.__dBlock.getObj(catName)
        # nRows = catObj.getRowCount()
        #
        # Get column name index.
        #
        itDict = {}
        itNameList = catObj.getItemNameList()
        for idxIt, itName in enumerate(itNameList):
            itDict[itName] = idxIt
        #
        # Find the mapping to the local category definition
        #
        colDict = {}
        #
        for _ii, itTup in enumerate(itTupList):
            if itTup[0] in itDict:
                colDict[itTup[0]] = itDict[itTup[0]]
        #
        rowList = catObj.getRowList()
        dList = []
        for row in rowList:
            tD = {}
            for k, v in colDict.items():
                tD[k] = row[v]
            dList.append(tD)

        return dList

    # def __getDataList(self, catName='chem_comp_bond'):
    #     """Return  a list of data from the input category including
    #        data types and default value replacement.

    #        For list representing each row is column ordered according to the internal
    #        data structure PdbxCategoryDefinition._cDict[catName]

    #     """
    #     itTupList = PdbxCategoryDefinition._cDict[catName]
    #     catObj = self.__dBlock.getObj(catName)
    #     # nRows = catObj.getRowCount()

    #     itDict = {}
    #     itNameList = catObj.getItemNameList()
    #     for idxIt, itName in enumerate(itNameList):
    #         itDict[itName] = idxIt
    #     #
    #     colTupList = []
    #     # (column index of data or -1, type name, [default value]  )
    #     for _ii, itTup in enumerate(itTupList):
    #         if itTup[0] in itDict:
    #             colTupList.append((itDict[itTup[0]], itTup[2], itTup[3]))
    #         else:
    #             colTupList.append((-1, itTup[2], itTup[3]))
    #     #
    #     rowList = catObj.getRowList()
    #     dataList = []
    #     for row in rowList:
    #         uR = []
    #         for cTup in colTupList:

    #             if cTup[0] < 0:
    #                 uR.append(self.__applyType(cTup[1], cTup[2], cTup[2]))
    #             else:
    #                 uR.append(self.__applyType(cTup[1], cTup[2], row[cTup[0]]))

    #         dataList.append(uR)

    #     return dataList

    # def __applyType(self, type, default, val):
    #     """Apply type conversion to the input value and assign default values to
    #        missing values.
    #     """
    #     tval = val
    #     if val is None:
    #         tval = default
    #     if isinstance(tval, str) and (len(tval) < 1 or tval == '.' or tval == '?'):
    #         tval = default
    #     if type == "int":
    #         return int(str(tval))
    #     elif type == "float":
    #         return float(str(tval))
    #     elif type == "str":
    #         return str(tval)
    #     else:
    #         return tval
