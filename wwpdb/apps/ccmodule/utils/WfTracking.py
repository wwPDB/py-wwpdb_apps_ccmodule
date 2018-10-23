##
# File:    WfTracking.py
# Date:    27-Apr-2010
#
# Updates:
#
##
"""
Classes in this module manage the update of the progress and tracking
database for ligand editing operations.

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.07"

import os,sys
import datetime

from wwpdb.api.status.dbapi.WfDbApi import WfDbApi
from wwpdb.api.status.dbapi.WFEtime import getTimeNow

class WfTracking(object):
    """Provides methods to update progress and tracking information in the WF status database.

    """
    def __init__(self,verbose=False,log=sys.stderr):
        self.__verbose=verbose
        self.__lfh=log

    def setInstanceStatus(self,depId=None,instId=None,classId=None,status=None):
        """Update a status record for the an instance step.
        """
        
        now = getTimeNow()
        DBstatusAPI = WfDbApi(verbose=self.__verbose)
        instD = {}
        instD['WF_INST_ID']  = instId
        instD['WF_CLASS_ID'] = classId
        instD['DEP_SET_ID']  = depId
        instD['INST_STATUS'] = status
        instD['STATUS_TIMESTAMP'] = now

        rd = DBstatusAPI.getObject(depId,classId, instId)
        if ((rd is None) or (len(rd) == 0)):
            self.__lfh.write("+WfTracking.setInstanceStatus() no status records for depId %s classId %s instId %s\n" %
                             (depId,classId,instId))
            # new insert --- 
            DBstatusAPI.saveObject(instD, 'insert')
            
# TOM : new table to update in parallel - 
#        Put in protection of system for ownership of the module
        sql = "update wf_instance_last set status_timestamp=" + str(now) + ", inst_status='" + str(status) + "' where dep_set_id = '" + depId + "' and wf_class_id = '" + classId + "' and wf_inst_id = '" + instId + "'"
        ok = DBstatusAPI.runUpdateSQL(sql)
	if ok < 1:
            self.__lfh.write("+WfTracking.setInstanceStatus() CRITICAL : failed to update wf_instance_last table \n")
            self.__lfh.write("+WfTracking.setInstanceStatus() Possible UI does not own module state \n")

        else:

        # Can update existing record using  ---
            DBstatusAPI.updateStatus(instD,status)
        
        # Verify the status
            if (self.__verbose):        
                rd = DBstatusAPI.getObject(depId,classId, instId)        
                self.__lfh.write("+WfTracking.setInstanceStatus() new status is: %r\n" % DBstatusAPI.getStatus(rd))

        return True

    def setTaskStatus(self,depId=None,instId=None,classId=None,taskId=None,status=None):
        """ Insert a status record for a task step.
        """
        now = getTimeNow()
        taskD = {}
        taskD['WF_TASK_ID']   = taskId
        taskD['WF_INST_ID']   = instId
        taskD['WF_CLASS_ID']  = classId
        taskD['DEP_SET_ID']   = depId
        taskD['TASK_STATUS']  = stsus
        taskD['STATUS_TIMESTAMP'] = now

        rd = DBstatusAPI.getObject(depId,classId,instId,taskId)
        if ((rd is None) or (len(rd) == 0)):
            self.__lfh.write("+WfTracking.setTaskStatus() no status records for depId %s classId %s instId %s taskId %s\n" %
                             (depId,classId,instId,taskId))
        
        DBstatusAPI.saveObject(taskD, 'insert')

        # To update a current record --- 
        #DBstatusAPI.updateStatus(taskID,"open")
        #DBstatusAPI.updateStatus(taskID,"closed(0)")
        #
        # Verify the status setting
        if (self.__verbose):        
            rd = DBstatusAPI.getObject(depId,classId, instId,taskId)        
            self.__lfh.write("+WfTracking.setTaskStatus() new status is: %r\n" % DBstatusAPI.getStatus(rd))        

        return True

    
