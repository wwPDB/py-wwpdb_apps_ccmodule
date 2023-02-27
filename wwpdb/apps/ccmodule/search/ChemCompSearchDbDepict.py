##
# File:  ChemCompSearchDbDepict.py
# Date:  06-Aug-2010
# Updates:
# ---------------------------------------------------------------------------
# 2011-05-12  RPS  Piloting changes to doRender() for standalone Ligand Editor Tool
#
##
"""
Create HTML depiction for simple chemical component database search

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import sys
from wwpdb.apps.ccmodule.depict.ChemCompDepict import ChemCompDepict


class ChemCompSearchDbDepict(ChemCompDepict):
    """Create HTML depiction for chemical component database searches.

    """
    def __init__(self, verbose=False, log=sys.stderr):
        """

         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        super(ChemCompSearchDbDepict, self).__init__(verbose, log)
        # self.__verbose = verbose
        # self.__lfh = log
        # self.__debug = True
        #
        #

    def doRender(self, d=None):
        ''' Render in HTML
        '''
        if d is None:
            d = {}
        oL = []
        oL.append(self._pragma)
        oL.append('<html>')
        oL.append(self._header % 'Chemical Component Database Search')
        oL.append('<body class="oneColLiqCtrHdr">')
        oL.append(self._menuCommonInclude)
        #
        oL.append('<h1>Database Search Result Summary</h1>')
        oL.append('<p>')
        # '''
        # oL.append('<table>')
        # oL.append('<tr><td><b>Target ID:</b></td><td>%s</td></tr>' % d['targetid'])
        # oL.append('<tr><td><b>Count in released entries:</b></td><td>%r</td></tr>' % d['count'])
        # oL.append('<tr><td><b>Count in other entries:</b></td><td>%r</td></tr>' %   d['countother'])
        # oL.append('</table>')
        # '''
        oL.append('<div>')
        oL.append('<table style="width: 25%">')
        oL.append('<tr><th>Target ID:</th><td>%s</td></tr>' % d['targetid'])
        oL.append('<tr><th>Count in released entries:</th><td>%s</td></tr>' % d['count'])
        oL.append('<tr><th>Count in unreleased entries:</th><td>%s</td></tr>' % d['countother'])
        oL.append('</table>')
        oL.append('</div>')
        #
        if d['searchOp'] == "LIKE":
            oL.append('<h2>Instances like %s  in Released Entries</h2>' % d['targetid'])
        else:
            oL.append('<h2>Instances of %s in Released Entries</h2>' % d['targetid'])
        #
        oL.append('<table class="rs1">')
        oL.append('<tr>')
        oL.append('	<th class="rs1">PDB ID</th>')
        oL.append('	<th class="rs1">DEP DATASET ID</th>')
        oL.append('	<th class="rs1">CC ID</th>')
        oL.append('	<th class="rs1">Status</th>')
        oL.append('	<th class="rs1">Method</th>')
        oL.append('	<th class="rs1">Title</th>')
        oL.append('	<th class="rs1">Release Date</th>')
        oL.append('</tr>')
        #
        # row data -
        #
        i = 0
        for result in d['resultlist']:
            i += 1
            if (i % 2) == 0:
                trcls = "rs1-even"
            else:
                trcls = "rs1-odd"

            oL.append('<tr class="%s">' % trcls)
            oL.append('          <td class="rs1" nowrap="nowrap">%s ( <a target="_blank" href="https://www.ebi.ac.uk/pdbe-srv/view/entry/%s/summary.html" title="View at PDBe">E</a> | <a target="_blank" href="http://service.pdbj.org/mine/Detail?PDBID=%s&PAGEID=Summary" title="View at PDBj">J</a> | <a target="_blank" href="http://www.rcsb.org/pdb/explore/explore.do?structureId=%s" title="View at RCSB PDB">R</a> )</td>' %  # noqa: E501
                      (result['pdbId'], result['pdbId'], result['pdbId'], result['pdbId']))
            oL.append('          <td class="rs1">%s</td>' % result['rcsbId'])
            oL.append('          <td class="rs1">%s</td>' % result['compId'])
            oL.append('          <td class="rs1">%s</td>' % result['status'])
            oL.append('          <td class="rs1">%s</td>' % result['method'])
            oL.append('          <td class="rs1">%s</td>' % result['title'])
            oL.append('          <td class="rs1">%s</td>' % result['releaseDate'])
            oL.append('  	  </td>')
            oL.append('     </tr>')

        oL.append('</table>')

        ##
        if d['searchOp'] == "LIKE":
            oL.append('<h2>Instances like %s  in Unreleased Entries</h2>' % d['targetid'])
        else:
            oL.append('<h2>Instances of %s in Unreleased Entries</h2>' % d['targetid'])
        #
        oL.append('<table class="rs1">')
        oL.append('<tr>')
        # oL.append('	<th class="rs1">PDB ID</th>')
        oL.append('	<th class="rs1">RCSB ID</th>')
        oL.append('	<th class="rs1">CC ID</th>')
        oL.append('	<th class="rs1">Status</th>')
        oL.append('	<th class="rs1">Method</th>')
        oL.append('	<th class="rs1">Title</th>')
        oL.append('	<th class="rs1">Deposition Date</th>')
        oL.append('</tr>')
        #
        # row data -
        #
        i = 0
        for result in d['resultotherlist']:
            i += 1
            if (i % 2) == 0:
                trcls = "rs1-even"
            else:
                trcls = "rs1-odd"

            oL.append('<tr class="%s">' % trcls)
            # oL.append('          <td class="rs1"><a target="_blank" href="http://www.rcsb.org/pdb/explore/explore.do?structureId=%s">%s</a></td>' % (result['pdbId'],result['pdbId']))
            oL.append('          <td class="rs1">%s</td>' % result['rcsbId'])
            oL.append('          <td class="rs1">%s</td>' % result['compId'])
            oL.append('          <td class="rs1">%s</td>' % result['status'])
            oL.append('          <td class="rs1">%s</td>' % result['method'])
            oL.append('          <td class="rs1">%s</td>' % result['title'])
            oL.append('          <td class="rs1">%s</td>' % result['depositionDate'])
            oL.append('  	  </td>')
            oL.append('     </tr>')

        oL.append('</table>')

        oL.append(self._trailer)
        oL.append('</body>')
        oL.append('</html>')
        return oL
