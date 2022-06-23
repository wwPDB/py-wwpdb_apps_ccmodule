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
__author__    = "Zukang Feng"
__email__     = "zfeng@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.01"

import os, sys

from wwpdb.utils.config.ConfigInfo import ConfigInfo
from wwpdb.utils.config.ConfigInfoApp import ConfigInfoAppCommon
from wwpdb.utils.dp.RcsbDpUtility                       import RcsbDpUtility
from wwpdb.io.locator.ChemRefPathInfo     import ChemRefPathInfo
from wwpdb.io.locator.PathInfo                               import PathInfo

from wwpdb.apps.ccmodule.reports.ChemCompBigAlignImages import ChemCompBigAlignImages
from wwpdb.utils.oe_util.oedepict.OeDepict            import OeDepict
from wwpdb.utils.oe_util.build.OeChemCompIoUtils      import OeChemCompIoUtils
#

class ChemCompAlignImageGenerator(object):
    """Utility Class for generating aligned ligand images
    """
    def __init__(self, reqObj=None, verbose=False, log=sys.stderr, runLocal=False):
        """
            runLocal: runs image generation code on local machine instead of using
                the WFE. This should be used only when generating single images
        """
        self.__reqObj=reqObj
        self.__verbose=verbose
        self.__lfh=log
        self.__runLocal=runLocal
        #
        self.__sObj=self.__reqObj.getSessionObj()
        self.__sessionPath=self.__sObj.getPath()
        #
        self.__siteId = str(self.__reqObj.getValue("WWPDB_SITE_ID"))
        self.__cI = ConfigInfo(self.__siteId)
        self.__cICommon = ConfigInfoAppCommon(self.__siteId)
        #
        self.__ccRefPathInfo = ChemRefPathInfo(configObj=self.__cI, configCommonObj=self.__cICommon,
                                               verbose=self.__verbose, log=self.__lfh)

    def generateImages(self, instId=None, instFile=None, hitList=[], isWorkflow=False):
        if (not instId) or (not instFile):
            return
        #
        if not isWorkflow:
            self.__imagePath = os.path.join(self.__sessionPath, 'assign', instId, 'image')
        else:
            instancePath = PathInfo().getInstancePath(self.__reqObj.getValue('identifier'), self.__reqObj.getValue('instance'))
            self.__imagePath = os.path.join(instancePath, 'cc_analysis', instId, 'image')
        if not os.access(self.__imagePath, os.F_OK):
            try:
                os.makedirs(self.__imagePath)
            except:
                return
            #
        #
        foundList = []
        imageFile = os.path.join(self.__imagePath, 'image.txt')
        ofh = open(imageFile, 'w')
        ofh.write(instId + ' ' + instFile + '\n')
        for id in hitList:
            refFile = self.__ccRefPathInfo.getFilePath(str(id).upper())
            if not os.access(refFile, os.F_OK):
                continue
            #
            ofh.write(id + ' ' + refFile + '\n')
            #
            list = []
            list.append(id)
            list.append(refFile)
            foundList.append(list)
        #
        ofh.close()
        #
        if foundList:
            self.__lfh.write('+ChemCompAlignImageGenerator.generateImages() - Generating images \n')

            if not self.__runLocal:
                dp = RcsbDpUtility(tmpPath=self.__imagePath, siteId=self.__cI.get('SITE_PREFIX'), verbose=self.__verbose, log=self.__lfh)
                dp.addInput(name='image_file', value=imageFile)
                dp.setWorkingDir(self.__imagePath)
                returnCode = dp.op('chem-comp-align-img-gen')
                # dp.cleanup()
            else:
                ccbai = ChemCompBigAlignImages(imageFile)
                ccbai.generateImage()
                returnCode = 0

            self.__lfh.write('+ChemCompAlignImageGenerator.generateImages() - remote process returned %d \n' % returnCode)

            if returnCode == 0:
                FounImage = True
                imageFile = os.path.join(self.__imagePath, instId + '.svg')
                if not os.access(imageFile, os.F_OK):
                    FounImage = False
                #
                for id in hitList:
                    imageFile = os.path.join(self.__imagePath, id  + '.svg')
                    if not os.access(imageFile, os.F_OK):
                        FounImage = False
                    #
                #
                if FounImage:
                    return
                #
            #
        #

        self.__generateSingleImage(Id=instId, FileName=instFile)
        self.__generateSingleImage(Id=instId, FileName=instFile, size=1000, labelAtomName=True, suffix='_Big')
        if foundList:
            for list in foundList:
                self.__generateSingleImage(Id=list[0], FileName=list[1])
                self.__generateSingleImage(Id=list[0], FileName=list[1], size=1000, labelAtomName=True, suffix='_Big')
                #
            #
        #

    def __generateSingleImage(self, Id=None, FileName=None, size=300, labelAtomName=False, suffix=''):
        imgPth = os.path.join(self.__imagePath, Id + suffix + '.svg')

        if not self.__runLocal:
            dp = RcsbDpUtility(tmpPath=self.__imagePath, siteId=self.__cI.get('SITE_PREFIX'), verbose=self.__verbose, log=self.__lfh)
            dp.addInput(name="title", value=Id)
            dp.addInput(name="path", value=FileName)
            dp.addInput(name="image_path", value=imgPth)
            dp.addInput(name="size", value=size)
            dp.addInput(name="label", value=labelAtomName)
            
            retStatus = dp.op("chem-comp-gen-images")
            # dp.cleanup()
            return retStatus
        else:
            if( os.access(FileName,os.R_OK) ):
                try:
                    #
                    oeU=OeChemCompIoUtils(verbose=True,log=sys.stdout)
                    oemList=oeU.getFromPathList([FileName],use3D=True,coordType='model')
                    oed=OeDepict(verbose=True,log=sys.stdout)
                    oedInputTupl = (Id,oemList[0],"")
                    oed.setMolTitleList([oedInputTupl])
                    oed.setDisplayOptions(imageSizeX=size,imageSizeY=size,labelAtomName=labelAtomName,labelAtomCIPStereo=True,
                                        labelAtomIndex=False,labelBondIndex=False,
                                        highlightStyleFit='ballAndStickInverse',
                                        bondDisplayWidth=1.0)
                    oed.setGridOptions(rows=1,cols=1,cellBorders=False)
                    oed.prepare()
                    oed.write(imgPth)
                
                except Exception as e:
                    self.__lfh.write('+ChemCompAlignImageGenerator.generateImages() - error generating images: %s \n' % e)

            else:      
                return -1
        #
