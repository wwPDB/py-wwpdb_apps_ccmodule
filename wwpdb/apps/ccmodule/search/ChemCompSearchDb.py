##
# File:  ChemCompSearchDb.py
# Date:  11-Aug-2010  J. Westbrook
#
# Update:
# 11-Aug-2010   jdw ported to ccmodule framework
# 19-Apr-2012   rps updated to accommodate siteId == "WWPDB_DEPLOY"
# 14-Sep-2015   rps updated to use ConfigInfo for getting site related config
# 15-Mar-2016   rps updated to derive database port number from ConfigInfo
#                    replacing use of "nonstandard_groups" table with use of "chem_comp" table.
##
"""


mysql> describe chem_comp;
+-------------------------------------+---------------+------+-----+---------+-------+
| Field                               | Type          | Null | Key | Default | Extra |
+-------------------------------------+---------------+------+-----+---------+-------+
| Structure_ID                        | varchar(10)   | NO   | PRI | NULL    |       |
| formula                             | varchar(200)  | YES  |     | NULL    |       |
| formula_weight                      | float         | YES  |     | NULL    |       |
| id                                  | varchar(10)   | NO   | PRI | NULL    |       |
| model_details                       | varchar(200)  | YES  |     | NULL    |       |
| model_erf                           | varchar(80)   | YES  |     | NULL    |       |
| model_source                        | varchar(200)  | YES  |     | NULL    |       |
| mon_nstd_class                      | varchar(200)  | YES  |     | NULL    |       |
| mon_nstd_details                    | varchar(200)  | YES  |     | NULL    |       |
| mon_nstd_flag                       | varchar(10)   | YES  |     | NULL    |       |
| mon_nstd_parent                     | varchar(10)   | YES  |     | NULL    |       |
| mon_nstd_parent_comp_id             | varchar(80)   | YES  |     | NULL    |       |
| name                                | varchar(1023) | YES  |     | NULL    |       |
| number_atoms_all                    | int(11)       | YES  |     | NULL    |       |
| number_atoms_nh                     | int(11)       | YES  |     | NULL    |       |
| one_letter_code                     | varchar(10)   | YES  |     | NULL    |       |
| three_letter_code                   | varchar(4)    | YES  |     | NULL    |       |
| type                                | varchar(80)   | YES  |     | NULL    |       |
| pdbx_synonyms                       | varchar(511)  | YES  |     | NULL    |       |
| pdbx_modification_details           | varchar(200)  | YES  |     | NULL    |       |
| pdbx_component_no                   | int(11)       | YES  |     | NULL    |       |
| pdbx_type                           | varchar(80)   | YES  |     | NULL    |       |
| pdbx_ambiguous_flag                 | varchar(10)   | YES  |     | NULL    |       |
| pdbx_replaced_by                    | varchar(10)   | YES  |     | NULL    |       |
| pdbx_replaces                       | varchar(80)   | YES  |     | NULL    |       |
| pdbx_formal_charge                  | int(11)       | YES  |     | NULL    |       |
| pdbx_subcomponent_list              | varchar(200)  | YES  |     | NULL    |       |
| pdbx_model_coordinates_details      | varchar(200)  | YES  |     | NULL    |       |
| pdbx_model_coordinates_db_code      | varchar(80)   | YES  |     | NULL    |       |
| pdbx_ideal_coordinates_details      | varchar(200)  | YES  |     | NULL    |       |
| pdbx_ideal_coordinates_missing_flag | varchar(10)   | YES  |     | NULL    |       |
| pdbx_model_coordinates_missing_flag | varchar(10)   | YES  |     | NULL    |       |
| pdbx_initial_date                   | datetime      | YES  |     | NULL    |       |
| pdbx_modified_date                  | datetime      | YES  |     | NULL    |       |
| pdbx_release_status                 | varchar(80)   | YES  |     | NULL    |       |
| pdbx_processing_site                | varchar(10)   | YES  |     | NULL    |       |
+-------------------------------------+---------------+------+-----+---------+-------+


mysql> describe pdb_entry;
+----------------------------+--------------+------+-----+---------+-------+
| Field                      | Type         | Null | Key | Default | Extra |
+----------------------------+--------------+------+-----+---------+-------+
| Structure_ID               | varchar(11)  | NO   | PRI |         |       |
| pdb_id                     | varchar(8)   | NO   | MUL |         |       |
| rcsb_annotator             | varchar(10)  | YES  |     | NULL    |       |
| status_code                | varchar(10)  | YES  |     | NULL    |       |
| author_release_status_code | varchar(10)  | YES  |     | NULL    |       |
| deposit_site               | varchar(10)  | YES  |     | NULL    |       |
| process_site               | varchar(10)  | YES  |     | NULL    |       |
| initial_deposition_date    | date         | YES  |     | NULL    |       |
| date_author_approval       | date         | YES  |     | NULL    |       |
| recvd_author_approval      | varchar(1)   | YES  |     | NULL    |       |
| author_approval_type       | varchar(10)  | YES  |     | NULL    |       |
| date_hold_coordinates      | date         | YES  |     | NULL    |       |
| date_hold_struct_fact      | date         | YES  |     | NULL    |       |
| date_hold_nmr_constraints  | date         | YES  |     | NULL    |       |
| date_of_RCSB_release       | date         | YES  |     | NULL    |       |
| date_deposition_form       | date         | YES  |     | NULL    |       |
| date_coordinates           | date         | YES  |     | NULL    |       |
| date_struct_fact           | date         | YES  |     | NULL    |       |
| date_manuscript            | date         | YES  |     | NULL    |       |
| date_nmr_constraints       | date         | YES  |     | NULL    |       |
| replaced_entry_id          | varchar(10)  | YES  |     | NULL    |       |
| revision_description       | varchar(255) | YES  |     | NULL    |       |
| author_list                | varchar(500) | YES  |     | NULL    |       |
| title                      | varchar(500) | YES  |     | NULL    |       |
| titleUC                    | varchar(500) | YES  |     | NULL    |       |
| date_last_update           | date         | YES  |     | NULL    |       |
| author_release_sequence    | varchar(20)  | YES  |     | NULL    |       |
| status_code_sf             | varchar(10)  | YES  |     | NULL    |       |
| status_code_mr             | varchar(10)  | YES  |     | NULL    |       |
| SG_entry                   | varchar(50)  | YES  |     | NULL    |       |
| date_of_sf_release         | date         | YES  |     | NULL    |       |
| date_of_mr_release         | date         | YES  |     | NULL    |       |
| method                     | varchar(80)  | YES  |     | NULL    |       |
| header                     | varchar(80)  | YES  |     | NULL    |       |
| ebi_id                     | varchar(10)  | YES  |     | NULL    |       |
| ndb_id                     | varchar(10)  | YES  |     | NULL    |       |
| suppressed_title_Y_N       | varchar(2)   | YES  |     | NULL    |       |
+----------------------------+--------------+------+-----+---------+-------+

"""

