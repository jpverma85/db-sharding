#!/usr/bin/python

# LICENSE UPL 1.0
#
# Copyright (c) 2020,2021 Oracle and/or its affiliates.
#
# Since: January, 2020
# Author: sanjay.singh@oracle.com, paramdeep.saini@oracle.com


import os
import sys
import os.path
import re
import socket
from oralogger import *
from oraenv import *
from oracommon import *
from oramachine import *
import traceback

class OraPShard:
      """
      This calss setup the primary shard after DB installation.
      """
      def __init__(self,oralogger,orahandler,oraenv,oracommon):
        """
        This constructor of OraPShard class to setup the shard on primary DB.

        Attributes:
           oralogger (object): object of OraLogger Class.
           ohandler (object): object of Handler class.
           oenv (object): object of singleton OraEnv class.
           ocommon(object): object of OraCommon class.
           ora_env_dict(dict): Dict of env variable populated based on env variable for the setup.
           file_name(string): Filename from where logging message is populated.
        """
        try:
          self.ologger             = oralogger
          self.ohandler            = orahandler
          self.oenv                = oraenv.get_instance()
          self.ocommon             = oracommon
          self.ora_env_dict        = oraenv.get_env_vars()
          self.file_name           = os.path.basename(__file__)
          self.omachine            = OraMachine(self.ologger,self.ohandler,self.oenv,self.ocommon)
        except BaseException as ex:
          ex_type, ex_value, ex_traceback = sys.exc_info()
          trace_back = traceback.extract_tb(ex_traceback)
          stack_trace = list()
          for trace in trace_back:
              stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
          self.ocommon.log_info_message(ex_type.__name__,self.file_name)
          self.ocommon.log_info_message(ex_value,self.file_name)
          self.ocommon.log_info_message(stack_trace,self.file_name)
      def setup(self):
          """
           This function setup the shard on Primary DB.
          """
          self.check_for_racdb()
          if self.ocommon.check_key("ORACLE_FREE_PDB",self.ora_env_dict):
            self.ora_env_dict=self.ocommon.update_key("ORACLE_PDB",self.ora_env_dict["ORACLE_FREE_PDB"],self.ora_env_dict)
          if self.ocommon.check_key("RESET_LISTENER",self.ora_env_dict):
            status = self.shard_setup_check()
            if not status:
               self.ocommon.log_info_message("Primary shard is still not setup.Exiting...",self.file_name)
               self.ocommon.prog_exit("127")
            self.reset_listener()
            self.restart_listener()
          if self.ocommon.check_key("RESTART_DB",self.ora_env_dict):
            status = self.shard_setup_check()
            if not status:
               self.ocommon.log_info_message("Primary shard is still not setup.Exiting...",self.file_name)
               self.ocommon.prog_exit("127")
            else:
               self.ocommon.shutdown_db(self.ora_env_dict)
               self.ocommon.start_db(self.ora_env_dict) 
          elif self.ocommon.check_key("CHECK_LIVENESS",self.ora_env_dict):
             create_db_file_lck=self.ocommon.get_db_lock_location() + self.ora_env_dict["ORACLE_SID"] + ".create_lck"
             exist_db_file_lck=self.ocommon.get_db_lock_location() + self.ora_env_dict["ORACLE_SID"] + ".exist_lck"
             self.ocommon.log_info_message("DB create lock file set to :" + create_db_file_lck ,self.file_name)
             self.ocommon.log_info_message("DB exist lock file set to :" + exist_db_file_lck ,self.file_name)
             if os.path.exists(create_db_file_lck):
                self.ocommon.log_info_message("provisioning is still in progress as file " + create_db_file_lck + " still exist!",self.file_name)
                sys.exit(127)             
             elif os.path.exists(exist_db_file_lck):
                self.ocommon.log_info_message("Database is up and running as file " + exist_db_file_lck + " exist!",self.file_name)
                status = self.shard_setup_check()
                if not status:
                  self.ocommon.prog_exit("127")
                self.ocommon.log_info_message("Shard liveness check completed sucessfully!",self.file_name)
                sys.exit(0)
             else:
                status = self.shard_setup_check()
                if not status:
                  self.ocommon.prog_exit("127")
                self.ocommon.log_info_message("Shard liveness check completed sucessfully!",self.file_name)
                sys.exit(0)
          elif self.ocommon.check_key("CHECK_READYNESS",self.ora_env_dict):
            status = self.shard_setup_check()
            if not status:
               self.ocommon.log_info_message("Shard readyness check completed sucessfully!",self.file_name)
               self.ocommon.prog_exit("127")
          else: 
            self.setup_machine() 
            self.db_checks()
            self.reset_shard_setup()
            status = self.shard_setup_check()
            if status:
              self.ocommon.log_info_message("Shard Setup is already completed on this database",self.file_name)
            else:
              self.reset_passwd()
              self.setup_cdb_shard()
              self.set_spfile_nonm_params()
              self.ocommon.set_events("spfile")
              self.set_dbparams_version()
              self.restart_db()
              self.restart_for_db_unique_name()
              self.create_pdb()
              self.alter_db()
              self.setup_pdb_shard ()
              self.update_shard_setup()
              self.set_primary_listener()
              self.restart_listener()
              self.register_services()
              self.list_services()
              self.backup_files() 
              self.gsm_completion_message()
              self.run_custom_scripts()

      ###########  SETUP_MACHINE begins here ####################
      ## Function to machine setup
      def setup_machine(self):
          """
           This function performs the compute before performing setup
          """
          self.omachine.setup()
      ###########  SETUP_MACHINE ENDS here ####################

      ###########  DB_CHECKS  Related Functions Begin Here  ####################
      ## Function to perfom DB checks ######
      def db_checks(self):
          """
           This function perform db checks before starting the setup
          """
          self.ohome_check()
          self.passwd_check()
          self.set_user()
          self.sid_check()
          self.dbunique_name_check()
          self.hostname_check()
          self.dbport_check()
          self.dbr_dest_checks()
          self.dpump_dir_checks()
 
      def ohome_check(self):
          """
             This function performs the oracle home related checks
          """
          if self.ocommon.check_key("ORACLE_HOME",self.ora_env_dict):
             self.ocommon.log_info_message("ORACLE_HOME variable is set. Check Passed!",self.file_name)   
          else:
             self.ocommon.log_error_message("ORACLE_HOME variable is not set. Exiting!",self.file_name)
             self.ocommon.prog_exit("127")

          if os.path.isdir(self.ora_env_dict["ORACLE_HOME"]):
             msg='''ORACLE_HOME {0} dirctory exist. Directory Check passed!'''.format(self.ora_env_dict["ORACLE_HOME"])
             self.ocommon.log_info_message(msg,self.file_name)
          else:
             msg='''ORACLE_HOME {0} dirctory does not exist. Directory Check Failed!'''.format(self.ora_env_dict["ORACLE_HOME"])
             self.ocommon.log_error_message(msg,self.file_name)
             self.ocommon.prog_exit("127")

      def passwd_check(self):
           """
           This funnction perform password related checks
           """
           self.ocommon.get_password(None)
           if self.ocommon.check_key("ORACLE_PWD",self.ora_env_dict):
               msg='''ORACLE_PWD key is set. Check Passed!'''
               self.ocommon.log_info_message(msg,self.file_name)
              
      def set_user(self):
           """
           This funnction set the user for pdb and cdb.
           """
           if self.ocommon.check_key("SHARD_ADMIN_USER",self.ora_env_dict):
               msg='''SHARD_ADMIN_USER {0} is passed as an env variable. Check Passed!'''.format(self.ora_env_dict["SHARD_ADMIN_USER"])
               self.ocommon.log_info_message(msg,self.file_name)
           else:
               self.ora_env_dict=self.ocommon.add_key("SHARD_ADMIN_USER","mysdbadmin",self.ora_env_dict)
               msg="SHARD_ADMIN_USER is not set, setting default to mysdbadmin"
               self.ocommon.log_info_message(msg,self.file_name)

           if self.ocommon.check_key("PDB_ADMIN_USER",self.ora_env_dict):
               msg='''PDB_ADMIN_USER {0} is passed as an env variable. Check Passed!'''.format(self.ora_env_dict["PDB_ADMIN_USER"])
               self.ocommon.log_info_message(msg,self.file_name)
           else:
               self.ora_env_dict=self.ocommon.add_key("PDB_ADMIN_USER","PDBADMIN",self.ora_env_dict)
               msg="PDB_ADMIN_USER is not set, setting default to PDBADMIN."
               self.ocommon.log_info_message(msg,self.file_name)

      def sid_check(self):
           """
           This funnction heck and set the SID for cdb and PDB.
           """
           if self.ocommon.check_key("ORACLE_SID",self.ora_env_dict):
               msg='''ORACLE_SID {0} is passed as an env variable. Check Passed!'''.format(self.ora_env_dict["ORACLE_SID"])
               self.ocommon.log_info_message(msg,self.file_name)
           else:
               msg="ORACLE_SID is not set, existing!"
               self.ocommon.log_error_message(msg,self.file_name)
               self.ocommon.prog_exit("127")

      def dbunique_name_check(self):
           """
           This funnction check and set the db unique name for standby
           """
           if self.ocommon.check_key("DB_UNIQUE_NAME",self.ora_env_dict):
               msg='''DB_UNIQUE_NAME {0} is passed as an env variable. Check Passed!'''.format(self.ora_env_dict["DB_UNIQUE_NAME"])
               self.ocommon.log_info_message(msg,self.file_name)

               msg='''Setting the Flag to restart the DB to set DB_UNIQUE_NAME to {0}! '''.format(self.ora_env_dict["DB_UNIQUE_NAME"])
               self.ocommon.log_info_message(msg,self.file_name)
               restart_db_to_set_db_unique_name='true'
               self.ora_env_dict=self.ocommon.add_key("RESTART_DB_TO_SET_DB_UNIQUE_NAME",restart_db_to_set_db_unique_name,self.ora_env_dict)
           else:
               msg="DB_UNIQUE_NAME is not set. Setting DB_UNIQUE_NAME to Oracle_SID"
               self.ocommon.log_info_message(msg,self.file_name)
               dbsid=self.ora_env_dict["ORACLE_SID"]
               self.ora_env_dict=self.ocommon.add_key("DB_UNIQUE_NAME",dbsid,self.ora_env_dict)

      def hostname_check(self):
           """
           This function check and set the hostname.
           """
           if self.ocommon.check_key("ORACLE_HOSTNAME",self.ora_env_dict):
              msg='''ORACLE_HOSTNAME {0} is passed as an env variable. Check Passed!'''.format(self.ora_env_dict["ORACLE_HOSTNAME"])
              self.ocommon.log_info_message(msg,self.file_name)
           else:
              if self.ocommon.check_key("KUBE_SVC",self.ora_env_dict):
                 ## hostname='''{0}.{1}'''.format(socket.gethostname(),self.ora_env_dict["KUBE_SVC"])
                 hostname='''{0}'''.format(socket.getfqdn())
              else:
                 hostname='''{0}'''.format(socket.gethostname())
              msg='''ORACLE_HOSTNAME is not set, setting it to hostname {0} of the compute!'''.format(hostname)
              self.ora_env_dict=self.ocommon.add_key("ORACLE_HOSTNAME",hostname,self.ora_env_dict)                 
              self.ocommon.log_info_message(msg,self.file_name) 

      def dbport_check(self):
           """
           This funnction checks and set the SID for cdb and PDB.
           """
           if self.ocommon.check_key("DB_PORT",self.ora_env_dict):
               msg='''DB_PORT {0} is passed as an env variable. Check Passed!'''.format(self.ora_env_dict["DB_PORT"])
               self.ocommon.log_info_message(msg,self.file_name)
           else:
               self.ora_env_dict=self.ocommon.add_key("DB_PORT","1521",self.ora_env_dict)
               msg="DB_PORT is not set, setting default to 1521"
               self.ocommon.log_info_message(msg,self.file_name)

      def dbr_dest_checks(self):
           """
           This funnction checks and set the DB_CREATE_FILE_DEST and DB_CREATE_FILE_DEST_SIZE.
           """
           if self.ocommon.check_key("DB_RECOVERY_FILE_DEST",self.ora_env_dict):
               msg='''DB_RECOVERY_FILE_DEST {0} is passed as an env variable. Check Passed!'''.format(self.ora_env_dict["DB_RECOVERY_FILE_DEST"])
               self.ocommon.log_info_message(msg,self.file_name)
           elif self.ocommon.check_key("CRS_GPC",self.ora_env_dict) and self.ora_env_dict["CRS_GPC"].lower() == 'true':
              dest=self.ora_env_dict["CRS_ASM_DISKGROUP"] if self.ocommon.check_key("CRS_ASM_DISKGROUP",self.ora_env_dict) else "+DATA"
              self.ora_env_dict=self.ocommon.add_key("DB_RECOVERY_FILE_DEST",dest,self.ora_env_dict)
              msg='''DB_RECOVERY_FILE_DEST set to {0}'''.format(dest)
              self.ocommon.log_info_message(msg,self.file_name)
           elif self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
              dest=self.ora_env_dict["CRS_ASM_DISKGROUP"] if self.ocommon.check_key("CRS_ASM_DISKGROUP",self.ora_env_dict) else "+DATA"
              self.ora_env_dict=self.ocommon.add_key("DB_RECOVERY_FILE_DEST",dest,self.ora_env_dict)
              msg='''DB_RECOVERY_FILE_DEST set to {0}'''.format(dest)
              self.ocommon.log_info_message(msg,self.file_name)
           else:
               dest='''{0}/oradata/fast_recovery_area/{1}'''.format(self.ora_env_dict["ORACLE_BASE"],self.ora_env_dict["ORACLE_SID"])
               self.ora_env_dict=self.ocommon.add_key("DB_RECOVERY_FILE_DEST",dest,self.ora_env_dict)
               msg='''DB_RECOVERY_FILE_DEST set to {0}'''.format(dest)
               self.ocommon.log_info_message(msg,self.file_name)
               msg='''Checking dir {0} on local machine. If not then create the dir {0} on local machine'''.format(self.ora_env_dict["DB_RECOVERY_FILE_DEST"])
               self.ocommon.log_info_message(msg,self.file_name)
               self.ocommon.create_dir(self.ora_env_dict["DB_RECOVERY_FILE_DEST"],True,None,None)

           # Checking the DB_RECOVERY_FILE_DEST_SIZE

           if self.ocommon.check_key("DB_RECOVERY_FILE_DEST_SIZE",self.ora_env_dict):
               msg='''DB_RECOVERY_FILE_DEST_SIZE {0} is passed as an env variable. Check Passed!'''.format(self.ora_env_dict["DB_RECOVERY_FILE_DEST_SIZE"])
               self.ocommon.log_info_message(msg,self.file_name)
           else:
               self.ora_env_dict=self.ocommon.add_key("DB_RECOVERY_FILE_DEST_SIZE","40G",self.ora_env_dict)
               msg='''DB_RECOVERY_FILE_DEST_SIZE set to {0}'''.format("40G")
               self.ocommon.log_info_message(msg,self.file_name)

           # Checking the DB_CREATE_FILE_DEST

           if self.ocommon.check_key("DB_CREATE_FILE_DEST",self.ora_env_dict):
               msg='''DB_CREATE_FILE_DEST {0} is passed as an env variable. Check Passed!'''.format(self.ora_env_dict["DB_CREATE_FILE_DEST"])
               self.ocommon.log_info_message(msg,self.file_name)
           elif self.ocommon.check_key("CRS_GPC",self.ora_env_dict) and self.ora_env_dict["CRS_GPC"].lower() == 'true':
              if self.ocommon.check_key("DB_DATA_FILE_DEST",self.ora_env_dict):
                 dest=self.ora_env_dict["DB_DATA_FILE_DEST"]
              elif self.ocommon.check_key("CRS_ASM_DISKGROUP",self.ora_env_dict):
                 dest=self.ora_env_dict["CRS_ASM_DISKGROUP"]
              else:
                 dest="+DATA"
              self.ora_env_dict=self.ocommon.add_key("DB_CREATE_FILE_DEST",dest,self.ora_env_dict)
              msg='''DB_CREATE_FILE_DEST set to {0}'''.format(dest)
              self.ocommon.log_info_message(msg,self.file_name)
           elif self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
              if self.ocommon.check_key("DB_DATA_FILE_DEST",self.ora_env_dict):
                 dest=self.ora_env_dict["DB_DATA_FILE_DEST"]
              elif self.ocommon.check_key("CRS_ASM_DISKGROUP",self.ora_env_dict):
                 dest=self.ora_env_dict["CRS_ASM_DISKGROUP"]
              else:
                 dest="+DATA"
              self.ora_env_dict=self.ocommon.add_key("DB_CREATE_FILE_DEST",dest,self.ora_env_dict)
              msg='''DB_CREATE_FILE_DEST set to {0}'''.format(dest)
              self.ocommon.log_info_message(msg,self.file_name)
           else:
               dest='''{0}/oradata/{1}'''.format(self.ora_env_dict["ORACLE_BASE"],self.ora_env_dict["ORACLE_SID"])
               self.ora_env_dict=self.ocommon.add_key("DB_CREATE_FILE_DEST",dest,self.ora_env_dict)
               msg='''DB_CREATE_FILE_DEST set to {0}'''.format(dest)
               self.ocommon.log_info_message(msg,self.file_name)
               msg='''Checking dir {0} on local machine. If not then create the dir {0} on local machine'''.format(self.ora_env_dict["DB_CREATE_FILE_DEST"])
               self.ocommon.log_info_message(msg,self.file_name)
               self.ocommon.create_dir(self.ora_env_dict["DB_CREATE_FILE_DEST"],True,None,None)


      def dpump_dir_checks(self):
           """
           This funnction checks and set the DATA_PUMP dir and location.
           """
           if self.ocommon.check_key("DATA_PUMP_DIR",self.ora_env_dict):
               msg='''DATA_PUMP_DIR {0} is passed as an env variable. Check Passed!'''.format(self.ora_env_dict["DATA_PUMP_DIR"])
               self.ocommon.log_info_message(msg,self.file_name)
           else:
               dest='''{0}/oradata/data_pump_dir'''.format(self.ora_env_dict["ORACLE_BASE"])
               self.ora_env_dict=self.ocommon.add_key("DATA_PUMP_DIR",dest,self.ora_env_dict)
               msg='''DATA_PUMP_DIR set to {0}'''.format(dest)
               self.ocommon.log_info_message(msg,self.file_name)
           msg='''Checking dir {0} on local machine. If not then create the dir {0} on local machine'''.format(self.ora_env_dict["DATA_PUMP_DIR"])
           self.ocommon.log_info_message(msg,self.file_name)
           self.ocommon.create_dir(self.ora_env_dict["DATA_PUMP_DIR"],True,None,None)

       ###########  DB_CHECKS  Related Functions Begin Here  #################### 

       ## Function to check for RAC DB and populate keys for RAC DB
      def check_for_racdb(self):
         """
           This function will:
           - check if its RAC Database
           - will add the key COMMA_SEPARATED_CLS_NODES
         """
         self.ocommon.log_info_message("Inside check_for_racdb()",self.file_name)
         if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
            msg='''CRS_RACDB is set to TRUE. Populating parameters for RAC Database before running scripts for sharding setup'''
            self.ocommon.log_info_message(msg,self.file_name)

            COMMA_SEPARATED_CLS_NODES=self.ocommon.get_all_cls_nodes()
            msg='''Adding Key COMMA_SEPARATED_CLS_NODES with value = {0}'''.format(COMMA_SEPARATED_CLS_NODES)
            self.ocommon.log_info_message(msg,self.file_name)
            self.ora_env_dict=self.ocommon.add_key("COMMA_SEPARATED_CLS_NODES",COMMA_SEPARATED_CLS_NODES,self.ora_env_dict)


       ########## RESET_PASSWORD function Begin here #############################
       ## Function to perform password reset
      def reset_passwd(self):
         """
           This function reset the password.
         """
         self.ocommon.log_info_message("Inside reset_passwd()",self.file_name)
         inst_sid=self.ora_env_dict["ORACLE_SID"]
         ohome=self.ora_env_dict["ORACLE_HOME"]
         if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
            opdb=self.ora_env_dict["ORACLE_PDB_NAME"]
            # Check if its the first instance of the RAC Database, only then reset the password
            if inst_sid[-1] == '1':
               msg='''Current instance {0} is the Instance 1 of the RAC Database. Password reset will be done on this instance.'''.format(inst_sid)
               self.ocommon.log_info_message(msg,self.file_name)
               self.ocommon.reset_passwd_rac(ohome,opdb,inst_sid)
            else:
               msg='''Current instance {0} is NOT the Instance 1 of the RAC Database. Password reset will be NOT  done on this instance.'''.format(inst_sid)
               self.ocommon.log_info_message(msg,self.file_name)
         elif self.ocommon.check_key("CRS_GPC",self.ora_env_dict) and self.ora_env_dict["CRS_GPC"].lower() == 'true':
             opdb=self.ora_env_dict["ORACLE_PDB_NAME"]
             self.ocommon.reset_passwd()
         else:
            opdb=self.ora_env_dict["ORACLE_PDB"]
            self.ocommon.reset_passwd()

       ########## RESET_PASSWORD function ENDS here #############################

       ########## SETUP_CDB_SHARD FUNCTION BEGIN HERE ###############################

      def reset_shard_setup(self):
           """
            This function drop teh shard setup table and reste the env to default values. 
           """
      #     systemStr='''{0}/bin/sqlplus {1}/{2}'''.format(self.ora_env_dict["ORACLE_HOME"],"system",self.ora_env_dict["ORACLE_PWD"])
      #     sqlpluslogincmd='''{0}/bin/sqlplus "/as sysdba"'''.format(self.ora_env_dict["ORACLE_HOME"])
           ohome=self.ora_env_dict["ORACLE_HOME"]
           inst_sid=self.ora_env_dict["ORACLE_SID"]
           sqlpluslogincmd=self.ocommon.get_sqlplus_str(ohome,inst_sid,"sys",None,None,None,None,None,None,None)
           self.ocommon.log_info_message("Inside reset_shard_setup()",self.file_name)
           shard_reset_file='''{0}/.shard/reset_shard_completed'''.format(self.ora_env_dict["HOME"])
           if self.ocommon.check_key("RESET_ENV",self.ora_env_dict):
              if self.ora_env_dict["RESET_ENV"]:
                 if not os.path.isfile(shard_reset_file):
                    msg='''Dropping shardsetup table from CDB'''
                    self.ocommon.log_info_message(msg,self.file_name)
                    sqlcmd='''
                     drop table system.shardsetup;
                    '''
                    output,error,retcode=self.ocommon.run_sqlplus(sqlpluslogincmd,sqlcmd,None)
                    self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
                    self.ocommon.check_sql_err(output,error,retcode,True)
                 else:
                    msg='''Reset env already completed on this enviornment as {0} exist on this machine and not executing env reset'''.format(shard_reset_file)
                    self.ocommon.log_info_message(msg,self.file_name)                    


      def shard_setup_check(self):
           """
            This function check the shard status.
           """
