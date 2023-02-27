##
# File:  ChemCompAlignImages.py
# Date:  20-Jan-2014
# Updates:
#
"""
Helper script for using oe_util.oedepict.OeAlignDepictUtils to generate 2D images that are aligned to same orientation,
Written to allow image generation task to be run as command line operation and subjected to timeout constraints.

This software was developed as part of the World Wide Protein Data Bank
Common Deposition and Annotation System Project

Copyright (c) 2016 wwPDB

This software is provided under a Creative Commons Attribution 3.0 Unported
License described at http://creativecommons.org/licenses/by/3.0/.

This is invoked from RcsbDpUtility

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
from wwpdb.utils.oe_util.oedepict.OeAlignDepictUtils import OeDepictMCSAlignSingle
# from wwpdb.utils.oe_util.oedepict.OeDepict import OeDepict
# from wwpdb.utils.oe_util.build.OeChemCompIoUtils import OeChemCompIoUtils


def usage():
    sys.stderr.write("usage: %s -i <ccid> -f <fileListPath> -v (verbose)\n" % str(sys.argv[0]).split('/')[-1])


def main(argv):

    # cmd="all"
    vrbs = False
    ccid = filePth = ""

    try:
        opts, _args = getopt.getopt(argv, "hi:f:v", ["help", "id=", "filepath=", "verbose"])

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

        elif opt in ("-v", "--verbose"):
            vrbs = True

        else:
            usage()
            sys.exit(1)

    lt = time.strftime("%Y %m %d %H:%M:%S", time.localtime())
    sys.stdout.write("Starting %s at %s\n" % (str(sys.argv[0]).split('/')[-1], lt))
    #
    if os.access(filePth, os.R_OK):
        try:
            ifh = open(filePth, 'r')

            masterId = masterDefPath = masterImgPath = ""
            alignLst = []
            thisAlignRef = None
            for line in ifh:
                if 'ASSIGN_PATH' in line:
                    assignPath = (line.split(":")[1]).strip()
                    ofh = open(os.path.join(assignPath, 'ChemCompAlignImages_' + ccid + '.log'), 'w')
                    ofh.write('Assign Path is: %s\n' % assignPath)
                    if vrbs:
                        sys.stdout.write("+ChemCompAlignImages -- assign path identified as: %s\n" % assignPath)
                elif 'MASTER_ID' in line:
                    masterId = (line.split(":")[1]).strip()
                elif 'MASTER_DEF_PTH' in line:
                    masterDefPath = (line.split(":")[1]).strip()
                elif 'MASTER_IMG_PTH' in line:
                    masterImgPath = (line.split(":")[1]).strip()
                elif 'ALIGN_ID' in line:
                    thisAlignRef = []
                    thisAlignRef.append((line.split(":")[1]).strip())
                elif 'ALIGN_DEF_PTH' in line:
                    thisAlignRef.append((line.split(":")[1]).strip())
                elif 'ALIGN_IMG_PTH' in line:
                    thisAlignRef.append((line.split(":")[1]).strip())
                    alignLst.append(thisAlignRef)

            ofh.write("masterId -> %s | masterDefPath -> %s | masterImgPath -> %s\n" % (masterId, masterDefPath, masterImgPath))
            ofh.write("alignLst is %r\n" % alignLst)

            ifh.close()
            ofh.close()

            sys.stdout.write("masterId -> %s | masterDefPath -> %s | masterImgPath -> %s\n" % (masterId, masterDefPath, masterImgPath))
            sys.stdout.write("alignLst is %r \n" % alignLst)

            oed = OeDepictMCSAlignSingle(verbose=vrbs, log=sys.stdout)
            # using 'inverse' display options
            oed.setDisplayOptions(imageSizeX=300, imageSizeY=300, labelAtomName=False, labelAtomCIPStereo=True,
                                  labelAtomIndex=False, labelBondIndex=False,
                                  highlightStyleFit='ballAndStickInverse',
                                  bondDisplayWidth=1.0)

            oed.setRefPath(masterId, masterDefPath, title="", imagePath=masterImgPath)
            for record in alignLst:
                oed.addFitPath(record[0], record[1], title="", imagePath=record[2])

            _aML = oed.alignOneWithList()  # noqa: F841

        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=sys.stdout)

    else:
        usage()
        sys.exit(1)

    lt = time.strftime("%Y %m %d %H:%M:%S", time.localtime())
    sys.stdout.write("Completed %s at %s\n" % (str(sys.argv[0]).split('/')[-1], lt))


if __name__ == "__main__":
    main(sys.argv[1:])
