##
# File:  ChemCompExtractDepict.py
# Date:  06-Aug-2010
# Updates:
# 2010-08-19    RPS    Introducing pagination feature for convenient navigation of extracted chem components.
#                        Fix typo preventing "Show hydrogens" behavior from working.
# 2011-11-18    RPS    Interim changes to allow further development of stand alone ligand tool functionality such as cc-extract within the
#                        consolidated common tool setup.
##
"""
Create HTML depiction for chemical component extraction result page.

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.02"

import os, sys
from wwpdb.apps.ccmodule.depict.ChemCompDepict import ChemCompDepict


class ChemCompExtractDepict(ChemCompDepict):
    """Create HTML depiction for chemical component extraction result page.

    """
    def __init__(self,verbose=False,log=sys.stderr):
        """

         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.
          
        """
        super(ChemCompExtractDepict,self).__init__(verbose,log)
        self.__verbose=verbose
        self.__lfh=log
        self.__debug=True
        self.__graphics=True
        #

    def doRender(self,extractList):
        ''' Render extraction results in HTML
        '''

        oL=[]
        oL.append(self._pragma)
        oL.append('<html>')
        oL.append(self._headerExtrctRslts % 'Chemical Component Extraction Results')
        oL.append('<body>')        
        oL.append(self._menuCommonIncludeExtrctRslts)
        oL.append(self._jmolInclude)
        #
        oL.append('<h2>Chemical Component Extraction Results</h2>')
        oL.append('<br/>')
        oL.append('<span class="fltlft">Choose Extracted Chem Component by Entity Group</span>\n<div id="pagi" class="noprint fltlft"></div>\n<br class="clearfloat" />\n')
        i=0
        srtdXtrctLst = sorted(extractList, lambda x,y: cmp(x['id'], y['id']) );
        prevGrp = ''
        newGrp = False
        for cc in srtdXtrctLst:
            id  = cc['id']
            grp = (id.split('_'))[0] 
            if( grp != prevGrp ):
                i+=1
                prevGrp = grp
                newGrp = True
            else:
                newGrp = False
            sessionid = cc['sessionid']
            if cc.has_key("cifPathRel"):
                (pth,cifFile) = os.path.split(cc['cifPathRel'])
            if cc.has_key("cifExtractPathRel"):
                (pth,cifExtractFile) = os.path.split(cc['cifExtractPathRel'])
                #cifExtractFile = id + "-extract.cif"
            if cc.has_key("annCifPathRel"):
                (pth,annCifFile) = os.path.split(cc['annCifPathRel'])                            
                #annCifFile = id + "-v3.cif"

            if cc.has_key("reportPathRel"):
                (pth,reportFile) = os.path.split(cc['reportPathRel'])                                            
                # reportFile = id + "-v3.html"
                # checkCifFile = id + "-check-v3.html"
                
            tabStyle="displaynone"
            if i==1:
                tabStyle="_current"
            
            if newGrp:
                if i > 1:
                    oL.append('</div>')
                oL.append('<div id="p%s" class="%s tabscount">'% (str(i),tabStyle))
                oL.append('<div class="cmpnt_grp displaynone">%s</div>' % grp)
            oL.append('<table border="1" >')
            oL.append('    <tr>')
            oL.append('    <td colspan=3 align=left>')
            oL.append('    <table>')
            oL.append('        <tr>')
            oL.append('                  <td><b>Extracted ID:</b> </td>')
            oL.append('                  <td class="extracted_id"> %s</td>' % cc['id'])
            oL.append('                </tr>')
            oL.append('        <tr>')
            oL.append('              <td>')
            oL.append('            <table>')
            oL.append('                    <tr>')
            oL.append('                    <td><b>Name:</b> </td>')
            oL.append('                <td align=left>    ')
            oL.append('            <form method="post" action="/service/cc/search/cc-index" target="_blank">')
            oL.append('                    <input id="formid" name="formid" TYPE="hidden" VALUE="cc-index-search">')
            oL.append('                <input type="hidden" name="operation" value="name-similar">')
            oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
            oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
            oL.append('                <input type="hidden" name="target" value="%s">' % cc['acdName'])
            oL.append('                <input type="submit" class="submit-text" value=" (Search &raquo;)">')
            oL.append('            </form>')
            oL.append('              </td>    ')
            oL.append('                    </tr>')
            oL.append('                   </table>')
            oL.append('                  </td>')
            oL.append('                  <td >%s</td>' % cc['acdName'])
            oL.append('        </tr>')
            oL.append('        <tr>')
            oL.append('          <td>')
            oL.append('            <table>')
            oL.append('                    <tr>')
            oL.append('               <td><b>Formula:</b></td>')
            oL.append('             <td>    ')
            oL.append('                <form method="post" action="/service/cc/search/cc-index" target="_blank">')
            oL.append('                    <input id="formid" name="formid" TYPE="hidden" VALUE="cc-index-search">')
            oL.append('                <input type="hidden" name="operation" value="formula-exact-subset">')
            oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
            oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
            oL.append('                <input type="hidden" name="target" value="%s">' % cc['formula'])
            oL.append('                <input type="submit" class="submit-text" value="(Search &raquo;)">')
            oL.append('            </form>')
            oL.append('             </td>    ')
            oL.append('                 </tr>')
            oL.append('                     </table>')
            oL.append('                  </td>')
            oL.append('           <td >%s</td>' % cc['formula'])
            oL.append('        </tr>')
            oL.append('')
            oL.append('        <tr>')
            oL.append('           <td><b>Formal Charge:</b></td>')
            oL.append('          <td>%s</td>' % cc['formal_charge'])
            oL.append('        </tr>')

            if cc.has_key("cifExtractPathRel"):
                (pth,cifExtractFile) = os.path.split(cc['cifExtractPathRel'])

                oL.append('        <tr>')
                oL.append('              <td><b>Extracted CC: </b> </td>')
                oL.append('             <td>')
                oL.append('             <table>')
                oL.append('                     <tr>')
                oL.append('                    <td><a href="%s" TARGET="_blank"> View &raquo; </a></td>' % cc['cifExtractPathRel'])
                oL.append('                        <td>    ')
                oL.append('            <form method="post" action="/service/cc/send" enctype="multipart/form-data">')
                oL.append('                    <input id="formid" name="formid" TYPE="hidden" VALUE="ccsend">')
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                <input type="hidden" name="filename" value="%s">' % cifExtractFile)
                oL.append('                <input type="submit" class="submit-text" value="Download &raquo;">')
                oL.append('            </form>')
                oL.append('            </td><td>')
                oL.append('            <form method="post" action="/service/cc/edit" target="_blank">')
                oL.append('                    <INPUT id="formid" name="formid" TYPE="hidden" VALUE="ccedit">')
                oL.append('                <input type="hidden" name="caller" value="extractor">')
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                <input type="hidden" name="filetype" value="pre-extracted-atom">')
                oL.append('                <input type="hidden" name="filename" value="%s">' % cifExtractFile)
                oL.append('                <input type="submit" class="submit-text" value="Edit &raquo;">')
                oL.append('                 </form>')
                oL.append('            </td><td>')
                oL.append('            <form method="post" action="/service/cc/edittable" target="_blank">')
                oL.append('                    <INPUT id="formid" name="formid" TYPE="hidden" VALUE="ccedittable">')
                oL.append('                <input type="hidden" name="caller" value="extractor">')
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                <input type="hidden" name="filetype" value="pre-extracted-atom">')
                oL.append('                <input type="hidden" name="filename" value="%s">' % cifExtractFile)
                oL.append('                <input type="submit" class="submit-text" value="Edit Table &raquo;">')
                oL.append('                 </form>')
                oL.append('            </td><td>')
                oL.append('            <form method="post" action="/service/cc/reannotate" target="_blank">')
                oL.append('                    <INPUT id="formid" name="formid" TYPE="hidden" VALUE="ccreannotate">')
                oL.append('                <input type="hidden" name="caller" value="extractor">')
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                <input type="hidden" name="filetype" value="pre-extracted-atom">')
                oL.append('                <input type="hidden" name="filename" value="%s ">' % cifExtractFile)
                oL.append('                <input type="submit" class="submit-text" value="Update &raquo;">')
                oL.append('                 </form>')
                oL.append('            </td>')
                oL.append('                      </tr>')
                oL.append('                    </table>')
                oL.append('              </td>')
                oL.append('                </tr>')
            # end if'
            if cc.has_key("cifPathRel"):
                (pth,cifFile) = os.path.split(cc['cifPathRel'])

                oL.append('        <tr>')
                oL.append('             <td><b>All Atom CC: </b> </td>')
                oL.append('            <td>')
                oL.append('             <table>')
                oL.append('                      <tr>')
                oL.append('                     <td><a href="%s" TARGET="_blank">View &raquo; </a></td>' % cc['cifPathRel'])
                oL.append('                        <td>    ')
                oL.append('            <form method="post" action="/service/cc/send" enctype="multipart/form-data">')
                oL.append('                    <input id="formid" name="formid" TYPE="hidden" VALUE="ccsend">')
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                <input type="hidden" name="filename" value="%s">' % cifFile)
                oL.append('                <input type="submit" class="submit-text" value="Download &raquo;">')
                oL.append('            </form>')
                oL.append('            </td><td>')
                oL.append('            <form method="post" action="/service/cc/edit" target="_blank">')
                oL.append('                    <INPUT id="formid" name="formid" TYPE="hidden" VALUE="ccedit">')
                oL.append('                <input type="hidden" name="caller" value="extractor">')
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                <input type="hidden" name="filetype" value="pre-all-atom">')
                oL.append('                <input type="hidden" name="filename" value="%s">' % cifFile)
                oL.append('                <input type="submit" class="submit-text" value="Edit &raquo;">')
                oL.append('                 </form>')
                oL.append('            </td><td>')
                oL.append('            <form method="post" action="/service/cc/edittable" target="_blank">')
                oL.append('                    <INPUT id="formid" name="formid" TYPE="hidden" VALUE="ccedittable">')
                oL.append('                <input type="hidden" name="caller" value="extractor">')
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                <input type="hidden" name="filetype" value="pre-all-atom">')
                oL.append('                <input type="hidden" name="filename" value="%s">' % cifFile)
                oL.append('                <input type="submit" class="submit-text" value="Edit Table &raquo;">')
                oL.append('                 </form>')
                oL.append('            </td><td>')
                oL.append('            <form method="post" action="/service/cc/sketch" target="_blank">')
                oL.append('                <input id="formid" name="formid" TYPE="hidden" VALUE="cc-sketch">')
                oL.append('                <input type="hidden" name="caller"       value="extractor">')
                oL.append('                <input type="hidden" name="inputformat"  value="cif">')
                oL.append('                  <input type="hidden" name="smiles"       value="">')
                oL.append('                <input type="hidden" name="operation"    value="sketch-view-default">')
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                <input type="hidden" name="filetype"     value="pre-all-atom">')
                oL.append('                <input type="hidden" name="filename"     value="%s">' % cifFile)
                oL.append('                <input type="submit" class="submit-text" value="Edit Sketch &raquo;">')
                oL.append('            </form>    ')
                oL.append('            </td><td>')
                oL.append('            <form method="post" action="/service/cc/reannotate" target="_blank">')
                oL.append('                    <INPUT id="formid" name="formid" TYPE="hidden" VALUE="ccreannotate">')
                oL.append('                <input type="hidden" name="caller" value="extractor">')
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                <input type="hidden" name="filetype" value="pre-all-atom">')
                oL.append('                <input type="hidden" name="filename" value="%s">' % cifFile)
                oL.append('                <input type="submit" class="submit-text" value="Update &raquo;">')
                oL.append('                 </form>')
                oL.append('            </td>')
                oL.append('                      </tr>')
                oL.append('                    </table>')
                oL.append('              </td>')
                oL.append('                </tr>')
                # end if
            if cc.has_key("annCifPathRel"):
                (pth,annCifFile) = os.path.split(cc['annCifPathRel'])
                oL.append('        <tr>')
                oL.append('             <td><b>V3 Annotated CC: </b> </td>')
                oL.append('            <td>')
                oL.append('                      <table>')
                oL.append('                       <tr>')
                oL.append('                     <td><a href="%s" TARGET="_blank">View &raquo;</a></td>' % cc['annCifPathRel'])
                oL.append('                        <td>     ')
                oL.append('            <form method="post" action="/service/cc/send" enctype="multipart/form-data">')
                oL.append('                    <input id="formid" name="formid" TYPE="hidden" VALUE="ccsend">')
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                <input type="hidden" name="filename" value="%s">' % annCifFile)
                oL.append('                <input type="submit" class="submit-text" value="Download &raquo;">')
                oL.append('            </form>')
                oL.append('            </td><td>')
                oL.append('                    <!--')
                oL.append('            <form method="post" action="/service/cc/edit" target="_blank">')
                oL.append('                    <INPUT id="formid" name="formid" TYPE="hidden" VALUE="ccedit">')
                oL.append('                <input type="hidden" name="caller" value="extractor">')
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                <input type="hidden" name="filetype" value="ann-all-atom">')
                oL.append('                <input type="hidden" name="filename" value="%s">' % annCifFile)
                oL.append('                <input type="submit" class="submit-text" value="Edit &raquo;">')
                oL.append('                 </form>')
                oL.append('                        -->')
                oL.append('            </td><td>')
                oL.append('             <form method="post" action="/service/cc/mail" target="_blank">')
                oL.append('                    <INPUT id="formid" name="formid" TYPE="hidden" VALUE="ccmail">')
                oL.append('                <input type="hidden" name="filename" value="%s">' % annCifFile)
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                <input type="hidden" name="caller" value="extractor">')
                oL.append('                <input type="submit" class="submit-text" value="Email &raquo;">')
                oL.append('            </form>')
                oL.append('            </td>')
                oL.append('            </tr>')
                oL.append('            </table>')
                oL.append('            <table>')
                oL.append('                        <tr>')
                oL.append('            <td>')
                oL.append('            <form method="post" action="/service/cc/search/cc-graph" target="_blank">')
                oL.append('                    <input id="formid" name="formid" TYPE="hidden" VALUE="cc-ss-search">')
                oL.append('                <input type="hidden" name="operation" value="prefilter-strict">')
                oL.append('                <input type="hidden" name="filename" value="%s">' % annCifFile)
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                 <input type="hidden" name="caller" value="extractor">    ')
                oL.append('                <input type="submit" class="submit-text" value="SS(all atom exact) &raquo;">')
                oL.append('            </form>')
                oL.append('            </td>')
                oL.append('            <td>')
                oL.append('            <form method="post" action="/service/cc/search/cc-graph" target="_blank">')
                oL.append('                    <input id="formid" name="formid" TYPE="hidden" VALUE="cc-ss-search">')
                oL.append('                <input type="hidden" name="operation" value="prefilter-skip-h-strict">')
                oL.append('                <input type="hidden" name="filename" value="%s">' % annCifFile)
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                 <input type="hidden" name="caller" value="extractor">    ')
                oL.append('                <input type="submit" class="submit-text" value="SS(heavy atom exact) &raquo;">')
                oL.append('            </form>')
                oL.append('            </td>')
                oL.append('            <td>')
                oL.append('            <form method="post" action="/service/cc/cc-graph" target="_blank">')
                oL.append('                    <input id="formid" name="formid" TYPE="hidden" VALUE="cc-ss-search">')
                oL.append('                <input type="hidden" name="operation" value="prefilter-skip-h-close">')
                oL.append('                <input type="hidden" name="filename" value="%s">' % annCifFile)
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                 <input type="hidden" name="caller" value="extractor">    ')
                oL.append('                <input type="submit" class="submit-text" value="SS(formula bounded) &raquo;">')
                oL.append('            </form>')
                oL.append('            </td>')
                oL.append('')
                oL.append('            <td>')
                oL.append('            <form method="post" action="/service/cc/cc-graph" target="_blank">')
                oL.append('                    <input id="formid" name="formid" TYPE="hidden" VALUE="cc-ss-search">')
                oL.append('                <input type="hidden" name="operation" value="prefilter-skip-h-subset">')
                oL.append('                <input type="hidden" name="filename" value="%s">' % annCifFile)
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                 <input type="hidden" name="caller" value="extractor">    ')
                oL.append('                <input type="submit" class="submit-text" value="SS(formula subset) &raquo;">')
                oL.append('            </form>')
                oL.append('            </td>')
                oL.append('')
                oL.append('                        </tr>')
                oL.append('             </table>')
                oL.append('                   </td>')
                oL.append('        </tr>')
                # end if
            if cc.has_key("checkCifPathRel"):
                (pth,annCifFile) = os.path.split(cc['annCifPathRel'])
                oL.append('        <tr>')
                oL.append('                    <td><b>V3 Check Report: </b> </td>')
                oL.append('            <td>')
                oL.append('                      <table>')
                oL.append('                        <tr>')
                oL.append('                 <td><a href="%s" TARGET="_blank"> View &raquo;</a></td>' % cc['checkCifPathRel'])
                oL.append('                <td align=left>    ')
                oL.append('                <form method="post" action="/service/cc/recheck" target="_blank">')
                oL.append('                    <INPUT id="formid" name="formid" TYPE="hidden" VALUE="ccrecheck">')
                oL.append('                <input type="hidden" name="caller" value="extractor">')
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                <input type="hidden" name="filename" value="%s">' % annCifFile)
                oL.append('                <input type="submit" class="submit-text" value="Re-check &raquo;">')
                oL.append('                     </form>')
                oL.append('            </td>')
                oL.append('               </tr>')
                oL.append('                      </table>')
                oL.append('                    <td>')
                oL.append('                 </tr>')
                # end if
            if cc.has_key("reportPathRel"):
                oL.append('        <tr>')
                oL.append('                    <td><b>V3 Summary Report: </b> </td>')
                oL.append('                    <td>')
                oL.append('                      <table>')
                oL.append('                        <tr>')
                oL.append('                 <td><a href="%s" TARGET="_blank">View &raquo;</a></td>' % cc['reportPathRel'])
                oL.append('              <td align=left>    ')
                oL.append('                <form method="post" action="/service/cc/report" target="_blank">')
                oL.append('                    <INPUT id="formid" name="formid" TYPE="hidden" VALUE="ccrereport">')
                oL.append('                <input type="hidden" name="caller" value="extractor">')
                oL.append('                <input type="hidden" name="sessionid" value="%s">' % sessionid )
                oL.append('                <input type="hidden" name="ccid" value="%s">' % id)
                oL.append('                <input type="hidden" name="filename" value="%s">' % annCifFile)
                oL.append('                <input type="submit" class="submit-text" value="Re-report &raquo;">')
                oL.append('                     </form>')
                oL.append('                  </td>')
                oL.append('            </tr>')
                oL.append('            </table>    ')
                oL.append('                      </td>')
                oL.append('                   </tr>')
                # end if
            oL.append('    </table>')
            oL.append('    </tr>')
            #
            if self.__graphics:
                oL.append('    <tr>')
                oL.append('        <td align=center>Starting Diagram </td>')
                oL.append('        <td align=center>Starting Model Coordinates</td>')
                oL.append('                <td align=center>&nbsp</td>')
                oL.append('    </tr>')
                oL.append('    <tr>')
                oL.append('    <td width=300 align="center"><img src="%s"></td>' % cc['gifPathRel'])
                oL.append('    <td width=300 align="center">')
                oL.append('    <script>')
                oL.append('        jmolApplet(300, "load %s", %d);' % (cc['sdfPathRel'],i))
                oL.append('    </script>')
                oL.append('    </td>')
                oL.append('    <td>')
                oL.append('          <form name="appletcontrols">')
                oL.append('           <input  checked="checked"  onClick="js_jmol_display_hydrogens(this,%d)" type="checkbox">Show hydrogens <br/>' % i)
                oL.append('    <!--           <input                     onClick="js_jmol_display_atom_labels(this,%d)" type="checkbox">Show labels -->' % i)
                oL.append('          </form>')
                oL.append('    </td>')
                oL.append('    </tr>')
                # end if
            oL.append('</table>')
            
            oL.append('<br/>')
            oL.append('')
            
            oL.append('')
            oL.append('</table>')
            #oL.append('</div>')
            
        #end of iterating through all chem components
        oL.append('</div>')
        #above needed to seal off last chem cmpnt_grp div
        oL.append('</div>')
        oL.append(self._trailer)
        oL.append('</body>')
        oL.append('</html>')
        return oL


if __name__ == '__main__':
    ccd=ChemCompExtractDepict()
