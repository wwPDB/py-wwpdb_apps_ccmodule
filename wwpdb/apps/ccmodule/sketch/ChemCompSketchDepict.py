##
# File:  ChemCompSketchDepict.py
# Date:  06-Dec-2012
# Updates:
#
##
"""
Create HTML depiction surrounding the chemical sketch applet.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import sys
from wwpdb.apps.ccmodule.depict.ChemCompDepict import ChemCompDepict


class ChemCompSketchDepict(ChemCompDepict):
    """Create HTML depiction surrounding the chemical sketch applet.

    """
    def __init__(self, verbose=False, log=sys.stderr):
        """

         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        super(ChemCompSketchDepict, self).__init__(verbose, log)
        # self.__verbose = verbose
        # self.__lfh = log
        # self.__debug = True
        #
        #

    def doRender(self, d):
        ''' Render in HTML ---   This currently uses a very minimal template which can be
                                 customized as needed for integration into other page sections.
        '''
        oL = []
        oL.append(self._pragma)
        oL.append('<html>')
        oL.append(self._headerMarvin % 'Chemical Component Sketch Tool')

        oL.append('<script LANGUAGE="JavaScript1.1">')
        # oL.append('<!--')
        oL.append('function launchSketcher3(size) {')
        oL.append('	msketch_name = "MSketch";')
        oL.append('	msketch_begin("/applets/marvin", size, size);')
        oL.append('	msketch_param("mol", %s,  "%s");' % (d['strmol'], d['sketchoptions']))
        oL.append('	msketch_param("background", "#99ccff");')
        oL.append('	msketch_param("molbg", "#eeeeee");')
        oL.append('	msketch_param("colorscheme", "cpk");')
        oL.append('	msketch_param("preload", "MolExport,Parity,SmilesExport,Clean2D,Clean3D,PdbImport");')
        oL.append('	msketch_param("autoscale", "true");')
        oL.append('	msketch_param("implicitH", "all");')
        oL.append('	msketch_param("explicitH", "true");')
        oL.append('	msketch_param("imgConv", "+Hc-a");')
        oL.append('	msketch_param("clean2dOpts", "O2");')
        oL.append('	msketch_param("clean3dOpts", "S{fine}");')
        oL.append('	msketch_param("cleanDim", "3");')
        oL.append('	msketch_param("chiralitySupport", "all");')
        oL.append('	msketch_end();')
        oL.append('   }')
        # oL.append('//-->')
        oL.append('</script>')

        oL.append('<body>')
        # oL.append(self._menuCommonInclude)
        oL.append('<h2>Chemical Component Sketch Tool</h2>')
        oL.append('<br/>')

        oL.append(self._marvinInclude % int(d['sizexy']))

        oL.append('<p>')
        oL.append('<form name="MyExportForm" method="post" action="/service/cc/sketch-save" target="_blank">')
        oL.append(' <fieldset>')
        oL.append('  <legend>Save file</legend>')
        oL.append('  <input TYPE="hidden" id="formid"   name="formid"  VALUE="cc-sketch"> ')
        oL.append('  <input type="hidden" name="caller"   value="sketch-input">')
        oL.append('  <input type="hidden" name="ccid"     value="%s">' % d['ccid'])
        oL.append('  <input type="hidden" name="filename" value="%s">' % d['filename'])
        oL.append('  <input type="hidden" name="sessionid" value="%s">' % d['sessionid'])
        oL.append('  <input type="hidden" name="MolData" >')
        oL.append('  <input type="hidden" name="molformat" value="cif">')

        oL.append(' <label for="tid">Component ID Code </label>')
        oL.append(' <input class="formInputText" type="text" size="10" name="tid"  value="%s">' % d['ccid'])
        oL.append(' <br />')
        # oL.append('  <label for="remap">Retain author atoms names</label>')
        # oL.append('  <select class="formSelect" name="remap">')
        # oL.append('	<option VALUE="no">No</option>')
        # oL.append(' 	<option VALUE="heavy">Heavy atoms only</option>')
        # oL.append(' 	<option SELECTED VALUE="all">All atoms</option>')
        # oL.append(' </select>')
        #
        oL.append('  <input type="hidden" name="remap" value="all">')
        oL.append('  <input type="hidden" name="inputformat" value="sdf">')
        oL.append('  <input class="formInputButton" type="submit" value="Save as file"  onClick="myExportMol(\'mol:-a+H\')">')
        oL.append(' </fieldset>')
        oL.append('</form>')

        oL.append('<br />')

        # oL.append('<form name="MySearchForm" method="post" action="/service/cc/sketch" target="_blank">')
        # oL.append(' <fieldset>')
        # oL.append('   <legend>Substructure search options</legend>')
        # oL.append('  <input id="formid"   name="formid" TYPE="hidden" VALUE="cc-sketch">')
        # oL.append('  <input type="hidden" name="caller" value="search">')
        # oL.append('  <input type="hidden" name="ccid"   value="%s">' % d['ccid'])
        # oL.append('  <input type="hidden" name="filename" value="%s">' % d['filename'])
        # oL.append('  <input type="hidden" name="sessionid" value="%s">' % d['sessionid'])
        # oL.append('  <input type="hidden" name="MolData" >')
        # oL.append('  <input type="hidden" name="molformat" value="cif">')
        # oL.append('  <label for="operation">Search type</label>')
        # oL.append('  <select class="formSelect" name="operation">')
        # oL.append('            <option selected="selected"  value="prefilter-strict">Strict (all atom)</option>')
        # oL.append('            <option                      value="prefilter-skip-h-strict">Strict (heavy atom)</option>')
        # oL.append('            <option                      value="prefilter-relaxed" >Relaxed (all atom/connectivity only)</option>')
        # oL.append('            <option                      value="prefilter-skip-h-relaxed">Relaxed (heavy atom/connectivity only)</option>')
        # oL.append('            <option                      value="prefilter-skip-h-close">Close (close formula/connectivity only)</option>')
        # oL.append('	</select>')
        # oL.append('  <input class="formInputButton" type="submit" value="Search" onClick="mySearchMol(\'mol:-a+H\')">')
        # oL.append(' </fieldset>')
        # oL.append('</form>')

        oL.append(self._trailer)
        oL.append('</body>')
        oL.append('</html>')

        return oL
