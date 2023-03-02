##
# File:  ChemCompTableEditorDepict.py
# Date:  23-Aug-2010
# Updates:
#
# 2012-10-24    RPS    Updated to reflect reorganization of modules in pdbx packages
#
##
"""
Create HTML depiction chemical component text editor.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import sys
from wwpdb.apps.ccmodule.depict.ChemCompDepict import ChemCompDepict
from mmcif_utils.chemcomp.PdbxChemCompUtils import PdbxChemCompCategoryDefinition


class ChemCompTableEditorDepict(ChemCompDepict):
    """Create HTML depiction for chemical component text editor.

    """
    def __init__(self, verbose=False, log=sys.stderr):
        """

         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        super(ChemCompTableEditorDepict, self).__init__(verbose, log)
        # self.__verbose = verbose
        # self.__lfh = log
        # self.__debug = True
        #
        self.__cDict = PdbxChemCompCategoryDefinition._cDict
        #
        self.__noEditList = ['_chem_comp_atom.comp_id', '_chem_comp_bond.comp_id']
        #
        self.__setup()

    def doRender(self, eD):
        ''' Render in HTML
        '''
        oL = []
        oL.append(self._pragmaXhtml)
        oL.append('<html>')
        oL.append('<head>')
        oL.append(self._jQueryGenericInclude)
        oL.append(self._jQueryTableInclude)
        oL.append('</head>')
        oL.append('<body>')

        tableList = ['chem_comp', 'chem_comp_atom', 'chem_comp_bond']
        self.__jQueryTableEditScript1(tableList, eD, oL)

        oL.append('<h2>Chemical Component Editor</h2>')
        oL.append('<br/>')

        self.__renderControlButtons(oL)

        cD = eD['dataDict']

        for catName in ['chem_comp']:
            if catName in cD and (len(cD[catName]) > 0):
                # oL.append('<h4>Category: %s</h4>' %  catName)
                # oL.append('<h4><a href="" id="toggle_%s">Hide</a> Category: %s</h4>' % (catName, catName))

                oL.append('<div class="sectionbar1">')
                oL.append('  <a class="sectionbar1" href="" id="toggle_section_%s">Edit</a> Category: %s' % (catName, catName))
                oL.append('</div>')

                oL.append('<div style="display: block;" id="d_%s" class="displaynone">' % catName)
                oL.append('<table id="%s">' % catName)
                self.__renderTableColumnWise(catName, cD[catName][0], oL)
                oL.append('</table>')
                oL.append('</div>')

        for catName in ['chem_comp_atom', 'chem_comp_bond']:
            if catName in cD and (len(cD[catName]) > 0):
                # oL.append('<h4>Category: %s</h4>' %  catName)
                # oL.append('<h4><a href="" id="toggle_%s">Hide</a> Category: %s</h4>' % (catName, catName))

                oL.append('<div class="sectionbar1">')
                oL.append('<a class="sectionbar1" href="" id="toggle_section_%s">Edit</a> Category: %s' % (catName, catName))
                oL.append('</div>')

                oL.append('<div style="display: block;" id="d_%s" class="displaynone">' % catName)
                oL.append('<table id="%s">' % catName)
                self.__renderTableRowWise(catName, cD[catName], oL)
                oL.append('</table>')
                oL.append('</div>')

        oL.append(self._trailer)
        oL.append('</body>')
        oL.append('</html>')
        #
        return oL

    def __renderTableColumnWise(self, catName, rD, oL):
        """ Render table with unit cardinality.  Columns for the single row are listed vertically
            to the left of column values.
        """

        #
        iCol = 0
        iRow = 0
        insertCode = ''
        opNum = 0
        for (itemName, _itemFormat, _itemType, itemDefault) in self.__cDict[catName]:
            if itemName in self.__noEditList:
                editClass = 'editNone'
            else:
                editClass = 'editinp'

            if itemName in self.__itemEnumMap:
                editClass = 'editsel_%s' % self.__itemEnumMap[itemName]

            if itemName in rD:
                itemValue = rD[itemName]
            else:
                itemValue = itemDefault

            attributeName = self.__attributePart(itemName)
            oL.append('<tr class="%s">' % self.__rowClass(iCol))
            oL.append('<td>%s</td>' % self.__attributePart(itemName))

            oL.append('<td class="%s" id="%s:%s:%d:%s:%d">%s</td>' %
                      (editClass, catName, attributeName, iRow, insertCode, opNum, itemValue))
            oL.append('</tr>')
            iCol += 1

    def __renderTableRowWise(self, catName, rL, oL):
        """ Render a multirow table.
        """
        # Column labels --
        oL.append('<tr>')
        oL.append('<th>%s</th>' % 'Row Op.')
        for (itemName, _itemFormat, _itemType, _itemDefault) in self.__cDict[catName]:
            oL.append('<th>%s</th>' % self.__attributePart(itemName))
        oL.append('</tr>')
        #
        # Column data ---
        #
        iRow = 0
        for row in rL:
            self.__renderRow(catName, row, iRow, oL, insertDefault=False, insertCode='', opNum=0)
            iRow += 1
        #
        #

    def __renderRow(self, catName, row, iRow, oL, insertDefault=False, insertCode='', opNum=0):
        """ Render a row in a multirow table.
        """
        oL.append('<tr id="%s:%d:%s:%d" class="%s">' % (catName, iRow, insertCode, opNum, self.__rowClass(iRow, insertDefault)))
        #
        # First data element has row edit controls ---
        oL.append('<td class="%s" id="%s:%s:%d:%s:%d">%s</td>' % ('editrow', catName, 'rowop', iRow, insertCode, opNum, '+/-'))
        #
        for (itemName, _itemFormat, _itemType, itemDefault) in self.__cDict[catName]:
            if itemName in self.__noEditList:
                editClass = 'editNone'
            else:
                editClass = 'editinp'

            if itemName in self.__itemEnumMap:
                editClass = 'editsel_%s' % self.__itemEnumMap[itemName]

            if insertDefault:
                itemValue = itemDefault
            elif itemName in row:
                itemValue = row[itemName]
            else:
                itemValue = itemDefault

            attributeName = self.__attributePart(itemName)
            oL.append('<td class="%s" id="%s:%s:%d:%s:%d">%s</td>' %
                      (editClass, catName, attributeName, iRow, insertCode, opNum, itemValue))
        oL.append('</tr>')
        #

    def __rowClass(self, iRow, insertDefault=False):
        if (insertDefault):
            return "rs1-insert"
        else:
            return (iRow % 2 and "rs1-odd" or 'rs1-even')

    def __renderControlButtons(self, oL):
        """ Add  UNDO and SAVE buttons --
        """
        oL.append('<div id="controls" class="controls-1">')
        oL.append('<span>')
        oL.append('<button id="buttonUndo"  class="control-button" type="button">Undo</button>')
        oL.append('<button id="buttonSave"  class="control-button" type="button">Save</button>')
        oL.append('</span>')
        oL.append('</div>')

    def __jQueryButtonScripts(self, eD, oL):  # pylint: disable=unused-argument
        #
        # filePath = eD['filePath']
        # localPath = eD['localPath']
        # localRelativePath = eD['localRelativePath']
        # sessionId = eD['sessionId']
        #
        oL.append('  $("#buttonUndo").click(function () {')
        oL.append('  $.ajax({')
        oL.append('         url: "/service/cc/edit/undo",')
        oL.append('         data: {')
        oL.append('               "filePath"          : filePath,')
        oL.append('               "localPath"         : localPath,')
        oL.append('               "localRelativePath" : localRelativePath,')
        oL.append('               "blockId"           : blockId,')
        oL.append('               "sessionid"         : sessionId,')
        oL.append('               "editOpNumber"      : editNumber')
        oL.append('                },')
        oL.append('         success: function (jsonObj) {')
        oL.append('                   try {')
        oL.append('                        for (var i=0; i < jsonObj.valuelist.length; i++){')
        oL.append('                            var id=jsonObj.valuelist[i].id;')
        oL.append('                            var val=jsonObj.valuelist[i].value;')
        oL.append('                            console.log("id="+id+" value="+val);')
        oL.append('                            id = id.replace(/:/g,"\\\\:");')
        oL.append('                            $(id).html(val);')
        oL.append('                        }')
        oL.append('                        editNumber=jsonObj.editOpNumber;')
        oL.append('                        if (editNumber > 0) {')
        oL.append('                            $("#buttonUndo").show()')
        oL.append('                        } else {')
        oL.append('                            $("#buttonUndo").hide()')
        oL.append('                        }')
        # oL.append('                    })')
        oL.append('                   } catch (err) {')
        oL.append('                    $(".errmsg").html(errStyle + "Error: " + JSON.stringify(jsonObj)).show().delay(30000).slideUp(800)')
        oL.append('                   }')
        oL.append('            }')
        oL.append('        })')
        oL.append('    });')

        oL.append('$("#closewindow").click(function () {')
        oL.append('self.close()')
        oL.append('});')

    def __jQueryTableEditScript1(self, tableList, eD, oL):

        # Context  that will get encoded for call back --
        filePath = eD['filePath']
        localPath = eD['localPath']
        localRelativePath = eD['localRelativePath']
        sessionId = eD['sessionId']
        editOpNumber = eD['editOpNumber']
        blockId = eD['blockId']
        #
        #
        # Text input controls
        #
        oL.append('<script type="text/javascript">')
        oL.append('     var editNumber        = %d;' % editOpNumber)
        oL.append('     var filePath          = "%s";' % filePath)
        oL.append('     var localPath         = "%s";' % localPath)
        oL.append('     var localRelativePath = "%s";' % localRelativePath)
        oL.append('     var blockId           = "%s";' % blockId)
        oL.append('     var sessionId         = "%s";' % sessionId)
        oL.append('     var ajaxTimeout       = 60000;')
        oL.append('$(document).ready(function(){')
        #
        oL.append('    $.ajaxSetup({')
        oL.append('        type: "POST",')
        oL.append('        dataType: "json",')
        oL.append('        async: true,')
        oL.append('        timeout: ajaxTimeout,')
        oL.append('        cache: false')
        oL.append('    });')
        #
        oL.append('    function updateButtonState() {')
        oL.append('         if (editNumber > 0) {')
        oL.append('              $("#buttonUndo").show()')
        oL.append('              $("#buttonSave").show()')
        oL.append('         } else {')
        oL.append('              $("#buttonUndo").hide()')
        oL.append('              $("#buttonSave").hide()')
        oL.append('         }')
        oL.append('     }')
        #
        # oL.append('	$("#%s").tablesorter();' % tableId)
        #
        oL.append('     updateButtonState();')
        #
        oL.append('	$(".editinp").editable("/service/cc/edit/update",')
        oL.append('      {ajaxoptions: {dataType: "json"}, width: 150,')
        oL.append('       submitdata: function (value, setttings) { ')
        # oL.append('         var targetRowId = $(this).parents("tr").attr("id");')
        # oL.append('         var myId = $(this).attr("id");')
        # oL.append('         console.log("targetRowId ="+targetRowId);')
        # oL.append('         console.log("myId ="+myId);')
        oL.append('         return {')
        oL.append('          "rowUpdate"         : "%s",' % 'no')
        oL.append('          "filePath"          : filePath,')
        oL.append('          "localPath"         : localPath,')
        oL.append('          "localRelativePath" : localRelativePath,')
        oL.append('          "sessionid"         : sessionId,')
        oL.append('          "blockId"           : blockId,')
        oL.append('          "priorValue"        : value,')
        oL.append('          "targetRowId"       : $(this).parents("tr").attr("id"),')
        oL.append('          "editOpNumber"      : editNumber')
        oL.append('           }')
        oL.append('       }, ')
        oL.append('       callback : function(jsonObj, settings) {')
        oL.append('                    $(this).html(jsonObj.value);')
        oL.append('                    editNumber=jsonObj.editOpNumber;')
        oL.append('                    console.log("jsonObj.editOpNumber="+jsonObj.editOpNumber);')
        oL.append('                    console.log("editNumber="+editNumber);')
        oL.append('                    updateButtonState();')
        oL.append('                  }')
        oL.append('       } );')
        #
        #  Text area --
        #
        oL.append('$(".edittxtarea").editable("/service/cc/edit/update", {type:"textarea", submit:"OK", style: "display: inline",')
        oL.append('     ajaxoptions: {dataType: "json"}, width: 150,')
        oL.append('     submitdata: function (value, setttings) { return {')
        oL.append('        "rowUpdate"         : "%s",' % 'no')
        oL.append('        "filePath"          : filePath,')
        oL.append('        "localPath"         : localPath,')
        oL.append('        "localRelativePath" : localRelativePath,')
        oL.append('        "sessionid"         : sessionId,')
        oL.append('        "priorValue"        : value,')
        oL.append('        "targetRowId"       : $(this).parents("tr").attr("id"),')
        oL.append('        "editOpNumber"      : editNumber')
        oL.append('           }')
        oL.append('       }, ')
        oL.append('       callback : function(jsonObj, settings) {')
        oL.append('                    $(this).html(jsonObj.value);')
        oL.append('                    editNumber=jsonObj.editOpNumber;')
        oL.append('                    console.log("jsonObj.editOpNumber="+jsonObj.editOpNumber);')
        oL.append('                    console.log("editNumber="+editNumber);')
        oL.append('                    updateButtonState();')
        oL.append('                  }')
        oL.append('});')

        #
        #  Insert/Delete control --
        #
        oL.append('$(".editrow").editable("/service/cc/edit/update", {type:"select", width: 50,')
        oL.append('   data : {')
        for ev, ed in self.__enumRowList[:-1]:
            oL.append("     '%s':'%s'," % (ev, ed))
        (ev, ed) = self.__enumRowList[-1]
        oL.append("       '%s':'%s'" % (ev, ed))
        oL.append('   },')
        oL.append('   submitdata: function (value, settings) {')
        oL.append('          console.log($(this).parent("tr").attr("id"));')
        oL.append('          console.log($(this).parents("tr").attr("id"));')
        oL.append('           return {')
        oL.append('        "rowUpdate"         : "%s",' % 'yes')
        oL.append('        "filePath"          : filePath,')
        oL.append('        "localPath"         : localPath,')
        oL.append('        "localRelativePath" : localRelativePath,')
        oL.append('        "sessionid"         : sessionId,')
        oL.append('        "priorValue"        : $(this).parents("tr").filter(":first").html(),')
        oL.append('        "targetRowId"       : $(this).parents("tr").attr("id"),')
        oL.append('        "editOpNumber"      : editNumber')
        oL.append('           }')
        oL.append('        }, ')
        oL.append('   ajaxoptions: {dataType: "json"}, submit:"OK", style: "display: inline",')
        oL.append('   callback : function(jsonObj, settings) {')
        oL.append('                    $(this).html(jsonObj.value);')
        oL.append('                    editNumber=jsonObj.editOpNumber;')
        oL.append('                    console.log("jsonObj.editOpNumber="+jsonObj.editOpNumber);')
        oL.append('                    console.log("editNumber="+editNumber);')
        oL.append('                    console.log("op="+jsonObj.op);')
        oL.append('                    console.log("id="+jsonObj.id);')
        oL.append('                    var idU = jsonObj.id;')
        oL.append('                    if (jsonObj.op == "delete") {')
        oL.append('                       idU = idU.replace(/:/g,"\\\\:");')
        oL.append('                       console.log("idU="+idU);')
        oL.append('                       $(idU).parents("tr").filter(":first").remove();')
        oL.append('                     } else if (jsonObj.op == "insert-after")  {')
        oL.append('                     } else if (jsonObj.op == "insert-before") {')
        oL.append('                     }')
        oL.append('                    updateButtonState();')
        oL.append('               }')
        oL.append('});')

        #
        # Text input controls for items with controled vocabularies.
        #        write out all of the enum classes --
        #
        for nm, enumList in self.__enumDict.items():

            oL.append('$(".editsel_%s").editable("/service/cc/edit/update", {type:"select",' % nm)
            oL.append('   data : {')
            for ev, ed in enumList[:-1]:
                oL.append("      '%s':'%s'," % (ev, ed))
            (ev, ed) = enumList[-1]
            oL.append("      '%s':'%s'" % (ev, ed))
            oL.append('   },')
            oL.append('   submitdata: function (value, setttings) { return {')
            oL.append('        "rowUpdate"         : "%s",' % 'no')
            oL.append('        "filePath"          : filePath,')
            oL.append('        "localPath"         : localPath,')
            oL.append('        "localRelativePath" : localRelativePath,')
            oL.append('        "sessionid"         : sessionId,')
            oL.append('        "priorValue"        : value,')
            oL.append('        "targetRowId"       : $(this).parents("tr").attr("id"),')
            oL.append('        "editOpNumber"      : editNumber')
            oL.append('         }')
            oL.append('    }, ')
            oL.append('    ajaxoptions: {dataType: "json"}, submit:"OK", style: "display: inline",')
            oL.append('    callback : function(jsonObj, settings) {')
            oL.append('                    $(this).html(jsonObj.value);')
            oL.append('                    editNumber=jsonObj.editOpNumber;')
            oL.append('                    console.log("jsonObj.editOpNumber="+jsonObj.editOpNumber);')
            oL.append('                    console.log("editNumber="+editNumber);')
            oL.append('                    updateButtonState();')
            oL.append('                  }')
            oL.append('});')

        #
        dS = ""
        for t in tableList[:-1]:
            dS += "#d_%s, " % t
        dS += "#d_%s" % tableList[-1]
        oL.append('$("%s").hide();' % dS)

        #
        tS = ""
        for t in tableList[:-1]:
            tS += "#toggle_section_%s, " % t
        tS += "#toggle_section_%s" % tableList[-1]

        oL.append('$("%s").click(function() {' % tS)
        oL.append('        console.log("TOGGLE VALUE "+$(this).text());')
        oL.append('        $(this).parents("div").filter(":first").next().toggle(400);')
        oL.append('        $(this).text($(this).text() == "Edit" ? "Hide" : "Edit");')
        oL.append('        return false;')
        oL.append(' });')

        oL.append(' $(".sectionbar1").corner("round");')

        # button controls --
        self.__jQueryButtonScripts(eD, oL)
        #
        oL.append('});')

        oL.append('</script>')

    # def __categoryPart(self, name):
    #     tname = ""
    #     if name.startswith("_"):
    #         tname = name[1:]
    #     else:
    #         tname = name

    #     i = tname.find(".")
    #     if i == -1:
    #         return tname
    #     else:
    #         return tname[:i]

    def __attributePart(self, name):
        i = name.find(".")
        if i == -1:
            return None
        else:
            return name[i + 1:]

    def __setup(self):
        """ Enumeration details --
        """
        #
        self.__enumRowList = [("insert", "Insert"), ("delete", "Delete")]
        #
        self.__itemEnumMap = {
            '_chem_comp.mon_nstd_parent_comp_id': 'parentCCList',
            '_chem_comp.type': 'ccTypeList',
            '_chem_comp.pdbx_type': 'ndbTypeList',
            '_chem_comp_atom.pdbx_leaving_atom_flag': 'ynList',
            '_chem_comp_atom.pdbx_stereo_config': 'rsList',
            '_chem_comp_bond.pdbx_stereo_config': 'ezList',
            '_chem_comp_bond.pdbx_aromatic_flag': 'ynList',
            '_chem_comp_atom.pdbx_aromatic_flag': 'ynList',
            '_chem_comp_bond.value_order': 'bondTypeList'
        }
        #

        self.__enumDict = {'ynList': [("Y", "Y"), ("N", "N")],
                           'rsList': [("R", "R"), ("S", "S"), ("N", "N")],
                           'ezList': [("E", "E"), ("Z", "Z"), ("N", "N")],
                           'parentCCList' : [
                               ("?", "?"),
                               ("A", "A"),
                               ("C", "C"),
                               ("G", "G"),
                               ("T", "T"),
                               ("U", "U"),
                               ("DA", "DA"),
                               ("DC", "DC"),
                               ("DG", "DG"),
                               ("DT", "DT"),
                               ("DU", "DU"),
                               ("ALA", "ALA"),
                               ("ARG", "ARG"),
                               ("ASN", "ASN"),
                               ("ASP", "ASP"),
                               ("CYS", "CYS"),
                               ("GLN", "GLN"),
                               ("GLU", "GLU"),
                               ("GLY", "GLY"),
                               ("HIS", "HIS"),
                               ("ILE", "ILE"),
                               ("LEU", "LEU"),
                               ("LYS", "LYS"),
                               ("MET", "MET"),
                               ("PHE", "PHE"),
                               ("PRO", "PRO"),
                               ("SER", "SER"),
                               ("THR", "THR"),
                               ("TRP", "TRP"),
                               ("TYR", "TYR"),
                               ("VAL", "VAL")],
                           'ccTypeList' : [
                               ("non-polymer", "non-polymer"),
                               ("D-peptide linking", "D-peptide linking"),
                               ("L-peptide linking", "L-peptide linking"),
                               ("D-peptide NH3 amino terminus", "D-peptide NH3 amino terminus"),
                               ("L-peptide NH3 amino terminus", "L-peptide NH3 amino terminus"),
                               ("D-peptide COOH carboxy terminus", "D-peptide COOH carboxy terminus"),
                               ("L-peptide COOH carboxy terminus", "L-peptide COOH carboxy terminus"),
                               ("DNA linking", "DNA linking"),
                               ("RNA linking", "RNA linking"),
                               ("DNA OH 5 prime terminus", "DNA OH 5 prime terminus"),
                               ("RNA OH 5 prime terminus", "RNA OH 5 prime terminus"),
                               ("DNA OH 3 prime terminus", "DNA OH 3 prime terminus"),
                               ("RNA OH 3 prime terminus", "RNA OH 3 prime terminus"),
                               ("D-saccharide 1,4 and 1,4 linking", "D-saccharide 1,4 and 1,4 linking"),
                               ("L-saccharide 1,4 and 1,4 linking", "L-saccharide 1,4 and 1,4 linking"),
                               ("D-saccharide 1,4 and 1,6 linking", "D-saccharide 1,4 and 1,6 linking"),
                               ("L-saccharide 1,4 and 1,6 linking", "L-saccharide 1,4 and 1,6 linking"),
                               ("L-saccharide", "L-saccharide"),
                               ("D-saccharide", "D-saccharide"),
                               ("saccharide", "saccharide")],

                           'ndbTypeList' : [
                               ("HETAIN", "HETAIN (heterogen/inhibitor)"),
                               ("ATOMN", "ATOMN (nucleic acid or modified nucleic acid)"),
                               ("ATOMP", "ATOMP (amino acid or modified amino acid)"),
                               ("ATOMS", "ATOMS (polysaccharide)"),
                               ("HETAC", "HETAC (coenzyme)"),
                               ("HETAD", "HETAD (drug)"),
                               ("HETAI", "HETAI (ion)"),
                               ("HETAS", "HETAS (solvent)"),
                               ("HETIC", "HETIC (complexed ion)")],
                           'bondTypeList' : [
                               ("SING", "Single bond"),
                               ("DOUB", "Double bond"),
                               ("TRIP", "Triple bond"),
                               ("QUAD", "Quadruple bond"),
                               ("DELO", "Delocalized Pi bond"),
                               ("PI", "Pi bond")]
                           }
