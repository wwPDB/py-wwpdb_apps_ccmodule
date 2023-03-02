##
# File:  ChemCompSearchDepict.py
# Date:  06-Aug-2010
# Updates:
# ---------------------------------------------------------------------------
# 2011-05-12  RPS  Piloting changes to doRender methods for standalone Ligand Editor Tool
##
"""
Create HTML depiction for simple chemical component search

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import sys
from wwpdb.apps.ccmodule.depict.ChemCompDepict import ChemCompDepict


class ChemCompSearchDepict(ChemCompDepict):
    """Create HTML depiction for chemical component searches.

    """
    def __init__(self, verbose=False, log=sys.stderr):
        """

         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        super(ChemCompSearchDepict, self).__init__(verbose, log)
        # self.__verbose = verbose
        # self.__lfh = log
        # self.__debug = True
        #
        #

    def doRenderIndex(self, d=None):
        ''' Render in HTML
        '''
        if d is None:
            d = {}
        oL = []
        oL.append(self._pragma)
        oL.append('<html>')
        oL.append(self._header % 'Chemical Component Index Search')
        oL.append('<body class="oneColLiqCtrHdr">')
        oL.append(self._menuCommonInclude)

        oL.append('<h1>Index Search Result Summary</h1>')
        oL.append('<p>')
        oL.append('<p>')
        # '''
        # oL.append('<table>')
        # oL.append('<tr><td><b>Query:</b>    </td><td>%s</td></tr>' % d['query'])
        # oL.append('<tr><td><b>Query type:</b>    </td><td>%s </td></tr>' % d['querytype'])
        # oL.append('<tr><td><b>Result count:</b>  </td><td>%r</td></tr>' % d['count'])
        # oL.append('</table>')
        # '''
        oL.append('<div>')
        oL.append('<table style="width: 25%">')
        oL.append('<tr><th>Query:</th><td>%s</td></tr>' % d['query'])
        oL.append('<tr><th>Query Type:</th><td>%s</td></tr>' % d['querytype'])
        oL.append('<tr><th>Result count:</th><td>%s</td></tr>' % d['count'])
        oL.append('</table>')
        oL.append('</div>')
        #
        oL.append('<br/><br/>')
        oL.append('<table class="rs1">')
        oL.append('<tr>')
        oL.append('<th class="rs1">ID</th>')
        oL.append('<th class="rs1">View</th>')
        oL.append('<th class="rs1">Creator</th>')
        oL.append('<th class="rs1">Status</th>')
        oL.append('<th class="rs1">Formula</th>')
        oL.append('<th class="rs1" width="50%">Name</th>')
        oL.append('<th class="rs1">Subcomponent List</th>')
        oL.append('</tr>')

        i = 0
        for result in d['resultlist']:
            i += 1
            if (i % 2) == 0:
                trcls = "rs1-even"
                # subcls = "submit-text-even"
            else:
                trcls = "rs1-odd"
                # subcls = "submit-text-odd"

            oL.append('	<tr class="%s">' % trcls)
            oL.append('          <td class="rs1">%s</td>' % result['ccid'])
            oL.append('')
            oL.append('	  <td class="rs1">')
            # '''
            # oL.append('		<form method="post" action="/service/cc/report" target="_blank" >')
            # oL.append('	        	<input id="formid"      name="formid"    type="hidden" value="ccidops">')
            # oL.append('	        	<input id="operation"   name="operation" type="hidden" value="report">')
            # oL.append('	        	<input id="ccid"        name="ccid"      type="hidden" value="%s">' % result['ccid'])
            # oL.append('			<input id="sessionid"   name="sessionid" type="hidden" value="%s">' % d['sessionid'])
            # oL.append('			<input type="submit" name="submit" class="%s"  value="Report &raquo;">' % subcls)
            # oL.append('		</form>')
            # oL.append('')
            # '''
            oL.append('<a href="/ccmodule/cc-view.html?ccid=%s" target="_blank">Profile in Viewer</a>' % result['ccid'])
            oL.append('  	  </td>')
            oL.append('          <td class="rs1">%s</td>' % result['creator'])
            oL.append('          <td class="rs1">%s</td>' % result['status'])
            oL.append('          <td class="rs1">%s</td>' % result['formula'])
            oL.append('          <td class="rs1">%s</td>' % result['name'])
            oL.append('          <td class="rs1">%s</td>' % result['subcomplist'])
            oL.append('        </tr>')

        oL.append('</table>')

        oL.append(self._trailer)
        oL.append('</body>')
        oL.append('</html>')
        return oL

    def doRenderGraph(self, d=None):
        ''' Render graph search results in HTML
        '''
        if d is None:
            d = {}
        oL = []
        oL.append(self._pragma)
        oL.append('<html>')
        oL.append(self._header % 'Chemical Component Index Search')
        oL.append('<body>')
        oL.append(self._menuCommonInclude)

        oL.append('<h1>Graph Search Result Summary</h1>')
        oL.append('<p>')
        # '''
        # oL.append('<table>')
        # oL.append('<tr><td><b>Query file:</b>    </td><td> %s </td></tr>' % d['queryfile'])
        # oL.append('<tr><td><b>Query type:</b>    </td><td> %s </td></tr>' % d['querytype'])
        # oL.append('<tr><td><b>Result count:</b>  </td><td> %r </td></tr>' % d['count'])
        # oL.append('<tr><td><b>Target name:</b>   </td><td> %s </td></tr>' % d['nametarget'])
        # oL.append('<tr><td><b>Target formula:</b></td><td> %s </td></tr>' % d['formulatarget'])
        # oL.append('</table>')
        # '''
        #
        oL.append('<div>')
        oL.append('<table style="width: 25%">')
        oL.append('<tr><th>Query file:</th><td>%s</td></tr>' % d['queryfile'])
        oL.append('<tr><th>Query Type:</th><td>%s</td></tr>' % d['querytype'])
        oL.append('<tr><th>Result count:</th><td>%s</td></tr>' % d['count'])
        oL.append('<tr><th>Target name:</th><td>%s</td></tr>' % d['nametarget'])
        oL.append('<tr><th>Target formula:</th><td>%s</td></tr>' % d['formulatarget'])
        oL.append('</table>')
        oL.append('</div>')
        #
        oL.append('<br/><br/>')
        oL.append('<table border=1 cellpadding=2>')

        if len(d['resultlist']) > 0:
            oL.append('<tr>')
            oL.append('<th class="rs1">ID</th>')
            oL.append('<th class="rs1">Atom Mapping</th>')
            oL.append('<th class="rs1">Report</th>')
            oL.append('<th class="rs1">Formula</th>')
            oL.append('<th class="rs1">Name</th>')
            oL.append('</tr>')
            i = 0
            for result in d['resultlist']:
                # start for loop
                i += 1
                if (i % 2) == 0:
                    trcls = "rs1-even"
                    # subcls = "submit-text-even"
                else:
                    trcls = "rs1-odd"
                    # subcls = "submit-text-odd"
                # here

                oL.append('<tr class="%s">' % trcls)
                oL.append('<td class="rs1">%s</td>' % result['ccidReference'])
                oL.append('<td class="rs1"><a href="%s" target=_blank>Atom mapping &raquo;</a></td>' % result['mappingFile'])
                oL.append('<td class="rs1">')
                # ccidops is this a report ??
                # '''
                # oL.append('<form method="post" action="/service/cc/report" target="_blank" >')
                # oL.append('     <input id="formid"      name="formid"    type="hidden" value="id-report">')
                # oL.append('     <input id="operation"   name="operation" type="hidden" value="id-report">')
                # oL.append('     <input id="ccid"        name="ccid"      type="hidden" value="%s">' % result['ccidReference'])
                # oL.append('     <input id="sessionid"   name="sessionid" type="hidden" value="%s">' % d['sessionid'])
                # oL.append('     <input type="submit" name="submit"   class="<%=subcls%>" value="Report &raquo;">')
                # oL.append('</form>')
                # '''
                oL.append('<a href="/ccmodule/cc-view.html?ccid=%s" target="_blank">Profile in Viewer</a>' % result['ccidReference'])
                oL.append('</td>')
                oL.append('<td class="rs1">%s</td>' % result['formulaReference'])
                oL.append('<td class="rs1">%s</td>' % result['nameReference'])
                oL.append('</tr>')

        oL.append('</table>')
        oL.append(self._trailer)
        oL.append('</body>')
        oL.append('</html>')
        return oL
