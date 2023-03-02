##
# File:  ChemCompGenImage.py
# Date:  29-Apr-2016
# Updates:
#
"""
Helper script for generating 2D image of given chem component using oe_util.oedepict.OeAlignDepictUtils
Written to allow image generation task to be run as command line operation and subjected to timeout constraints.

This software was developed as part of the World Wide Protein Data Bank
Common Deposition and Annotation System Project

Copyright (c) 2016 wwPDB

This software is provided under a Creative Commons Attribution 3.0 Unported
License described at http://creativecommons.org/licenses/by/3.0/.

"""
__docformat__ = "restructuredtext en"
__author__ = "Raul Sala"
__email__ = "rsala@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import os
import sys
import getopt
import time
import traceback
#
from wwpdb.utils.oe_util.oedepict.OeDepict import OeDepict
from wwpdb.utils.oe_util.build.OeChemCompIoUtils import OeChemCompIoUtils


def usage():
    sys.stderr.write("usage: %s -i <ccid> -f <filePath> -o <outputPath> -v (verbose)\n" % str(sys.argv[0]).split('/')[-1])


def main(argv):

    # cmd="all"
    vrbs = False
    size = 300
    labelAtomName = False
    ccid = filePth = outputPth = ""

    try:
        opts, _args = getopt.getopt(argv, "hi:f:o:v", ["help", "id=", "filepath=", "outputpath=", "verbose", "label=", "size="])

    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()

        elif opt in ("-i", "--ccid"):
            ccid = arg

        elif opt in ("-f", "--filepath"):
            filePth = arg

        elif opt in ("-o", "--outputpath"):
            outputPth = arg

        elif opt in ("-v", "--verbose"):
            vrbs = True

        elif opt in ("--label"):
            labelAtomName = True if arg.lower() == 'true' else False

        elif opt in ("--size"):
            size = int(arg)

        else:
            usage()
            sys.exit(1)

    lt = time.strftime("%Y %m %d %H:%M:%S", time.localtime())
    sys.stdout.write("Starting %s at %s\n" % (str(sys.argv[0]).split('/')[-1], lt))
    #
    if os.access(filePth, os.R_OK):
        try:
            #
            oeU = OeChemCompIoUtils(verbose=vrbs, log=sys.stdout)
            oemList = oeU.getFromPathList([filePth], use3D=True, coordType='model')
            oed = OeDepict(verbose=vrbs, log=sys.stdout)
            oedInputTupl = (ccid, oemList[0], "")
            oed.setMolTitleList([oedInputTupl])
            oed.setDisplayOptions(imageSizeX=size, imageSizeY=size, labelAtomName=labelAtomName, labelAtomCIPStereo=True,
                                  labelAtomIndex=False, labelBondIndex=False,
                                  highlightStyleFit='ballAndStickInverse',
                                  bondDisplayWidth=1.0)
            oed.setGridOptions(rows=1, cols=1, cellBorders=False)
            oed.prepare()
            oed.write(outputPth)

        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=sys.stdout)

    else:
        usage()
        sys.exit(1)

    lt = time.strftime("%Y %m %d %H:%M:%S", time.localtime())
    sys.stdout.write("Completed %s at %s\n" % (str(sys.argv[0]).split('/')[-1], lt))


if __name__ == "__main__":
    main(sys.argv[1:])
