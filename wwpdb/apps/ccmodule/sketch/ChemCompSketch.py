##
# File:  ChemCompSketch.py
# Date:  05-Dec-2012  jdw
# Updates:
#
##
"""
Sketch setup functions  and launcher
"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import os
import sys
import shutil


from wwpdb.apps.ccmodule.utils.ChemCompConfig import ChemCompConfig
from wwpdb.apps.ccmodule.io.ChemCompIo import ChemCompReader
from wwpdb.apps.ccmodule.extract.ccOps import ccOps


class ChemCompSketch(object):
    """Chemical component sketch launcher -

    """
    def __init__(self, reqObj, verbose=False, log=sys.stderr):
        """Chemical component sketch launcher --


         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        self.__verbose = verbose
        self.__lfh = log
        # self.__debug = True
        #
        self.__reqObj = reqObj
        #
        self.__sObj = self.__reqObj.getSessionObj()
        self.__sessionPath = self.__sObj.getPath()
        self.__sessionRelativePath = self.__sObj.getRelativePath()
        self.__sessionId = self.__sObj.getId()
        #
        self.__ccConfig = ChemCompConfig(reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        self.__ccId = None
        self.__ccFilePath = None
        self.__ccFileName = None
        #
        self.__ccFileFormat = None
        #

    def setCcId(self, ccId):
        """Set an existing chemical component identifier in archive collection as
           the sketch target
        """
        self.__ccId = str(ccId.upper())
        return self.__getFilePathFromId(self.__ccId)

    def setFilePath(self, ccFilePath, ccFileFormat='cif', ccId="TMP"):
        self.__ccFilePath = ccFilePath
        self.__ccFileFormat = ccFileFormat
        if (not os.access(self.__ccFilePath, os.R_OK)):
            return False
        self.__ccId = str(ccId).upper()
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
        if (not os.access(self.__ccFilePath, os.R_OK)):
            return False
        self.__ccFileFormat = 'cif'
        return True

    ##
    ##
    def doSketch(self):
        """ Launch sketch applet ---
        """
        #
        retDict = {}
        dirPath = os.path.join(self.__sessionPath, self.__ccId, 'sketch')
        dirRelativePath = os.path.join(self.__sessionRelativePath, self.__ccId, 'sketch')
        #
        # create the sketch path in the session directory
        #
        if (not os.access(dirPath, os.F_OK)):
            try:
                os.makedirs(dirPath)
            except:  # noqa: E722 pylint: disable=bare-except
                return False
        #
        # make a local copy of the file (if required)
        #
        (_pth, fileName) = os.path.split(self.__ccFilePath)
        lclPath = os.path.join(dirPath, fileName)
        if (self.__ccFilePath != lclPath):
            shutil.copyfile(self.__ccFilePath, lclPath)
            #
            if (self.__verbose):
                self.__lfh.write("+ChemCompSketch.doSketch() - Copied input file %s to local path %s \n" %
                                 (self.__ccFilePath, lclPath))
                self.__lfh.flush()
        #
        self.__ccFileName = fileName
        logPath = os.path.join(dirPath, "sketch.log")

        operation = self.__reqObj.getValue("operation")
        sizeXy = self.__reqObj.getValue("sizexy")
        if sizeXy is None or len(sizeXy) < 1:
            sizeXy = 600

        inputFormat = self.__ccFileFormat
        #
        if (self.__verbose):
            self.__lfh.write("+ChemCompSketch.doSketch() directory path  = %s\n" % dirPath)
            self.__lfh.write("+ChemCompSketch.doSketch() target filename = %s\n" % self.__ccFileName)
            self.__lfh.write("+ChemCompSketch.doSketch() file format     = %s\n" % self.__ccFileFormat)
            self.__lfh.write("+ChemCompSketch.doSketch() target id code  = %s\n" % self.__ccId)
            self.__lfh.write("+ChemCompSketch.doSketch() log path        = %s\n" % logPath)
            self.__lfh.write("+ChemCompSketch.doSketch() operation       = %s\n" % operation)
            self.__lfh.write("+ChemCompSketch.doSketch() sizeXy          = %r\n" % sizeXy)
            self.__lfh.write("+ChemCompSketch.doSketch() input format    = %s\n" % inputFormat)
            #
        #  Setup done ---
        #
        tIdCode = self.__ccId
        #
        if (inputFormat == "smiles") :
            smilesInput = self.__reqObj.getValue("smiles")
            #
            tmpFileName = "smiles-input.smi"
            tmpFilePath = os.path.join(dirPath, tmpFileName)
            f = open(tmpFilePath, 'w')
            f.write("%s\n" % smilesInput)
            f.close()
            strMol = '"' + smilesInput + '"'
        elif (inputFormat in ['pdb-babel', 'pdb-bali', 'cif']):
            (tId, strMol) = self.__processInputFile(dirPath, self.__ccFileName, inputFormat)
            if (tId != '__T'):
                tIdCode = tId
        else:
            strMol = ""

        sketchOptions = self.__getSketchFormatOptions(inputFormat)

        retDict = {"ccid": self.__ccId,
                   "sessionid": self.__sessionId,
                   "tid": tIdCode[:3],
                   "inputformat": inputFormat,
                   "filename": self.__ccFileName,
                   "op": operation,
                   "sketchoptions": sketchOptions,
                   "strmol": strMol,
                   "sizexy": sizeXy,
                   "dirRelativePath": dirRelativePath,
                   "loadfromstring": True}

        return retDict
    ##

    def __getSketchFormatOptions(self, inputFormat):
        sketchFormatOps = ""
        if (inputFormat == "pdb-babel"):
            sketchFormatOps = "mol:+Hc-a"
        elif (inputFormat == "pdb-bali"):
            sketchFormatOps = "mol2:+Hc-a"
        elif (inputFormat[:3] == "cif"):
            sketchFormatOps = "mol:+Hc-a"
        elif (inputFormat == "smiles"):
            sketchFormatOps = "smiles"
        else:
            pass

        return sketchFormatOps

    def __getChemCompInfo(self, cifPath):
        ccDict = {}
        ccDict['id'] = None
        if os.path.exists(cifPath):
            ccf = ChemCompReader(verbose=self.__verbose, log=self.__lfh)
            # ccf.setFilePath(cifPath,compId=self.__ccId)
            ccf.setFilePath(cifPath, compId=None)
            ccD = ccf.getChemCompDict()
            if (self.__verbose):
                for k, v in ccD.items():
                    self.__lfh.write("+ChemCompSketch.__getChemCompInfo() key %20s  value %s\n" % (k, v))
            #
            # Mapping only - id here
            ccDict['id'] = ccD['_chem_comp.id']

        return ccDict

    def __processInputFile(self, dirPath, fileName, inputFormat):
        """  Convert input file to MOL format.

             JDW -  This will be adjusted later to according to wwPDB system requirements --
                    For now this is working fine for convering PDBx/mmCIF definitions to MOL/SDF
                    in a manner that Marvin can accept.

             Return:

             Tuple of idCode and data file in MOL format as a string with punctuation for Marvin Sketch

        """
        tIdCode = "__T"
        if (self.__verbose):
            self.__lfh.write("+ChemCompSketch.__processInputFile() dirPath %s fileName %s inputFormat %s\n"
                             % (dirPath, fileName, inputFormat))
        # ---------------
        #
        #
        # Some format conversions here  (pdb & cif  -> sdf)
        #
        if (inputFormat == "pdb-babel"):
            tMolFileName = fileName + "-babel.sdf"
            myops = ccOps(self.__ccConfig, self.__lfh, self.__verbose)
            myops.doPdb2MolBabel(dirPath, fileName, tMolFileName)
        elif (inputFormat == "pdb-bali"):
            tMolFileName = fileName + "-bali.mol2"
            myops = ccOps(self.__ccConfig, self.__lfh, self.__verbose)
            myops.doPdb2MolBali(dirPath, fileName, tMolFileName)
        elif (inputFormat[:3] == "cif"):
            # copy file not sure why -
            fp = os.path.join(dirPath, fileName)
            fpCopy = os.path.join(dirPath, "reference-sketch.cif")
            shutil.copyfile(fp, fpCopy)

            ccD = self.__getChemCompInfo(fp)
            if ccD['id'] is not None:
                tIdCode = ccD['id']
            tMolFileName = fileName + ".sdf"
            myops = ccOps(self.__ccConfig, self.__lfh, self.__verbose)
            myops.doCif2Mol(dirPath, fileName, tMolFileName)

        #
        # String-ify the mol file -
        #
        f = open(tMolFileName, 'r')
        lines = f.readlines()
        f.close()
        strMol = ""
        for line in lines[:-2]:
            strMol += '"' + line[:-1] + '\\n"+' + '\n'
            # tStr += t

        strMol += '"M END"'
        #
        return (tIdCode, strMol)
