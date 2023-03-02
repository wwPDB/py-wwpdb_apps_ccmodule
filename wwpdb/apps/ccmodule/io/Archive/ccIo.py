"""
File: ccIo.py

Legacy module with containers for mmCIF chem comp storage.

Por

Handles the interchange of chemical components between forms and file formats.

Update: 2007-10-07 stripped this out of the table editor to facilitate reuse.


"""

import os
import time
from wwpdb.apps.ccmodule.io.mmCIF import *
from openeye.oechem  import *
from openeye.oeiupac import *

class ccIo:
        def __init__(self, lfh=None, debug=True):
                self.debug   = debug
                self.lf      = lfh
                # Handle to mmCIF file object/parser
                self.cf      = None
                #
                # Internal storage of component data  -
                #
                self.ccTable = {}
                self.ccAtomTableList = []
                self.ccBondTableList = []
                self.ccDescriptorTableList = []
                self.ccIdentifierTableList = []
                self.ccFeatureTableList = []
                self.ccAuditTableList = []
                #
                # Load dictionaries and lists of item/column names and labels.
                #
                self.__setup()

        def initRowDict(self,keys):
                rD={}
                for k in keys:
                        rD[k]="?"
                return rD

        def setFormulaCC(self,formula):
                self.ccTable['formula'] = formula

        def setIdCC(self,id):
                self.ccTable['id']=id

        def setFormalChargeCC(self,charge):
                self.ccTable['pdbx_formal_charge']=charge

        def setNameCC(self,name):
                self.ccTable['name']=name

        def setTableCC(self,ccDict):
                self.ccTable=self.initRowDict(self.columns_cc)
                for k,v in ccDict.items():
                        self.ccTable[k]=v

        def setDefaultTableCC(self,idcode,name=None,formula=None,charge=None):
                self.ccTable=self.initRowDict(self.columns_cc)
                self.ccTable['id']=idcode
                if name is not None:
                        self.ccTable['name']=name
                else:
                        self.ccTable['name']='?'
                self.ccTable['type']='NON-POLYMER'
                self.ccTable['pdbx_type']='HETAIN'
                if formula is not None:
                        self.ccTable['formula']= formula
                else:
                        self.ccTable['formula']='?'
                self.ccTable['mon_nstd_parent_comp_id']='?'
                self.ccTable['pdbx_synonyms']='?'
                if charge is not None:
                        self.ccTable['pdbx_formal_charge']=charge
                else:
                        self.ccTable['pdbx_formal_charge']='?'
                self.ccTable['pdbx_ambiguous_flag']='N'
                self.ccTable['pdbx_initial_date']=self.lt
                self.ccTable['pdbx_modified_date']=self.lt
                self.ccTable['pdbx_release_status']='HOLD'
                self.ccTable['pdbx_replaced_by']='?'
                self.ccTable['pdbx_replaces']='?'
                self.ccTable['formula_weight']='?'
                self.ccTable['one_letter_code']='?'
                self.ccTable['three_letter_code']=idcode[:3]
                self.ccTable['pdbx_model_coordinates_details']='?'
                self.ccTable['pdbx_ideal_coordinates_details']='?'
                self.ccTable['pdbx_model_coordinates_missing_flag']='N'
                self.ccTable['pdbx_model_coordinates_db_code']='?'
                self.ccTable['pdbx_processing_site']='RCSB'
                self.ccTable['pdbx_subcomponent_list']='?'

        def getOeMolecule(self):
                mol = OEGraphMol()
                atmDict={}
                for atm in self.ccAtomTableList:
                        type=atm['type_symbol']
                        itype = OEGetAtomicNum(type)
                        oeAtom=mol.NewAtom(itype)
                        name=str(atm['atom_id'])
                        x=str(atm['model_Cartn_x'])
                        y=str(atm['model_Cartn_y'])
                        z=str(atm['model_Cartn_z'])
                        fCharge=str(atm['charge'])
                        aroFlag=str(atm['pdbx_aromatic_flag'])
                        stereoFlag=str(atm['pdbx_stereo_config'])
                        if (not self.isCifNull(x) and not self.isCifNull(y) and not self.isCifNull(z)):
                                xyztup = (float(x),float(y),float(z))
                                mol.SetCoords(oeAtom, xyztup)
                        if (not self.isCifNull(fCharge)):
                                oeAtom.SetFormalCharge(int(fCharge))
                        if (not self.isCifNull(name)):
                                oeAtom.SetName(name)
                        atmDict[name]= oeAtom

                mol.SetDimension(3)

                bndList=[]
                for bnd in self.ccBondTableList:
                        at1 = str(bnd['atom_id_1'])
                        at2 = str(bnd['atom_id_2'])
                        type = str(bnd['value_order'])
                        if (not self.isCifNull(at1) and not self.isCifNull(at2) \
                            and not self.isCifNull(type)):
                                oeType = self.getOeBondType(type)
                                aroFlag    =  str(bnd['pdbx_aromatic_flag']).lower()
                                stereoFlag =  str(bnd['pdbx_stereo_config']).lower()
                                oeBond = mol.NewBond(atmDict[at1], atmDict[at2], oeType)
                                if (not self.isCifNull(aroFlag)):
                                        if (aroFlag == 'y'):
                                                oeBond.SetAromatic(True)
                                                oeBond.SetIntType(5)
                return mol

        def isCifNull(self,value):
                if (value is not None and len(value) > 1):
                        return False
                if (len(value) == 0 or (len(value) == 1 and (value == '.' or value == '?'))):
                        return True
                return False;

        def getOeBondType(self,cifBondType):
                cbt = str(cifBondType).lower()
                if (cbt == "sing"):
                        oeType = 1
                elif (cbt == "doub"):
                        oeType = 2
                elif (cbt == "trip"):
                        oeType = 3
                elif (cbt == "quad"):
                        oeType = 4
                elif (cbt == "arom"):
                        oeType = 5
                else:
                        oeType = 1

                return oeType

        def loadForm(self,fst):
                #
                # read chem_comp, chem_comp_atom and chem_comp_bond from input form.
                #
                # Pull out all of the input fields with prefix tb:
                #
                # Form element coding is tb:<table prefix>:<column>:<row>
                #
                ccD=self.initRowDict(self.columns_cc)
                ccAtomD={}
                ccBondD={}
                for fld in fst.list:
                        fName = str(fld.name)
                        fValue= fld.value
                        #if self.debug:
                        #       self.lf.write("++INFO - form element name %s value %s\n" %(fName,fValue))
                        #
                        if fName.startswith("tb:"):
                                dl=fName.split(':')
                                if dl[1] == "cc":
                                        ccD[dl[2]] = fValue
                                elif dl[1] == "cca":
                                        row=dl[3]
                                        if row in ccAtomD:
                                                ccAtomD[row][dl[2]]=fValue
                                        else:
                                                # new row dictionary
                                                ccAtomD[row]=self.initRowDict(self.columns_cca)
                                                ccAtomD[row][dl[2]]=fValue

                                elif dl[1] == "ccb":
                                        row=dl[3]
                                        if row in ccBondD:
                                                ccBondD[row][dl[2]]=fValue
                                        else:
                                                # new row dictionary
                                                ccBondD[row]=self.initRowDict(self.columns_ccb)
                                                ccBondD[row][dl[2]]=fValue

                #
                # Now load the local data structures for each category.
                #
                self.ccTable=ccD
                #if (self.debug):
                #       for k,v in self.ccTable.items():
                #               self.lf.write("++INFO - CCTABLE - k=%s  v=%s\n" % (k,v))
                # Atom table
                #
                rowList=[]
                for r in ccAtomD.keys():
                        rowList.append(int(r))
                rowList.sort()
                self.ccAtomTableList=[]
                for rw in rowList:
                        srw=str(rw)
                        rD=ccAtomD[srw]
                        #if self.debug:
                        #       self._printDict(rD)
                        if str(rD['comp_id']) != "?":
                                self.ccAtomTableList.append(ccAtomD[srw])

                #  Bond table
                #
                rowList=[]
                for r in ccBondD.keys():
                        rowList.append(int(r))
                rowList.sort()
                self.ccBondTableList=[]
                for rw in rowList:
                        srw=str(rw)
                        rD=ccBondD[srw]
                        if str(rD['comp_id']) != "?":
                                self.ccBondTableList.append(ccBondD[srw])
                #
                return True

        def _printDict(self,d):
                self.lf.write("++INFO - Dictionary has - %d keys\n" % len(d.keys()))
                for k,v in d.items():
                        self.lf.write("++INFO -Row dictionary - key %s value %s\n" % (str(k),str(v)))

        def getIdCode(self):
                if 'id' in self.ccTable:
                        return self.ccTable['id']
                else:
                        return None

        def getParentCC(self):
                if 'mon_nstd_parent_comp_id' in self.ccTable:
                        return self.ccTable['mon_nstd_parent_comp_id']
                else:
                        return None

        def getTypeCC(self):
                if 'type' in self.ccTable:
                        return self.ccTable['type']
                else:
                        return None

        def getPdbxTypeCC(self):
                if 'pdbx_type' in self.ccTable:
                        return self.ccTable['pdbx_type']
                else:
                        return None

        def _updateIdcode(self, cf, idcode):
                cf[0].name = idcode
                cf[0]['chem_comp']['id'] = idcode
                cf[0]['chem_comp']['three_letter_code'] = idcode[:3]
                for row in cf[0]['chem_comp_atom'].iter_rows():
                        row['comp_id'] = idcode
                for row in cf[0]['chem_comp_bond'].iter_rows():
                        row['comp_id'] = idcode

                if cf[0].has_table('pdbx_chem_comp_descriptor'):
                        if cf[0]['pdbx_chem_comp_descriptor'].is_single():
                                cf[0]['pdbx_chem_comp_descriptor']['comp_id'] = idcode
                        else:
                                for row in cf[0]['pdbx_chem_comp_descriptor'].iter_rows():
                                        row['comp_id'] = idcode

                if  cf[0].has_table('pdbx_chem_comp_identifier'):
                        if cf[0]['pdbx_chem_comp_identifier'].is_single():
                                cf[0]['pdbx_chem_comp_identifier']['comp_id'] = idcode
                        else:
                                for row in cf[0]['pdbx_chem_comp_identifier'].iter_rows():
                                        row['comp_id'] = idcode

                if  cf[0].has_table('pdbx_chem_comp_feature'):
                        if cf[0]['pdbx_chem_comp_feature'].is_single():
                                cf[0]['pdbx_chem_comp_feature']['comp_id'] = idcode
                        else:
                                for row in cf[0]['pdbx_chem_comp_feature'].iter_rows():
                                        row['comp_id'] = idcode

                if  cf[0].has_table('pdbx_chem_comp_audit'):
                        if cf[0]['pdbx_chem_comp_audit'].is_single():
                                cf[0]['pdbx_chem_comp_audit']['comp_id'] = idcode
                        else:
                                for row in cf[0]['pdbx_chem_comp_audit'].iter_rows():
                                        row['comp_id'] = idcode


        def readCif(self,cifPath):
                #    try:
                f = open(cifPath, "r")
                self.cf = mmCIFFile()
                self.cf.load_file(f)
                self.getCifData()
                #               f.close()
                return True
                #except:
                #return False

        def getCifData(self):
                self.getChemCompCategory()
                self.getChemCompAtomCategory()
                self.getChemCompBondCategory()
                self.getChemCompDescriptorCategory()
                self.getChemCompIdentifierCategory()
                self.getChemCompFeatureCategory()
                self.getChemCompAuditCategory()

        def getChemCompCategory(self):
                cD={}
                for cname in self.columns_cc:
                        if self.debug:
                                self.lf.write("++INFO - checking key %s\n" % cname)
                                self.lf.flush()
                        try:
                                if self.cf[0]['chem_comp'].has_column(cname):
                                        cD[cname] = self.cf[0]['chem_comp'][cname]
                                else:
                                        cD[cname] = '?'
                        except:
                                cD[cname]='?'
                self.ccTable = cD
                #               if self.debug:  self._printDict(cD)
                return cD

        def getChemCompAtomCategory(self):
                cList=[]
                for row in self.cf[0]['chem_comp_atom'].iter_rows():
                        #if self.debug:         self._printDict(row)
                        cD={}
                        for cname in self.columns_cca:
                                if cname in row:
                                        cD[cname] = row[cname]
                                else:
                                        cD[cname] = '?'
                        #if self.debug:         self._printDict(cD)
                        cList.append(cD)
                self.ccAtomTableList = cList
                return cList

        def getChemCompBondCategory(self):
                cList=[]
                for row in self.cf[0]['chem_comp_bond'].iter_rows():
                        cD={}
                        for cname in self.columns_ccb:
                                if cname in row:
                                        cD[cname] = row[cname]
                                else:
                                        cD[cname] = '?'
                        cList.append(cD)
                self.ccBondTableList = cList
                return cList

        def getChemCompDescriptorCategory(self):
                cList=[]
                if not self.cf[0].has_table('pdbx_chem_comp_descriptor'):
                        return cList
                if self.cf[0]['pdbx_chem_comp_descriptor'].is_single():
                        cD={}
                        for cname in self.columns_ccd:
                                cD[cname] = self.cf[0]['pdbx_chem_comp_descriptor'][cname]
                        cList.append(cD)
                else:
                        for row in self.cf[0]['pdbx_chem_comp_descriptor'].iter_rows():
                                cD={}
                                for cname in self.columns_ccd:
                                        if cname in row:
                                                cD[cname] = row[cname]
                                        else:
                                                cD[cname] = '?'
                                cList.append(cD)

                self.ccDescriptorTableList = cList
                return cList

        def getChemCompIdentifierCategory(self):
                cList=[]
                if not self.cf[0].has_table('pdbx_chem_comp_identifier'):
                        return cList
                for row in self.cf[0]['pdbx_chem_comp_identifier'].iter_rows():
                        cD={}
                        for cname in self.columns_cci:
                                if cname in row:
                                        cD[cname] = row[cname]
                                else:
                                        cD[cname] = '?'
                        cList.append(cD)
                self.ccIdentifierTableList = cList
                return cList

        def getChemCompFeatureCategory(self):
                cList=[]
                if not self.cf[0].has_table('pdbx_chem_comp_feature'):
                        return cList
                for row in self.cf[0]['pdbx_chem_comp_feature'].iter_rows():
                        cD={}
                        for cname in self.columns_ccf:
                                if cname in row:
                                        cD[cname] = row[cname]
                                else:
                                        cD[cname] = '?'
                        cList.append(cD)
                self.ccFeatureTableList = cList
                return cList

        def getChemCompAuditCategory(self):
                cList=[]
                if not self.cf[0].has_table('pdbx_chem_comp_audit'):
                        return cList
                for row in self.cf[0]['pdbx_chem_comp_audit'].iter_rows():
                        cD={}
                        for cname in self.columns_ccau:
                                if cname in row:
                                        cD[cname] = row[cname]
                                else:
                                        cD[cname] = '?'
                        cList.append(cD)
                self.ccAuditTableList = cList
                return cList

        def writeCif(self,cifPath):

                if self.debug:
                        self.lf.write("++INFO - writing CIF file %s\n" % cifPath)

                ccId=self.getIdCode()
                if ccId is None:
                        return False


                cf = mmCIFFile()
                cf.new_data(ccId)
                #
                cf[ccId].new_table('chem_comp',self.columns_cc)
                for col in self.columns_cc:
                        cf[ccId]['chem_comp'].__setitem__(col,'?')
                for k,v in self.ccTable.items():
                        cf[ccId]['chem_comp'].__setitem__(k,v)

                cf[ccId]['chem_comp'].autoset_columns()
                #
                #
                cf[ccId].new_table('chem_comp_atom',self.columns_cca)
                irow = 0
                if self.debug:
                        self.lf.write("++INFO - length atom list %d\n" % len(self.ccAtomTableList))
                for rw in self.ccAtomTableList:
                        cf[ccId]['chem_comp_atom'].new_row()
                        for col in self.columns_cca:
                                cf[ccId]['chem_comp_atom'][irow].__setitem__(col,'?')
                        for k,v in rw.items():
                                #if self.debug:
                                #       self.lf.write("++INFO - CHEM_COMP_ATOM row %d k=%s v=%s\n" % (irow,k,v))
                                cf[ccId]['chem_comp_atom'][irow].__setitem__(k,v)
                        irow += 1
                cf[ccId]['chem_comp_atom'].autoset_columns()
                #

                cf[ccId].new_table('chem_comp_bond',self.columns_ccb)
                irow = 0
                for rw in self.ccBondTableList:
                        cf[ccId]['chem_comp_bond'].new_row()
                        for col in self.columns_ccb:
                                cf[ccId]['chem_comp_bond'][irow].__setitem__(col,'?')
                        for k,v in rw.items():
                                cf[ccId]['chem_comp_bond'][irow].__setitem__(k,v)
                        irow += 1

                cf[ccId]['chem_comp_bond'].autoset_columns()
                #

                if (len(self.ccDescriptorTableList) > 0):
                        if self.debug:
                                self.lf.write("++INFO - length descriptor list %d\n" % len(self.ccDescriptorTableList))
                        cf[ccId].new_table('pdbx_chem_comp_descriptor',self.columns_ccd)
                        irow = 0
                        for rw in self.ccDescriptorTableList:
                                cf[ccId]['pdbx_chem_comp_descriptor'].new_row()
                                for col in self.columns_ccd:
                                        cf[ccId]['pdbx_chem_comp_descriptor'][irow].__setitem__(col,'?')
                                for k,v in rw.items():
                                        cf[ccId]['pdbx_chem_comp_descriptor'][irow].__setitem__(k,v)
                                irow += 1
                        cf[ccId]['pdbx_chem_comp_descriptor'].autoset.columns()

                #
                if (len(self.ccIdentifierTableList) > 0):
                        if self.debug:
                                self.lf.write("++INFO - length identifier list %d\n" % len(self.ccIdentifierTableList))
                        cf[ccId].new_table('pdbx_chem_comp_identifier',self.columns_cci)
                        irow = 0
                        for rw in self.ccIdentifierTableList:
                                cf[ccId]['pdbx_chem_comp_identifier'].new_row()
                                for col in self.columns_cci:
                                        cf[ccId]['pdbx_chem_comp_identifier'][irow].__setitem__(col,'?')
                                for k,v in rw.items():
                                        cf[ccId]['pdbx_chem_comp_identifier'][irow].__setitem__(k,v)
                                irow += 1
                        cf[ccId]['pdbx_chem_comp_identifier'].autoset.columns()

                #
                if (len(self.ccFeatureTableList) > 0):
                        if self.debug:
                                self.lf.write("++INFO - length feature list %d\n" % len(self.ccFeatureTableList))
                        cf[ccId].new_table('pdbx_chem_comp_feature',self.columns_ccf)
                        irow = 0
                        for rw in self.ccFeatureTableList:
                                cf[ccId]['pdbx_chem_comp_feature'].new_row()
                                for col in self.columns_ccf:
                                        cf[ccId]['pdbx_chem_comp_feature'][irow].__setitem__(col,'?')
                                for k,v in rw.items():
                                        cf[ccId]['pdbx_chem_comp_feature'][irow].__setitem__(k,v)
                                irow += 1
                        cf[ccId]['pdbx_chem_comp_feature'].autoset.columns()

                #
                if (len(self.ccAuditTableList) > 0):
                        if self.debug:
                                self.lf.write("++INFO - length audit list %d\n" % len(self.ccAuditTableList))
                        cf[ccId].new_table('pdbx_chem_comp_audit',self.columns_ccau)
                        irow = 0
                        for rw in self.ccAuditTableList:
                                cf[ccId]['pdbx_chem_comp_audit'].new_row()
                                for col in self.columns_ccau:
                                        cf[ccId]['pdbx_chem_comp_audit'][irow].__setitem__(col,'?')
                                for k,v in rw.items():
                                        cf[ccId]['pdbx_chem_comp_audit'][irow].__setitem__(k,v)
                                irow += 1
                        cf[ccId]['pdbx_chem_comp_audit'].autoset.columns()


                # make sure the idcode is consistent in all categories
                self._updateIdcode (cf, ccId)

                cf.save_file(cifPath)
                return True

        def loadOeAtomsAndBonds(self, mol):
                """ Load atoms and bonds from input oe mol into internal cc storage.
                """
                #
                idcode = str(self.ccTable['id'])
                #
                self.ccAtomTableList = []
                acount = 0
                for atom in mol.GetAtoms():
                        atRow=self.initRowDict(self.columns_cca)
                        atRow['comp_id'] = idcode
                        (x,y,z) = mol.GetCoords(atom)
                        atRow['model_Cartn_x'] = '%0.3f' % x
                        atRow['model_Cartn_y'] = '%0.3f' % y
                        atRow['model_Cartn_z'] = '%0.3f' % z
                        atRow['atom_id']       = atom.GetName().strip()
                        atRow['alt_atom_id']   = atom.GetName().strip()
                        atRow['type_symbol']   = atom.GetType()
                        atRow['charge']        = atom.GetFormalCharge()
                        atRow['pdbx_leaving_atom_flag'] = 'N'
                        if len(atRow['atom_id']) > 3 or len(atRow['type_symbol']) == 2:
                                atRow['pdbx_align'] = 0
                        else:
                                atRow['pdbx_align'] = 1

                        if atom.IsAromatic():
                                atRow['pdbx_aromatic_flag']= 'Y'
                        else:
                                atRow['pdbx_aromatic_flag']= 'N'
                        oeSt = OEGetCIPStereo(mol,atom)
                        if (oeSt is not None and (len(oeSt) > 0) and (oeSt == "R" or oeSt == "S")):
                                atRow['pdbx_stereo_config']= oeSt
                        else:
                                atRow['pdbx_stereo_config']= 'N'
                        acount += 1
                        atRow['pdbx_ordinal']= str(acount)
                        self.ccAtomTableList.append(atRow)
                #
                self.ccBondTableList = []
                bcount = 0
                iBondD = {1:"SING", 2:"DOUB", 3:"TRIP", 4:"QUAD", 5:"AROM", 0:"DELO"}
                for bond in mol.GetBonds():
                        oeOrder = str(bond.GetOrder()).upper()
                        b1 = bond.GetBgn().GetName().strip()
                        b2 = bond.GetEnd().GetName().strip()
                        if self.debug:
                                self.lf.write("++INFO - oe create bond %s %s order %s\n" % (b1,b2,oeOrder))
                        if (int(oeOrder) in iBondD and not self.isCifNull(b1) and not self.isCifNull(b2)):
                                bndRow=self.initRowDict(self.columns_ccb)
                                bndRow['comp_id']     = idcode
                                bndRow['atom_id_1']   = b1
                                bndRow['atom_id_2']   = b2
                                bndRow['value_order'] = iBondD[int(oeOrder)]

                                if bond.IsAromatic():
                                        bndRow['pdbx_aromatic_flag'] = 'Y'
                                else:
                                        bndRow['pdbx_aromatic_flag'] = 'N'

                                oeSt = OEGetCIPStereo(mol,bond)
                                if (oeSt is not None and (len(oeSt) > 0) and (oeSt == "E" or oeSt == "Z")):
                                        bndRow['pdbx_stereo_config'] = oeSt
                                else:
                                        bndRow['pdbx_stereo_config'] = 'N'

                                bcount += 1
                                bndRow['pdbx_ordinal'] = str(bcount)
                                self.ccBondTableList.append(bndRow)




        def _renameHydrogenAtoms(self,mol):
                # Assign new H atom names --- only rotates leading digits in names -
                if (self.debug): self.lf.write("++INFO - renameHydrogenAtoms\n")
                for atom in mol.GetAtoms():
                        if atom.GetAtomicNum() == 1:
                                name=atom.GetName().strip()
                                if name[0] == 'H':
                                        continue
                                elif name[1] == 'H':
                                        newName=name[1:]+name[0]
                                        atom.SetName(newName)
        #
        def fixHydrogenAtomNames(self,mol):
                # Quick check of atom name uniqueness adding a suffix for duplicates
                #
                if (self.debug): self.lf.write("++INFO - fixHydrogenNames\n")
                # make all H atoms begin with type symbol -
                self._renameHydrogenAtoms(mol)
                #
                nameDict={}
                for atom in mol.GetAtoms():
                        if atom.GetAtomicNum() == 1:
                                name=atom.GetName().strip()
                                oldName= name
                                if name in nameDict and (len(name) == 4):
                                        for suffix in ['A','B','C','D','E','F','G','H','J']:
                                                nameNew = name[:3] + suffix
                                                if nameNew not in nameDict:
                                                        name = nameNew
                                                        if (self.debug): self.lf.write("++INFO - rename %s to %s\n" % (oldName,nameNew))
                                                        atom.SetName(name)
                                                        break
                                elif name in nameDict and (len(name)<4):
                                        for suffix in ['A','B','C','D','E','F','G','H','J']:
                                                nameNew = name + suffix
                                                if nameNew not in nameDict:
                                                        if (self.debug): self.lf.write("++INFO - rename %s to %s\n" % (oldName,nameNew))
                                                        name = nameNew
                                                        atom.SetName(name)
                                                        break
                                else:
                                        pass
                                if (self.debug): self.lf.write("++INFO - Adding name %s\n" % name)
                                nameDict[name]=oldName

        def assignHydrogenAtomNames(self,mol):
                """Assign hydrogen atom names to the input molecule if these are missing -
                """
                # Assign new H atom names ---
                if (self.debug): self.lf.write("++INFO - fixHydrogenNames\n")
                for atom in mol.GetAtoms():
                        if atom.GetAtomicNum() == 1:
                                front = atom.GetName().strip()
                                if (self.debug): self.lf.write("++INFO - front %s\n" % front )
                                if front == "":
                                        front = "H"
                                elif front[0] == "H":
                                        front = "H"
                                else:
                                        front = front[1] + front[0]
                                #
                                for nbor in atom.GetAtoms():
                                        end = nbor.GetName().strip()
                                        if (self.debug): self.lf.write("++INFO - end %s\n" % end )
                                        if nbor.GetAtomicNum() == 6:
                                                end = end[1:]
                                        if (len(front) + len(end)) > 4:
                                                end = end[-4+(len(front)+len(end)):]
                                        name = front + end
                                        if (self.debug): self.lf.write("++INFO - name %s\n" % name)
                                        atom.SetName(name)


        def updateFormalCharge(self):
                """ Return the charge some of the current component
                """
                fc=0
                for atm in self.ccAtomTableList:
                        fc += int(str(atm['charge']))
                        #if (self.debug): self.lf.write("++INFO - updateFormalCharge %s %s %d\n" % (atm['atom_id'],str(atm['charge']),fc))

                self.ccTable['pdbx_formal_charge'] = fc
                return fc

        def updateFormula(self):
                """ Return the molecular formula in approximate Hill format
                """
                mfdict = {}
                mf=[]
                fc=0
                for atm in self.ccAtomTableList:
                        fc += int(str(atm['charge']))
                        type=str(atm['type_symbol'])
                        mfdict[type] = 1 + mfdict.get(type,0)

                #
                try:
                        if mfdict["C"] == 1:
                                mf.append("C")
                        else:
                                mf.append("C%s" % mfdict["C"])
                        del mfdict["C"]
                except KeyError:
                        pass
                #
                try:
                        if mfdict["H"] == 1:
                                mf.append("H")
                        else:
                                mf.append("H%s" % mfdict["H"])
                        del mfdict["H"]
                except KeyError:
                        pass
                #
                mfkeys = mfdict.keys()
                mfkeys.sort()
                #
                for key in mfkeys:
                        if (mfdict.__getitem__(key) == 1 ):
                                mf.append("%s" % key)
                        else:
                                mf.append("%s%s" % (key, mfdict.__getitem__(key)))
                formula = " ".join(mf)
                #
                self.ccTable['formula']=formula
                return formula

        def makeFormulaFromMol(self,mol):
                """ Return the molecular formula in approximate Hill format
                """
                mfdict = {}
                mf=[]
                for atom in mol.GetAtoms():
                        mfdict[atom.GetIntType()] = 1 + mfdict.get(atom.GetIntType(), 0)
                #
                try:
                        if mfdict[6] == 1:
                                mf.append("C")
                        else:
                                mf.append("C%s" % mfdict[6])
                        del mfdict[6]
                except KeyError:
                        pass
                #
                try:
                        if mfdict[1] == 1:
                                mf.append("H")
                        else:
                                mf.append("H%s" % mfdict[1])
                        del mfdict[1]
                except KeyError:
                        pass
                #
                mfkeys = mfdict.keys()
                mfkeys.sort()
                for key in mfkeys:
                        if (mfdict.__getitem__(key) == 1 ):
                                mf.append("%s" % OEGetAtomicSymbol(key))
                        else:
                                mf.append("%s%s" % (OEGetAtomicSymbol(key), mfdict.__getitem__(key)))
                formula = " ".join(mf)
                #
                return formula


        def getColumnsChemComp(self):
                return self.columns_cc

        def getColumnsChemCompAtomLabels(self):
                return self.columns_cca_labels

        def getColumnsChemCompAtom(self):
                return self.columns_cca

        def getColumnsChemCompBond(self):
                return self.columns_ccb

        def getColumnsChemCompBondLabels(self):
                return self.columns_ccb_labels

        def getColumnsChemCompDescriptor(self):
                return self.columns_ccd

        def getColumnsChemCompIdentifier(self):
                return self.columns_cci

        def getColumnsChemCompAudit(self):
                return self.columns_ccau

        def getColumnsChemCompAuditLabels(self):
                return self.columns_ccau_labels

        def getTableCC(self):
                return self.ccTable

        def getTableAtom(self):
                return self.ccAtomTableList

        def getTableBond(self):
                return self.ccBondTableList

        def getTableDescriptor(self):
                return self.ccDescriptorTableList

        def getTableIdentifier(self):
                return self.ccIdentifierTableList

        def getTableAudit(self):
                return self.ccAuditTableList

        #
        def __setup(self):
                #
                # chem_comp table column names
                #
                self.lt = time.strftime("%Y-%m-%d", time.localtime())
                self.columns_cc=['id',
                                 'name',
                                 'type',
                                 'pdbx_type',
                                 'formula',
                                 'mon_nstd_parent_comp_id',
                                 'pdbx_synonyms',
                                 'pdbx_formal_charge',
                                 'pdbx_ambiguous_flag',
                                 'pdbx_initial_date',
                                 'pdbx_modified_date',
                                 'pdbx_release_status',
                                 'pdbx_replaced_by',
                                 'pdbx_replaces',
                                 'formula_weight',
                                 'one_letter_code',
                                 'three_letter_code',
                                 'pdbx_subcomponent_list',
                                 'pdbx_model_coordinates_details',
                                 'pdbx_ideal_coordinates_details',
                                 'pdbx_model_coordinates_missing_flag',
                                 'pdbx_model_coordinates_db_code',
                                 'pdbx_processing_site']
                self.ccTable=self.initRowDict(self.columns_cc)
                #
                # chem_comp_atom table column names
                #
                self.columns_cca = ['comp_id',
                                    'atom_id',
                                    'alt_atom_id',
                                    'type_symbol',
                                    'charge',
                                    'pdbx_align',
                                    'pdbx_aromatic_flag',
                                    'pdbx_leaving_atom_flag',
                                    'pdbx_stereo_config',
                                    'model_Cartn_x',
                                    'model_Cartn_y',
                                    'model_Cartn_z',
                                    'pdbx_model_Cartn_x_ideal',
                                    'pdbx_model_Cartn_y_ideal',
                                    'pdbx_model_Cartn_z_ideal',
                                    'pdbx_component_atom_id',
                                    'pdbx_component_comp_id',
                                    'pdbx_ordinal']
                self.columns_cca_labels = ['comp_id',
                                    'atom_id',
                                    'alt_atom_id',
                                    'type_symbol',
                                    'charge',
                                    'align',
                                    'aromatic_flag',
                                    'leaving_atom_flag',
                                    'stereo_config',
                                    'model_x',
                                    'model_y',
                                    'model_z',
                                    'ideal_x',
                                    'ideal_y',
                                    'ideal_z',
                                    'component_atom_id',
                                    'component_comp_id',
                                    'ordinal']

                #
                # chem_comp_bond table column names
                #

                self.columns_ccb=['comp_id',
                                  'atom_id_1',
                                  'atom_id_2',
                                  'value_order',
                                  'pdbx_aromatic_flag',
                                  'pdbx_stereo_config',
                                  'pdbx_ordinal']

                self.columns_ccb_labels=['comp_id',
                                  'atom_id_1',
                                  'atom_id_2',
                                  'value_order',
                                  'aromatic_flag',
                                  'stereo_config',
                                  'ordinal']

                #
                # pdbx_chem_comp_descriptor table column names
                #
                self.columns_ccd=['comp_id',
                                  'descriptor',
                                  'program',
                                  'program_version',
                                  'type']
                #
                #
                # pdbx_chem_comp_identifier table column names
                #
                self.columns_cci=['comp_id',
                                  'identifier',
                                  'program',
                                  'program_version',
                                  'type']

                #
                # pdbx_chem_comp_feature table column names
                #
                self.columns_ccf=['comp_id',
                                  'type',
                                  'source',
                                  'value']



                #
                # pdbx_chem_comp_audit table column names
                #

                self.columns_ccau=['comp_id',
                                  'action_type',
                                  'date',
                                  'processing_site',
                                  'annotator',
                                  'details']

                self.columns_ccau_labels=['comp_id',
                                  'action_type',
                                  'date',
                                  'processing_site',
                                  'annotator',
                                  'details']


if __name__ == '__main__':
        import sys
        myIo=ccIo(lfh=sys.stderr, debug=True)
        cifPath="Test.cif"
        myIo.readCif(cifPath)
        id = myIo.getIdCode()
        print(id)

