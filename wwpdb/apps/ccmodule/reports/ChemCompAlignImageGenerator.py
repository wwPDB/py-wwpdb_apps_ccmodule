##
# File:  ChemCompAlignImageGenerator.py
# Date:  31-Oct-2014
##
"""
Utility Class for generating aligned ligand images

This software was developed as part of the World Wide Protein Data Bank
Common Deposition and Annotation System Project

Copyright (c) 2012 wwPDB

This software is provided under a Creative Commons Attribution 3.0 Unported
License described at http://creativecommons.org/licenses/by/3.0/.

"""
__docformat__ = "restructuredtext en"
__author__ = "Zukang Feng"
__email__ = "zfeng@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import os
import sys
import traceback

from wwpdb.utils.config.ConfigInfo import ConfigInfo
from wwpdb.utils.dp.RcsbDpUtility import RcsbDpUtility
from wwpdb.io.file.mmCIFUtil import mmCIFUtil
from wwpdb.io.locator.ChemRefPathInfo import ChemRefPathInfo


class ChemCompAlignImageGenerator(object):
    """Utility Class for generating aligned ligand images
    """
    def __init__(self, reqObj=None, verbose=False, log=sys.stderr):
        self.__reqObj = reqObj
        self.__verbose = verbose
        self.__lfh = log
        #
        self.__sObj = self.__reqObj.getSessionObj()
        self.__sessionPath = self.__sObj.getPath()
        #
        self.__imagePath = None

        self.__siteId = str(self.__reqObj.getValue("WWPDB_SITE_ID"))
        self.__cI = ConfigInfo(self.__siteId)
        #
        self.__ccRefPathInfo = ChemRefPathInfo(self.__siteId, verbose=self.__verbose, log=self.__lfh)

    def generateImages(self, instId=None, instFile=None, hitList=None):
        if (not instId) or (not instFile) or (not os.access(instFile, os.F_OK)):
            return
        if hitList is None:
            hitList = []
        #
        self.__imagePath = os.path.join(self.__sessionPath, "assign", instId, "image")
        if not os.access(self.__imagePath, os.F_OK):
            try:
                os.makedirs(self.__imagePath)
            except:  # noqa: E722 pylint: disable=bare-except
                return
            #
        #
        foundList = []
        imageFile = os.path.join(self.__imagePath, "image.txt")
        ofh = open(imageFile, "w")
        ofh.write(instId + " " + instFile + "\n")
        for hitId in hitList:  # pylint: disable=redefined-builtin
            refFile = self.__ccRefPathInfo.getFilePath(str(hitId).upper())
            if not os.access(refFile, os.F_OK):
                continue
            #
            ofh.write(hitId + " " + refFile + "\n")
            #
            alist = []
            alist.append(hitId)
            alist.append(refFile)
            foundList.append(alist)
        #
        ofh.close()
        #
        if foundList:
            try:
                heavyAtomCount = 0
                cifObj = mmCIFUtil(filePath=instFile)
                dlist = cifObj.GetValue("chem_comp_atom")
                for ccDic in dlist:
                    if ("type_symbol" not in ccDic) or (not ccDic["type_symbol"]):
                        continue
                    #
                    type_symbol = ccDic["type_symbol"].upper().strip()
                    if (type_symbol == "H") or (type_symbol == "D"):
                        continue
                    #
                    heavyAtomCount += 1
                #
                # Only generate aligned images for small ligands - DAOTHER-9883 for D_1292143423: TP3 -> A1IZO
                #
                if heavyAtomCount < 100:
                    self.__lfh.write("+ChemCompAlignImageGenerator.generateImages() - Generating images \n")

                    dp = RcsbDpUtility(tmpPath=self.__imagePath, siteId=self.__cI.get("SITE_PREFIX"), verbose=self.__verbose, log=self.__lfh)
                    dp.addInput(name="image_file", value=imageFile)
                    dp.setWorkingDir(self.__imagePath)
                    returnCode = dp.op("chem-comp-align-img-gen")

                    self.__lfh.write("+ChemCompAlignImageGenerator.generateImages() - remote process returned %d \n" % returnCode)

                    if returnCode == 0:
                        FounImage = True
                        imageFile = os.path.join(self.__imagePath, instId + ".svg")
                        if not os.access(imageFile, os.F_OK):
                            FounImage = False
                        #
                        for hitId in hitList:
                            imageFile = os.path.join(self.__imagePath, hitId + ".svg")
                            if not os.access(imageFile, os.F_OK):
                                FounImage = False
                            #
                        #
                        if FounImage:
                            return
                        #
                    #
                #
            except:  # noqa: E722 pylint: disable=bare-except
                if self.__verbose:
                    traceback.print_exc(file=self.__lfh)
                #
            #
        #

        self.__generateSingleImage(Id=instId, FileName=instFile)
        self.__generateSingleImage(Id=instId, FileName=instFile, size=1000, labelAtomName=True, suffix="_Big")
        if foundList:
            for flist in foundList:
                self.__generateSingleImage(Id=flist[0], FileName=flist[1])
                self.__generateSingleImage(Id=flist[0], FileName=flist[1], size=1000, labelAtomName=True, suffix="_Big")
            #
        #

    def __generateSingleImage(self, Id=None, FileName=None, size=300, labelAtomName=False, suffix=""):
        imgPth = os.path.join(self.__imagePath, Id + suffix + ".svg")

        dp = RcsbDpUtility(tmpPath=self.__imagePath, siteId=self.__cI.get("SITE_PREFIX"), verbose=self.__verbose, log=self.__lfh)
        dp.addInput(name="title", value=Id)
        dp.addInput(name="path", value=FileName)
        dp.addInput(name="image_path", value=imgPth)
        dp.addInput(name="size", value=size)
        dp.addInput(name="label", value=labelAtomName)

        return dp.op("chem-comp-gen-images")
        #
