"""
File:  ccOps.py

       Class provides wrappers around a variety of common cc operations -

Update: 2007-10-07 stripped this out of the extractor  to facilitate reuse.

Updated: 2009-06-08 - repoint acd namebat.

"""

import os
import os.path
# from openeye.oechem import *


class ccOps:
    def __init__(self, ccPath, lfh=None, debug=False):
        self.debug = debug
        self.lf = lfh
        self.__ccPath = ccPath

    def doCif2Mol(self, dirPath, cifFile, molFile):

        logPath = "cif2mol.log"

        cmd = "cd " + dirPath + " ; " + self.__ccPath.getPath("cif2sdf") + " -i " + \
            cifFile + " -o " + molFile + " -type model  > " + logPath + " 2>&1"

        if self.debug:
            self.lf.write("+doCif2Mol()\n")
            self.lf.write("Working directory path   = %s\n" % dirPath)
            self.lf.write("Target filename          = %s\n" % cifFile)
            self.lf.write("Mol path                 = %s\n" % molFile)
            self.lf.write("Log    path              = %s\n" % logPath)
            self.lf.write("Command                  = %s\n" % cmd)

        os.system(cmd)
        #
        outPath = os.path.join(dirPath, molFile)

        if os.path.exists(outPath):
            return True
        else:
            return False

    def doPdb2MolBali(self, dirPath, pdbFile, molFile):

        logPath = "bali.log"

        cmd = "cd " + dirPath + " ; " + self.__ccPath.getPath("bali") + " " + \
            pdbFile + " " + molFile + " > " + logPath + " 2>&1"

        if (self.debug):
            self.lf.write("Beginning report in path = %s\n" % dirPath)
            self.lf.write("Target filename          = %s\n" % pdbFile)
            self.lf.write("Mol path                 = %s\n" % molFile)
            self.lf.write("Log    path              = %s\n" % logPath)
            self.lf.write("Command                  = %s\n" % cmd)

        os.system(cmd)
        outPath = os.path.join(dirPath, molFile)
        #
        if os.path.exists(outPath):
            return True
        else:
            return False

    def doPdb2MolBabel(self, dirPath, pdbFile, molFile, opts=""):
        # Invoked from ChemCompSketch

        logPath = "babel.log"

        cmd = "cd " + dirPath + " ; " + self.__ccPath.getPath("babel") + " -ipdb " + \
            pdbFile + " -omol " + molFile + " " + opts + " > " + logPath + " 2>&1"

        if (self.debug):
            self.lf.write("Beginning report in path = %s\n" % dirPath)
            self.lf.write("Target filename          = %s\n" % pdbFile)
            self.lf.write("Mol path                 = %s\n" % molFile)
            self.lf.write("Log    path              = %s\n" % logPath)
            self.lf.write("Command                  = %s\n" % cmd)

        os.system(cmd)
        outPath = os.path.join(dirPath, molFile)
        #
        if os.path.exists(outPath):
            return True
        else:
            return False
        ##
