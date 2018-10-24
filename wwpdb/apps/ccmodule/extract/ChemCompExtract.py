##
# File:  ChemCompExtract.py
# Date:  8-Aug-2010
# Updates:
#
#
##
"""
Residue-level chemical component extraction operations.

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.01"

import os, sys, time, types, string, shutil, traceback

from openeye.oechem import *
#
# temporary - 
from wwpdb.apps.ccmodule.io.ccIo                 import ccIo
from wwpdb.apps.ccmodule.extract.ccOps           import ccOps

from wwpdb.apps.ccmodule.utils.ChemCompConfig    import ChemCompConfig
#from wwpdb.apps.ccmodule.io.ChemCompIo           import ChemCompReader
#from wwpdb.apps.ccmodule.reports.ChemCompReports  import ChemCompReport

class ChemCompExtract(object):
    """Residue-level chemical component extraction operations

    """
    def __init__(self,reqObj,verbose=False,log=sys.stderr):
        """Create simple web views from chemical component definitions.

         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.
          
        """
        self.__verbose=verbose
        self.__lfh=log
        self.__debug=True
        #
        self.__reqObj=reqObj
        # 
        self.__sObj=self.__reqObj.newSessionObj()
        self.__sessionPath=self.__sObj.getPath()
        self.__sessionRelativePath=self.__sObj.getRelativePath()        
        self.__sessionId  =self.__sObj.getId()        
        #
        self.__ccConfig=ChemCompConfig(self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        self.__setup()
        #

    def __setup(self):
        self.normal = ['ALA', 'CYS', 'ASP', 'GLU', 'PHE', 'GLY', 'HIS', 'ILE', 
                       'LYS', 'LEU', 'MET', 'ASN', 'PRO', 'GLN', 'ARG', 'SER',
                       'THR', 'VAL', 'TRP', 'TYR', 'C', 'G', 'T', 'A', 'U',
                       'DC', 'DA', 'DU', 'DT', 'DG',
                       'HOH', 'TIP', 'WAT', 'OH2', 'MSE']	
        #

    def doExtract(self):
        """  
        """
        # oD is the return dictionary - 
        oD={}        
        #
        view3d    = self.__reqObj.getValue("view3d")
        hAddOpt   = self.__reqObj.getValue("hydrogens")
        bgcolor   = self.__reqObj.getValue("bgcolor")
        bondOpt   = self.__reqObj.getValue("bondopt")
        caller    = self.__reqObj.getValue("caller")
        #
        if hAddOpt.lower() == "yes":
            addHydrogens=True
        else:
            addHydrogens=False        
        #
        filePath  = self.__reqObj.getValue('filePath')
        fileType  = self.__reqObj.getValue('fileType')
        
        if self.__verbose:
            self.__lfh.write("+ChemCompExtract.doExtract() - Starting doExtract() \n")
            self.__lfh.write("+ChemCompExtract.doExtract() - view3d  %s\n" % view3d)
            self.__lfh.write("+ChemCompExtract.doExtract() - bgcolor %s\n" % bgcolor)
            self.__lfh.write("+ChemCompExtract.doExtract() - caller  %s\n" % caller)
            self.__lfh.write("+ChemCompExtract.doExtract() - file path  %s\n" % filePath)
            self.__lfh.write("+ChemCompExtract.doExtract() - file type  %s\n" % fileType)
            self.__lfh.flush()
        #
        
        #
        # make a local copy of the file (if required)
        #
        (pth,fileName)=os.path.split(filePath)
        lclPath=os.path.join(self.__sessionPath,fileName)
        if (filePath != lclPath):
            shutil.copyfile(filePath,lclPath)
            #
            if (self.__verbose):
                self.__lfh.write("+ChemCompExtract.doExtract() - Copied input file %s to session path %s \n" % (filePath,lclPath))
                self.__lfh.flush()				

        
        fileExt=str(fileName[-4:]).lower()
        fileNamePdb=fileName
        try:
            os.chdir(self.__sessionPath)            
            if (fileType == 'cif' or fileType == 'cifeps'):
                scriptPath     = self.__ccConfig.getPath('maxitApp')
                cmd = "%s -o 2 -i %s " % (scriptPath,fileName)
                if (self.__verbose):
                    self.__lfh.write("+ChemCompExtract.doExtract() - cif2pdb using:  %s\n" % fileName)

                os.system("env > LOGENV")
                os.system(cmd)
                fileNamePdb += ".pdb"
            elif (fileType == 'pdb' and fileExt == ".pdb"):
                pass
            elif (fileType == 'pdb' and fileExt != ".pdb"):
                fileNamePdb += ".pdb"                
            else:
                fileNamePdb += ".pdb"

            
        except:
            if (self.__verbose):
                self.__lfh.write("+ChemCompExtract.doExtract() - format pre-processing failed for:  %s\n" % fileName)
                traceback.print_exc(file=self.__lfh)
                self.__lfh.flush()                            
            return oD
        #
        # ------------------------------------------------------------------
        #
        filePathPdb = os.path.join(self.__sessionPath,fileNamePdb)
        #
        try:
            if (self.__verbose):
                self.__lfh.write("+ChemCompExtract.doExtract() - Extracting components from input file:  %s\n" % fileNamePdb)
                self.__lfh.flush()				
            oeResDict = self.extractComponents(fileNamePdb)
        except:
            if (self.__verbose):
                self.__lfh.write("+ChemCompExtract.doExtract() - component extraction failed for :  %s\n" % fileName)
                traceback.print_exc(file=self.__lfh)
                self.__lfh.flush()                                            
            return oD
        #
        #

        if (self.__verbose):
            self.__lfh.write("+ChemCompExtract.doExtract() - Starting component extraction processing  %s\n" % fileNamePdb)

        #
        try:
            extractList=[]
            for key, oeRes in oeResDict.items():
                resId = self._makeCleanResName(key)
                if self.__verbose: self.__lfh.write("+ChemCompExtract.doExtract() - Processing component %s\n" % resId)
                aCount=oeRes.NumAtoms()
                if aCount <= 1:
                    if self.__verbose: self.__lfh.write("+ChemCompExtract.doExtract() - skipping ion component  %s with atom count %d\n" % (resId,aCount))
                    continue
                #
                tD = self.processComponent(oeRes, resId, addHydrogens, bondOpt)
                extractList.append(tD)
        except:
            if (self.__verbose):
                self.__lfh.write("+ChemCompExtract.doExtract() - component processing failed for :  %s\n" % key)
                traceback.print_exc(file=self.__lfh)
                self.__lfh.flush()                                            
            return oD
            

        if  self.__verbose:
            self.__lfh.write("+ChemCompExtract.doExtract() - Finished component extraction processing\n")
            for cc in extractList:
                for k,v in cc.items():
                    self.__lfh.write("+ChemCompExtract.doExtract() - key %s :%s\n" % (k,v))


        # JDW - is this used?
        tarFiles = [("targif","gifs.tar"),("tarcif", "cifs.tar"),("tarism", "isms.tar")]
        oD['tarFiles']=tarFiles

        oD['bgcolor']=bgcolor
        oD['graphics']="yes"
        oD['sessionid']=self.__sessionId
        oD['filename']=fileName
        oD['filepathpdb']=filePathPdb
        oD['view3d']=view3d
        oD['hydrogens']='yes'
        oD['bondopt']=bondOpt
        oD['extractlist']=extractList
        #
        return oD


    def extractComponents(self, pdbFileName): 
        """ Returns a dictionary of OE molecule objects that represent the residues in the PDB file.
        """
        #
        if self.__verbose:
            self.__lfh.write("In extractComponents() with %s\n" % pdbFileName)
            self.__lfh.flush()
        ifs = oemolistream()

        # Filename must have a '.pdb' extension for OE to recognize the format as PDB
        #
        if self.__verbose:
            self.__lfh.write("before open with %s\n" % pdbFileName)
            self.__lfh.flush()

        if (ifs.open(pdbFileName) != 1):
            if self.__verbose:
                self.__lfh.write("Could not open the input file %s\n" % pdbFileName)
                self.__lfh.flush()
            raise ValueError("Could not open input file %s" % pdbFileName)
        else:
            #create new mol object and read in the mol from the pdb file
            #		ifs.SetFlavor(OEFormat_PDB,OEIFlavor_PDB_END
            #			      | OEIFlavor_PDB_ENDM
            #			      | OEIFlavor_PDB_DELPHI
            #			      | OEIFlavor_PDB_ImplicitH
            #			      | OEIFlavor_PDB_BondOrder
            #			      | OEIFlavor_PDB_Rings
            #			      | OEIFlavor_PDB_Connect)
            #

            if self.__verbose:
                self.__lfh.write("After open with %s\n" % pdbFileName)
                self.__lfh.flush()

            flavorR = OEIFlavor_Generic_Default | OEIFlavor_PDB_END | OEIFlavor_PDB_ENDM
            ifs.SetFlavor(OEFormat_PDB, flavorR)
#
            mol = OEGraphMol()
            OEReadMolecule(ifs, mol)
            if not mol:
                if self.__verbose:
                    self.__lfh.write("OEreadMolecule failing with %s\n" % pdbFileName)
                    self.__lfh.flush()				
                raise ValueError("<h1>There was no molecule in the pdb file!</h1>")
            #
            #Loop over the atoms and collect all the residues
            resDict = {}
            for atom in mol.GetAtoms():
                res = OEAtomGetResidue(atom)
                if res.GetName().strip().upper() in self.normal:
                    continue

                # make unique name is 'residueName_chainId_residueNum' (strip any quotes)

                resKey = res.GetName() + '_' + res.GetChainID().strip() + '_' + str(res.GetResidueNumber())
                resKey = resKey.strip().strip('\'').strip('\"')
                if self.__verbose:
                    self.__lfh.write("++INFO - extracted residue  %s\n" % resKey)
                    self.__lfh.flush()
                if not resDict.has_key(resKey):
                    #Add new residue				
                    if (self.__verbose): self.__lfh.write("Added new residue %s\n" % resKey)				
                    resDict[resKey] = OEGraphMol()
                #append a copy of the atom onto the residue
                atom.SetIntType(atom.GetAtomicNum())
                atom.SetType(OEGetAtomicSymbol(atom.GetAtomicNum()))
                resDict[resKey].NewAtom(atom)
            if self.__verbose:
                self.__lfh.write("++INFO - residues extracted %d\n" % len(resDict))
                self.__lfh.flush()
            return resDict

        
    def processComponent(self, oeRes, resId, addHydrogens, bondOpt):
        """
        All files created in sessionPath/resId path

        Return: dictionary with keys:  id, sdfPathRel, gifPathRel, cifPathRel,
            ismPathRel, pdbPathRel, formula, formal_charge, acdName, annCifPathRel,
            checkCifPathRel, reportPathRel
        """
        #aroModel=OEAroModelOpenEye
        aroModel=OEAroModelMDL
        #

        rDict={}
        rDict['id']=resId
        rDict['sessionid']=self.__sessionId
        
        if self.__verbose:
            self.__lfh.write("++INFO - processig residue %s\n" % resId)
            self.__lfh.flush()

        myops=ccOps(self.__ccConfig,self.__lfh,self.__verbose)
        
        #
        # -------------------------------------------------------------------------
        # Output files are written in subdirectories in the current session directory
        #
        #sessionPath   =self.__ccConfig.getPath('sessionPath')
        #sessionPathRel=self.__ccConfig.getPath('sessionPathRel')
        
        dirPath    = os.path.join(self.__sessionPath,resId)
        dirPathRel = os.path.join(self.__sessionRelativePath,resId)
        #
        if (not os.access(dirPath,os.F_OK)):
            os.mkdir(dirPath)
        os.chdir(dirPath)
        #
        ## -------------------------------------------------------------------------
        ## ***  ALTERNATIVE bondorder perceptions -
        #
        myIo = ccIo(self.__lfh,self.__verbose)

        pdbFileName = "%s-org.pdb" % resId
        myops.writePdbFromMol(oeRes,pdbFileName)
        #
        # atNameList[] saves a copy of the initial atom names - 
        #
        dup = {}
        fCharge = 0
        atNameList=[]
        atChargeList=[]		
        for atom in oeRes.GetAtoms():
            fCharge += atom.GetFormalCharge()
            atChargeList.append(atom.GetFormalCharge())
            atNameList.append(atom.GetName())
            if not dup.has_key(atom.GetName()):
                dup[atom.GetName()] = None
            else:
                if self.__verbose: self.__lfh.write("++ERROR - Duplicate atom name %s\n" % str(atom.GetName()))
                pass
        #
        #

        if (bondOpt == "type1"):
            useBonds = "bali"
            molFileNameBali =resId + "-bali.mol2"
            myops.doPdb2MolBali(dirPath,pdbFileName,molFileNameBali)			
            molFileNameBonds=molFileNameBali			
        elif (bondOpt == "type2"):
            useBonds = "babel"
            molFileNameBabel=resId + "-babel.sdf"
            myops=ccOps(self.__ccConfig,self.__lfh,self.__verbose)
            myops.doPdb2MolBabel(dirPath,pdbFileName,molFileNameBabel,"-h")
            molFileNameBonds=molFileNameBabel			
        elif (bondOpt == "type3"):			
            useBonds = "oe"
        else:
            useBonds = "oe"

        #
        if ((bondOpt == "type1" or bondOpt == "type2") and os.access(molFileNameBonds,os.F_OK)):
            molB=myops.getOeMolFromFile(molFileNameBonds)
            for name, atom in map(None,atNameList,molB.GetAtoms()):
                atom.SetName(name)
                if self.__verbose: self.__lfh.write("++INFO ressetting extracted atom name to %s\n" % name)

            OEFindRingAtomsAndBonds(molB)
            if (bondOpt == "type2"):
                OEAssignMDLHydrogens(molB)							
                #OEAssignImplicitHydrogens(molB)
                #OEAssignMDLHydrogens(molB)			
                #OEAssignFormalCharges(molB)
                OEAddExplicitHydrogens(molB)
                OESet3DHydrogenGeom(molB)
            else:
                OEAssignAromaticFlags(molB, aroModel)
                OEAddExplicitHydrogens(molB)
                OESet3DHydrogenGeom(molB)				

            mol = OEGraphMol()
            mol.Clear()
            OEAddMols(mol, molB)
            #
            molT = OEGraphMol()
            molT.Clear()
            OEAddMols(molT, molB)
            if (bondOpt == "type1"):
                OESuppressHydrogens(molT)
            #
            if self.__verbose: 
                for atom in molT.GetAtoms():
                    self.__lfh.write("++INFO extracted atom name now %s\n" % atom.GetName())
        else:
            #
            mol = OEGraphMol()
            mol.Clear()
            OEAddMols(mol, oeRes)
            self._molInfo(resId,mol,"Initial molecule")
            OEDetermineConnectivity(mol)
            OEFindRingAtomsAndBonds(mol)
            OEPerceiveBondOrders(mol)
            self._molInfo(resId,mol,"After OE bond order perception")
            OEAssignImplicitHydrogens(mol)
            self._molInfo(resId,mol,"After implicit hydrogen addition")			
            OEAssignFormalCharges(mol)
            self._molInfo(resId,mol,"After formal charge assignment")			
            OEAssignAromaticFlags(mol, aroModel)

            if OEHasExplicitHydrogens(mol):
                if self.__verbose: self.__lfh.write("++INFO - Detected explicit hydrogrens on %s\n" % resId)			
                if (addHydrogens):
                    if self.__verbose: self.__lfh.write("++INFO - Stripping hydrogrens from %s\n" % resId)
                    OESuppressHydrogens(mol)
                    OEAssignImplicitHydrogens(mol)				
                    OEAssignFormalCharges(mol)
                    OEAssignAromaticFlags(mol, aroModel)
                    OEAddExplicitHydrogens(mol)
                    OESet3DHydrogenGeom(mol)
                else:
                    if self.__verbose: self.__lfh.write("++INFO - Using explicit hydrogrens from %s\n" % resId)
                    OEAssignFormalCharges(mol)
                    OEAssignAromaticFlags(mol, aroModel)
            else:
                OEAddExplicitHydrogens(mol)
                OESet3DHydrogenGeom(mol)
                self._molInfo(resId,mol,"After explicit h atom addition ")

            # -------------------------------------------------------------------------
            #

            molT = OEGraphMol()
            molT.Clear()
            OEAddMols(molT, oeRes)
            OEDetermineConnectivity(molT)
            OEFindRingAtomsAndBonds(molT)
            OEPerceiveBondOrders(molT)
            OESuppressHydrogens(molT)
            OEAssignImplicitHydrogens(molT)				
            OEAssignFormalCharges(molT)
            OEAssignAromaticFlags(molT, aroModel)
            #
        # --------------------------------------------------------------------
        #  molT is the extracted component -- 
        #
        fCharge = 0		
        for atom in molT.GetAtoms():
            fCharge += atom.GetFormalCharge()		
        #
        #
        if self.__verbose: self.__lfh.write("++INFO - Writing extracted atom CIF for %s\n" % resId)
        cifExtractFileName= "%s-extract.cif" % resId  			
        cifio = ccIo(self.__lfh,self.__verbose)
        molFormula = cifio.makeFormulaFromMol(molT)		
        cifio.setDefaultTableCC(resId[:3],name=None,formula=molFormula,charge=fCharge)
        cifio.loadOeAtomsAndBonds(molT)
        cifio.updateFormalCharge()
        cifio.updateFormula()										
        ok=cifio.writeCif(cifExtractFileName)
        if ok:
            cifExtractPathRel=os.path.join(dirPathRel,cifExtractFileName)
            rDict['cifExtractPathRel']=cifExtractPathRel
        #
        #

        # Make sure any added atoms are properly typed... 
        for atom in mol.GetAtoms():
            atom.SetIntType(atom.GetAtomicNum())
            atom.SetType(OEGetAtomicSymbol(atom.GetAtomicNum()))
        #
        OESetDimensionFromCoords(mol)
        OE3DToInternalStereo(mol)
        #
        self._molInfo(resId,mol,"After adding explict hydrogen atoms before renaming ")
        # 
        if self.__verbose: self.__lfh.write("++INFO - Renaming atoms in %s\n" % resId)
        cifio2 = ccIo(self.__lfh,self.__verbose)
        cifio2.assignHydrogenAtomNames(mol)		
        cifio2.fixHydrogenAtomNames(mol)
        self._molInfo(resId,mol,"Final molecule after renaming")
        #
        # Verify unique atom names ...
        #
        dup = {}
        fCharge = 0		
        for atom in mol.GetAtoms():
            fCharge += atom.GetFormalCharge()		
            if not dup.has_key(atom.GetName()):
                dup[atom.GetName()] = None
            else:
                if self.__verbose: self.__lfh.write("++ERROR - Duplicate atom name %s\n" % str(atom.GetName()))
                pass

        rDict['formal_charge']=fCharge
        #
        molFormula = cifio2.makeFormulaFromMol(mol)				
        rDict['formula']=molFormula
        #
        # Make a clean copy of the final molecule as some of the output
        # options change the atom names -
        #
        molS = OEGraphMol()
        molS.Clear()
        OEAddMols(molS, mol)
        # ------------------------------------------------------------------------
        #  OE molecule is complete and fully named  at this point -
        #

        #
        sdfFileName = "%s.sdf" % resId
        myops.writeSdfFromMol(mol,sdfFileName)
        sdfPathRel=os.path.join(dirPathRel,sdfFileName)
        rDict['sdfPathRel']=sdfPathRel
        if self.__verbose: self.__lfh.write("++INFO - Wrote SDF %s\n" % sdfPathRel)
        #
        #
        pdbFileName = "%s.pdb" % resId
        myops.writePdbFromMol(mol,pdbFileName)		
        pdbPathRel=os.path.join(dirPathRel,pdbFileName)
        rDict['pdbPathRel']=pdbPathRel
        if self.__verbose: self.__lfh.write("++INFO - Wrote PDB %s\n" % pdbPathRel)
        #
        #
        ismFileName = "%s.ism" % resId
        myops.writeSmilesFromOeMol(mol,ismFileName)				
        ismPathRel=os.path.join(dirPathRel,ismFileName)
        rDict['ismPathRel']=ismPathRel
        if self.__verbose: self.__lfh.write("++INFO - Wrote SMILES %s\n" % ismPathRel)
        #
        #
        if self.__verbose: self.__lfh.write("++INFO - Get ACD name using %s\n" % sdfFileName)
        acdName = myops.getAcdName(sdfFileName)
        rDict['acdName']=acdName		
        #
        if self.__verbose: self.__lfh.write("++INFO - make image from SMILES\n")
        #gifFileName= "%s-ism.gif" % resId  
        #gifFile   = myops.makeGifFromSmiles(ismFileName, gifFileName)
        #gifPathRel=os.path.join(dirPathRel,gifFileName)
        #rDict['gifPathRel']=gifPathRel

        gifFileName= "%s-300.gif" % resId[0:3]  
        gifPathRel=os.path.join(dirPathRel,gifFileName)
        rDict['gifPathRel']=gifPathRel

        #
        #
        if self.__verbose: self.__lfh.write("++INFO - Writing CIF for %s\n" % resId)
        cifFileName= "%s.cif" % resId
        cifio2.setDefaultTableCC(resId[:3],name=acdName,formula=molFormula,charge=fCharge)
        cifio2.loadOeAtomsAndBonds(molS)
        cifio2.setNameCC(acdName)
        cifio2.updateFormalCharge()
        cifio2.updateFormula()								
        ok=cifio2.writeCif(cifFileName)
        if ok:
            cifPathRel=os.path.join(dirPathRel,cifFileName)
            rDict['cifPathRel']=cifPathRel
        #
        # Create an annotated CIF file
        #
        annCifFileName="%s-v3.cif" % resId
        ok = myops.doAnnotateFile(dirPath,cifFileName,annCifFileName,"SWAP")
        if ok:
            annCifPathRel=os.path.join(dirPathRel,annCifFileName)
            rDict['annCifPathRel']= annCifPathRel
        #
        # Create a check report file
        #
        checkCifFileName="%s-check-v3.html" % resId
        ok = myops.doCheckFile(dirPath,annCifFileName,checkCifFileName,version="3")
        if ok:
            checkCifPathRel=os.path.join(dirPathRel,checkCifFileName)
            rDict['checkCifPathRel']= checkCifPathRel
        #
        # Create a report file
        #
        reportFileName="%s-v3.html" % resId
        ok = myops.doReportFile(dirPath,dirPathRel,annCifFileName,reportFileName)
        if ok:
            reportPathRel=os.path.join(dirPathRel,reportFileName)
            rDict['reportPathRel']= reportPathRel
        #

        return rDict


    def _molInfo(self,key,mol,title=None):
        if not self.__verbose: return
        #
        if title != None:
            if self.__verbose:	self.__lfh.write("++INFO - %s \n" % title)

        if self.__verbose: self.__lfh.write("++INFO - molecule %s dimension %d \n" % (key,mol.GetDimension()))
        if self.__verbose: self.__lfh.write("++INFO - atoms %d  bonds %d\n" % (mol.NumAtoms(),mol.NumBonds()))
        tcharge=0
        for atom in mol.GetAtoms():
            name=str(atom.GetName())
            type=str(atom.GetType())
            atNo=str(atom.GetAtomicNum())
            (x,y,z) = mol.GetCoords(atom)
            charge=str(atom.GetFormalCharge())
            tcharge+= atom.GetFormalCharge()
            valence=atom.GetValence()
            hcount=atom.GetTotalHCount()
            degree=atom.GetDegree()
            aroFlag=str(atom.IsAromatic())
            chiralFlag=str(atom.IsChiral())
            if self.__verbose:
                self.__lfh.write("++INFO - ATOM name=%s type=%s atNo=%s charge=%s valence %d hcount %d degree %d aromatic %s chiral %s x %8.3f y %8.3f z %8.3f\n" % \
                          (name,type,atNo,charge,valence,hcount,degree,aroFlag,chiralFlag,x,y,z))
        for bond in mol.GetBonds():
            oeOrder = str(bond.GetOrder()).upper()
            b1 = bond.GetBgn().GetName().strip()
            b2 = bond.GetEnd().GetName().strip()
            if self.__verbose:
                self.__lfh.write("++INFO - BOND %s %s order %s\n" % (b1,b2,oeOrder))				
        if self.__verbose: self.__lfh.write("++INFO - total charge %d\n" % tcharge)


    def _fixResidue(self,res):
        """This method corrects problems with stereocenters (especially nitrogen and phosporus) as well as 
        improper formal charges on nitrogen.
        """
        for atom in res.GetAtoms():
            if atom.IsNitrogen():
                ntest = []
                for bond in atom.GetBonds():
                    nbor = bond.GetNbr(atom)
                    ntest.append(nbor.GetAtomicNum())
                if len(ntest) == 4 and ntest.count(1) < 1:
                    atom.SetFormalCharge(1)
                else:
                    v = []
                    atom.SetStereo(v, OEAtomStereo_Tetrahedral, OEAtomStereo_Undefined)
            if atom.IsPhosphorus():
                ptest = []
                for bond in atom.GetBonds():
                    nbor = bond.GetNbr(atom)
                    ptest.append(nbor.GetAtomicNum())
                if len(ptest) > 3 and ptest.count(8) > 2:
                    v = []
                    atom.SetStereo(v, OEAtomStereo_Tetrahedral, OEAtomStereo_Undefined)
        OEClearAromaticFlags(res)
        OEAssignAromaticFlags(res, OEAroModelMDL)


    def _makeCleanResName(self,resname):
        """Makes the resname contain only alphanumeric characters and underscores."""
        letters = list(resname)
        return "".join([(self._isCleanResName(letter) and letter or "") for letter in letters])

    def _isCleanResName(self,letter):
        if (letter.isalnum()) or (letter == "_"):
            return True
        else:
            return False	


    def reProcessExtractedComponent(self, inpCifFileName, resId):
        """ Use starting connectivity, bond orders & charges to recompute everything else...
            This method reprocesses the starting extracted component which is typically
                the preliminary/extracted heavy-atom version - 

        Return: dictionary with keys:  id, sdfPathRel, gifPathRel, cifPathRel,
            ismPathRel, pdbPathRel, formula, formal_charge, acdName, annCifPathRel,
            checkCifPathRel, reportPathRel

        """
        #
        # This is the residue unique identifier tied to relative directory location
        # in the session path...
        #
        rDict={}
        rDict['id']=resId
        #
        # -------------------------------------------------------------------------
        # Output files are written in subdirectories in the current session directory
        #
        sessionPath   =self.__ccPath.getPath('sessionPath')
        sessionPathRel=self.__ccPath.getPath('sessionPathRel')
        dirPath    = os.path.join(sessionPath,resId)
        dirPathRel = os.path.join(sessionPathRel,resId)
        #
        if (not os.access(dirPath,os.F_OK)):
            os.mkdir(dirPath)
        os.chdir(dirPath)
        #
        # -------------------------------------------------------------------------
        #
        # read input file build starting molecule
        #
        cifioInp  = ccIo( self.lf,self.debug)			
        ok     = cifioInp.readCif(inpCifFileName)
        oeMol  = cifioInp.getOeMolecule()
        # save the chem_comp category from the input file
        ccTableInp = cifioInp.getTableCC()

        #
        #aroModel=OEAroModelOpenEye
        aroModel=OEAroModelMDL 

        mol = OEGraphMol()
        mol.Clear()

        OEAddMols(mol, oeMol)
        OEFindRingAtomsAndBonds(mol)		
        self._molInfo(resId,mol,"Initial molecule")
        # -------------------------------------------------------------------------
        #
        #
        # Add the extracted-atom file to the list of files -
        #
        cifExtractFileName= "%s-extract.cif" % resId  			
        cifExtractPathRel=os.path.join(dirPathRel,cifExtractFileName)
        rDict['cifExtractPathRel']=cifExtractPathRel
        #
        # The treatment here depends on whether the molecule has explict hydrogens...
        # 		
        #  no longer use: OEAssignMDLHydrogens(mol)
        #
        #aroModel=OEAroModelOpenEye
        aroModel=OEAroModelMDL 

        if OEHasExplicitHydrogens(mol):
            if self.debug: self.lf.write("++INFO - Using explicit hydrogrens from %s\n" % resId)
            #OEAssignFormalCharges(mol)
            OEAssignAromaticFlags(mol, aroModel)
        else:
            OEAssignMDLHydrogens(mol)
            #OEAssignImplicitHydrogens(mol)
            self._molInfo(resId,mol,"After implicit hydrogen addition")			
            #OEAssignFormalCharges(mol)
            #self._molInfo(resId,mol,"After formal charge assignment")			
            OEAssignAromaticFlags(mol, aroModel)			
            OEAddExplicitHydrogens(mol)
            OESet3DHydrogenGeom(mol)

        # Make sure any added atoms are properly typed... 
        for atom in mol.GetAtoms():
            atom.SetIntType(atom.GetAtomicNum())
            atom.SetType(OEGetAtomicSymbol(atom.GetAtomicNum()))
        #
        self._molInfo(resId,mol,"After H atom addition molecule")
        OESetDimensionFromCoords(mol)
        OE3DToInternalStereo(mol)
        #
        #
        self._molInfo(resId,mol,"Final molecule before renaming")
        if self.debug: self.lf.write("++INFO - Renaming atoms in %s\n" % resId)
        cifio2 = ccIo(self.lf,self.debug)
        cifio2.assignHydrogenAtomNames(mol)
        cifio2.fixHydrogenAtomNames(mol)
        self._molInfo(resId,mol,"Final molecule after renaming")
        #
        # Verify unique atom names ...
        #
        dup = {}
        fCharge = 0		
        for atom in mol.GetAtoms():
            fCharge += atom.GetFormalCharge()		
            if not dup.has_key(atom.GetName()):
                dup[atom.GetName()] = None
            else:
                if self.debug: self.lf.write("++ERROR - Duplicate atom name %s\n" % str(atom.GetName()))
                pass

        rDict['formal_charge']=fCharge
        #
        molFormula = cifio2.makeFormulaFromMol(mol)
        rDict['formula']=molFormula
        #
        #
        # Make a clean copy of the final molecule as some of the output
        # options change the atom names -
        #
        molS = OEGraphMol()
        molS.Clear()
        OEAddMols(molS, mol)

        # ------------------------------------------------------------------------
        #  OE molecule is complete and fully named at this point -
        #
        sdfFileName = "%s.sdf" % resId
        myops.writeSdfFromMol(mol,sdfFileName)
        sdfPathRel=os.path.join(dirPathRel,sdfFileName)
        rDict['sdfPathRel']=sdfPathRel
        if self.debug: self.lf.write("++INFO - Wrote SDF %s\n" % sdfPathRel)
        #
        #
        ismFileName = "%s.ism" % resId
        myops.writeSmilesFromOeMol(mol,ismFileName)				
        ismPathRel=os.path.join(dirPathRel,ismFileName)
        rDict['ismPathRel']=ismPathRel
        if self.debug: self.lf.write("++INFO - Wrote SMILES %s\n" % ismPathRel)
        #
        myops=ccOps(self.__ccPath,self.lf,self.debug)
        #
        if self.debug: self.lf.write("++INFO - Get ACD name using %s\n" % sdfFileName)
        acdName = myops.getAcdName(sdfFileName)
        rDict['acdName']=acdName
        if self.debug: self.lf.write("++INFO - ACD name is %s\n" % acdName)		
        #
        if self.debug: self.lf.write("++INFO - make image from SMILES\n")
        gifFileName= "%s-ism.gif" % resId  
        gifFile   = myops.makeGifFromSmiles(ismFileName, gifFileName)
        gifPathRel=os.path.join(dirPathRel,gifFileName)
        rDict['gifPathRel']=gifPathRel
        # 

        if self.debug: self.lf.write("++INFO - Writing all atom CIF for %s\n" % resId)
        #
        #self._molInfo(resId,mol,"Before writing cif - ")

        cifFileName= "%s.cif" % resId
        cifio2.setTableCC(ccTableInp)
        cifio2.loadOeAtomsAndBonds(molS)
        cifio2.setNameCC(acdName)
        cifio2.updateFormalCharge()
        cifio2.updateFormula()				
        ok=cifio2.writeCif(cifFileName)
        if ok:
            cifPathRel=os.path.join(dirPathRel,cifFileName)
            rDict['cifPathRel']=cifPathRel
        #
        #
        pdbFileName = "%s.pdb" % resId
        myops.writePdbFromMol(molS,pdbFileName)		
        pdbPathRel=os.path.join(dirPathRel,pdbFileName)
        rDict['pdbPathRel']=pdbPathRel
        if self.debug: self.lf.write("++INFO - Wrote PDB %s\n" % pdbPathRel)
        #
        #
        #
        # Create an annotated CIF file
        #
        annCifFileName="%s-v3.cif" % resId
        ok = myops.doAnnotateFile(dirPath,cifFileName,annCifFileName,"SWAP")
        if ok:
            annCifPathRel=os.path.join(dirPathRel,annCifFileName)
            rDict['annCifPathRel']= annCifPathRel
        #
        # Create a check report file
        #
        checkCifFileName="%s-check-v3.html" % resId
        ok = myops.doCheckFile(dirPath,annCifFileName,checkCifFileName,version="3")
        if ok:
            checkCifPathRel=os.path.join(dirPathRel,checkCifFileName)
            rDict['checkCifPathRel']= checkCifPathRel
        #
        # Create a report file
        #
        reportFileName="%s-v3.html" % resId
        ok = myops.doReportFile(dirPath,dirPathRel,annCifFileName,reportFileName)
        if ok:
            reportPathRel=os.path.join(dirPathRel,reportFileName)
            rDict['reportPathRel']= reportPathRel
        #

        return rDict


    def reProcessAllAtomComponent(self, inpCifFileName, resId):
        """ Use starting connectivity, bond orders, & charges + hydrogens and recompute everything else...
        This method reprocesses the unannotated all atom component --- 

        Return: dictionary with keys:  id, sdfPathRel, gifPathRel, cifPathRel,
        ismPathRel, pdbPathRel, formula, formal_charge, acdName, annCifPathRel,
        checkCifPathRel, reportPathRel

        """

        # This is the residue unique identifier tied to relative directory location
        # in the session path...
        #
        rDict={}
        rDict['id']=resId
        #
        # -------------------------------------------------------------------------
        # Output files are written in subdirectories in the current session directory
        #
        sessionPath   =self.__ccPath.getPath('sessionPath')
        sessionPathRel=self.__ccPath.getPath('sessionPathRel')
        dirPath    = os.path.join(sessionPath,resId)
        dirPathRel = os.path.join(sessionPathRel,resId)
        #
        if (not os.access(dirPath,os.F_OK)):
            os.mkdir(dirPath)
        os.chdir(dirPath)
        #
        # -------------------------------------------------------------------------
        # read input file build starting molecule
        #
        cifioInp  = ccIo( self.lf,self.debug)			
        ok     = cifioInp.readCif(inpCifFileName)
        oeMol  = cifioInp.getOeMolecule()
        # save the chem_comp category from the input file
        ccTableInp = cifioInp.getTableCC()

        #
        #aroModel=OEAroModelOpenEye
        aroModel=OEAroModelMDL 

        mol = OEGraphMol()
        mol.Clear()

        OEAddMols(mol, oeMol)
        self._molInfo(resId,mol,"Initial molecule")
        OEFindRingAtomsAndBonds(mol)

        #
        # Add the extracted-atom file to the list of files -
        #
        cifExtractFileName= "%s-extract.cif" % resId  			
        cifExtractPathRel=os.path.join(dirPathRel,cifExtractFileName)
        rDict['cifExtractPathRel']=cifExtractPathRel
        #
        # The treatment here depends on whether the molecule has explict hydrogens...
        # 		
        #  no longer use: OEAssignMDLHydrogens(mol)
        #
        #aroModel=OEAroModelOpenEye
        aroModel=OEAroModelMDL 

        if OEHasExplicitHydrogens(mol):
            if self.debug: self.lf.write("++INFO - Using explicit hydrogrens from %s\n" % resId)
            OEAssignAromaticFlags(mol, aroModel)						
            # to recompute h-atoms you need to set h-atom coords to their parents -
            for atom in mol.GetAtoms():
                if ((atom.GetAtomicNum() == 1) and (atom.GetExplicitDegree() == 1)):
                    for neighborAt in atom.GetAtoms():
                        (x,y,z) = mol.GetCoords(neighborAt)
                        mol.SetCoords(atom,(x,y,z))
        else:
            OEAssignMDLHydrogens(mol)			
            self._molInfo(resId,mol,"After implicit hydrogen addition")			
            OEAssignAromaticFlags(mol, aroModel)			
            OEAddExplicitHydrogens(mol)


        OESet3DHydrogenGeom(mol)

        # Make sure any added atoms are properly typed... 
        for atom in mol.GetAtoms():
            atom.SetIntType(atom.GetAtomicNum())
            atom.SetType(OEGetAtomicSymbol(atom.GetAtomicNum()))
        #
        self._molInfo(resId,mol,"After H atom addition molecule")
        OESetDimensionFromCoords(mol)
        OE3DToInternalStereo(mol)
        #
        #
        self._molInfo(resId,mol,"Final molecule before renaming")
        if self.debug: self.lf.write("++INFO - Renaming atoms in %s\n" % resId)
        cifio2 = ccIo(self.lf,self.debug)
        #cifio2.assignHydrogenAtomNames(mol)		
        cifio2.fixHydrogenAtomNames(mol)
        self._molInfo(resId,mol,"Final molecule after renaming")
        #
        # Verify unique atom names ...
        #
        dup = {}
        fCharge = 0		
        for atom in mol.GetAtoms():
            fCharge += atom.GetFormalCharge()		
            if not dup.has_key(atom.GetName()):
                dup[atom.GetName()] = None
            else:
                if self.debug: self.lf.write("++ERROR - Duplicate atom name %s\n" % str(atom.GetName()))
                pass

        rDict['formal_charge']=fCharge
        #
        molFormula = cifio2.makeFormulaFromMol(mol)
        rDict['formula']=molFormula
        #
        molS = OEGraphMol()
        molS.Clear()
        OEAddMols(molS, mol)

        # ------------------------------------------------------------------------
        #  OE molecule is complete and fully named  at this point -
        #
        #
        sdfFileName = "%s.sdf" % resId
        myops.writeSdfFromMol(mol,sdfFileName)
        sdfPathRel=os.path.join(dirPathRel,sdfFileName)
        rDict['sdfPathRel']=sdfPathRel
        if self.debug: self.lf.write("++INFO - Wrote SDF %s\n" % sdfPathRel)
        # 
        ismFileName = "%s.ism" % resId
        myops.writeSmilesFromOeMol(mol,ismFileName)				
        ismPathRel=os.path.join(dirPathRel,ismFileName)
        rDict['ismPathRel']=ismPathRel
        if self.debug: self.lf.write("++INFO - Wrote SMILES %s\n" % ismPathRel)
        #

        myops=ccOps(self.__ccPath,self.lf,self.debug)
        #
        if self.debug: self.lf.write("++INFO - Get ACD name using %s\n" % sdfFileName)
        acdName = myops.getAcdName(sdfFileName)
        rDict['acdName']=acdName		
        #
        if self.debug: self.lf.write("++INFO - make image from SMILES\n")
        gifFileName= "%s-ism.gif" % resId  
        gifFile   = myops.makeGifFromSmiles(ismFileName, gifFileName)
        gifPathRel=os.path.join(dirPathRel,gifFileName)
        rDict['gifPathRel']=gifPathRel

        #
        if self.debug: self.lf.write("++INFO - Writing all atom CIF for %s\n" % resId)
        self._molInfo(resId,mol,"Before writing cif - ")
        cifFileName= "%s.cif" % resId
        cifio2.setTableCC(ccTableInp)
        cifio2.loadOeAtomsAndBonds(molS)
        cifio2.setNameCC(acdName)
        cifio2.updateFormalCharge()
        cifio2.updateFormula()						
        ok=cifio2.writeCif(cifFileName)
        if ok:
            cifPathRel=os.path.join(dirPathRel,cifFileName)
            rDict['cifPathRel']=cifPathRel
        #
        #
        pdbFileName = "%s.pdb" % resId
        myops.writePdbFromMol(mol,pdbFileName)		
        pdbPathRel=os.path.join(dirPathRel,pdbFileName)
        rDict['pdbPathRel']=pdbPathRel
        if self.debug: self.lf.write("++INFO - Wrote PDB %s\n" % pdbPathRel)
        #
        #
        #
        #
        # Create an annotated CIF file
        #
        annCifFileName="%s-v3.cif" % resId
        ok = myops.doAnnotateFile(dirPath,cifFileName,annCifFileName,"SWAP")
        if ok:
            annCifPathRel=os.path.join(dirPathRel,annCifFileName)
            rDict['annCifPathRel']= annCifPathRel
        #
        # Create a check report file
        #
        checkCifFileName="%s-check-v3.html" % resId
        ok = myops.doCheckFile(dirPath,annCifFileName,checkCifFileName,version="3")
        if ok:
            checkCifPathRel=os.path.join(dirPathRel,checkCifFileName)
            rDict['checkCifPathRel']= checkCifPathRel
        #
        # Create a report file
        #
        reportFileName="%s-v3.html" % resId
        ok = myops.doReportFile(dirPath,dirPathRel,annCifFileName,reportFileName)
        if ok:
            reportPathRel=os.path.join(dirPathRel,reportFileName)
            rDict['reportPathRel']= reportPathRel
        #

        return rDict


        
if __name__ == '__main__':
    pass
#
    