import sys
import wwpdb.apps.ccmodule.search.DbSession as DbSession
from wwpdb.utils.config.ConfigInfo import ConfigInfo


class ChemCompSearchDb(object):
    def __init__(self, reqObj, verbose=False, log=sys.stderr):
        self.__reqObj = reqObj
        self.__verbose = verbose
        self.__lfh = log
        #
        self.__sObj = self.__reqObj.newSessionObj()
        self.__sessionPath = self.__sObj.getPath()
        # self.__sessionRelativePath = self.__sObj.getRelativePath()
        self.__sessionId = self.__sObj.getId()

        #
        # self.__ccConfig=ChemCompConfig(self.__reqObj, verbose=self.__verbose,log=self.__lfh)
        #
        siteId = self.__reqObj.getValue("WWPDB_SITE_ID")
        self.__cI = ConfigInfo(siteId)
        self.dbUser = self.__cI.get('SITE_INSTANCE_DB_USER_NAME')
        self.dbPw = self.__cI.get('SITE_INSTANCE_DB_PASSWORD')
        self.dbName = self.__cI.get('SITE_INSTANCE_DB_NAME')
        self.dbHost = self.__cI.get('SITE_INSTANCE_DB_HOST_NAME')
        self.dbServer = self.__cI.get('SITE_DB_SERVER')
        self.dbPort = self.__cI.get('SITE_INSTANCE_DB_PORT_NUMBER')

        self.db = None
        self.dbcon = None

    def _openSession(self):
        """ create a db session -
        """
        self.db = DbSession.DbSession(dbServer=self.dbServer, dbHost=self.dbHost, dbName=self.dbName, dbUser=self.dbUser, dbPw=self.dbPw, dbPort=self.dbPort)
        self.dbcon = self.db.connect()
        #

    def _closeSession(self):
        """ close db session
        """
        self.dbcon.close()

    def _getMethod(self, meth):
        if meth.find("x-ray") != -1:
            return "x-ray"
        elif meth.find("nmr") != -1:
            return "nmr"
        else:
            return meth

    def _runIdSearch(self, ccId, op):
        """Return a list of structures containing the input component id.
        """
        rList = []
        curs = self.dbcon.cursor()
        if (op == "LIKE"):
            pc = "%"
            tccId = pc + ccId + pc
            constraint = "where chem_comp.id LIKE \"%s\" and chem_comp.Structure_ID = pdb_entry.pdb_id order by pdb_entry.date_of_RCSB_release DESC " % tccId
        else:
            constraint = "where chem_comp.id = \"%s\" and chem_comp.Structure_ID = pdb_entry.pdb_id order by pdb_entry.date_of_RCSB_release DESC " % ccId

        query = "select distinct chem_comp.Structure_ID,pdb_entry.method,pdb_entry.title,pdb_entry.date_of_RCSB_release,pdb_entry.status_code,pdb_entry.Structure_ID,chem_comp.id from chem_comp,pdb_entry  " + constraint  # noqa: E501
        if self.__verbose:
            self.__lfh.write("SQL Id query: %s\n" % query)
        curs.execute(query)
        while True:
            result = curs.fetchone()
            if (result is not None):
                entry = {}
                entry['pdbId'] = result[0]
                meth = str(result[1]).lower()
                entry['method'] = self._getMethod(meth)
                entry['title'] = result[2]
                entry['releaseDate'] = result[3]
                entry['status'] = result[4]
                entry['rcsbId'] = result[5]
                entry['compId'] = result[6]
                rList.append(entry)
            else:
                break
        return rList

    def _runIdHoldSearch(self, ccId, op):
        """Return a list of structures on HOLD containing the input component id.
        """
        rList = []

        curs = self.dbcon.cursor()
        if (op == 'LIKE'):
            pc = "%"
            tccId = pc + ccId + pc
            constraint = "where chem_comp.id LIKE \"%s\" and pdb_entry.status_code != \"REL\" and chem_comp.Structure_ID = pdb_entry.Structure_ID order by pdb_entry.initial_deposition_date DESC " % tccId  # noqa: E501
        else:
            constraint = "where chem_comp.id = \"%s\" and pdb_entry.status_code != \"REL\" and chem_comp.Structure_ID = pdb_entry.Structure_ID order by pdb_entry.initial_deposition_date DESC " % ccId  # noqa: E501

        query = "select distinct chem_comp.Structure_ID,pdb_entry.method,pdb_entry.title,pdb_entry.initial_deposition_date,pdb_entry.status_code,chem_comp.id from chem_comp,pdb_entry  " + constraint  # noqa: E501

        if self.__verbose:
            self.__lfh.write("SQL Id query: %s\n" % query)
        curs.execute(query)
        while True:
            result = curs.fetchone()
            if (result is not None):
                entry = {}
                entry['rcsbId'] = result[0]
                meth = str(result[1]).lower()
                entry['method'] = self._getMethod(meth)
                entry['title'] = result[2]
                entry['depositionDate'] = result[3]
                entry['status'] = result[4]
                entry['compId'] = result[5]
                rList.append(entry)
            else:
                break
        return rList

    def doIdSearch(self):
        """ Index for structure containing a component.
        """
        targetId = self.__reqObj.getValue("targetId")
        searchOp = self.__reqObj.getValue("searchOp")
        retDict = {}
        if (targetId is None or len(targetId) < 1):
            return retDict
        #
        if (self.__verbose):
            self.__lfh.write("Beginning report in path = %s\n" % self.__sessionPath)
            self.__lfh.write("Target ID                = %s\n" % targetId)
            self.__lfh.write("Search Operation         = %s\n" % searchOp)

        self._openSession()
        rList = self._runIdSearch(targetId, searchOp)
        oList = self._runIdHoldSearch(targetId, searchOp)
        self._closeSession()
        count = len(rList)
        countOther = len(oList)

        retDict = {"sid": self.__sessionId,
                   "targetid": targetId,
                   "searchOp": searchOp,
                   "count": count,
                   "countother": countOther,
                   "resultlist": rList,
                   "resultotherlist": oList}

        return retDict
