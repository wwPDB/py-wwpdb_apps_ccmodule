##
# File:  ChemCompBigAlignImages.py
# Date:  31-Oct-2014
# Updates:
#
"""
Helper class for generating 2D images that are aligned to same orientation

This software was developed as part of the World Wide Protein Data Bank
Common Deposition and Annotation System Project

Copyright (c) 2014 wwPDB

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
import time
import traceback
#
from wwpdb.utils.oe_util.oedepict.OeAlignDepictUtils import OeDepictMCSAlignSingle


class ChemCompBigAlignImages(object):
    def __init__(self, inputFile=None):
        self.__inputFile = inputFile
        self.__inputList = []
        self.__parseFile()

    def generateImage(self):
        if not self.__inputList:
            return
        #
        self.__generateImage()
        self.__generateImage(size=1000, labelAtomName=True, suffix='_Big')

    def __parseFile(self):
        if not os.access(self.__inputFile, os.R_OK):
            return
        #
        f = open(self.__inputFile, 'r')
        data = f.read()
        f.close()
        #
        slist = data.split('\n')
        for line in slist:
            if not line:
                continue
            #
            list1 = line.split(' ')
            self.__inputList.append(list1)
        #

    def __generateImage(self, size=300, labelAtomName=False, suffix=''):
        sys.stdout.write("Starting at %s\n" % time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        try:
            oed = OeDepictMCSAlignSingle(verbose=True, log=sys.stdout)
            # using 'inverse' display options
            oed.setDisplayOptions(imageSizeX=size, imageSizeY=size, labelAtomName=labelAtomName, labelAtomCIPStereo=True,
                                  labelAtomIndex=False, labelBondIndex=False, highlightStyleFit='ballAndStickInverse',
                                  bondDisplayWidth=1.0)
            oed.setRefPath(self.__inputList[0][0], self.__inputList[0][1], title='', imagePath=self.__inputList[0][0] + suffix + '.svg')
            for slist in self.__inputList[1:]:
                oed.addFitPath(slist[0], slist[1], title='', imagePath=slist[0] + suffix + '.svg')
            #
            oed.alignOneWithList()
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=sys.stdout)
        #
        sys.stdout.write("Completed at %s\n" % time.strftime("%Y %m %d %H:%M:%S", time.localtime()))


def main(argv):
    ccbai = ChemCompBigAlignImages(argv[0])
    ccbai.generateImage()


if __name__ == "__main__":
    main(sys.argv[1:])