#           systemStr='''{0}/bin/sqlplus "/as sysdba"'''.format(self.ora_env_dict["ORACLE_HOME"])

        #   self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
           ohome=self.ora_env_dict["ORACLE_HOME"]
           inst_sid=self.ora_env_dict["ORACLE_SID"]
           systemStr=self.ocommon.get_sqlplus_str(ohome,inst_sid,"sys",None,None,None,None,None,None,None)
           msg='''Checking shardsetup table in CDB'''
           self.ocommon.log_info_message(msg,self.file_name)
           sqlcmd='''
            set heading off
            set feedback off
            set  term off
            SET NEWPAGE NONE
            spool /tmp/shard_setup.txt
            select * from system.shardsetup WHERE ROWNUM = 1; 
            spool off
            exit;
           '''
           output,error,retcode=self.ocommon.run_sqlplus(systemStr,sqlcmd,None)
           # self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
           self.ocommon.check_sql_err(output,error,retcode,None)
           fname='''/tmp/{0}'''.format("shard_setup.txt")
           fdata=self.ocommon.read_file(fname)
           ### Unsetting the encrypt value to None
         #  self.ocommon.unset_mask_str()

           if re.search('completed',fdata):
              return True
           else:
              return False

      def setup_cdb_shard(self):
           """
            This function setup the shard.
           """
           self.ocommon.log_info_message("Inside setup_cdb_shard()",self.file_name)
           # sqlpluslogincmd='''{0}/bin/sqlplus "/as sysdba"'''.format(self.ora_env_dict["ORACLE_HOME"])            
           # Assigning variable
           ohome=self.ora_env_dict["ORACLE_HOME"]
           inst_sid=self.ora_env_dict["ORACLE_SID"]
           sqlpluslogincmd=self.ocommon.get_sqlplus_str(ohome,inst_sid,"sys",None,None,None,None,None,None,None)
           dbf_dest=self.ora_env_dict["DB_CREATE_FILE_DEST"]
           dbr_dest=self.ora_env_dict["DB_RECOVERY_FILE_DEST"]
           dbr_dest_size=self.ora_env_dict["DB_RECOVERY_FILE_DEST_SIZE"]
           host_name=self.ora_env_dict["ORACLE_HOSTNAME"]
           dpump_dir = self.ora_env_dict["DATA_PUMP_DIR"]
           db_port=self.ora_env_dict["DB_PORT"]
           obase=self.ora_env_dict["ORACLE_BASE"]
           dbuname=self.ora_env_dict["DB_UNIQUE_NAME"] 
                 
           self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
           msg='''Setting up Shard CDB'''
           self.ocommon.log_info_message(msg,self.file_name)
           if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
               # RAC Database case
               sqlcmd='''
                 alter system set db_create_file_dest=\"{0}\" scope=both sid='*';
                 alter system set db_recovery_file_dest_size={1} scope=both sid='*';
                 alter system set db_recovery_file_dest=\"{2}\" scope=both sid='*'; 
                 alter system set db_file_name_convert='*','{0}/' scope=spfile sid='*';
                 alter system set standby_file_management='AUTO' scope=spfile sid='*';
                 alter user gsmrootuser account unlock;
                 grant sysdg to gsmrootuser;
                 grant sysbackup to gsmrootuser;
                 alter user gsmrootuser identified by HIDDEN_STRING  container=all;
                 alter user GSMUSER account unlock;
                 alter user GSMUSER  identified by HIDDEN_STRING  container=all;
                 grant sysdg to GSMUSER;
                 grant sysbackup to GSMUSER;
                 create or replace directory DATA_PUMP_DIR as '{3}';
                 grant read,write on directory DATA_PUMP_DIR to GSMADMIN_INTERNAL;
                 alter system set local_listener='{4}:{5}' scope=spfile;
               '''.format(dbf_dest,dbr_dest_size,dbr_dest,dpump_dir,host_name,db_port,obase,"dbconfig",dbuname)

               if self.ocommon.check_key("COMMA_SEPARATED_CLS_NODES",self.ora_env_dict):
                  nodes = self.ora_env_dict["COMMA_SEPARATED_CLS_NODES"].split(",")
                  for value in nodes:
                     #sqlcmd += f"alter system set local_listener='{value}:{db_port}' scope=both sid='{value}';\n"
                     sqlcmd += """alter system set local_listener='{0}:{1}' scope=both sid='{2}';\n""".format(value,db_port,value)
               else:
                  self.ocommon.log_error_message("Key COMMA_SEPARATED_CLS_NODES not found. Exiting!",self.file_name)
                  self.ocommon.prog_exit("127")
           else:
              sqlcmd='''
                alter system set db_create_file_dest=\"{0}\" scope=both;
                alter system set db_recovery_file_dest_size={1} scope=both;
                alter system set db_recovery_file_dest=\"{2}\" scope=both;
                alter system set db_file_name_convert='*','{0}/' scope=spfile;
                alter system set standby_file_management='AUTO' scope=spfile;
                alter user gsmrootuser account unlock;
                grant sysdg to gsmrootuser;
                grant sysbackup to gsmrootuser;
                alter user gsmrootuser identified by HIDDEN_STRING  container=all;
                alter user GSMUSER account unlock;
                alter user GSMUSER  identified by HIDDEN_STRING  container=all;
                grant sysdg to GSMUSER;
                grant sysbackup to GSMUSER;
                create or replace directory DATA_PUMP_DIR as '{3}';
                grant read,write on directory DATA_PUMP_DIR to GSMADMIN_INTERNAL;
                alter system set local_listener='{4}:{5}' scope=spfile;
                alter system set db_unique_name='{8}' scope=spfile;
              '''.format(dbf_dest,dbr_dest_size,dbr_dest,dpump_dir,host_name,db_port,obase,"dbconfig",dbuname)
                  
           output,error,retcode=self.ocommon.run_sqlplus(sqlpluslogincmd,sqlcmd,None)
           self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
           self.ocommon.check_sql_err(output,error,retcode,True)
           ### Unsetting the encrypt value to None 
           self.ocommon.unset_mask_str()             

      def set_spfile_nonm_params(self):
           """
            This function setup the catalog.
           """
           #sqlpluslogincmd='''{0}/bin/sqlplus "/as sysdba"'''.format(self.ora_env_dict["ORACLE_HOME"])
           self.ocommon.log_info_message("Inside set_spfile_nonm_params()",self.file_name)
           if self.ocommon.check_key("CLONE_DB",self.ora_env_dict):
              if self.ora_env_dict["CLONE_DB"] != 'true':
                  ohome=self.ora_env_dict["ORACLE_HOME"]
                  inst_sid=self.ora_env_dict["ORACLE_SID"]
                  sqlpluslogincmd=self.ocommon.get_sqlplus_str(ohome,inst_sid,"sys",None,None,None,None,None,None,None)
                  self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                  dbf_dest=self.ora_env_dict["DB_CREATE_FILE_DEST"]
                  obase=self.ora_env_dict["ORACLE_BASE"]
                  dbuname=self.ora_env_dict["DB_UNIQUE_NAME"]
                  dskgrp=self.ora_env_dict["CRS_ASM_DISKGROUP"] if self.ocommon.check_key("CRS_ASM_DISKGROUP",self.ora_env_dict) else "+DATA"

                  msg='''Setting up catalog CDB with spfile non modifiable parameters'''
                  self.ocommon.log_info_message(msg,self.file_name)
                  if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
                     # RAC Database case
                     sqlcmd='''
                       alter system set open_links_per_instance=16 scope=spfile sid='*';
                       alter system set db_file_name_convert='*','{0}' scope=spfile sid='*';
                       alter system set standby_file_management='AUTO' scope=spfile sid='*';
                       alter system set dg_broker_config_file1=\"{4}/{3}/dr1.dat\" scope=spfile sid='*';
                       alter system set dg_broker_config_file2=\"{4}/{3}/dr2.dat\" scope=spfile sid='*';
                     '''.format(dbf_dest,obase,"dbconfig",dbuname,dskgrp)
                  else:
                     sqlcmd='''
                       alter system set open_links_per_instance=16 scope=spfile;
                       alter system set db_file_name_convert='*','{0}/' scope=spfile;
                       alter system set standby_file_management='AUTO' scope=spfile;
                       alter system set dg_broker_config_file1=\"{1}/oradata/{2}/{3}/dr1{3}.dat\" scope=spfile;
                       alter system set dg_broker_config_file2=\"{1}/oradata/{2}/{3}/dr2{3}.dat\" scope=spfile;
                     '''.format(dbf_dest,obase,"dbconfig",dbuname)

                  output,error,retcode=self.ocommon.run_sqlplus(sqlpluslogincmd,sqlcmd,None)
                  self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
                  self.ocommon.check_sql_err(output,error,retcode,True)

      def set_dbparams_version(self):
           """
            This function setup the catalog parameter based on db version.
           """
           self.ocommon.log_info_message("Inside set_dbparams_version()",self.file_name)
           ohome1=self.ora_env_dict["ORACLE_HOME"]
           version=self.ocommon.get_oraversion(ohome1).strip()
           self.ocommon.log_info_message(version,self.file_name)
           if int(version) > 21:
              ohome=self.ora_env_dict["ORACLE_HOME"]
              inst_sid=self.ora_env_dict["ORACLE_SID"]
              sqlpluslogincmd=self.ocommon.get_sqlplus_str(ohome,inst_sid,"sys",None,None,None,None,None,None,None)
              self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
              dbf_dest=self.ora_env_dict["DB_CREATE_FILE_DEST"]
              obase=self.ora_env_dict["ORACLE_BASE"]
              dbuname=self.ora_env_dict["DB_UNIQUE_NAME"]


              msg='''Setting up catalog CDB with spfile non modifiable parameters based on version'''
              self.ocommon.log_info_message(msg,self.file_name)

              if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
