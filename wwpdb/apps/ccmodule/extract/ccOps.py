"""
File:  ccOps.py

       Class provides wrappers around a variety of common cc operations -

Update: 2007-10-07 stripped this out of the extractor  to facilitate reuse.

Updated: 2009-06-08 - repoint acd namebat.

"""

import os, os.path
from openeye.oechem import *


class ccOps:	
	def __init__(self, ccPath, lfh=None, debug=False):
		self.debug   = debug
		self.lf      = lfh
		self.__ccPath = ccPath

	def writeSdfFromMol(self, mol, sdfFileName):
		ofs = oemolostream()
		ofs.open(sdfFileName)
		OEWriteMolecule(ofs, mol)
		ofs.close()

	def writePdbFromMol(self, mol, pdbFileName):
		#
		ofs = oemolostream()		
		ofs.open(pdbFileName)
		OEWriteMolecule(ofs, mol)
		ofs.close()


	def getOeMolFromFile(self, inpFileName): 
		""" Returns an OE molecule object that represents the input file.
		"""
		#
		ifs = oemolistream()
		#
		# inpFileName must have a extension that OE recognizes
		#
		if (ifs.open(inpFileName) != 1):
			if self.debug:	self.lf.write("Could not open the input file %s\n" % inpFileName)
		else:
			mol = OEGraphMol()
			OEReadMolecule(ifs, mol)
			# Make sure any added atoms are properly typed... 
			for atom in mol.GetAtoms():
				atom.SetIntType(atom.GetAtomicNum())
				atom.SetType(OEGetAtomicSymbol(atom.GetAtomicNum()))
			OETriposAtomNames(mol)
			return mol


	def writeSmilesFromOeMol(self, mol, ismFileName):
		ism = OECreateIsoSmiString(mol)
		f=open(ismFileName, "w")
		f.write(ism)
		f.close()


	def writeOeMol(self, oeMol, outFile): 
		""" Write the OE molecule object 
		"""
		#
		if self.debug:	self.lf.write("++INFO - writing OE molecule to %s\n" % outFile)		
		ofs = oemolostream()
		#
		# outFile must have a recogized file extension (sdf,mol,pdb,mol2...)
		#
		if (ofs.open(outFile) != 1):
			if self.debug:	self.lf.write("++ERROR - Could not open the output file %s\n" % outFile)
			return False
		else:
			OEWriteMolecule(ofs, oeMol)
			ofs.close()
			return True

		
	def doAnnotateFile(self,dirPath, inpFile, outFile, swap):
		""" In the current working directory ---
		"""
		logPath= "annotate.log"
		if (self.debug):
			self.lf.write("SWAP is  = %s\n" % str(swap).upper())			
		
		if str(swap).upper() == "SWAP":
			cmd = self.__ccPath.getPath("annotateFileScript") + " " + \
			      self.__ccPath.getPath("binPath") + " " + dirPath + " " + inpFile + \
			      " " + outFile + " SWAP > " + logPath + " 2>&1"
		else:
			cmd = self.__ccPath.getPath("annotateFileScript") + " " + \
			      self.__ccPath.getPath("binPath") + " " + dirPath + " " + inpFile + \
			      " " + outFile + " > " + logPath + " 2>&1"
		if (self.debug):
			self.lf.write("Beginning annotation in  = %s\n" % dirPath)	
			self.lf.write("Target filename          = %s\n" % inpFile)
			self.lf.write("Output filename          = %s\n" % outFile)
			self.lf.write("Swap option              = %s\n" % str(swap))			      			
			self.lf.write("Log    path              = %s\n" % logPath)	
			self.lf.write("Annotate command         = %s\n" % cmd)
            
		os.system(cmd)
		outPath  = os.path.join(dirPath,outFile)        
		if os.path.exists(outPath):
			return True
		else:
			return False

	def doAlignAtomNames(self,dirPath,inpCifFile,refCifFile,outCifFile,op):

		logPath      = "alignNames.log"
		if (op == "heavy"):
			myOpt=" -skipH "
		else:
			myOpt=" -op special "
		#
		cmd = self.__ccPath.getPath("alignComp") + "  -renameAltId -i " + \
		      inpCifFile + " -or " + outCifFile +  " -ref " + refCifFile +  \
		      " -om mapping-em.out " + myOpt + " > " + logPath + " 2>&1"

		if (self.debug):
			self.lf.write("Beginning align  in path = %s\n" % dirPath)	
			self.lf.write("Target filename          = %s\n" % inpCifFile)
			self.lf.write("Reference filename       = %s\n" % refCifFile)
			self.lf.write("Output filename          = %s\n" % outCifFile)			
			self.lf.write("Log path                 = %s\n" % logPath)
			self.lf.write("Command                  = %s\n" % cmd)

		os.chdir(dirPath)			

		os.system(cmd)
		outPath  = os.path.join(dirPath,outCifFile)
		#
		if os.path.exists(outPath):
			return True
		else:
			return False		


	def doCif2Mol(self,dirPath,cifFile,molFile):

		logPath      = "cif2mol.log"

		cmd = self.__ccPath.getPath("cif2sdf") + " -i " + \
		      cifFile + " -o " + molFile +  " -type model  > " + logPath + " 2>&1"

		if (self.debug):
			self.lf.write("+doCif2Mol()\n")
			self.lf.write("Working directory path   = %s\n" % dirPath)	
			self.lf.write("Target filename          = %s\n" % cifFile)
			self.lf.write("Mol path                 = %s\n" % molFile)
			self.lf.write("Log    path              = %s\n" % logPath)
			self.lf.write("Command                  = %s\n" % cmd)

		os.chdir(dirPath)			

		os.system(cmd)
		outPath  = os.path.join(dirPath,molFile)
		#
		if os.path.exists(outPath):
			return True
		else:
			return False		

	def doPdb2MolBali(self,dirPath,pdbFile,molFile):

		logPath      = "bali.log"

		
		cmd = self.__ccPath.getPath("bali") + " " + \
		      pdbFile + " " + molFile +  " > " + logPath + " 2>&1"

		if (self.debug):
			self.lf.write("Beginning report in path = %s\n" % dirPath)	
			self.lf.write("Target filename          = %s\n" % pdbFile)
			self.lf.write("Mol path                 = %s\n" % molFile)
			self.lf.write("Log    path              = %s\n" % logPath)
			self.lf.write("Command                  = %s\n" % cmd)

		os.chdir(dirPath)			

		os.system(cmd)
		outPath  = os.path.join(dirPath,molFile)
		#
		if os.path.exists(outPath):
			return True
		else:
			return False		

	def doPdb2MolBabel(self,dirPath,pdbFile,molFile,opts=""):

		logPath      = "babel.log"

		
		cmd = self.__ccPath.getPath("babel") + " -ipdb " + \
		      pdbFile + " -omol " + molFile +  " " + opts + " > " + logPath + " 2>&1"

		if (self.debug):
			self.lf.write("Beginning report in path = %s\n" % dirPath)	
			self.lf.write("Target filename          = %s\n" % pdbFile)
			self.lf.write("Mol path                 = %s\n" % molFile)
			self.lf.write("Log    path              = %s\n" % logPath)
			self.lf.write("Command                  = %s\n" % cmd)

		os.chdir(dirPath)			

		os.system(cmd)
		outPath  = os.path.join(dirPath,molFile)
		#
		if os.path.exists(outPath):
			return True
		else:
			return False		


	def doCheckFile(self,dirPath,inpFile,checkFile,version="3"):

		logPath      = "check.log"
        
		cmd = self.__ccPath.getPath("checkFileScript") + " " + \
		      self.__ccPath.getPath("binPath") + " " +  dirPath + " " + inpFile + \
		      " " + checkFile + " " + version + " > " + logPath + " 2>&1"

		if (self.debug):
			self.lf.write("Beginning report in path = %s\n" % dirPath)	
			self.lf.write("Target filename          = %s\n" % inpFile)
			self.lf.write("Check path               = %s\n" % checkFile)
			self.lf.write("Log    path              = %s\n" % logPath)
			self.lf.write("Check command            = %s\n" % cmd)
			
		os.system(cmd)
		outPath  = os.path.join(dirPath,checkFile)        
		#
		if os.path.exists(outPath):
			return True
		else:
			return False		

	def doReportFile(self, dirPath, dirPathRel, inpFile, reportFile):
		""" 
		"""
		reportFilePath = os.path.join(dirPath,reportFile)
		logPath        = os.path.join(dirPath,"report.log")

		cmd = self.__ccPath.getPath("reportFileScript") + " " + \
		      self.__ccPath.getPath("binPath") + " " + dirPath + " " + inpFile + \
		      " " + dirPathRel + " " + reportFile + " > " + logPath + " 2>&1"

		if (self.debug):
			self.lf.write("Beginning report in path = %s\n" % dirPath)	
			self.lf.write("Target filename          = %s\n" % inpFile)
			self.lf.write("Report filename          = %s\n" % reportFile)
			self.lf.write("Log    path              = %s\n" % logPath)
			self.lf.write("Session relative path    = %s\n" % dirPathRel)	            
			self.lf.write("Report command           = %s\n" % cmd)
			self.lf.flush()
		os.system(cmd)

		if os.path.exists(reportFilePath):            
			return True
		else:
			return False

	def makeGifFromSmiles(self,smilesFileName,gifFileName):
		cmd = self.__ccPath.getPath("mol2gif") + \
		      " -width 300 -height 300 %s %s " % (smilesFileName, gifFileName)
		os.system(cmd)
		return True

	def getAcdName(self, filename):
		"""  Input is SDF file name in current directory
			Returns iupac name - 
		""" 
		ofn=filename + ".txt"
		if os.path.exists(ofn):
			os.remove(ofn)
		cmdLine = self.__ccPath.getPath("acdName")  \
			  + " " + filename + " " + ofn + "  -CALCIUP -STEREO -CALCSM  -IUPPREF31=1"
		if self.debug: self.lf.write("++INFO - Running %s\n" % cmdLine)
		os.system(cmdLine)
		#
		iupacname=""
		if os.path.exists(ofn):
			f = open(ofn, "r")
			iupacname = f.readline()[2:].strip()
			f.close()
		else:
			if self.debug: self.lf.write("++ERROR - ACD naming failed\n")
		if ((iupacname.find("disallowed") > 0) or
		    (iupacname.find("not supported") > 0) or 
		    (iupacname.find("current version") > 0)):		    
			return "?"
		else:
			return iupacname


##
		
