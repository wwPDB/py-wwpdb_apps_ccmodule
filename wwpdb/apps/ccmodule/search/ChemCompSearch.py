"""
File:     ChemCompSearch.py
Date:     11-Aug-2010 J. Westbrook

Updated:
11-Aug-2010  jdw   ported to ccmodule


"""
import os
import os.path
import sys
from wwpdb.apps.ccmodule.utils.ChemCompConfig import ChemCompConfig


class ChemCompSearch(object):
    def __init__(self, reqObj, verbose=False, log=sys.stderr):
        self.__verbose = verbose
        self.__lfh = log
        self.__reqObj = reqObj
        #
        self.__sObj = self.__reqObj.newSessionObj()
        self.__sessionPath = self.__sObj.getPath()
        self.__sessionRelativePath = self.__sObj.getRelativePath()
        self.__sessionId = self.__sObj.getId()

        self.__ccConfig = ChemCompConfig(self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        #
        self.iQueryTypes = {"formula-exact": "Formula (exact)",
                            "formula-heavy-exact": "Formula (heavy atom exact)",
                            "formula-exact-subset": "Formula (exact subset)",
                            "formula-subset": "Formula (subset)",
                            "name-exact": "Molecular name (exact)",
                            "name-substring": "Molecular name (exact sub-string)",
                            "name-close": "Molecular name (close)",
                            "name-similar": "Molecular name (similar)",
                            "smiles-exact": "SMILES",
                            "smiles": "Containing SMILES pattern",
                            "fpcc": "Similar to component (3-letter code)",
                            "fpsmi": "Similar to chemical fingerprint",
                            "inchi-substring": "InChI",
                            "inchikey-substring": "InChIKey",
                            "subcomplist-exact": "Subcomponent list (exact)",
                            "subcomplist-substring": "Subcomponent list (substring)"}

        self.ssQueryTypes = {"prefilter-strict": "Strict (all atom)",
                             "prefilter-skip-h-strict": "Strict (heavy atom)",
                             "prefilter-relaxed": "Relaxed (all atom/connectivity only)",
                             "prefilter-skip-h-relaxed": "Relaxed (heavy atom/connectivity only)",
                             "prefilter-skip-h-close": "Close (formula bounded)",
                             "prefilter-skip-h-subset": "Close (formula subset)"}

    def addWordBreakAtHyphen(self, iString):
        oString = ""
        for i in iString:
            if i == '-':
                oString += i
                oString += "<wbr />"
            else:
                oString += i
        return oString

    def addWordBreakAtPunct(self, iString):
        oString = ""
        for i in iString:
            if i == ')' or i == ']':
                oString += i
                oString += "<wbr />"
            else:
                oString += i
        return oString

    def doIndex(self):
        """ Index search for name or formula.
        """
        op = self.__reqObj.getValue("operation")
        target = self.__reqObj.getValue("target")
        target = target.strip()
        retDict = {}
        #
        if op.startswith("formula"):
            # reformat input formula - El## El## ...
            lt = target.upper().split(' ')
            # standardize counts
            l = []  # noqa: E741
            for el in lt:
                if not el[-1].isdigit():
                    el += "1"
                l.append(el)

            tt = ''.join(l)
            if len(tt) > 0:
                aa = tt[0]
                for i in range(1, len(tt)):
                    if (tt[i - 1].isdigit() and tt[i].isalpha()):
                        aa += " "
                    aa += tt[i]
                target = aa
        #
        if op.startswith("formula"):
            qType = "formula"
        elif op.startswith("name"):
            qType = "name"
        elif op.startswith("smiles"):
            qType = "smiles"
        elif op.startswith("fpcc"):
            qType = "fpcc"
        elif op.startswith("fpsmi"):
            qType = "fpsmi"
        elif op.startswith("inchikey"):
            qType = "inchikey"
        elif op.startswith("inchi"):
            qType = "inchi"
        elif op.startswith("subcomplist"):
            qType = "subcomponentlist"
        else:
            qType = "unknown"
        #
        scriptPath = self.__ccConfig.getPath('matchApp')
        ccIndexPath = self.__ccConfig.getPath('serializedCcIndexPath')
        ccDictPath = self.__ccConfig.getPath('serializedCcDictPath')
        outputFile = "index-search.out"
        cmd = "cd %s ; %s  -type %s -index %s  -query \"%s\"  -op %s -o %s " % \
              (self.__sessionPath, scriptPath, qType, ccIndexPath, target, op, outputFile)

        if (self.__verbose):
            self.__lfh.write("Beginning report in path = %s\n" % self.__sessionPath)
            self.__lfh.write("Target                   = %s\n" % target)
            self.__lfh.write("Type                     = %s\n" % qType)
            self.__lfh.write("Operation                = %s\n" % op)
            self.__lfh.write("Script path              = %s\n" % scriptPath)
            self.__lfh.write("Index  path              = %s\n" % ccIndexPath)
            self.__lfh.write("Serialized dictionary    = %s\n" % ccDictPath)
            self.__lfh.write("Search command           = %s\n" % cmd)

        os.system(cmd)
        #
        outputFile = os.path.join(self.__sessionPath, outputFile)
        if (not os.access(outputFile, os.F_OK)):
            if (self.__verbose):
                self.__lfh.write("++INFO -  %s does not exist\n" % outputFile)
                return retDict

        with open(outputFile, 'r') as f:
            oLines = f.readlines()
        #
        lineOne = str(oLines[0]).strip().split('\t')
        query = str(lineOne[0])
        queryType = str(lineOne[1])
        count = lineOne[2]
        #
        rList = []
        for line in oLines[1:]:
            rD = {}
            lT = str(line).split('\t')
            rD['ccid'] = str(lT[0])
            rD['name'] = self.addWordBreakAtHyphen(str(lT[1]))
            if (len(lT) > 2):
                rD['formula'] = str(lT[2])
            else:
                rD['formula'] = ""
            rD['creator'] = str(lT[5])
            rD['status'] = str(lT[6])
            rD['subcomplist'] = str(lT[7])
            rList.append(rD)

        retDict = {"sessionid": self.__sessionId,
                   "query": query,
                   "querytype": self.iQueryTypes[queryType],
                   "count": count,
                   "resultlist": rList}
        #

        return retDict

    def doGraphIso(self):
        """ Graph Isomorphism search
        """
        op = self.__reqObj.getValue("operation")
        #
        # File path relative to the current session directory path -
        #
        fileName = self.__reqObj.getValue("fileName")

        retDict = self.doGraphIsoFile(fileName, op)
        return retDict

    def doGraphIsoFile(self, filePath, op):
        #
        tab = '\t'
        retDict = {}
        #
        scriptPath = self.__ccConfig.getPath('matchApp')
        ccIndexPath = self.__ccConfig.getPath('serializedCcIndexPath')
        ccDictPath = self.__ccConfig.getPath('serializedCcDictPath')
        patternPath = self.__ccConfig.getPath('fpPatternPath')
        outputFile = "ss-search.out"
        outputEmFile = "ss-search-em.out"
        qType = "structure"
        #
        cmd = "cd %s ; %s  -type %s -index %s -fplib %s  -lib %s -i %s  -op %s  -o %s -om %s " % \
              (self.__sessionPath, scriptPath, qType, ccIndexPath, patternPath, ccDictPath, filePath, op, outputFile, outputEmFile)

        if (self.__verbose):
            self.__lfh.write("Beginning report in path = %s\n" % self.__sessionPath)
            self.__lfh.write("Target filename          = %s\n" % filePath)
            self.__lfh.write("Operation                = %s\n" % op)
            self.__lfh.write("Script path              = %s\n" % scriptPath)
            self.__lfh.write("Index  path              = %s\n" % ccIndexPath)
            self.__lfh.write("Serialized dictionary    = %s\n" % ccDictPath)
            self.__lfh.write("Search command           = %s\n" % cmd)

        os.system(cmd)
        #
        outputFile = os.path.join(self.__sessionPath, outputFile)
        if (not os.access(outputFile, os.F_OK)):
            if (self.__verbose):
                self.__lfh.write("++INFO -  %s does not exist\n" % outputFile)
                return retDict

        outputEmFile = os.path.join(self.__sessionPath, outputEmFile)
        if (not os.access(outputEmFile, os.F_OK)):
            if (self.__verbose):
                self.__lfh.write("++INFO -  %s does not exist\n" % outputEmFile)
                return retDict

        f = open(outputFile, 'r')
        oLines = f.readlines()
        f.close()
        #
        f = open(outputEmFile, 'r')
        emLines = f.readlines()
        f.close()
        #

        lineOne = str(oLines[0]).strip().split(tab)
        queryFile = str(lineOne[0])
        queryType = str(lineOne[1])
        count = int(str(lineOne[2]))
        nameTarget = ""
        formulaTarget = ""
        heavyAtomCountTarget = 0
        if (len(oLines) > 1):
            lT = str(oLines[1]).split(tab)
            nameTarget = lT[1]
            formulaTarget = lT[2]
            heavyAtomCountTarget = lT[3]
        #
        # Read
        #
        rList = []
        for line in oLines[1:]:
            rD = {}
            lT = str(line).split(tab)
            rD['ccidTarget'] = lT[0]
            rD['nameTarget'] = lT[1]
            rD['formulaTarget'] = lT[2]
            rD['heavyAtomCountTarget'] = lT[3]
            rD['ccidReference'] = lT[4]
            idRef = lT[4]
            rD['nameReference'] = lT[5]
            rD['formulaReference'] = lT[6]
            rD['heavyAtomCountReference'] = lT[7]
            fn1 = os.path.join(self.__sessionPath, idRef + "-em.txt")
            rD['mappingFile'] = os.path.join(self.__sessionRelativePath, fn1)
            f = open(fn1, 'w')
            for emline in emLines:
                lT1 = str(emline).split(tab)
                if (lT1[1] == idRef):
                    ol = lT1[0] + tab + lT1[2] + tab + lT1[1] + tab + lT1[4]
                    f.write("%s\n" % ol)
            f.close()
            rList.append(rD)
        #
        retDict = {"sessionid": self.__sessionId,
                   "queryfile": queryFile,
                   "querytype": self.ssQueryTypes[queryType],
                   "count": count,
                   "nametarget": nameTarget,
                   "formulatarget": formulaTarget,
                   "heavyatomcounttarget": heavyAtomCountTarget,
                   "resultlist": rList}

        return retDict