##############This can be implemented once the support for wallet_root for ASM Diskgroup is implemented, Until then, we need to keep the wallet_root pointing to a disk location
#                 sqlcmd='''
#                   alter system set wallet_root=\"{0}/{3}\" scope=spfile sid='*';
#                 '''.format(dbf_dest,obase,"dbconfig",dbuname)

                 sqlcmd='''
                   alter system set wallet_root=\"{1}/oradata/{2}/{3}\" scope=spfile sid='*';
                 '''.format(dbf_dest,obase,"dbconfig",dbuname)
                 output,error,retcode=self.ocommon.run_sqlplus(sqlpluslogincmd,sqlcmd,None)
              else:
                 sqlcmd='''
                   alter system set wallet_root=\"{1}/oradata/{2}/{3}\" scope=spfile;
                 '''.format(dbf_dest,obase,"dbconfig",dbuname)
                 output,error,retcode=self.ocommon.run_sqlplus(sqlpluslogincmd,sqlcmd,None)

              self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
              self.ocommon.check_sql_err(output,error,retcode,True)

      def restart_db(self):

          """
          restarting the db
          """
          self.ocommon.log_info_message("Inside restart_db()",self.file_name)
          #if self.ocommon.check_key("CLONE_DB",self.ora_env_dict):
          #  if self.ora_env_dict["CLONE_DB"] != 'true':
          if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
              # Its RAC Database
              dbuser=self.ora_env_dict["ORA_DB_USER"]
              dbhome=self.ora_env_dict["ORACLE_HOME"]
              dbuname=self.ora_env_dict["DB_UNIQUE_NAME"]
              hostname='''{0}'''.format(socket.gethostname())
              self.ocommon.log_info_message("Calling stop_rac_db() to shutdown the rac database",self.file_name)
              self.ocommon.stop_rac_db(dbuser,dbhome,dbuname,hostname)
              self.ocommon.log_info_message("Calling start_rac_db() to start the rac database",self.file_name)
              self.ocommon.start_rac_db(dbuser,dbhome,dbuname,hostname,None)
          else:
              ohome=self.ora_env_dict["ORACLE_HOME"]
              inst_sid=self.ora_env_dict["ORACLE_SID"]
              sqlpluslogincmd=self.ocommon.get_sqlplus_str(ohome,inst_sid,"sys",None,None,None,None,None,None,None)
              self.ocommon.log_info_message("Calling shutdown_db() to shutdown the database",self.file_name)
              self.ocommon.shutdown_db(self.ora_env_dict)
              self.ocommon.log_info_message("Calling start_db() to start the database",self.file_name)
              self.ocommon.start_db(self.ora_env_dict)

           # self.ocommon.log_info_message("Enabling archivelog at DB level",self.file_name)
           # sqlcmd='''
           #  alter database archivelog;
           #  alter database open;
           # '''
           # output,error,retcode=self.ocommon.run_sqlplus(sqlpluslogincmd,sqlcmd,None)
           # self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
           # self.ocommon.check_sql_err(output,error,retcode,True)

      def restart_for_db_unique_name(self):
          """
          restarting the db, when db_unique_name is passed explicitly
          """
          self.ocommon.log_info_message("Inside restart_for_db_unique_name()",self.file_name)
          if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
             self.ocommon.log_info_message("It is a RAC Database and DB_UNIQUE_NAME being mandatory parameter was already set. No need to restart to set DB_UNIQUE_NAME",self.file_name)
          else:
             if self.ocommon.check_key("RESTART_DB_TO_SET_DB_UNIQUE_NAME",self.ora_env_dict):
                 if self.ora_env_dict["RESTART_DB_TO_SET_DB_UNIQUE_NAME"] == 'true':
                     msg='''DB_UNIQUE_NAME {0} is passed as an env variable. Restarting the Database to set the DB_UNIQUE_NAME! '''.format(self.ora_env_dict["DB_UNIQUE_NAME"])
                     self.ocommon.log_info_message(msg,self.file_name)

                     ohome=self.ora_env_dict["ORACLE_HOME"]
                     inst_sid=self.ora_env_dict["ORACLE_SID"]
                     sqlpluslogincmd=self.ocommon.get_sqlplus_str(ohome,inst_sid,"sys",None,None,None,None,None,None,None)
                     self.ocommon.log_info_message("Calling shutdown_db() to shutdown the database",self.file_name)
                     self.ocommon.shutdown_db(self.ora_env_dict)
                     self.ocommon.log_info_message("Calling start_db() to start the database",self.file_name)
                     self.ocommon.start_db(self.ora_env_dict)

      def create_pdb(self):
         """
         This function creates the PDB
         """
         self.ocommon.log_info_message("Inside create_pdb()",self.file_name)
         if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
            # RAC Database Case, FREE PDB is NOT supported
            dbname=self.ora_env_dict["DB_NAME"]
            ohome=self.ora_env_dict["ORACLE_HOME"]
            opdb=self.ora_env_dict["ORACLE_PDB"]
            status=self.ocommon.check_pdb(opdb)
            if not status:
              msg='''PDB {0} does not exist. Creating the PDB..'''.format(opdb)
              self.ocommon.log_info_message(msg,self.file_name)
              self.ocommon.create_pdb(ohome,opdb,dbname)
              if self.ocommon.check_key("COMMA_SEPARATED_CLS_NODES",self.ora_env_dict):
                  nodes = self.ora_env_dict["COMMA_SEPARATED_CLS_NODES"].split(",")
                  for node in nodes:
                     self.ocommon.create_pdb_tns_entry_racdb(ohome,opdb,node)
              else:
                  self.ocommon.log_error_message("Key COMMA_SEPARATED_CLS_NODES not found. Exiting!",self.file_name)
                  self.ocommon.prog_exit("127")
            else:
              msg='''PDB {0} already exists.'''.format(opdb)
              self.ocommon.log_info_message(msg,self.file_name)
         else:
            inst_sid=self.ora_env_dict["ORACLE_SID"]
            ohome=self.ora_env_dict["ORACLE_HOME"]
            if self.ocommon.check_key("ORACLE_FREE_PDB",self.ora_env_dict):
               self.ora_env_dict=self.ocommon.update_key("ORACLE_PDB",self.ora_env_dict["ORACLE_FREE_PDB"],self.ora_env_dict)
               opdb=self.ora_env_dict["ORACLE_PDB"]
               status=self.ocommon.check_pdb(opdb)
               if not status:
                 self.ocommon.create_pdb(ohome,opdb,inst_sid)
                 self.ocommon.create_pdb_tns_entry(ohome,opdb)

      def alter_db(self):
          """
          Alter db
          """
          self.ocommon.log_info_message("Inside alter_db()",self.file_name)
          ohome=self.ora_env_dict["ORACLE_HOME"]
          inst_sid=self.ora_env_dict["ORACLE_SID"]
          sqlpluslogincmd=self.ocommon.get_sqlplus_str(ohome,inst_sid,"sys",None,None,None,None,None,None,None)
          self.ocommon.log_info_message("Enabling flashback and force logging at DB level",self.file_name)
          if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
              # RAC DB Case
              sqlcmd='''
                alter database flashback on;
                alter database force logging;
                ALTER PLUGGABLE DATABASE ALL OPEN INSTANCES=ALL;
              '''
          else:
              sqlcmd='''
                alter database flashback on;
                alter database force logging;
                ALTER PLUGGABLE DATABASE ALL OPEN;
              '''
          output,error,retcode=self.ocommon.run_sqlplus(sqlpluslogincmd,sqlcmd,None)
          self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
          self.ocommon.check_sql_err(output,error,retcode,None)
                             
      def setup_pdb_shard(self):
           """
            This function setup the shard.
           """
           self.ocommon.log_info_message("Inside setup_pdb_shard()",self.file_name)
           ohome=self.ora_env_dict["ORACLE_HOME"]
           inst_sid=self.ora_env_dict["ORACLE_SID"]
           sqlpluslogincmd=self.ocommon.get_sqlplus_str(ohome,inst_sid,"sys",None,None,None,None,None,None,None)
           # Assigning variable
           self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])

           if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
               # RAC DB case
               if self.ocommon.check_key("ORACLE_PDB",self.ora_env_dict):
                  msg='''Setting up catalog PDB'''
                  self.ocommon.log_info_message(msg,self.file_name)
                  sqlcmd='''
                  alter pluggable database {0} close immediate instances=all;
                  alter pluggable database {0} open services=All;
                  alter pluggable database {0} open instances=all;
                  ALTER PLUGGABLE DATABASE {0} SAVE STATE;
                  alter session set container={0};
                  grant inherit privileges on user SYS to GSMADMIN_INTERNAL;
                  grant sysdg to GSMUSER;
                  grant sysbackup to GSMUSER;
                  execute DBMS_GSM_FIX.validateShard;
                  '''.format(self.ora_env_dict["ORACLE_PDB"])

                  output,error,retcode=self.ocommon.run_sqlplus(sqlpluslogincmd,sqlcmd,None)
                  self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
                  self.ocommon.check_sql_err(output,error,retcode,True)

                  # Handle to run "alter system register" for all instances of RAC DB
                  if self.ocommon.check_key("COMMA_SEPARATED_CLS_NODES",self.ora_env_dict):
                     self.ocommon.log_info_message("Running alter system register for all instances of RAC DB",self.file_name)
                     osuser,dbhome,dbbase,oinv=self.ocommon.get_db_params()
                     dbname,osid,dbuname=self.ocommon.getdbnameinfo()
                     nodes = self.ora_env_dict["COMMA_SEPARATED_CLS_NODES"].split(",")
                     for hostname in nodes:
                        inst_sid=self.ocommon.get_inst_sid(osuser,dbhome,osid,hostname)
                        cmd='''ssh {0}@{1} "export ORACLE_SID={2}; $ORACLE_HOME/bin/sqlplus -s / as sysdba <<EOF
set heading off;
set pagesize 0;
alter system register;
alter session set container={3};
alter system register;
exit;
EOF"
'''.format(osuser,hostname,inst_sid,self.ora_env_dict["ORACLE_PDB"])
                        output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
                        self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
                        self.ocommon.check_sql_err(output,error,retcode,None)
                        self.ocommon.unset_mask_str()
                  else:
                     self.ocommon.log_error_message("Key COMMA_SEPAATED_CLS_NODES not found. Exiting!",self.file_name)
                     self.ocommon.prog_exit("127")

           elif self.ocommon.check_key("ORACLE_PDB",self.ora_env_dict):
              msg='''Setting up Shard PDB'''
              self.ocommon.log_info_message(msg,self.file_name)
              sqlcmd='''
              alter pluggable database {0} close immediate;
              alter pluggable database {0} open services=All;
              ALTER PLUGGABLE DATABASE {0} SAVE STATE;
              alter system register;
              alter session set container={0};
              grant read,write on directory DATA_PUMP_DIR to GSMADMIN_INTERNAL;
              grant sysdg to GSMUSER;
              grant sysbackup to GSMUSER;
              execute DBMS_GSM_FIX.validateShard;
              alter system register;
              '''.format(self.ora_env_dict["ORACLE_PDB"])

              output,error,retcode=self.ocommon.run_sqlplus(sqlpluslogincmd,sqlcmd,None)
              self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
              self.ocommon.check_sql_err(output,error,retcode,True)

           ### Unsetting the encrypt value to None
           self.ocommon.unset_mask_str()
              
      def update_shard_setup(self):
           """
            This function update the shard setup on this DB.
           """
       #    systemStr='''{0}/bin/sqlplus {1}/{2}'''.format(self.ora_env_dict["ORACLE_HOME"],"system","HIDDEN_STRING")
           self.ocommon.log_info_message("Inside update_catalog_setup()",self.file_name)
           ohome=self.ora_env_dict["ORACLE_HOME"]
           inst_sid=self.ora_env_dict["ORACLE_SID"]
           systemStr='''{0}/bin/sqlplus "/as sysdba"'''.format(self.ora_env_dict["ORACLE_HOME"])

#           self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])

           msg='''Updating shardsetup table'''
           self.ocommon.log_info_message(msg,self.file_name)
           sqlcmd='''
            set heading off
            set feedback off
            create table system.shardsetup (status varchar2(10));
            insert into system.shardsetup values('completed');
            commit; 
            exit;
           '''
           output,error,retcode=self.ocommon.run_sqlplus(systemStr,sqlcmd,None)
           self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
           self.ocommon.check_sql_err(output,error,retcode,True)

           ### Reset File
           shard_reset_dir='''{0}/.shard'''.format(self.ora_env_dict["HOME"]) 
           shard_reset_file='''{0}/.shard/reset_shard_completed'''.format(self.ora_env_dict["HOME"])

           self.ocommon.log_info_message("Creating reset_file_fir if it does not exist",self.file_name)
           if not os.path.isdir(shard_reset_dir):
              self.ocommon.create_dir(shard_reset_dir,True,None,None)

           if not os.path.isfile(shard_reset_file):
              self.ocommon.create_file(shard_reset_file,True,None,None)
 
#          self.ocommon.unset_mask_str()
        
       ########## SETUP_CDB_SHARD FUNCTION ENDS HERE ###############################

          ###################################### Run custom scripts ##################################################
      def run_custom_scripts(self):
          """
           Custom script to be excuted on every restart of enviornment
          """
          self.ocommon.log_info_message("Inside run_custom_scripts()",self.file_name)
          if self.ocommon.check_key("CUSTOM_SHARD_SCRIPT_DIR",self.ora_env_dict):
             shard_dir=self.ora_env_dict["CUSTOM_SHARD_SCRIPT_DIR"]
             if self.ocommon.check_key("CUSTOM_SHARD_SCRIPT_FILE",self.ora_env_dict):
                shard_file=self.ora_env_dict["CUSTOM_SHARD_SCRIPT_FILE"]
                script_file = '''{0}/{1}'''.format(shard_dir,shard_file)
                if os.path.isfile(script_file):
                   msg='''Custom shard script exist {0}'''.format(script_file)
                   self.ocommon.log_info_message(msg,self.file_name)
                   cmd='''sh {0}'''.format(script_file)
                   output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
                   self.ocommon.check_os_err(output,error,retcode,True)

      ############################### GSM Completion Message #######################################################
      def gsm_completion_message(self):
          """
           Funtion print completion message
          """
          self.ocommon.log_info_message("Inside gsm_completion_message()",self.file_name)
          msg=[]
          msg.append('==============================================')
          msg.append('     GSM Shard Setup Completed                ')
          msg.append('==============================================')

          for text in msg:
              self.ocommon.log_info_message(text,self.file_name)
      ################################  Reset and standby functions #################################################
      
      def set_primary_listener(self):
          """
           Function to set the primary listener
          """
          self.ocommon.log_info_message("Inside set_primary_listener()",self.file_name)
          if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
              # RAC DB Case
              if self.ocommon.check_key("COMMA_SEPARATED_CLS_NODES",self.ora_env_dict):
                  nodes = self.ora_env_dict["COMMA_SEPARATED_CLS_NODES"].split(",")
                  global_dbname=self.ocommon.get_global_dbdomain(self.ora_env_dict["ORACLE_HOSTNAME"],self.ora_env_dict["DB_UNIQUE_NAME"])
                  osuser,dbhome,dbbase,oinv=self.ocommon.get_db_params()
                  dbname,osid,dbuname=self.ocommon.getdbnameinfo()
                  for node in nodes:
                      msg='''Calling set_db_listener_racdb for node {0} '''.format(node)
                      self.ocommon.log_info_message(msg,self.file_name)
                      inst_sid=self.ocommon.get_inst_sid(osuser,dbhome,osid,node)
                      self.set_db_listener_racdb(global_dbname,dbhome,inst_sid,node)
              else:
                  self.ocommon.log_error_message("Key COMMA_SEPARATED_CLS_NODES not found. Exiting!",self.file_name)
                  self.ocommon.prog_exit("127")
          elif self.ocommon.check_key("CRS_GPC",self.ora_env_dict) and self.ora_env_dict["CRS_GPC"].lower() == 'true':
              global_dbname=self.ocommon.get_global_dbdomain(self.ora_env_dict["ORACLE_HOSTNAME"],self.ora_env_dict["DB_UNIQUE_NAME"])
              osuser,dbhome,dbbase,oinv=self.ocommon.get_db_params()
              dbname,osid,dbuname=self.ocommon.getdbnameinfo()
              msg='''Calling set_db_listener_racdb for GPC node {0} '''.format(self.ora_env_dict["ORACLE_HOSTNAME"])
              self.ocommon.log_info_message(msg,self.file_name)
              inst_sid=self.ocommon.get_inst_sid(osuser,dbhome,osid,self.ora_env_dict["ORACLE_HOSTNAME"])
              self.set_db_listener_racdb(global_dbname,dbhome,inst_sid,self.ora_env_dict["ORACLE_HOSTNAME"])
          else:
              global_dbname=self.ocommon.get_global_dbdomain(self.ora_env_dict["ORACLE_HOSTNAME"],self.ora_env_dict["DB_UNIQUE_NAME"] + "_DGMRL")
              self.set_db_listener(global_dbname,self.ora_env_dict["DB_UNIQUE_NAME"])
              global_dbname=self.ocommon.get_global_dbdomain(self.ora_env_dict["ORACLE_HOSTNAME"],self.ora_env_dict["DB_UNIQUE_NAME"])
              self.set_db_listener(global_dbname,self.ora_env_dict["DB_UNIQUE_NAME"])

      def set_db_listener(self,gdbname,sid):
          """
           Funtion to reset the listener
          """
          self.ocommon.log_info_message("Inside set_db_listener()",self.file_name)
          start = 'SID_LIST_LISTENER'
          end = r'^\)$'
          oracle_home=self.ora_env_dict["ORACLE_HOME"]
          lisora='''{0}/network/admin/listener.ora'''.format(oracle_home)
          buffer = "SID_LIST_LISTENER=" + '\n'
          start_flag = False
          try:
            with open(lisora) as f:
              for line1 in f:
                if start_flag == False:
                   if (re.match(start, line1.strip())):
                      start_flag = True
                elif (re.match(end, line1.strip())):
                   line2 = f.next()
                   if (re.match(end, line2.strip())):
                      break
                   else:
                      buffer += line1
                      buffer += line2
                else:
                   if start_flag == True:
                      buffer += line1
          except:
            pass

          if start_flag == True:
              buffer +=  self.ocommon.get_sid_desc(gdbname,oracle_home,sid,"SID_DESC1")
              listener =  self.ocommon.get_lisora(1521)
              listener += '\n' + buffer
          else:
              buffer += self.ocommon.get_sid_desc(gdbname,oracle_home,sid,"SID_DESC")
              listener =  self.ocommon.get_lisora(1521)
              listener += '\n' + buffer

          wr = open(lisora, 'w')
          wr.write(listener)


      def set_db_listener_racdb(self,gdbname,ohome,sid,node):
          """
           Funtion to reset the listener in RAC setup
          """
          self.ocommon.log_info_message("Inside set_db_listener_racdb()",self.file_name)
          giuser=self.ora_env_dict["GRID_USER"]
          static_services_entry='''
SID_LIST_LISTENER =
  (SID_LIST =
    (SID_DESC =
      (GLOBAL_DBNAME = {0}_DGMGRL
      (ORACLE_HOME = {1})
      (SID_NAME = {2})
    )
  )'''.format(gdbname,ohome,sid)
          oracle_home=self.ora_env_dict["GRID_HOME"]
          lisora='''{0}/network/admin/listener.ora'''.format(oracle_home)
          #remote_cmd = f"ssh {giuser}@{node} 'echo \"{static_services_entry}\" >> {lisora}'"
          #cmd = f'sudo -u {giuser} {remote_cmd}'
          remote_cmd = """ssh {0}@{1} 'echo \"{2}\" >> {3}'""".format(giuser,node,static_services_entry,lisora)
          cmd = '''sudo -u {0} {1}'''.format(giuser,remote_cmd)
          output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
          self.ocommon.check_os_err(output,error,retcode,True)
          msg='''Successfully added tns entry on {0}'''.format(node)
          self.ocommon.log_info_message(msg,self.file_name)

      def restart_listener(self):
          """
          restart listener
          """
          self.ocommon.log_info_message("Inside restart_listener()",self.file_name)
          if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
              # RAC DB Case
              if self.ocommon.check_key("COMMA_SEPARATED_CLS_NODES",self.ora_env_dict):
                  nodes = self.ora_env_dict["COMMA_SEPARATED_CLS_NODES"].split(",")
                  oracle_home=self.ora_env_dict["GRID_HOME"]
                  giuser=self.ora_env_dict["GRID_USER"]
                  for node in nodes:
                      msg='''Stopping Listener on node {0}'''.format(node)
                      self.ocommon.log_info_message(msg,self.file_name)
                      #remote_cmd = f"ssh {giuser}@{node} '{oracle_home}/bin/lsnrctl stop'"
                      #cmd = f'sudo -u {giuser} {remote_cmd}'
                      remote_cmd = """ssh {0}@{1} '{2}/bin/lsnrctl stop'""".format(giuser,node,oracle_home)
                      cmd = '''sudo -u {0} {1}'''.format(giuser,remote_cmd)
                      output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
                      self.ocommon.check_os_err(output,error,retcode,True)

                      msg='''Starting Listener on node {0}'''.format(node)
                      self.ocommon.log_info_message(msg,self.file_name)
                      #remote_cmd = f"ssh {giuser}@{node} '{oracle_home}/bin/lsnrctl start'"
                      #cmd = f'sudo -u {giuser} {remote_cmd}'
                      remote_cmd = """ssh {0}@{1} '{2}/bin/lsnrctl start'""".format(giuser,node,oracle_home)
                      cmd = '''sudo -u {0} {1}'''.format(giuser,remote_cmd)
                      output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
                      self.ocommon.check_os_err(output,error,retcode,True)
              else:
                  self.ocommon.log_error_message("Key COMMA_SEPARATED_CLS_NODES not found. Exiting!",self.file_name)
                  self.ocommon.prog_exit("127")
          elif self.ocommon.check_key("CRS_GPC",self.ora_env_dict) and self.ora_env_dict["CRS_GPC"].lower() == 'true':
              oracle_home=self.ora_env_dict["GRID_HOME"]
              giuser=self.ora_env_dict["GRID_USER"]
              node=self.ora_env_dict["ORACLE_HOSTNAME"]
              msg='''Stopping Listener on GPC node {0}'''.format(node)
              self.ocommon.log_info_message(msg,self.file_name)
              #remote_cmd = f"ssh {giuser}@{node} '{oracle_home}/bin/lsnrctl stop'"
              #cmd = f'sudo -u {giuser} {remote_cmd}'
              remote_cmd = """ssh {0}@{1} '{2}/bin/lsnrctl stop'""".format(giuser,node,oracle_home)
              cmd = '''sudo -u {0} {1}'''.format(giuser,remote_cmd)
              output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
              self.ocommon.check_os_err(output,error,retcode,True)

              msg='''Starting Listener on GPC node {0}'''.format(node)
              self.ocommon.log_info_message(msg,self.file_name)
              #remote_cmd = f"ssh {giuser}@{node} '{oracle_home}/bin/lsnrctl start'"
              #cmd = f'sudo -u {giuser} {remote_cmd}'
              remote_cmd = """ssh {0}@{1} '{2}/bin/lsnrctl start'""".format(giuser,node,oracle_home)
              cmd = '''sudo -u {0} {1}'''.format(giuser,remote_cmd)
              output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
              self.ocommon.check_os_err(output,error,retcode,True)
          else:
              self.ocommon.log_info_message("Stopping Listener",self.file_name)
              ohome=self.ora_env_dict["ORACLE_HOME"]
              cmd='''{0}/bin/lsnrctl stop'''.format(ohome)
              output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
              self.ocommon.check_os_err(output,error,retcode,None)

              self.ocommon.log_info_message("Starting Listener",self.file_name)
              ohome=self.ora_env_dict["ORACLE_HOME"]
              cmd='''{0}/bin/lsnrctl start'''.format(ohome)
              output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
              self.ocommon.check_os_err(output,error,retcode,None)
   
      def register_services(self):
           """
            This function setup the catalog.
           """
           # sqlpluslogincmd='''{0}/bin/sqlplus "/as sysdba"'''.format(self.ora_env_dict["ORACLE_HOME"])
           # Assigning variable
           self.ocommon.log_info_message("Inside register_services()",self.file_name)
           if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
               # RAC DB Case
               if self.ocommon.check_key("COMMA_SEPARATED_CLS_NODES",self.ora_env_dict):
                     self.ocommon.log_info_message("Running alter system register for all instances of RAC DB",self.file_name)
                     osuser,dbhome,dbbase,oinv=self.ocommon.get_db_params()
                     dbname,osid,dbuname=self.ocommon.getdbnameinfo()
                     nodes = self.ora_env_dict["COMMA_SEPARATED_CLS_NODES"].split(",")
                     for hostname in nodes:
                        self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                        inst_sid=self.ocommon.get_inst_sid(osuser,dbhome,osid,hostname)
                        cmd='''ssh {0}@{1} "export ORACLE_SID={2}; $ORACLE_HOME/bin/sqlplus -s / as sysdba <<EOF
set heading off;
set pagesize 0;
alter system register;
alter session set container={3};
alter system register;
exit;
EOF"
'''.format(osuser,hostname,inst_sid,self.ora_env_dict["ORACLE_PDB"])
                        output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
                        self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
                        self.ocommon.check_sql_err(output,error,retcode,None)
                        self.ocommon.unset_mask_str()
               else:
                  self.ocommon.log_error_message("Key COMMA_SEPARATED_CLS_NODES not found. Exiting!",self.file_name)
                  self.ocommon.prog_exit("127")
           else:
               ohome=self.ora_env_dict["ORACLE_HOME"]
               inst_sid=self.ora_env_dict["ORACLE_SID"]
               sqlpluslogincmd=self.ocommon.get_sqlplus_str(ohome,inst_sid,"sys",None,None,None,None,None,None,None)
               self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
               if self.ocommon.check_key("ORACLE_PDB",self.ora_env_dict):
                  msg='''Setting up catalog PDB'''
                  self.ocommon.log_info_message(msg,self.file_name)
                  sqlcmd='''
                  alter system register;
                  alter session set container={0};
                  alter system register;
                  exit;
                  '''.format(self.ora_env_dict["ORACLE_PDB"],self.ora_env_dict["SHARD_ADMIN_USER"])

                  output,error,retcode=self.ocommon.run_sqlplus(sqlpluslogincmd,sqlcmd,None)
                  self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
                  self.ocommon.check_sql_err(output,error,retcode,True)

           ### Unsetting the encrypt value to None
           self.ocommon.unset_mask_str()

      def list_services(self):
          """
          restart listener
          """
          self.ocommon.log_info_message("Inside list_services()",self.file_name)
          if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
              # RAC DB Case
              if self.ocommon.check_key("COMMA_SEPARATED_CLS_NODES",self.ora_env_dict):
                  nodes = self.ora_env_dict["COMMA_SEPARATED_CLS_NODES"].split(",")
                  oracle_home=self.ora_env_dict["GRID_HOME"]
                  giuser=self.ora_env_dict["GRID_USER"]
                  for node in nodes:
                      msg='''Listing services on node {0}'''.format(node)
                      self.ocommon.log_info_message(msg,self.file_name)
                      #remote_cmd = f"ssh {giuser}@{node} '{oracle_home}/bin/lsnrctl services'"
                      #cmd = f'sudo -u {giuser} {remote_cmd}'
                      remote_cmd = """ssh {0}@{1} '{2}/bin/lsnrctl services'""".format(giuser,node,oracle_home)
                      cmd = '''sudo -u {0} {1}'''.format(giuser,remote_cmd)
                      output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
                      self.ocommon.check_os_err(output,error,retcode,True)
              else:
                  self.ocommon.log_error_message("Key COMMA_SEPARATED_CLS_NODES not found. Exiting!",self.file_name)
                  self.ocommon.prog_exit("127")
          elif self.ocommon.check_key("CRS_GPC",self.ora_env_dict) and self.ora_env_dict["CRS_GPC"].lower() == 'true':
              oracle_home=self.ora_env_dict["GRID_HOME"]
              giuser=self.ora_env_dict["GRID_USER"]
              node=self.ora_env_dict["ORACLE_HOSTNAME"]
              msg='''Listing services on GPC node {0}'''.format(node)
              self.ocommon.log_info_message(msg,self.file_name)
              #remote_cmd = f"ssh {giuser}@{node} '{oracle_home}/bin/lsnrctl services'"
              #cmd = f'sudo -u {giuser} {remote_cmd}'
              remote_cmd = """ssh {0}@{1} '{2}/bin/lsnrctl services'""".format(giuser,node,oracle_home)
              cmd = '''sudo -u {0} {1}'''.format(giuser,remote_cmd)
              output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
              self.ocommon.check_os_err(output,error,retcode,True)
          else:
              self.ocommon.log_info_message("Listing Services",self.file_name)
              ohome=self.ora_env_dict["ORACLE_HOME"]
              cmd='''{0}/bin/lsnrctl services'''.format(ohome)
              output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
              self.ocommon.check_os_err(output,error,retcode,None)
 
      def backup_files(self):
          """
           This function backup the files such as spfile, password file and other required files to a under oradata/dbconfig
          """
          self.ocommon.log_info_message("Inside backup_files()",self.file_name)
          if self.ocommon.check_key("CRS_RACDB",self.ora_env_dict) and self.ora_env_dict["CRS_RACDB"].lower() == 'true':
              # RAC DB Case
              msg='''Inside backup_files(). This is a RAC Database. Skipping this step'''
              self.ocommon.log_info_message(msg,self.file_name)
          else:
              ohome=self.ora_env_dict["ORACLE_HOME"]
              obase=self.ora_env_dict["ORACLE_BASE"]
              dbuname=self.ora_env_dict["DB_UNIQUE_NAME"]
              dbsid=self.ora_env_dict["ORACLE_SID"]

              version=self.ocommon.get_oraversion(ohome).strip()
              wallet_backup_cmd='''ls -ltr /bin'''
              self.ocommon.log_info_message("Check Version " + version,self.file_name)
              if int(version) >= 21:
                 obase1=self.ora_env_dict["ORACLE_BASE"]
                 wallet_backup_cmd='''cp -r {3}/admin/ {0}/oradata/{1}/{2}/'''.format(obase,"dbconfig",dbuname,ohome)
              cmd_names='''
                   mkdir -p {0}/oradata/{1}/{2}
                   cp {3}/dbs/spfile{2}.ora {0}/oradata/{1}/{2}/
                   cp {3}/dbs/orapw{2}   {0}/oradata/{1}/{2}/
                   cp {3}/network/admin/sqlnet.ora {0}/oradata/{1}/{2}/
                   cp {3}/network/admin/listener.ora {0}/oradata/{1}/{2}/
                   cp {3}/network/admin/tnsnames.ora {0}/oradata/{1}/{2}/
                   touch {0}/oradata/{1}/{2}/status_completed
              '''.format(obase,"dbconfig",dbuname,ohome)
              cmd_list = [y for y in (x.strip() for x in cmd_names.splitlines()) if y]
              for cmd in cmd_list:
                 msg='''Executing cmd {0}'''.format(cmd)
                 self.ocommon.log_info_message(msg,self.file_name)
                 output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)

