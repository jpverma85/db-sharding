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
import random
from oralogger import *
from oraenv import *
from oracommon import *
from oramachine import *

class OraGSM:
      """
      This calss setup the Gsm after DB installation.
      """
      def __init__(self,oralogger,orahandler,oraenv,oracommon):
        """
        This constructor of OraGsm class to setup the Gsm on primary DB.

        Attributes:
           oralogger (object): object of OraLogger Class.
           ohandler (object): object of Handler class.
           oenv (object): object of singleton OraEnv class.
           ocommon(object): object of OraCommon class.
           ora_env_dict(dict): Dict of env variable populated based on env variable for the setup.
           file_name(string): Filename from where logging message is populated.
        """
        self.ologger             = oralogger
        self.ohandler            = orahandler
        self.oenv                = oraenv.get_instance()
        self.ocommon             = oracommon
        self.ora_env_dict        = oraenv.get_env_vars()
        self.file_name           = os.path.basename(__file__)
        self.omachine            = OraMachine(self.ologger,self.ohandler,self.oenv,self.ocommon)

      def setup(self):
          """
           This function setup the Gsm on Primary DB.
          """
          if self.ocommon.check_key("ADD_SHARD",self.ora_env_dict):
             self.catalog_checks()
             status = self.catalog_setup_checks()
             if not status:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.ocommon.prog_exit("127")
             else:
                self.add_gsm_shard()
                self.set_hostid_null()
                self.add_invited_node("ADD_SHARD")
                self.remove_invited_node("ADD_SHARD")
                sys.exit(0)
          if self.ocommon.check_key("DEPLOY_SHARD",self.ora_env_dict):
             self.catalog_checks()
             status = self.catalog_setup_checks()
             if not status:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.ocommon.prog_exit("127")
             else:
                self.deploy_shard()
                self.setup_gsm_service()
                sys.exit(0)
          elif self.ocommon.check_key("ADD_SGROUP_PARAMS",self.ora_env_dict):
             self.catalog_checks()
             status = self.catalog_setup_checks()
             if not status:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.ocommon.prog_exit("127")
             else:
                self.setup_gsm_shardg("ADD_SGROUP_PARAMS")
                sys.exit(0)
          elif self.ocommon.check_key("ADD_SSPACE_PARAMS",self.ora_env_dict):
             self.catalog_checks()
             status = self.catalog_setup_checks()
             if not status:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.ocommon.prog_exit("127")
             else:
                self.setup_gsm_sspace("ADD_SSPACE_PARAMS")
                sys.exit(0)
          elif self.ocommon.check_key("REMOVE_SHARD",self.ora_env_dict):
             self.catalog_checks()
             status = self.catalog_setup_checks()
             if not status:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.ocommon.prog_exit("127")
             else:
                status=self.remove_gsm_shard()
                
             if status:
                sys.exit(0)
             else:
                sys.exit(1)

          elif self.ocommon.check_key("MOVE_CHUNKS",self.ora_env_dict):
             self.catalog_checks()
             status = self.catalog_setup_checks()
             if not status:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.ocommon.prog_exit("127")
             else:
                self.move_shard_chunks()
                sys.exit(0)
          elif self.ocommon.check_key("TDE_KEY",self.ora_env_dict):
               self.ocommon.get_tde_key()
               sys.exit(0)
          elif self.ocommon.check_key("CANCEL_CHUNKS",self.ora_env_dict):
             self.catalog_checks()
             status = self.catalog_setup_checks()
             if not status:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.ocommon.prog_exit("127")
             else:
                self.cancel_move_chunks()
                sys.exit(0)
          elif self.ocommon.check_key("VALIDATE_NOCHUNKS",self.ora_env_dict):
             self.catalog_checks()
             status = self.catalog_setup_checks()
             if not status:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.ocommon.prog_exit("127")
             else:
                self.validate_nochunks()
                sys.exit(0)
          elif self.ocommon.check_key("CHECK_ONLINE_SHARD",self.ora_env_dict):
             self.catalog_checks()
             status = self.catalog_setup_checks()
             if not status:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.ocommon.prog_exit("127")
             else:
                self.verify_online_shard()
                sys.exit(0)
          elif self.ocommon.check_key("CHECK_GSM_SHARD",self.ora_env_dict):
             self.catalog_checks()
             status = self.catalog_setup_checks()
             if not status:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.ocommon.prog_exit("127")
             else:
                self.verify_gsm_shard()
                sys.exit(0)
          elif self.ocommon.check_key("VALIDATE_SHARD",self.ora_env_dict):
             self.catalog_checks()
             status = self.catalog_setup_checks()
             if not status:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.ocommon.prog_exit("127")
             else:
                self.validate_gsm_shard()
                sys.exit(0)
          elif self.ocommon.check_key("VALIDATE_GSM",self.ora_env_dict):
             self.catalog_checks()
             status = self.catalog_setup_checks()
             if not status:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.ocommon.prog_exit("127")
             else:
                sys.exit(0)
          elif self.ocommon.check_key("CHECK_LIVENESS",self.ora_env_dict):
             filename=self.ora_env_dict["GSM_LOCK_STATUS_FILE"]
             if os.path.exists(filename):
                self.ocommon.log_info_message("provisioning is still in progress as file " + filename + " still exist!",self.file_name)
                sys.exit(0)
             status = self.catalog_setup_checks()
             if not status:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.ocommon.prog_exit("127")
             status = self.check_gsm_director_status(None)
             if not status:
                self.ocommon.log_info_message("No GDS setup found on this system.",self.file_name)
                self.ocommon.prog_exit("127")
             self.ocommon.log_info_message("GSM liveness check completed sucessfully!",self.file_name)
             sys.exit(0)
          elif self.ocommon.check_key("INVITED_NODE_OP",self.ora_env_dict):
             self.catalog_checks()
             status = self.catalog_setup_checks()
             if not status:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.ocommon.prog_exit("127")
             else:
                self.invited_node_op()      
                sys.exit(0)
          elif self.ocommon.check_key("CATALOG_SETUP",self.ora_env_dict):
             # If user pass env avariable CATALOG_SETUP true then it will just create gsm director and add catalog but will not add any shard
             # It will also add service
             status = self.catalog_setup_checks()
             if status == False:
                self.ocommon.log_info_message("No existing catalog and GDS setup found on this system. Setting up GDS and will configure catalog on this machine.",self.file_name)
                self.setup_machine()
                self.catalog_checks()
                self.reset_gsm_setup()
                status1 = self.gsm_setup_check()
                if status1:
                   self.ocommon.log_info_message("Gsm Setup is already completed on this database",self.file_name)
                   self.start_gsm_director()
                   self.ocommon.log_info_message("Started GSM",self.file_name)
                else:
                   # Perform Catalog setup after check GSM_MASTER FLAG. IF GSM MASTER FLAG is set then only catalog will be added.
                   self.ocommon.log_info_message("No existing GDS found on this system. Setting up GDS on this machine.",self.file_name)
                   master_flag=self.gsm_master_flag_check()
                   if master_flag:
                     self.setup_gsm_calog()
                     self.setup_gsm_director()
                     self.start_gsm_director()
                     self.status_gsm_director()
                     if self.ocommon.check_key("SHARDING_TYPE",self.ora_env_dict):
                       if self.ora_env_dict["SHARDING_TYPE"].upper() != 'USER':
                           self.setup_gsm_shardg("SHARD_GROUP")
                     else:
                        self.setup_gsm_shardg("SHARD_GROUP")
                     self.gsm_backup_file()
                     self.gsm_completion_message()
                   ### Running Custom Scripts
                     self.run_custom_scripts()
                   else:
                     self.add_gsm_director()
                     self.start_gsm_director() 
                     self.gsm_backup_file()
                     self.gsm_completion_message()
          else:
             # This block run shard addition, catalog addition and service creation
             # This block also verifies if master flag is not not GSM director then it will not create catalog but add GSM ony
             self.setup_machine()
             self.gsm_checks()
             self.reset_gsm_setup()
             status = self.gsm_setup_check()
             if status:
                self.ocommon.log_info_message("Gsm Setup is already completed on this database",self.file_name)
                self.start_gsm_director()
                self.ocommon.log_info_message("Started GSM",self.file_name)
             else:
                # if the status = self.gsm_setup_check() return False then shard addition, catalog addition and service creation
                master_flag=self.gsm_master_flag_check()
                if master_flag:
                   self.ocommon.log_info_message("No existing GDS found on this system. Setting up GDS on this machine.",self.file_name)
                   self.setup_gsm_calog()
                   self.setup_gsm_director()
                   self.start_gsm_director()
                   self.status_gsm_director()
                   if self.ocommon.check_key("SHARDING_TYPE",self.ora_env_dict):
                       if self.ora_env_dict["SHARDING_TYPE"].upper() != 'USER':
                           self.setup_gsm_shardg("SHARD_GROUP")
                       if self.ora_env_dict["SHARDING_TYPE"].upper() == 'USER':
                           self.setup_gsm_sspace("SHARD_SPACE")
                   else:
                      self.setup_gsm_shardg("SHARD_GROUP")
                   self.setup_gsm_shard()
                   self.set_hostid_null()
                   self.stop_gsm_director()
                   time.sleep(30)
                   self.start_gsm_director()
                   self.add_invited_node("SHARD")
                   self.remove_invited_node("SHARD")
                   self.stop_gsm_director()
                   time.sleep(30)
                   self.start_gsm_director()
                   self.deploy_shard()
                   self.setup_gsm_service()
                   self.setup_sample_schema()
                   self.gsm_backup_file()
                   self.gsm_completion_message()
                ### Running Custom Scripts
                   self.run_custom_scripts()   
                else:
                   self.add_gsm_director()
                   self.start_gsm_director()          
                   self.gsm_backup_file()
                   self.gsm_completion_message()
      
      ###########  SETUP_MACHINE begins here ####################
      ## Function to machine setup
      def setup_machine(self):
          """
           This function performs the compute before performing setup
          """
          self.omachine.setup()
          filename = self.ora_env_dict["GSM_LOCK_STATUS_FILE"]
          touchfile = 'touch {0}'.format(filename)
          if not os.path.isfile(filename):
            self.ocommon.log_error_message("Setting file provisioning status file :" + filename ,self.file_name)
            output,error,retcode=self.ocommon.execute_cmd(touchfile,None,self.ora_env_dict)
            if retcode == 1:
                   self.ocommon.log_error_message("error occurred while touching the file :" + filename + ". Exiting!",self.file_name)
                   self.ocommon.prog_exit("127")

      ###########   ENDS here ####################

      def gsm_checks(self):
          """
          This function perform db checks before starting the setup
          """
          self.ohome_check()
          self.passwd_check()
          self.shard_user_check()
          self.gsm_hostname_check()
          self.director_params_checks()
          self.catalog_params_check()
          self.shard_params_check()
          self.sgroup_params_check()


      def catalog_checks(self):
          """
          This function perform db checks before starting the setup
          """
          self.ohome_check()
          self.passwd_check()
          self.shard_user_check()
          self.gsm_hostname_check()
          self.director_params_checks()
          self.catalog_params_check()
          self.sgroup_params_check()

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
           Set the password
           """
           self.ocommon.get_password(None)
           if self.ocommon.check_key("ORACLE_PWD",self.ora_env_dict):
               msg='''ORACLE_PWD key is set. Check Passed!'''
               self.ocommon.log_info_message(msg,self.file_name)                 

      def shard_user_check(self):
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

      def director_params_checks(self):
                 """
                 This funnction check and set the shard director name
                 """
                 status=False
                 reg_exp= self.director_regex()
                 for key in self.ora_env_dict.keys():
                   if(reg_exp.match(key)):
                       msg='''SHARD Director PARAMS {0} is set to {1}'''.format(key,self.ora_env_dict[key])
                       self.ocommon.log_info_message(msg,self.file_name)
                       status=True

      def gsm_hostname_check(self):
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

      def catalog_params_check(self):
                 """
                 This funnction check if CATALOG[1-9]_PARAMS such as CATALOG_PARAMS is passed as an env variable or not. If not passed then exit.
                 """
                 status=False
                 reg_exp= self.catalog_regex() 
                 for key in self.ora_env_dict.keys():
                     if(reg_exp.match(key)):
                        msg='''CATALOG PARAMS {0} is set to {1}'''.format(key,self.ora_env_dict[key])
                        self.ocommon.log_info_message(msg,self.file_name)
                        catalog_db,catalog_pdb,catalog_port,catalog_region,catalog_host,catalog_name,catalog_chunks,repl_type,repl_factor,repl_unit,stype,sspace,cfname=self.process_clog_vars(key)
                        if stype:
                          if stype.lower() == 'user':
                              if not self.ocommon.check_key("SHARDING_TYPE",self.ora_env_dict):
                                 self.ora_env_dict=self.ocommon.add_key("SHARDING_TYPE","USER",self.ora_env_dict)
                              if not self.ocommon.check_key("SHARD_SPACE",self.ora_env_dict):
                                 self.ora_env_dict=self.ocommon.add_key("SHARD_SPACE",sspace,self.ora_env_dict)
                        status=True

                 if not status:
                     msg="CATALOG[1-9]_PARAMS such as CATALOG_PARAMS is not set, exiting!"
                     self.ocommon.log_error_message(msg,self.file_name)
                     self.ocommon.prog_exit("127")

      def shard_params_check(self):
                 """
                 This funnction check if SHARD[1-9]_PARAMS such as SHARD1_PARAMS is passed as an env variable or not. If not passed then exit.
                 """
                 status=False
                 reg_exp= self.shard_regex()
                 for key in self.ora_env_dict.keys():
                     if(reg_exp.match(key)):
                        msg='''SHARD PARAMS {0} is set to {1}'''.format(key,self.ora_env_dict[key])
                        self.ocommon.log_info_message(msg,self.file_name)
                        status=True

                 if not status:
                     msg="SHARD[1-9]_PARAMS such as SHARD1_PARAMS is not set, exiting!"
                     self.ocommon.log_error_message(msg,self.file_name)
                     self.ocommon.prog_exit("127")

      def sgroup_params_check(self):
                 """
                 This funnction check if SHARD[1-9]_GROUP_PARAMS such as SHARD1_GROUP_PARAMS is passed as an env variable or not. If not passed then exit.
                 """
                 status=False
                 reg_exp= self.shardg_regex()
                 for key in self.ora_env_dict.keys():
                     if(reg_exp.match(key)):
                        msg='''SHARD GROUP PARAMS {0} is set to {1}'''.format(key,self.ora_env_dict[key])
                        self.ocommon.log_info_message(msg,self.file_name)
                        status=True
      def gsm_master_flag_check(self):
                 """
                 This funnction check if MASTER_GSM is passed as an env variable or not. If not passed then exit.
                 """
                 status=False
                 if self.ocommon.check_key("MASTER_GSM",self.ora_env_dict):
                    msg='''MASTER_GSM is set. This machine will be configured with as master GSM director.'''
                    self.ocommon.log_info_message(msg,self.file_name)
                    return True 
                 else:
                    return False

      def catalog_setup_checks(self):
                 """
                 This function checks if director and catalog is setup and connection is established.
                 """
                 status = False
                 gsm_status = self.check_gsm_director(None)
                 #catalog_status = self.check_gsm_catalog()

                 if gsm_status == 'completed':
                    status = True
                 else:
                    status = False

                 #if catalog_status == 'completed':
                 #   status = True
                 #else:
                 #   status = False

                 return status
             ###########  DB_CHECKS  Related Functions Begin Here  ####################


             ########## SETUP_CDB_catalog FUNCTION BEGIN HERE ###############################
      def reset_gsm_setup(self):
                 """
                  This function delete the GSM files.
                 """
                 self.ocommon.log_info_message("Inside reset_gsm_setup",self.file_name)
                 gsmdata_loc='/opt/oracle/gsmdata'
                 cmd_list=[]
                 if self.ocommon.check_key("RESET_ENV",self.ora_env_dict):
                    if self.ora_env_dict["RESET_ENV"]:
                       msg='''Deleteing files from {0}'''.format(gsmdata_loc)
                       self.ocommon.log_info_message(msg,self.file_name)
                       cmd_list[0]='''rm -f {0}/gsm.ora'''.format(gsmdata_loc)
                       cmd_list[1]='''rm -f {0}/tnsnames.ora'''.format(gsmdata_loc)
                       cmd_list[2]='''rm -rf {0}/wallets'''.format(gsmdata_loc)
                    for cmd in cmd_list:
                        output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
                        self.ocommon.check_os_err(output,error,retcode,True)

      def gsm_setup_check(self):
                 """
                  This function check if GSM is already setup on this
                 """
                 status=True
                 self.ocommon.log_info_message("Inside gsm_setup_check",self.file_name)
                 gsmdata_loc='/opt/oracle/gsmdata'
                 gsmfile_loc='''{0}/network/admin'''.format(self.ora_env_dict["ORACLE_HOME"])

                 gsmora='''{0}/gsm.ora'''.format(gsmdata_loc)
                 tnsnamesora='''{0}/tnsnames.ora'''.format(gsmdata_loc)
                 walletloc='''{0}/gsmwallet'''.format(gsmdata_loc)

                 if os.path.isfile(gsmora):
                    cmd='''cp -r -v -f {0} {1}/'''.format(gsmora,gsmfile_loc)
                    output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
                    self.ocommon.check_os_err(output,error,retcode,True)
                 else:
                    status=False

                 if os.path.isfile(tnsnamesora):
                    cmd='''cp -r -v -f {0} {1}/'''.format(tnsnamesora,gsmfile_loc)
                    output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
                    self.ocommon.check_os_err(output,error,retcode,True)
                 else:
                    status=False

                 if os.path.isdir(walletloc):
                    cmd='''cp -r -v -f {0} {1}/'''.format(walletloc,gsmfile_loc)
                    output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
                    self.ocommon.check_os_err(output,error,retcode,True)
                 else:
                    status=False

                 if status:
                    return True
                 else:
                    return False

      ####################  Catalog related Functions BEGINS Here ###########################
      def setup_gsm_calog(self):
                 """
                  This function setup the GSM catalog.
                 """
                 self.ocommon.log_info_message("Inside setup_gsm_calog()",self.file_name)
                 status=False
                 reg_exp= self.catalog_regex()
                 counter=1
                 end_counter=60
                 catalog_db_status=None
                 while counter < end_counter:                 
                       for key in self.ora_env_dict.keys():
                           if(reg_exp.match(key)):
                              catalog_db,catalog_pdb,catalog_port,catalog_region,catalog_host,catalog_name,catalog_chunks,repl_type,repl_factor,repl_unit,stype,sspace,cfname=self.process_clog_vars(key)
                              catalog_db_status=self.check_setup_status(catalog_host,catalog_db,catalog_pdb,catalog_port)
                              if catalog_db_status == 'completed':
                                 self.configure_gsm_clog(catalog_host,catalog_db,catalog_pdb,catalog_port,catalog_name,catalog_region,catalog_chunks,repl_type,repl_factor,repl_unit,stype,sspace,cfname)
                                 break 
                              else:
                                 msg='''Catalog Status must return completed but returned value is {0}'''.format(status)
                                 self.ocommon.log_info_message(msg,self.file_name)
                       if catalog_db_status == 'completed':
                          break
                       else:
                         msg='''Catalog setup is still not completed in GSM. Sleeping for 60 seconds and sleeping count is {0}'''.format(counter)
                         self.ocommon.log_info_message(msg,self.file_name)
                       time.sleep(60)
                       counter=counter+1

      def process_clog_vars(self,key):
          """
          This function process catalog vars based on key and return values to configure the GSM
          """
          catalog_db=None
          catalog_pdb=None
          catalog_port=None
          catalog_region=None
          catalog_host=None
          catalog_name=None
          catalog_chunks=None
          repl_type=None
          repl_factor=None
          repl_unit=None
          stype=None
          sspace=None
          cfname=None

          self.ocommon.log_info_message("Inside process_clog_vars()",self.file_name)
          cvar_str=self.ora_env_dict[key]
          cvar_dict=dict(item.split("=") for item in cvar_str.split(";"))
          for ckey in cvar_dict.keys():
              if ckey == 'catalog_db':
                 catalog_db = cvar_dict[ckey]
              if ckey == 'catalog_pdb':
                 catalog_pdb = cvar_dict[ckey]
              if ckey == 'catalog_port':
                 catalog_port = cvar_dict[ckey]
              if ckey == 'catalog_region':
                 catalog_region = cvar_dict[ckey]
              if ckey == 'catalog_host':
                 catalog_host = cvar_dict[ckey]
              if ckey == 'catalog_name':
                 catalog_name = cvar_dict[ckey]
              if ckey == 'catalog_chunks':
                 catalog_chunks = cvar_dict[ckey]
              if ckey == 'repl_type':
                 repl_type = cvar_dict[ckey]
              if ckey == 'repl_factor':
                 repl_factor = cvar_dict[ckey]
              if ckey == 'repl_unit':
                 repl_unit = cvar_dict[ckey]
              if ckey == 'sharding_type':
                 stype = cvar_dict[ckey]
              if ckey == 'shard_space':
                 sspace = cvar_dict[ckey]
              if ckey == 'shard_configname':
                 cfname = cvar_dict[ckey]
                       
              ## Set the values if not set in above block
          if not catalog_port:
              catalog_port=1521
          if not catalog_region:
              catalog_region="region1,region2"
          if stype:
             if not sspace:
               sspace="shardspace1,shardspace2"

              ### Check values must be set
          if catalog_host and catalog_db and catalog_pdb and catalog_port and catalog_region and catalog_name:
              return catalog_db,catalog_pdb,catalog_port,catalog_region,catalog_host,catalog_name,catalog_chunks,repl_type,repl_factor,repl_unit,stype,sspace,cfname
          else:
              msg1='''catalog_db={0},catalog_pdb={1}'''.format((catalog_db or "Missing Value"),(catalog_pdb or "Missing Value"))
              msg2='''catalog_port={0},catalog_host={1}'''.format((catalog_port or "Missing Value"),(catalog_host or "Missing Value"))
              msg3='''catalog_region={0},catalog_name={1}'''.format((catalog_region or "Missing Value"),(catalog_name or "Missing Value"))
              msg='''Catalog params {0} is not set correctly. One or more value is missing {1} {2} {3}'''.format(key,msg1,msg2,msg3)
              self.ocommon.log_info_message(msg,self.file_name)
              self.ocommon.prog_exit("127")

      def check_gsm_catalog(self):
          """
           This function check the catalog status in GSM
          """
          self.ocommon.log_info_message("Inside check_gsm_catalog()",self.file_name)
          #dtrname,dtrport,dtregion=self.process_director_vars()
          gsmcmd='''
            config;
            exit;
          '''.format("test")
          output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
          matched_output=re.findall("(?:GSMs\n)(?:.+\n)+",output)
          try:
             match=self.ocommon.check_substr_match(matched_output[0],"test")
          except:
             match=False
          return(self.ocommon.check_status_value(match))

        #  output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
        #  new_output=output[0].replace(" ","")
        #  self.ocommon.log_info_message(new_output,self.file_name)
        #  match=self.ocommon.check_substr_match(new_output,"Catalogconnectionisestablished")
        #  return(self.ocommon.check_status_value(match))

      def catalog_regex(self):
          """
            This function return the rgex to search the CATALOG PARAMS
          """ 
          self.ocommon.log_info_message("Inside catalog_regex()",self.file_name)
          return re.compile('CATALOG_PARAMS') 

      
      def configure_gsm_clog(self,chost,ccdb,cpdb,cport,catalog_name,catalog_region,catalog_chunks,repl_type,repl_factor,repl_unit,stype,sspace,cfname):
                 """
                  This function configure the GSM catalog.
                 """
                 self.ocommon.log_info_message("Inside configure_gsm_clog()",self.file_name)
                 gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
                 cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
                 replist=['native']             
    
                 ### User Define Shardig Variables
                 shardingtype=None
                 shardspace=None
                 configname=None
                 
                 # if stype and sspace: 
                 if stype:
                    if stype.lower() == 'user':
                        shardingtype="-sharding user"
                        #shardspace=""
                        shardspace=" -shardspace {0}".format(sspace)
                        if not self.ocommon.check_key("SHARDING_TYPE",self.ora_env_dict):
                           self.ora_env_dict=self.ocommon.add_key("SHARDING_TYPE","USER",self.ora_env_dict)
                        if not self.ocommon.check_key("SHARD_SPACE",self.ora_env_dict):
                           self.ora_env_dict=self.ocommon.add_key("SHARD_SPACE",sspace,self.ora_env_dict)
                    else:
                       shardspace=""
                       shardingtype=""
                 else:
                     shardspace=""
                     shardingtype=""
                       
                 if cfname:
                   configname=" -configname {0}".format(cfname)
                 else:
                  configname=""
                    
                 ### SNR Sharding
                 chunks=None
                 repl=None
                 repfactor=None
                 repunits=None
               
                 if catalog_chunks:
                    chunks="-chunks {0}".format(catalog_chunks)
                 else:
                    chunks=""

                 if repl_type and repl_type.lower() in replist:
                    self.ocommon.log_info_message("Repl_Type value Set to in block1:" + repl_type,self.file_name)
                    repl=" -repl {0}".format(repl_type)
                 else:
                    repl=""
                    
                 if repl_factor:
                    repfactor=" -repfactor {0}".format(repl_factor)
                 else:
                    repfactor=""

                 if repl_unit:
                    repunits=" -repunits {0}".format(repl_unit)
                 else:
                    repunits=""
                    
                 invited_subnet=""
                 add_invited_subnet=""
                 if self.ocommon.check_key("INVITED_NODE_SUBNET_FLAG",self.ora_env_dict):
                    if self.ocommon.check_key("INVITED_NODE_SUBNET",self.ora_env_dict):
                       invited_subnet=self.ora_env_dict["INVITED_NODE_SUBNET"]
                    else:
                       #self.ocommon.log_info_message("The catalog Host name is :" + chost,self.file_name)
                       chost_ip=self.ocommon.get_ip(chost,None)
                       ip_parts=chost_ip.split('.')
                       invited_subnet=ip_parts[0] + "." + ip_parts[1] + '.*' + '.*'
                    add_invited_subnet='''add invitedsubnet {0};'''.format(invited_subnet)
                 else:
                    chost_ip=self.ocommon.get_ip(chost,None)
                    ip_parts=chost_ip.split('.')
                    invited_subnet=ip_parts[0] + "." + ip_parts[1] + '.*' + '.*'
                    add_invited_subnet='''add invitedsubnet {0};'''.format(invited_subnet)

                 cpasswd="HIDDEN_STRING"
                 self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                 gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
                 gsmcmd='''
                  create shardcatalog -database \"(DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST={0})(PORT={1}))(CONNECT_DATA=(SERVICE_NAME={2})))\" {7} -user {3}/{4} -sdb {5} -region {6} -agent_port 8080 -agent_password {4} {8} {9} {10} {11} {12} {13} -autovncr off;
                  add invitednode {0};
                  {14}
                  exit;
                  '''.format(chost,cport,cpdb,cadmin,cpasswd,catalog_name,catalog_region,chunks,repl,repfactor,repunits,shardingtype,shardspace,configname,add_invited_subnet)

                 counter=1
                 while counter < 5:
                   output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
                   if retcode != 0:
                      self.ocommon.log_info_message("Error occurred while creating the shard catalog, sleeping for 60 seconds",self.file_name)
                      counter = counter + 1
                      time.sleep(60)
                   else:
                      break

                 ### Unsetting the encrypt value to None
                 self.ocommon.unset_mask_str()

      ########################################   GSM director Functions Begins Here #####################
      def process_director_vars(self,key):
          """
          This function process GSM director vars based on key and return values to configure the GSM
          """
          dtrname=None
          dtrport=None
          dtregion=None

          self.ocommon.log_info_message("Inside process_director_vars()",self.file_name)
          cvar_str=self.ora_env_dict[key]
          cvar_dict=dict(item.split("=") for item in cvar_str.split(";"))
          for ckey in cvar_dict.keys():
              if ckey == 'director_name':
                 dtrname = cvar_dict[ckey]
              if ckey == 'director_port':
                 dtrport = cvar_dict[ckey]
              if ckey == 'director_region':
                 dtregion = cvar_dict[ckey]

              ### Check values must be set
          if dtrname and dtrport and dtregion:
             return dtrname,dtrport,dtregion
          else:
             msg1='''director_name={0},director_port={1}'''.format((dtrname or "Missing Value"),(dtrport or "Missing Value"))
             msg2='''director_region={0}'''.format((dtregion or "Missing Value"))
             msg='''Director params {0} is not set correctly. One or more value is missing {1} {2}'''.format(key,msg1,msg2)
             self.ocommon.log_error_message(msg,self.file_name)
             self.ocommon.prog_exit("Error occurred")

      def check_gsm_director(self,dname):
          """
          This function check the GSM director status
          """  
          self.ocommon.log_info_message("Inside check_gsm_director()",self.file_name)
          status=False
          if dname:
            gsmcmd=self.get_gsm_config_cmd(dname)
            output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
            matched_output=re.findall("(?:GSMs\n)(?:.+\n)+",output)
            try:
              if self.ocommon.check_substr_match(matched_output[0],dname):
                 status=True   
            except:
              status=False 
          else:
            reg_exp= self.director_regex()
            for key in self.ora_env_dict.keys():
                if(reg_exp.match(key)):
                    dname,dtrport,dtregion=self.process_director_vars(key)
                    gsmcmd=self.get_gsm_config_cmd(dname)
                    output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
                    matched_output=re.findall("(?:GSMs\n)(?:.+\n)+",output)
                    try:
                      if self.ocommon.check_substr_match(matched_output[0],dname):
                         status=True
                    except:
                         status=False

          return(self.ocommon.check_status_value(status))

      def check_gsm_region(self,region):
          """
          This function check the GSM regions
          """  
          self.ocommon.log_info_message("Inside check_gsm_region()",self.file_name)
          gsmcmd=self.get_gsm_config_cmd(None)
          output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
          matched_output=re.findall("(?:Regions\n)(?:.+\n)+",output)
          status=False
          try:
            if self.ocommon.check_substr_match(matched_output[0],region):
              status=True   
          except:
             status=False 
          return(self.ocommon.check_status_value(status))

      def check_gsm_shardspace(self,sspace):
          """
          This function check the GSM shardspace
          """  
          self.ocommon.log_info_message("Inside check_gsm_shardspace()",self.file_name)
          gsmcmd=self.get_gsm_config_cmd(None)
          output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
          matched_output=re.findall("(?:Shard spaces\n)(?:.+\n)+",output)
          status=False
          try:
            if self.ocommon.check_substr_match(matched_output[0],sspace):
              status=True   
          except:
             status=False 
          return(self.ocommon.check_status_value(status))
       
      def check_gsm_director_status(self,dname):
          """
          This function check the GSM director status using 'gdsctl status'
          """
          self.ocommon.log_info_message("Inside check_gsm_director_status()",self.file_name)
          status=False
          gsmcmd='''
           status;
           exit;
          '''
          output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
          if "Connected to GDS catalog      Y".replace(" ","").lower() in output.replace(" ","").lower():
             return True
          else:
            return False

      def add_gsm_director(self):
          """ 
           This function add the GSM
          """
          status=False
          counter=1
          end_counter=60
          gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
          cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
          cpasswd="HIDDEN_STRING"
          gsm_trace_level=self.get_gsm_trace_level()
          reg_exp= self.director_regex()

          while counter < end_counter:
             for key in self.ora_env_dict.keys():
                 if(reg_exp.match(key)):
                     shard_director_status=None
                     dtrname,dtrport,dtregion=self.process_director_vars(key)
                     shard_director_status=self.check_gsm_director(dtrname)
                     if shard_director_status != 'completed':
                         self.configure_gsm_director(dtrname,dtrport,dtregion,gsmhost,cadmin,gsm_trace_level)
                     status = self.check_gsm_director(None)
                     if status == 'completed':
                          break
                     
             if status == 'completed':
               break
             else:             
               msg='''GSM shard director setup is still not completed in GSM. Sleeping for 60 seconds and sleeping count is {0}'''.format(counter)
               self.ocommon.log_info_message(msg,self.file_name)
               time.sleep(60)
               counter=counter+1

          status = self.check_gsm_director(None)
          if status == 'completed':
             msg='''Shard director  setup completed in GSM'''
             self.ocommon.log_info_message(msg,self.file_name)
          else:
             msg='''Waited 60 minute to complete shard director in GSM but setup did not complete or failed. Exiting...'''
             self.ocommon.log_error_message(msg,self.file_name)
             self.ocommon.prog_exit("127")
             
      def setup_gsm_director(self):
                 """
                 This function setup in GSM
                 """
                 self.ocommon.log_info_message("Inside setup_gsm_director()",self.file_name)
                 status=False
                 reg_exp= self.director_regex()
                 counter=1
                 end_counter=3
                 gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
                 cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
                 cpasswd="HIDDEN_STRING"
                 gsm_trace_level=self.get_gsm_trace_level()
                 while counter < end_counter:
                     for key in self.ora_env_dict.keys():
                         if(reg_exp.match(key)):
                            shard_director_status=None
                            dtrname,dtrport,dtregion=self.process_director_vars(key)
                            shard_director_status=self.check_gsm_director(dtrname)
                            if shard_director_status != 'completed':
                               self.configure_gsm_director(dtrname,dtrport,dtregion,gsmhost,cadmin,gsm_trace_level)
                     status = self.check_gsm_director(None)
                     if status == 'completed':
                        break
                     else:
                        msg='''GSM shard director setup is still not completed in GSM. Sleeping for 60 seconds and sleeping count is {0}'''.format(counter)
                     time.sleep(60)
                     counter=counter+1                              
                      
                 status = self.check_gsm_director(None)
                 if status == 'completed':
                   msg='''Shard director  setup completed in GSM'''
                   self.ocommon.log_info_message(msg,self.file_name)
                 else:
                   msg='''Waited 3 minute to complete shard director in GSM but setup did not complete or failed. Exiting...'''
                   self.ocommon.log_error_message(msg,self.file_name)
                   self.ocommon.prog_exit("127") 

      def configure_gsm_director(self,dtrname,dtrport,dtregion,gsmhost,cadmin,gsmtr):
                 """
                 This function configure GSM director
                 """
                 ## Getting the values of catalog_port,catalog_pdb,catalog_host
                 cpasswd="HIDDEN_STRING"
                 reg_exp= self.catalog_regex()
                 for key in self.ora_env_dict.keys():
                     if(reg_exp.match(key)):
                        catalog_db,catalog_pdb,catalog_port,catalog_region,catalog_host,catalog_name,catalog_chunks,repl_type,repl_factor,repl_unit,stype,sspace,cfname=self.process_clog_vars(key)
                 sregionFlag=self.check_gsm_region(dtregion)
                 if sregionFlag != 'completed':
                    self.configure_gsm_region(dtregion)
                 self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                 gsmcmd='''
                  add gsm -gsm {0}  -listener {1} -pwd {2} -catalog {3}:{4}/{5}  -region {6} -trace_level {8};
                  exit;
                  '''.format(dtrname,dtrport,cpasswd,catalog_host,catalog_port,catalog_pdb,dtregion,gsmhost,gsmtr)
                 output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)

                 ### Unsetting the encrypt value to None
                 self.ocommon.unset_mask_str()
                
      def start_gsm_director(self):
                 """
                 This function start the director in the GSM
                 """
                 status='noval'
                 self.ocommon.log_info_message("Inside start_gsm_director() function",self.file_name)
                 reg_exp= self.director_regex()
                 counter=1
                 end_counter=10
                 while counter < end_counter:
                   for key in self.ora_env_dict.keys():
                       if(reg_exp.match(key)):
                          dtrname,dtrport,dtregion=self.process_director_vars(key)
                          gsmcmd='''
                            start gsm -gsm {0};
                            exit;
                          '''.format(dtrname)
                          output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)             
                          status=self.check_gsm_director(dtrname)
                          if status == 'completed':
                             break;
                   if status == 'completed':
                      filename=self.ora_env_dict["GSM_LOCK_STATUS_FILE"]
                      remfile='''rm -f {0}'''.format(filename)
                      if os.path.isfile(filename):
                         output,error,retcode=self.ocommon.execute_cmd(remfile,None,self.ora_env_dict)
                      break
                   else:
                      msg='''GSM shard director failed to start.Sleeping for 60 seconds and sleeping count is {0}'''.format(counter)
                      self.ocommon.log_error_message(msg,self.file_name)
                      time.sleep(30)

                   counter=counter+1 
                                             

                 if status != 'completed':
                      msg='''GSM shard director failed to start.Exiting!'''
                      self.ocommon.log_error_message(msg,self.file_name)
                      self.ocommon.prog_exit("127")
                     
      def stop_gsm_director(self):
                 """
                 This function stop the director in the GSM
                 """
                 status=False
                 self.ocommon.log_info_message("Inside stop_gsm_director() function",self.file_name)
                 reg_exp= self.director_regex()
                 counter=1
                 end_counter=2
                 while counter < end_counter:
                   for key in self.ora_env_dict.keys():
                       if(reg_exp.match(key)):
                         dtrname,dtrport,dtregion=self.process_director_vars(key)
                         gsmcmd='''
                           stop gsm -gsm {0};
                           exit;
                         '''.format(dtrname)
                         output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
                   counter=counter+1

      def status_gsm_director(self):
                 """
                 This function check the GSM director status 
                 """
                 gsm_status = self.check_gsm_director(None)
                 #catalog_status = self.check_gsm_catalog()

                 if gsm_status == 'completed':
                    msg='''Director setup completed in GSM and catalog is connected'''
                    self.ocommon.log_info_message(msg,self.file_name)
                 else:
                    msg='''Shard director in GSM did not complete or not connected to catalog. Exiting...'''
                    self.ocommon.log_error_message(msg,self.file_name)
                    self.ocommon.prog_exit("127")

      ######################################## Shard Group Setup Begins Here ############################
      def setup_gsm_shardg(self,restype):
                 """
                  This function setup the shard group.
                 """
                 self.ocommon.log_info_message("Inside setup_gsm_shardg()",self.file_name)
                 status=False
                 if restype == 'ADD_SGROUP_PARAMS':
                    reg_exp = self.add_shardg_regex()
                 elif restype == 'SHARD_GROUP':
                    reg_exp = self.shardg_regex()
                 else:
                    self.ocommon.log_warn_message("No Key Specified! You can only pass ADD_SGROUP_PARAMS or SHARD_GROUP key to create a shard group",self.file_name)
                    self.ocommon.log_warn_message("Since no key specified for ADD_SGROUP_PARAMS and SHARD_GROUP, shardgroup will be created during shard creation",self.file_name)
                
                 sgListC=[]
                 sgListP=[]
                 counter=1
                 end_counter=3
                 while counter < end_counter:
                       for key in self.ora_env_dict.keys():
                           if(reg_exp.match(key)):
                              shard_group_status=None
                              self.ocommon.log_info_message("Key is set to : " + key,self.file_name)
                              group_name,deploy_as,group_region=self.process_shardg_vars(key)
                              self.ocommon.log_info_message("Name: " + group_name + "deploy_as" + deploy_as + "group_region" + group_region,self.file_name)
                              if group_name is not None:
                                 if group_name not in sgListC:
                                    dtrname=self.get_director_name(group_region)
                                    shard_group_status=self.check_shardg_status(group_name,dtrname)
                                    if shard_group_status != 'completed':
                                       self.configure_gsm_shardg(group_name,deploy_as,group_region,'add')
                                       shard_group_status = self.check_shardg_status(group_name,None)
                                       if shard_group_status == 'completed':
                                          sgListC.append(group_name)
                                          if group_name in sgListP: 
                                             sgListP.remove(group_name)
                                       else:
                                          sgListP=sgListP.append(group_name)
                                          time.sleep(30)
                           counter=counter + 1
                           
                 if sgListP == []:
                    msg='''Shard group setup completed in GSM'''
                    self.ocommon.log_info_message(msg,self.file_name)
                 else:
                    msg='''Waited 2 minute to complete catalog setup in GSM but setup did not complete or failed. Exiting...'''
                    self.ocommon.log_error_message(msg,self.file_name)
                    self.ocommon.prog_exit("127")

      def get_director_name(self,region_name):
          """
          This function get the director name based on the region
          """
          self.ocommon.log_info_message("Inside get_director_name()",self.file_name)
          status=False
          director_name=None
          reg_exp= self.director_regex()
          for key in self.ora_env_dict.keys():
              if(reg_exp.match(key)): 
                 dtrname,dtrport,dtregion=self.process_director_vars(key)
                 director_name=dtrname
                 gsm_status = self.check_gsm_director(dtrname)
                 if gsm_status == 'completed':
                    status = True
                 else:
                    status = False
                 if dtregion == region_name:
                    break
          if status:
             if director_name:
                return director_name
             else:
                self.ocommon.log_error_message("No director exist to match the region",self.file_name)
                self.ocommon.prog_exit("127")
          else:
             self.ocommon.log_error_message("Shard Director is not running!",self.file_name)
             self.ocommon.prog_exit("127")
            
      def get_shardg_region_name(self,sgname):
          """
          This function get the region name based on shard group name
          """
          self.ocommon.log_info_message("Inside get_region_name()",self.file_name)
          status=False
          region_name=None
          reg_exp= self.shardg_regex()
          for key in self.ora_env_dict.keys():
              if(reg_exp.match(key)):
                 group_name,deploy_as,group_region=self.process_shardg_vars(key)
                 region_name=group_region 
                 if sgname == group_name:
                    status=True
                    break
          if status:
             return region_name
          else:
             self.ocommon.log_error_message("No such shard group exist! exiting!",self.file_name)
             self.ocommon.prog_exit("127")

      def process_shardg_vars(self,key):
          """
          This function process shardG vars based on key and return values to configure the GSM
          """
          group_name=None
          deploy_as=None
          group_region=None
 
          self.ocommon.log_info_message("Inside process_shardg_vars()",self.file_name)
          cvar_str=self.ora_env_dict[key]
          cvar_dict=dict(item.split("=") for item in cvar_str.split(";"))
          for ckey in cvar_dict.keys():
              if ckey == 'group_name':
                 group_name = cvar_dict[ckey]
              if ckey == 'deploy_as':
                 deploy_as = cvar_dict[ckey]
              if ckey == 'group_region':
                 group_region = cvar_dict[ckey]

              ### Check values must be set
          if group_name and deploy_as and group_region:
             return group_name,deploy_as,group_region
          else:
             msg1='''group_name={0},deploy_as={1}'''.format((group_name or "Missing Value"),(deploy_as or "Missing Value"))
             msg2='''group_region={0}'''.format((group_region or "Missing Value"))
             msg='''Shard group params {0} is not set correctly. One or more value is missing {1} {2}'''.format(key,msg1,msg2)
             self.ocommon.log_error_message(msg,self.file_name)
             self.ocommon.prog_exit("Error occurred")

      
      def check_shardg_status(self,group_name,dname):
         """
         This function check the shard status in GSM
         """
         self.ocommon.log_info_message("Inside check_shardg_status()",self.file_name)
         status=False

         gsmcmd=self.get_gsm_config_cmd(dname)
         output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
         matched_output=re.findall("(?:Shard Groups\n)(?:.+\n)+",output)
         if self.ocommon.check_substr_match(matched_output[0],group_name):
            status=True
         else:
            status=False
            
         '''
          else:   
             reg_exp= self.shardg_regex()
             for key in self.ora_env_dict.keys():
                 if(reg_exp.match(key)):
                     group_name,deploy_as,group_region=self.process_shardg_vars(key)
                     dname=self.get_director_name(group_region)
                     gsmcmd=self.get_gsm_config_cmd(dname)
                     output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
                     matched_output=re.findall("(?:Shard Groups\n)(?:.+\n)+",output)  
                   #  match=re.search("(?i)(?m)"+group_name,matched_output)
                     if self.ocommon.check_substr_match(matched_output[0],group_name):
                          status=True
                     else:
                          status=False
         '''
         
         return(self.ocommon.check_status_value(status))

############################################# Director Related Block ############
      def get_director_name(self,region_name):
          """
          This function get the director name based on the region
          """
          self.ocommon.log_info_message("Inside get_director_name()",self.file_name)
          status=False
          director_name=None
          reg_exp= self.director_regex()
          for key in self.ora_env_dict.keys():
              if(reg_exp.match(key)): 
                 dtrname,dtrport,dtregion=self.process_director_vars(key)
                 director_name=dtrname
                 gsm_status = self.check_gsm_director(dtrname)
                 if gsm_status == 'completed':
                    status = True
                 else:
                    status = False
                 if dtregion == region_name:
                    break
          if status:
             if director_name:
                return director_name
             else:
                self.ocommon.log_error_message("No director exist to match the region",self.file_name)
                self.ocommon.prog_exit("127")
          else:
             self.ocommon.log_error_message("Shard Director is not running!",self.file_name)
             self.ocommon.prog_exit("127")

########

      def get_gsm_config_cmd(self,dname):
          """
            Get the GSM config command
          """
          self.ocommon.log_info_message("Inside get_gsm_config_cmd()",self.file_name)
          gsmcmd='''
            config;
            exit;
          '''.format("test")
          return gsmcmd
      
      def director_regex(self):
          """
            This function return the rgex to search the SHARD DIRECTOR  PARAMS
          """
          self.ocommon.log_info_message("Inside director_regex()",self.file_name)
          return re.compile('SHARD_DIRECTOR_PARAMS')

      def shardg_regex(self):
          """
            This function return the rgex to search the SHARD GROUP PARAMS
          """
          self.ocommon.log_info_message("Inside shardg_regex()",self.file_name)
          return re.compile('SHARD[0-9]+_GROUP_PARAMS')

      def add_shardg_regex(self):
          """
            This function return the rgex to search the SHARD GROUP PARAMS
          """
          self.ocommon.log_info_message("Inside shardg_regex()",self.file_name)
          return re.compile('ADD_SGROUP_PARAMS')

      def configure_gsm_shardg(self,group_name,deploy_as,group_region,type):
                 """
                  This function configure the Shard Group.
                 """
                 self.ocommon.log_info_message("Inside configure_gsm_shardg()",self.file_name)
                 cmd=None
                 gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
                 cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
                 cpasswd="HIDDEN_STRING"
                 dtrname=self.get_director_name(group_region)
                 reg_exp= self.catalog_regex()
                 if type == 'modify':
                    cmd=''' modify shardgroup -shardgroup {0} '''.format(group_name)
                 else:
                    cmd=''' add shardgroup -shardgroup {0} '''.format(group_name)

                 for key in self.ora_env_dict.keys():
                    if(reg_exp.match(key)):
                       catalog_db,catalog_pdb,catalog_port,catalog_region,catalog_host,catalog_name,catalog_chunks,repl_type,repl_factor,repl_unit,stype,sspace,cfname=self.process_clog_vars(key)
                       if repl_type:
                         cmd=cmd + " -region {0} ".format(group_region)
                       else:
                         cmd=cmd + " -deploy_as {0} -region {1} ".format(deploy_as,group_region)

                 self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                 gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
                 gsmcmd='''
                   connect {1}/{2};
                   {3};
                 exit;
                  '''.format("NA",cadmin,cpasswd,cmd)
                 output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)                 

                 ### Unsetting the encrypt value to None
                 self.ocommon.unset_mask_str()

############# Adding Shard Regions ###############
      def configure_gsm_region(self,region):
                 """
                  This function configure the Shard region.
                 """
                 self.ocommon.log_info_message("Inside configure_gsm_region()",self.file_name)
                 cmd=None
                 gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
                 cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
                 cpasswd="HIDDEN_STRING"
                 self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                 gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
                 gsmcmd='''
                   connect {1}/{2};
                   add region -region {3};
                 exit;
                  '''.format("NA",cadmin,cpasswd,region)
                 output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)                 

                 ### Unsetting the encrypt value to None
                 self.ocommon.unset_mask_str()
                 
##################### Adding Shard Space ###############
      def process_sspace_vars(self,key):
          """
          This function process shardG vars based on key and return values to configure the GSM
          """
          sspace=None
          chunks=None
          repfactor=None
          repunits=None
          protectedmode=None
          self.ocommon.log_info_message("Inside process_sspace_vars()",self.file_name)
          cvar_str=self.ora_env_dict[key]
          cvar_dict=dict(item.split("=") for item in cvar_str.split(";"))
          for ckey in cvar_dict.keys():
              if ckey == 'sspace_name':
                 sspace = cvar_dict[ckey]
              if ckey == 'chunks':
                 chunks = cvar_dict[ckey]
              if ckey == 'repfactor':
                 repfactor = cvar_dict[ckey]
              if ckey == 'repunits':
                 repunits = cvar_dict[ckey]
              if ckey == 'protectedmode':
                 protectedmode = cvar_dict[ckey]
                 
              ### Check values must be set
          if sspace:
             return sspace,chunks,repfactor,repunits,protectedmode
          else:
             msg1='''sspace={0}'''.format((sspace or "Missing Value"))
             msg='''Shard space params {0} is not set correctly. One or more value is missing {1}'''.format(key,msg1)
             self.ocommon.log_error_message(msg,self.file_name)
             self.ocommon.prog_exit("Error occurred")
             
      def setup_gsm_sspace(self,restype):
                 """
                  This function setup the shard sspace.
                 """
                 self.ocommon.log_info_message("Inside setup_gsm_sspace()",self.file_name)
                 status=False
                 if restype == 'ADD_SSPACE_PARAMS':
                    reg_exp = self.add_shardg_regex()
                 elif restype == 'SHARD_SPACE':
                    reg_exp = self.shardg_regex()
                 else:
                    self.ocommon.log_warn_message("No Key Specified! You can only pass ADD_SSPACE_PARAMS or SHARD_SPACE key to create a shard space",self.file_name)
                    self.ocommon.log_warn_message("Since no ADD_SSPACE_PARAMS or SHARD_SPACE defined, shardspace will be created during shard creation",self.file_name)
                 counter=1
                 ssListC=[]
                 ssListP=[]
                 counter=1
                 end_counter=3
                 while counter < end_counter:
                       for key in self.ora_env_dict.keys():
                           if(reg_exp.match(key)):
                              shard_space_status=None
                              sspace,chunks,repfactor,repuntis,protectedmode=self.process_sspace_vars(key)
                              if sspace is not None:
                                 if sspace not in ssListC:
                                   shard_sspace_status=self.check_gsm_shardspace(sspace)
                                   if shard_sspace_status != 'completed':
                                      self.configure_gsm_sspace(sspace,chunks,repfactor,repuntis,protectedmode,'add')
                                      shard_space_status = self.check_gsm_shardspace(sspace)
                                      if shard_sspace_status == 'completed':
                                          ssListC.append(sspace)
                                          if sspace in sgListP: 
                                             sgListP.remove(sspace)
                                      else:
                                          sgListP=sgListP.append(sspace)
                                          time.sleep(30)
                           counter=counter + 1

                 if ssListP == []:
                    msg='''Shard space setup completed in GSM'''
                    self.ocommon.log_info_message(msg,self.file_name)
                 else:
                    msg='''Waited 2 minute to complete shard space setup in GSM but setup did not complete or failed. Exiting...'''
                    self.ocommon.log_error_message(msg,self.file_name)
                    self.ocommon.prog_exit("127")
                    
      def configure_gsm_sspace(self,sspace,chunks,repfactor,repunits,protectedmode,type):
                 """
                  This function configure the Shard Group.
                 """
                 self.ocommon.log_info_message("Inside configure_gsm_sspace()",self.file_name)
                 cmd=None
                 gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
                 cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
                 cpasswd="HIDDEN_STRING"
                 if type == 'MODIFY':
                  cmd=''' modify shardspace -shardspace {0} '''.format(sspace)
                 else:
                   cmd=''' add shardspace -shardspace {0} '''.format(sspace)
                 if chunks is not None:
                    cmd = cmd + ''' -chunks {0}'''.format(chunks)
                 if repfactor:
                    cmd = cmd + ''' -repfactor {0}'''.format(repfactor)
                 if repunits is not None:
                    cmd = cmd + ''' -repunits {0}'''.format(repfactor)
                 if protectedmode is not None:
                    cmd = cmd + ''' -protectedmode {0}'''.format(protectedmode)

                 self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                 gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
                 gsmcmd='''
                   connect {1}/{2};
                   {3};
                 exit;
                  '''.format("NA",cadmin,cpasswd,cmd)
                 output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)                 
                 ### Unsetting the encrypt value to None
                 self.ocommon.unset_mask_str()
                 
        #########################################Shard Function Begins Here ##############################
      def setup_gsm_shard(self):
                """
                This function setup and add shard in the GSM
                """
                self.ocommon.log_info_message("Inside setup_gsm_shard()",self.file_name)
                status=False
                reg_exp= self.shard_regex()
                counter=1
                end_counter=60
                while counter < end_counter:                 
                      for key in self.ora_env_dict.keys():
                          if(reg_exp.match(key)):
                             shard_db_status=None
                             shard_db,shard_pdb,shard_port,shard_group,shard_host,sregion,sspace=self.process_shard_vars(key)
                             shard_db_status=self.check_setup_status(shard_host,shard_db,shard_pdb,shard_port)
                             if shard_db_status == 'completed':
                                self.configure_gsm_shard(shard_host,shard_db,shard_pdb,shard_port,shard_group,sregion,sspace)
                             else:
                                msg='''Shard db status must return completed but returned value is {0}'''.format(status)
                                self.ocommon.log_info_message(msg,self.file_name)
                                
                      status = self.check_shard_status(None) 
                      if status == 'completed':
                         break
                      else:
                         msg='''Shard DB setup is still not completed in GSM. Sleeping for 60 seconds and sleeping count is {0}'''.format(counter)
                         self.ocommon.log_info_message(msg,self.file_name)
                      time.sleep(60)
                      counter=counter+1

                status = self.check_shard_status(None)
                if status == 'completed':
                   msg='''Shard DB setup completed in GSM'''
                   self.ocommon.log_info_message(msg,self.file_name)
                else:
                   msg='''Waited 60 minute to complete shard db setup in GSM but setup did not complete or failed. Exiting...'''
                   self.ocommon.log_error_message(msg,self.file_name)
                   self.ocommon.prog_exit("127")     

      def add_gsm_shard(self):
                """
                This function add the shard in the GSM
                """
                self.ocommon.log_info_message("Inside add_gsm_shard()",self.file_name)
                status=False
                reg_exp= self.add_shard_regex()
                counter=1
                end_counter=3
                shard_name="none"
                while counter < end_counter:
                      for key in self.ora_env_dict.keys():
                          if(reg_exp.match(key)):
                             shard_db_status=None
                             shard_db,shard_pdb,shard_port,shard_group,shard_host,shard_region,shard_space=self.process_shard_vars(key)
                             shard_name='''{0}_{1}'''.format(shard_db,shard_pdb)
                             shard_db_status=self.check_setup_status(shard_host,shard_db,shard_pdb,shard_port)
                             self.ocommon.log_info_message("Shard Status : " + shard_db_status,self.file_name)
                             if shard_db_status == 'completed':
                                self.configure_gsm_shard(shard_host,shard_db,shard_pdb,shard_port,shard_group,shard_region,shard_space)
                                counter2=1
                                end_counter2=5
                                while counter2 < end_counter2:
                                       status1 = self.check_shard_status(shard_name)
                                       if status1 == 'completed':
                                          msg='''Shard DB setup completed in GSM'''
                                          self.ocommon.log_info_message(msg,self.file_name)
                                          break
                                       else:
                                          msg='''Shard DB is still not added in GSM. Sleeping for 60 seconds'''
                                          self.ocommon.log_info_message(msg,self.file_name)
                                          time.sleep(60)
                                          counter2=counter2+1
                             else:
                                msg='''Shard db status must return completed but returned value is {0}'''.format(status)
                                self.ocommon.log_info_message(msg,self.file_name)
                      
                      status = self.check_shard_status(None)
                      if status == 'completed':
                         break
                      else:
                         msg='''Shard DB setup is still not completed in GSM. Sleeping for 60 seconds and sleeping count is {0}'''.format(counter)
                         self.ocommon.log_info_message(msg,self.file_name)
                      time.sleep(60)
                      counter=counter+1
                status = self.check_shard_status(shard_name)
                if status == 'completed':
                   msg='''Shard DB setup completed in GSM'''
                   self.ocommon.log_info_message(msg,self.file_name)
                else:
                   msg='''Waited 3 minute to complete shard db setup in GSM but setup did not complete or failed. Exiting...'''
                   self.ocommon.log_error_message(msg,self.file_name)
                   self.ocommon.prog_exit("127")

      def remove_gsm_shard(self):
                """
                This function remove the shard in the GSM
                """
                self.ocommon.log_info_message("Inside remove_gsm_shard()",self.file_name)
                catalog_db,catalog_pdb,catalog_port,catalog_region,catalog_host,catalog_name,catalog_chunks,repl_type,repl_factor,repl_unit,stype,sspace,cfname=self.process_clog_vars("CATALOG_PARAMS")
                numOfShards=self.count_online_shards()
                status=False
                reg_exp=self.remove_shard_regex()
                for key in self.ora_env_dict.keys():
                    if(reg_exp.match(key)):
                          shard_db_status=None
                          shard_db,shard_pdb,shard_port,shard_group,shard_host,shard_region,shard_space=self.process_shard_vars(key)
                          shardname_to_delete=shard_db + "_" + shard_pdb
                          if repl_type is not None:
                            if(repl_type.upper() == 'NATIVE'):
                               self.move_shards_leader_rus(shardname_to_delete)
                               leaderCount=self.count_leader_shards(shardname_to_delete)
                               if(numOfShards < 4 or leaderCount > 0):
                                  msg='''ruType=[{0}]. NumofShards=[{1}]. LeaderCount=[{2}]. Ignoring remove of shard [{3}]'''.format(repl_type,numOfShards,leaderCount,shardname_to_delete)
                                  self.ocommon.log_info_message(msg,self.file_name)
                                  break

                               self.move_shard_rus(shardname_to_delete,None,None)
                               while self.count_shard_rus(shardname_to_delete) > 0:
                                   self.ocommon.log_info_message("Waiting for all the shard chunks to be moved.",self.file_name)
                                   time.sleep(15)

                          shard_db_status=self.check_setup_status(shard_host,shard_db,shard_pdb,shard_port)
                          if shard_db_status == 'completed':
                             self.delete_gsm_shard(shard_host,shard_db,shard_pdb,shard_port,shard_group)
                             status=True
                          else:
                             msg='''Shard db status must return completed but returned value is {0}'''.format(status)
                             self.ocommon.log_info_message(msg,self.file_name)

                return status

      def move_shards_leader_rus(self,shardname_to_delete):
          """
          This function move the shard leader RUs
          """
          shards=self.get_online_shards()
          leader_ru=self.get_rus(shardname_to_delete)
          all_ru=self.get_rus(None)
          count=0
          target_shards=[]
          value=0
          
          if len(shards) == 0:
            msg="""No Shard is online so no RU is available to be moved"""
            self.ocommon.log_info_message(msg,self.file_name)
          else:
            for line in leader_ru:
                value=None
                count += 1
                cols=line.split()
                if len(cols) > 0:
                  if cols[0].lower() == shardname_to_delete.lower():
                    if cols[1].isdigit:
                       value = int(cols[1])
                    else:
                       continue
             
                  target_shards.clear()
                  for line1 in all_ru:
                    cols1=line1.split()
                    print(cols1)
                    if len(cols1) > 5:
                      if cols1[0].lower() != shardname_to_delete.lower() and cols1[1].isdigit and cols1[2].lower() == 'follower':
                        if value is not None:
                          if int(cols1[1]) == value:
                             target_shards.append(cols1[0])
                             break

                  for shard in shards:
                    if shard.lower() != shardname_to_delete.lower():
                      if shard in target_shards:
                        msg="Shard_name= " + shard + " Status=True"  + "  Value = " + str(value)
                        self.ocommon.log_info_message(msg,self.file_name)
                        self.move_shard_rus(shardname_to_delete,shard,value)
                    
      def move_shard_chunks(self):
                """
                This function move the shard chunks
                """
                self.ocommon.log_info_message("Inside move_shard_chunks()",self.file_name)
                status=False
                reg_exp= self.move_chunks_regex()
                for key in self.ora_env_dict.keys():
                    if(reg_exp.match(key)):
                          gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
                          cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
                          cpasswd="HIDDEN_STRING"
                          gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
                          move_chunks_status=None
                          shard_db,shard_pdb=self.process_chunks_vars(key) 
                          shard_name = '''{0}_{1}'''.format(shard_db,shard_pdb)
                          shard_num = self.count_online_shards()
                          online_shard = self.check_online_shard(shard_name)      
                          if shard_num > 1 and online_shard == 0 :
                             self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                             gsmcmd='''
                              connect {1}/{2};
                              MOVE CHUNK -CHUNK ALL -SOURCE {0}
                              config shard;
                              exit;
                             '''.format(shard_name,cadmin,cpasswd)
                             output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
                             ### Unsetting the encrypt value to None
                             self.ocommon.unset_mask_str()

      def validate_nochunks(self):
                """
                This function check the chnunks
                """
                self.ocommon.log_info_message("Inside validate_nochunks()",self.file_name)
                status=False
                reg_exp= self.move_nochunks_regex()
                for key in self.ora_env_dict.keys():
                    if(reg_exp.match(key)):
                          gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
                          cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
                          cpasswd="HIDDEN_STRING"
                          gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
                          move_chunks_status=None
                          shard_db,shard_pdb=self.process_chunks_vars(key)
                          shard_name = '''{0}_{1}'''.format(shard_db,shard_pdb)
                          shard_num = self.count_online_shards()
                          online_shard = self.check_online_shard(shard_name)
                          if shard_num > 1 and online_shard == 0 :
                             self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                             gsmcmd='''
                              connect {1}/{2};
                              config chunks -shard {0}
                              exit;
                             '''.format(shard_name,cadmin,cpasswd)
                             output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
                             ### Unsetting the encrypt value to None
                             self.ocommon.unset_mask_str()
                             matched_output=re.findall("(?:Chunks\n)(?:.+\n)+",output)  
                             if self.ocommon.check_substr_match(matched_output[0].lower(),shard_name.lower()):
                                self.ocommon.prog_exit("127")

      def move_chunks_regex(self):
          """
            This function return the rgex to search the SHARD PARAMS
          """
          self.ocommon.log_info_message("Inside move_chnuks_regex()",self.file_name)
          return re.compile('MOVE_CHUNKS')

      def move_nochunks_regex(self):
          """
            This function return the rgex to search the SHARD PARAMS
          """
          self.ocommon.log_info_message("Inside move_nochunks_regex()",self.file_name)
          return re.compile('VALIDATE_NOCHUNKS')

      def check_shard_chunks(self):
                """
                This function check the shard chunks
                """
                self.ocommon.log_info_message("Inside check_shard_chunks()",self.file_name)
                status=False
                reg_exp= self.check_chunks_regex()
                for key in self.ora_env_dict.keys():
                    if(reg_exp.match(key)):
                          gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
                          cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
                          cpasswd="HIDDEN_STRING"
                          gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
                          move_chunks_status=None
                          shard_db,shard_pdb=self.process_chunks_vars(key)
                          shard_name = '''{0}_{1}'''.format(shard_db,shard_pdb)
                          online_shard = self.check_online_shard(shard_name)
                          if online_shard == 0 :
                             self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                             gsmcmd='''
                              connect {1}/{2};
                              config chunks -shard {0} 
                              config shard;
                              exit;
                             '''.format(shard_name,cadmin,cpasswd)
                             output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
                             ### Unsetting the encrypt value to None
                             self.ocommon.unset_mask_str()


      def check_chunks_regex(self):
          """
            This function return the rgex to search the chunks
          """
          self.ocommon.log_info_message("Inside check_chunks_regex()",self.file_name)
          return re.compile('CHECK_CHUNKS')

      def cancel_move_chunks(self):
                """
                This function cancel the shard Chunks
                """
                self.ocommon.log_info_message("Inside check_shard_chunks()",self.file_name)
                status=False
                reg_exp= self.cancel_chunks_regex()
                for key in self.ora_env_dict.keys():
                    if(reg_exp.match(key)):
                          gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
                          cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
                          cpasswd="HIDDEN_STRING"
                          gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
                          move_chunks_status=None
                          shard_db,shard_pdb=self.process_chunks_vars(key)
                          shard_name = '''{0}_{1}'''.format(shard_db,shard_pdb)
                          online_shard = self.check_online_shard(shard_name)
                          if online_shard == 1:
                             self.ocommon.log_info_message("Shard is not online. Performing chunk cancellation in GSM to set the shard chunk status.",self.file_name)
                             self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                             gsmcmd='''
                              connect {1}/{2};
                              ALTER MOVE -cancel -SHARD {0}
                              config shard;
                              exit;
                             '''.format(shard_name,cadmin,cpasswd)
                             output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
                             ### Unsetting the encrypt value to None
                             self.ocommon.unset_mask_str()
                          else: 
                             self.ocommon.log_info_message("Shard "  + shard_name  + "  is online. Unable to perform chunk cancellation.",self.file_name)

      def cancel_chunks_regex(self):
          """
            This function return the cancel chunk movement
          """
          self.ocommon.log_info_message("Inside cancel_chunks_regex()",self.file_name)
          return re.compile('CANCEL_CHUNKS')

      def verify_online_shard(self):
          """
           This function verify online shard
          """
          self.ocommon.log_info_message("Inside verify_online_shard()",self.file_name)
          status=False
          reg_exp= self.online_shard_regex()
          for key in self.ora_env_dict.keys():
              if(reg_exp.match(key)):
                  shard_db,shard_pdb=self.process_chunks_vars(key)
                  shard_name = '''{0}_{1}'''.format(shard_db,shard_pdb)
                  online_shard = self.check_online_shard(shard_name)
                  if online_shard == 0:
                     msg='''Shard {0} is online.'''.format(shard_name)
                     self.ocommon.log_info_message(msg,self.file_name)
                  else:
                     msg='''Shard {0} is not online.'''.format(shard_name)
                     self.ocommon.log_info_message(msg,self.file_name)
                     self.ocommon.prog_exit("157")


      def online_shard_regex(self):
          """
            This function return the rgex to search the ONLINE Shards
          """
          self.ocommon.log_info_message("Inside online_shard_regex()",self.file_name)
          return re.compile('CHECK_ONLINE_SHARD')

      def check_online_shard(self,shard_name):
               """
               This function check the online shard
               """
               self.ocommon.log_info_message("Inside check_online_shard()",self.file_name)
               name_flag = False
               availability_flag = False
               state_flag = False
               status_flag = False

               gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
               cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
               cpasswd="HIDDEN_STRING"
               gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
               self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
               gsmcmd='''
                 connect {1}/{2};
                 config shard -shard {0};
                 exit;
               '''.format(shard_name,cadmin,cpasswd)
               output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
               ### Unsetting the encrypt value to None
               self.ocommon.unset_mask_str()
               lines = output.split("\n")
               for line in lines:
                  list1 = line.split(":")
                  if list1[0].strip() == 'Name' and list1[1].strip().lower() == shard_name.lower():
                     name_flag = True
                  if list1[0].strip().lower() == 'Availability'.lower() and list1[1].strip().lower() == 'ONLINE'.lower():
                     availability_flag = True
                  if list1[0].strip().lower() == 'STATUS'.lower() and list1[1].strip().lower() == 'OK'.lower():
                     status_flag = True
                  if list1[0].strip().lower() == 'STATE'.lower() and list1[1].strip().lower() == 'DEPLOYED'.lower():
                     state_flag = True

                  del list1[:]

               if name_flag and availability_flag and state_flag and status_flag:
                  return 0
               else:
                  return 1

      def verify_gsm_shard(self):
          """
           This function verify GSM shard
          """
          self.ocommon.log_info_message("Inside verify_gsm_shard()",self.file_name)
          status=False
          reg_exp= self.check_shard_regex()
          for key in self.ora_env_dict.keys():
              if(reg_exp.match(key)):
                  shard_db,shard_pdb=self.process_chunks_vars(key)
                  shard_name = '''{0}_{1}'''.format(shard_db,shard_pdb)
                  gsm_shard = self.check_gsm_shard(shard_name)
                  if gsm_shard == 0:
                     msg='''Shard {0} is present in GSM.'''.format(shard_name)
                     self.ocommon.log_info_message(msg,self.file_name)
                  else:
                     msg='''Shard {0} is not present in GSM.'''.format(shard_name)
                     self.ocommon.log_info_message(msg,self.file_name)
                     self.ocommon.prog_exit("157")

      def check_shard_regex(self):
          """
            This function return the rgex to search the Shards in GSM
          """
          self.ocommon.log_info_message("Inside online_shard_regex()",self.file_name)
          return re.compile('CHECK_GSM_SHARD')

      def check_gsm_shard(self,shard_name):
               """
               This function check the shard in gsm
               """
               self.ocommon.log_info_message("Inside check_gsm_shard()",self.file_name)
               name_flag = False

               gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
               cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
               cpasswd="HIDDEN_STRING"
               gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
               self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
               gsmcmd='''
                 connect {1}/{2};
                 config shard -shard {0};
                 exit;
               '''.format(shard_name,cadmin,cpasswd)
               output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
               ### Unsetting the encrypt value to None
               self.ocommon.unset_mask_str()
               lines = output.split("\n")
               for line in lines:
                  list1 = line.split(":")
                  if list1[0].strip() == 'Name' and list1[1].strip().lower() == shard_name.lower():
                     name_flag = True

                  del list1[:]

               if name_flag:
                  return 0
               else:
                  return 1

      def count_online_shards(self):
          """
            This function return the returns the count of online shard
          """   
          self.ocommon.log_info_message("Inside count_online_shards()",self.file_name)
          gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
          cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
          cpasswd="HIDDEN_STRING"
          gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
          self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
          gsmcmd='''
            connect {0}/{1};
            config shard;
          exit;
          '''.format(cadmin,cpasswd)
          output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
          ### Unsetting the encrypt value to None
          self.ocommon.unset_mask_str()

          online_shard = 0
          lines = output.split("\n")
          for line in lines:
              if re.search('ok', line, re.IGNORECASE):
                 if re.search('deployed', line, re.IGNORECASE):
                    if re.search('online', line, re.IGNORECASE):
                       online_shard = online_shard + 1          

          return online_shard

      def get_online_shards(self):
          """
            This function return the returns the count of online shard
          """
          self.ocommon.log_info_message("Inside get_online_shards()",self.file_name)
          gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
          cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
          cpasswd="HIDDEN_STRING"
          gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
          self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
          gsmcmd='''
            connect {0}/{1};
            config shard;
          exit;
          '''.format(cadmin,cpasswd)
          output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
          ### Unsetting the encrypt value to None
          self.ocommon.unset_mask_str()

          shards=[]
          online_shard = 0
          for line in output.split("\n"):
             cols=line.split()
             print(cols)
             if len(cols) >= 5:
               if cols[5].lower() == "online" and cols[2].lower() == "ok":
                 shards.append(cols[0])

          return shards

      def get_rus(self,shardname_to_delete):
          """
            This function return the returns the count of online shard
          """
          self.ocommon.log_info_message("Inside get_online_shards()",self.file_name)
          gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
          cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
          cpasswd="HIDDEN_STRING"
          gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
          self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
          cmd=None
          if shardname_to_delete is not None:
              cmd='''status ru -leaders -shard {0}'''.format(shardname_to_delete)
          else:
              cmd='''status ru'''

          gsmcmd='''
            connect {0}/{1};
            {2}; 
          exit;
          '''.format(cadmin,cpasswd,cmd)
          output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
          ### Unsetting the encrypt value to None
          self.ocommon.unset_mask_str()

          return output.split('\n')

      def move_shard_rus(self,sshard,tshard,runum):
                """
                This function move the shard rus
                """
                self.ocommon.log_info_message("Inside move_shard_rus()",self.file_name)
                gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
                cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
                cpasswd="HIDDEN_STRING"
                gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
                self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                cmd1=""
                cmd2=""
                shardname=sshard
                if tshard is not None and runum is not None:
                   cmd1='''switchover ru -RU {0} -shard {1}'''.format(runum,tshard)
                else:
                   cmd1='''MOVE RU -RU ALL -SOURCE {0}'''.format(shardname)

                gsmcmd='''
                       connect {1}/{2};
                       configure -verbose off -save_config;
                       {3};
                       status RU -shard {0};
                       exit;
                '''.format(shardname,cadmin,cpasswd,cmd1,cmd2)
                output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
                ### Unsetting the encrypt value to None
                self.ocommon.unset_mask_str()

      def count_shard_rus(self,shardname):
          """
            This function return the returns the count of online shard chunks
          """   
          self.ocommon.log_info_message("Inside count_shard_chunks()",self.file_name)
          gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
          cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
          cpasswd="HIDDEN_STRING"
          gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
          self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
          gsmcmd='''
            connect {0}/{1};
            status ru -shard {2};
          exit;
          '''.format(cadmin,cpasswd,shardname)
          output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
          ### Unsetting the encrypt value to None
          self.ocommon.unset_mask_str()

          ru_count = 0
          lines = output.split("\n")
          for line in lines:
              if re.search(shardname, line, re.IGNORECASE):
                       ru_count = ru_count + 1          

          return ru_count

      def count_leader_shards(self,shardName):
          """
            This function return the returns the count of online shard
          """   
          self.ocommon.log_info_message("Inside count_leader_shards()",self.file_name)
          gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
          cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
          cpasswd="HIDDEN_STRING"
          gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
          self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
          gsmcmd='''
            connect {0}/{1};
            status ru -shard {2} -leaders;
          exit;
          '''.format(cadmin,cpasswd,shardName)
          output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
          ### Unsetting the encrypt value to None
          self.ocommon.unset_mask_str()

          leader_shard = 0
          lines = output.split("\n")
          for line in lines:
              if re.search('ok', line, re.IGNORECASE):
                 if re.search('Leader', line, re.IGNORECASE):
                       leader_shard = leader_shard + 1          

          return leader_shard

      def validate_gsm_shard(self):
                """
                This function validate the shard in the GSM
                """
                self.ocommon.log_info_message("Inside validate_gsm_shard()",self.file_name)
                status=False
                reg_exp= self.validate_shard_regex()
                for key in self.ora_env_dict.keys():
                    if(reg_exp.match(key)):
                          shard_db,shard_pdb,shard_port,shard_group,shard_host,shard_region,shard_space=self.process_shard_vars(key)
                          shard_name='''{0}_{1}'''.format(shard_db,shard_pdb)
                          status = self.check_shard_status(shard_name)
                          if status == 'completed':
                             msg='''Shard DB setup completed in GSM'''
                             self.ocommon.log_info_message(msg,self.file_name)
                          else:
                             msg='''Shard {0} info does not exist in GSM.'''.format(shard_name)
                             self.ocommon.log_info_message(msg,self.file_name)
                             self.ocommon.prog_exit("157")

      def process_shard_vars(self,key):
          """
          This function process sgard vars based on key and return values to configure the GSM
          """
          shard_db=None
          shard_pdb=None
          shard_port=None
          shard_group=None
          shard_host=None
          shard_region=None
          shard_space=None
          shard_deploy_as=None

          self.ocommon.log_info_message("Inside process_shard_vars()",self.file_name)
        #  self.ocommon.log_info_message(key,self.file_name)
          cvar_str=self.ora_env_dict[key]
          cvar_str=cvar_str.replace('"', '') 
        #  self.ocommon.log_info_message(cvar_str,self.file_name)
          cvar_dict=dict(item.split("=") for item in cvar_str.split(";"))
          for ckey in cvar_dict.keys():
             # self.ocommon.log_info_message("key : " + ckey,self.file_name)
             # self.ocommon.log_info_message("Value: " + cvar_dict[ckey],self.file_name)
              if ckey == 'shard_db':
                 shard_db = cvar_dict[ckey]
              if ckey == 'shard_pdb':
                 shard_pdb = cvar_dict[ckey]
              if ckey == 'shard_port':
                 shard_port = cvar_dict[ckey]
              if ckey == 'shard_group':
                 shard_group = cvar_dict[ckey]
              if ckey == 'shard_host':
                 shard_host = cvar_dict[ckey]
              if ckey == 'shard_region':
                #shard_region = self.validate_shard_param("region",cvar_dict[ckey])
                shard_region=cvar_dict[ckey]
              if ckey == 'deploy_as':
                 shard_deploy_as=cvar_dict[ckey] 
              if ckey == 'shard_space':
                 #shard_space = self.validate_shard_param("shardspace",cvar_dict[ckey])
                  shard_space=cvar_dict[ckey]
              # #  self.ocommon.log_info_message("shard_host: " + shard_host, self.file_name)
              ## Set the values if not set in above block
          if not shard_port:
             shard_port=1521

          if self.ocommon.check_key("SHARDING_TYPE",self.ora_env_dict):
             if self.ora_env_dict["SHARDING_TYPE"].upper() == 'USER':
                shard_group="nogrp"
                if not shard_deploy_as:
                   self.ora_env_dict=self.ocommon.add_key("SHARD_DEPLOY_AS","primary",self.ora_env_dict) 
                else:
                   self.ora_env_dict=self.ocommon.add_key("SHARD_DEPLOY_AS",shard_deploy_as,self.ora_env_dict)

              ### Check values must be set
          if shard_host and shard_db and shard_pdb and shard_port and shard_group:
              return shard_db,shard_pdb,shard_port,shard_group,shard_host,shard_region,shard_space
          else:
              msg1='''shard_db={0},shard_pdb={1}'''.format((shard_db or "Missing Value"),(shard_pdb or "Missing Value"))
              msg2='''shard_port={0},shard_host={1}'''.format((shard_port or "Missing Value"),(shard_host or "Missing Value"))
              msg3='''shard_group={0}'''.format((shard_group or "Missing Value"))
              msg='''Shard DB  params {0} is not set correctly. One or more value is missing {1} {2} {3}'''.format(key,msg1,msg2,msg3)
              self.ocommon.log_info_message(msg,self.file_name)
              self.ocommon.prog_exit("Error occurred")

      def validate_shard_param(self,param_type,value):
         """
         This function validaet the shard param such as region and shardspace
         """
         status=False
         reg_exp= self.catalog_regex()
         stype=None
         sspace=None
         catalog_region=None
         self.ocommon.log_info_message("Processing GSM params to verify the region and shardspace",self.file_name)
         for key in self.ora_env_dict.keys():
             if(reg_exp.match(key)):
                 catalog_db,catalog_pdb,catalog_port,catalog_region,catalog_host,catalog_name,catalog_chunks,repl_type,repl_factor,repl_unit,stype,sspace,cfname=self.process_clog_vars(key)

         if param_type == 'region':
            if stype:
               status=self.ocommon.find_str_in_string(catalog_region,'comma',value)
               if status:
                  
                  return value
               else:
                  return ""
         
         if param_type == 'shardspace':
            if sspace:
               status=self.ocommon.find_str_in_string(sspace,'comma',value)
               if status:
                  return value
               else:
                  return ""
            
         return False
         
      def process_chunks_vars(self,key):
          """
           This function process the chunks vars
          """
          shard_db=None
          shard_pdb=None
          self.ocommon.log_info_message("Inside process_chunks_vars()",self.file_name)
        #  self.ocommon.log_info_message(key,self.file_name)
          cvar_str=self.ora_env_dict[key]
          cvar_str=cvar_str.replace('"', '')
        #  self.ocommon.log_info_message(cvar_str,self.file_name)
          cvar_dict=dict(item.split("=") for item in cvar_str.split(";"))
          for ckey in cvar_dict.keys():
             # self.ocommon.log_info_message("key : " + ckey,self.file_name)
             # self.ocommon.log_info_message("Value: " + cvar_dict[ckey],self.file_name)
              if ckey == 'shard_db':
                 shard_db = cvar_dict[ckey]
              if ckey == 'shard_pdb':
                 shard_pdb = cvar_dict[ckey]
              # #  self.ocommon.log_info_message("shard_host: " + shard_host, self.file_name)
              ## Set the values if not set in above block

              ### Check values must be set
          if shard_pdb and shard_db:
              return shard_db,shard_pdb
          else:
              msg1='''shard_db={0},shard_pdb={1}'''.format((shard_db or "Missing Value"),(shard_pdb or "Missing Value"))
              self.ocommon.log_info_message(msg1,self.file_name)
              self.ocommon.prog_exit("Error occurred")

      def check_shard_status(self,shard_name):
          """
           This function check the shard status in GSM
          """
          self.ocommon.log_info_message("Inside check_shard_status()",self.file_name)
          #gsmcmd=self.get_gsm_config_cmd(dname)
          gsmcmd='''
            config;
            exit;
          '''
          counter=1
          end_counter=3
          status=False
          while counter < end_counter:
             output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
             error_check=re.findall("(?:GSM-45034\n)(?:.+\n)+",output)
             try: 
                if self.ocommon.check_substr_match(error_check[0],"GSM-45034"):
                   count = counter + 1
                   self.ocommon.log_info_message("Issue in catalog connection, retrying to connect to catalog in 30 seconds!",self.file_name)
                   time.sleep(20)
                   status=False
                   continue 
             except:
                status=False
             matched_output=re.findall("(?:Databases\n)(?:.+\n)+",output)
             if shard_name:
                try:
                  if self.ocommon.check_substr_match(matched_output[0],shard_name.lower()):
                     status=True
                     break
                  else:
                     status=False
                except:
                  status=False
             else:
                reg_exp= self.shard_regex()
                for key in self.ora_env_dict.keys():
                    if(reg_exp.match(key)):
                      shard_db,shard_pdb,shard_port,shard_region,shard_host,shard_region,shard_space=self.process_shard_vars(key)
                      shard_name='''{0}_{1}'''.format(shard_db,shard_pdb)
                      try:
                        if self.ocommon.check_substr_match(matched_output[0],shard_name.lower()):
                           status=True
                        else:
                          status=False
                      except:
                        status=False
                if status:
                   break;
             counter = counter + 1

          return(self.ocommon.check_status_value(status))

      def shard_regex(self):
          """
            This function return the rgex to search the SHARD PARAMS
          """ 
          self.ocommon.log_info_message("Inside shard_regex()",self.file_name)
          return re.compile('SHARD[0-9]+_PARAMS') 

      def add_shard_regex(self):
          """
            This function return the rgex to search the ADD_SHARD_PARAMS
          """
          self.ocommon.log_info_message("Inside add_shard_regex()",self.file_name)
          return re.compile('ADD_SHARD')

      def remove_shard_regex(self):
          """
            This function return the rgex to search the REMOVE_SHARD_PARAMS
          """
          self.ocommon.log_info_message("Inside remove_shard_regex()",self.file_name)
          return re.compile('REMOVE_SHARD')

      def validate_shard_regex(self):
          """
            This function return the rgex to search the VALIDATE_SHARD_PARAMS
          """
          self.ocommon.log_info_message("Inside remove_shard_regex()",self.file_name)
          return re.compile('VALIDATE_SHARD')

      def configure_gsm_shard(self,shost,scdb,spdb,sdbport,sgroup,sregion,sspace):
         """
         This function configure the shard db.
         """
         spasswd="HIDDEN_STRING"
         admuser= self.ora_env_dict["SHARD_ADMIN_USER"]
         #dtrname,dtrport,dtregion=self.process_director_vars()
         #group_region=self.get_shardg_region_name(sgroup)
         #dtrname=self.get_director_name(group_region)
         shard_name='''{0}_{1}'''.format(scdb,spdb)
         shard_region=None
         shard_space=None
         shard_group=None
         deploy_as=None

         if sregion:
            regionFlag=self.check_gsm_region(sregion)
            if regionFlag != 'completed':
               self.configure_gsm_region(sregion)
            shard_region=" -region {0}".format(sregion)
         else:
            shard_region=""
         if sspace:
            shard_space=" -shardspace {0}".format(sspace)
         else:
            shard_space=""

         if self.ocommon.check_key("SHARDING_TYPE",self.ora_env_dict):
            if self.ora_env_dict["SHARDING_TYPE"].upper() == 'USER':
               sspaceFlag=self.check_gsm_shardspace(sspace)
               if sspaceFlag != 'completed':
                  self.configure_gsm_sspace(sspace,None,None,None,None,'add')
               shard_group=""
               deploy_as,deploy_type=self.get_shard_deploy()
            else:
               shard_group,deploy_as=self.get_shardg_cmd(sgroup,sregion)
               shard_region=""
         else:
            shard_group,deploy_as=self.get_shardg_cmd(sgroup,sregion)
            shard_region=""
               
         self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
         gsmcmd='''
         connect {1}/{2};
         add cdb -connect {3}:{4}/{5} -pwd {2};
         add shard -cdb {5} -connect "(DESCRIPTION = (ADDRESS = (PROTOCOL = tcp)(HOST = {3})(PORT = {4})) (CONNECT_DATA = (SERVICE_NAME = {6}) (SERVER = DEDICATED)))" {7} -pwd {2} {9} {10} {11};
         config vncr;
         exit;
         '''.format("NA",admuser,spasswd,shost,sdbport,scdb,spdb,shard_group,shard_name,shard_region,shard_space,deploy_as)
         output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
         ### Unsetting the encrypt value to None
         self.ocommon.unset_mask_str()

      def get_shard_deploy(self):
         """
         get the shard deploy
         """
         deploy_as=None
         deploy_type=None
         if self.ocommon.check_key("SHARD_DEPLOY_AS",self.ora_env_dict):
            deploy_as="-deploy_as {0}".format(self.ora_env_dict["SHARD_DEPLOY_AS"])
            deploy_type=self.ora_env_dict["SHARD_DEPLOY_AS"]
         else:
            deploy_as="-deploy_as primary"
            deploy_type='primary'
            
         return deploy_as,deploy_type
      
      def get_shardg_cmd(self,sgroup,sregion):
         """
         Getting shard group cmd
         """
         sgFlag=self.check_shardg_status(sgroup,None)
         deploy_as,deploy_type=self.get_shard_deploy()
         if sgFlag != 'completed':
            self.configure_gsm_shardg(sgroup,deploy_type,sregion,'add')
         else:
            self.ocommon.log_info_message("Shardgroup exist " + sgroup, self.file_name)
         
         deploy_as=""
         cmd=''' -shardgroup {0}'''.format(sgroup)
         return cmd,deploy_as
         
      def delete_gsm_shard(self,shost,scdb,spdb,sdbport,sgroup):
         """
         This function delete the shard db.
         """
         spasswd="HIDDEN_STRING"
         admuser= self.ora_env_dict["SHARD_ADMIN_USER"]
         #dtrname,dtrport,dtregion=self.process_director_vars()
         self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
         shard_name='''{0}_{1}'''.format(scdb,spdb)
         #group_region=self.get_shardg_region_name(sgroup)
         #dtrname=self.get_director_name(group_region)
         gsmcmd='''
         connect {1}/{2};
         remove shard -shard {8};
         remove cdb -cdb {5};
         remove invitednode {3};
         config vncr;
         exit;
         '''.format("NA",admuser,spasswd,shost,sdbport,scdb,spdb,sgroup,shard_name)

         output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
         ### Unsetting the encrypt value to None
         self.ocommon.unset_mask_str()

      def set_hostid_null(self):
          """
           This function set the hostid to Null
          """
          spasswd="HIDDEN_STRING"
          admuser= self.ora_env_dict["SHARD_ADMIN_USER"]
          reg_exp= self.catalog_regex()
          for key in self.ora_env_dict.keys():
              if(reg_exp.match(key)):
                 catalog_db,catalog_pdb,catalog_port,catalog_region,catalog_host,catalog_name,catalog_chunks,repl_type,repl_factor,repl_unit,stype,sspace,cfname=self.process_clog_vars(key)
                 sqlpluslogin='''{0}/bin/sqlplus "sys/HIDDEN_STRING@{1}:{2}/{3} as sysdba"'''.format(self.ora_env_dict["ORACLE_HOME"],catalog_host,catalog_port,catalog_pdb,admuser)
                 self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                 msg='''Setting host Id null in catalog as auto vncr is disabled'''
                 self.ocommon.log_info_message(msg,self.file_name)
                 sqlcmd='''
                  set echo on
                  set termout on
                  set time on
                  update gsmadmin_internal.database set hostid=NULL;
                 '''
                 output,error,retcode=self.ocommon.run_sqlplus(sqlpluslogin,sqlcmd,None)
                 self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
                 self.ocommon.check_sql_err(output,error,retcode,None)
                 self.ocommon.unset_mask_str()

      def invited_node_op(self):
         """
         This function perform the invitedaddition and deletion
         """
         self.ocommon.log_info_message("Inside invited_node_op()",self.file_name)
         gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
         cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
         cpasswd="HIDDEN_STRING"
         #dtrname,dtrport,dtregion=self.process_director_vars()
         self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
         shard_host=self.ora_env_dict["INVITED_NODE_OP"]
         shardName=shard_host.split('.',1)[1].replace("\"","")
         shardName = shardName + "_" + shardName + "pdb"
         
         self.ocommon.log_info_message("Waiting for shard["+shardName+"] to be online",self.file_name)
         gsmcmd='''
            connect {1}/{2};
            remove invitednode {3}; 
            exit;
         '''.format("NA",cadmin,cpasswd,shard_host)
         output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)

         time.sleep(240)

         gsmcmd='''
            connect {1}/{2};
            add invitednode {3};
            exit;
         '''.format("NA",cadmin,cpasswd,shard_host)
         output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)

      def add_invited_node(self,op_str):
         """
         This function add the invited in the GSM configuration
         """
         self.ocommon.log_info_message("Inside add_invited_node()",self.file_name)
         if op_str == "SHARD":
            reg_exp = self.shard_regex()
         else:
            reg_exp = self.add_shard_regex()

         gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
         cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
         cpasswd="HIDDEN_STRING"
         #dtrname,dtrport,dtregion=self.process_director_vars()
         self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
         for key in self.ora_env_dict.keys():
            if(reg_exp.match(key)):
               shard_db,shard_pdb,shard_port,shard_group,shard_host,shard_region,shard_space=self.process_shard_vars(key)
               #group_region=self.get_shardg_region_name(shard_group)
               #dtrname=self.get_director_name(group_region)
               gsmcmd='''
                  connect {1}/{2};
                  add invitednode {3};
                  exit;
               '''.format("NA",cadmin,cpasswd,shard_host)
               output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)

      def remove_invited_node(self,op_str):
         """
         This function remove the invited in the GSM configuration
         """
         self.ocommon.log_info_message("Inside remove_invited_node()",self.file_name)
         if op_str == "SHARD":
            reg_exp = self.shard_regex()
         else:
            reg_exp = self.add_shard_regex()

         gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
         cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
         cpasswd="HIDDEN_STRING"
         #dtrname,dtrport,dtregion=self.process_director_vars()
         self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])

         if self.ocommon.check_key("KUBE_SVC",self.ora_env_dict):
            for key in self.ora_env_dict.keys():
               if(reg_exp.match(key)):
                  shard_db,shard_pdb,shard_port,shard_group,shard_host,shard_region,shard_space=self.process_shard_vars(key)
                  temp_host= shard_host.split('.',1)[0] 
                  #group_region=self.get_shardg_region_name(shard_group)
                  #dtrname=self.get_director_name(group_region)
                  gsmcmd='''
                     connect {1}/{2};
                     remove invitednode {3};
                     exit;
                  '''.format("NA",cadmin,cpasswd,temp_host)
                  output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
         else:
            self.ocommon.log_info_message("KUBE_SVC is not set. No need to remove invited node!",self.file_name)  


      def deploy_shard(self):
         """
         This function deploy shard
         """
         self.ocommon.log_info_message("Inside deploy_shard()",self.file_name)
         gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
         cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
         cpasswd="HIDDEN_STRING"
         gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
         shrdg_sspace=None
         #dtrname,dtrport,dtregion=self.process_director_vars()
         #if op_str == "SHARD":
         #   reg_exp = self.shard_regex()
         #else:
         #   reg_exp = self.add_shard_regex()

         #for key in self.ora_env_dict.keys():
         #   if(reg_exp.match(key)):
         if self.ocommon.check_key("SHARDING_TYPE",self.ora_env_dict):
            if self.ora_env_dict["SHARDING_TYPE"].upper() == 'USER':
               shardg_shardspace="config shardspace"
         else:
            shardg_shardspace="config shardgroup"
            
         self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
         gsmcmd='''
            connect {1}/{2};
            {3};
            config vncr;
            deploy;
            config shard; 
            exit;
         '''.format("test",cadmin,cpasswd,shardg_shardspace)
         output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
         ### Unsetting the encrypt value to None
         self.ocommon.unset_mask_str()

      def check_setup_status(self,host,ccdb,svc,port):
         """
            This function check the shard status.
         """
         systemStr='''{0}/bin/sqlplus "system/HIDDEN_STRING@{1}:{2}/{3}"'''.format(self.ora_env_dict["ORACLE_HOME"],host,port,ccdb)
         
         fname='''/tmp/{0}'''.format("shard_setup.txt") 
         self.ocommon.remove_file(fname)
         self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
         msg='''Checking shardsetup table in CDB'''
         self.ocommon.log_info_message(msg,self.file_name)
         sqlcmd='''
         set heading off
         set feedback off
         set  term off
         SET NEWPAGE NONE
         spool {0}
         select * from shardsetup WHERE ROWNUM = 1;
         spool off
         exit;
         '''.format(fname)
         output,error,retcode=self.ocommon.run_sqlplus(systemStr,sqlcmd,None)
         self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
         self.ocommon.check_sql_err(output,error,retcode,None)

         if os.path.isfile(fname): 
            fdata=self.ocommon.read_file(fname)
         else:
            fdata='nosetup'

         ### Unsetting the encrypt value to None
         self.ocommon.unset_mask_str()

         if re.search('completed',fdata):
            status = self.catalog_pdb_setup_check(host,ccdb,svc,port)
            if status == 'completed':
               return 'completed'
            else:
               return 'notcompleted'
         else:
            return 'notcompleted'


      def catalog_pdb_setup_check(self,host,ccdb,svc,port):
         """
            This function check the shard status.
         """
         systemStr='''{0}/bin/sqlplus "pdbadmin/HIDDEN_STRING@{1}:{2}/{3}"'''.format(self.ora_env_dict["ORACLE_HOME"],host,port,svc)

         fname='''/tmp/{0}'''.format("pdb_setup_check.txt")
         self.ocommon.remove_file(fname)
         self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
         msg='''Checking setup status in PDB'''
         self.ocommon.log_info_message(msg,self.file_name)
         sqlcmd='''
         set heading off
         set feedback off
         set  term off
         SET NEWPAGE NONE
         spool {0}
         select count(*) from dual;
         spool off
         exit;
         '''.format(fname)
         output,error,retcode=self.ocommon.run_sqlplus(systemStr,sqlcmd,None)
         self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
         self.ocommon.check_sql_err(output,error,retcode,None)

         if os.path.isfile(fname):
            fdata=self.ocommon.read_file(fname)
         else:
            fdata='nosetup'

         ### Unsetting the encrypt value to None
         self.ocommon.unset_mask_str()

         if re.search('1',fdata):
            return 'completed'
         else:
            return 'notcompleted'

      ############################# Setup GSM Service ###############################################
      def setup_gsm_service(self):
         """
         This function setup the shard service.
         """
         self.ocommon.log_info_message("Inside setup_gsm_service()",self.file_name)
         status=False
         service_value="service_name=oltp_rw_svc;service_role=primary"
   #     self.ora_env_dict=self.ocommon.add_key("SERVICE1_PARAMS",service_value,self.ora_env_dict)
         reg_exp= self.service_regex()
         counter=1
         end_counter=3
         while counter < end_counter:
               for key in self.ora_env_dict.keys():
                  if(reg_exp.match(key)):
                     shard_service_status=None
                     service_name,service_role=self.process_service_vars(key)
                     shard_service_status=self.check_service_status(service_name)
                     if shard_service_status != 'completed':
                        self.configure_gsm_service(service_name,service_role)
               status = self.check_service_status(None)
               if status == 'completed':
                  break
               else:
                  msg='''GSM service setup is still not completed in GSM. Sleeping for 60 seconds and sleeping count is {0}'''.format(counter)
               time.sleep(60)
               counter=counter+1

         status = self.check_service_status(None)
         if status == 'completed':
            msg='''Shard service setup completed in GSM'''
            self.ocommon.log_info_message(msg,self.file_name)
         else:
            msg='''Waited 2 minute to complete catalog setup in GSM but setup did not complete or failed. Exiting...'''
            self.ocommon.log_error_message(msg,self.file_name)
            self.ocommon.prog_exit("127")

      def process_service_vars(self,key):
          """
          This function process shardG vars based on key and return values to configure the GSM
          """
          service_name=None
          service_role=None

          self.ocommon.log_info_message("Inside process_service_vars()",self.file_name)
          cvar_str=self.ora_env_dict[key]
          cvar_dict=dict(item.split("=") for item in cvar_str.split(";"))
          for ckey in cvar_dict.keys():
              if ckey == 'service_name':
                 service_name = cvar_dict[ckey]
              if ckey == 'service_role':
                 service_role = cvar_dict[ckey]

              ### Check values must be set
          if service_name and service_role:
             return service_name,service_role
          else:
             msg1='''service_name={0},service_role={1}'''.format((service_name or "Missing Value"),(service_role or "Missing Value"))
             msg='''Shard service params {0} is not set correctly. One or more value is missing {1} {2}'''.format(key,msg1)
             self.ocommon.log_error_message(msg,self.file_name)
             self.ocommon.prog_exit("Error occurred")

      def check_service_status(self,service_name):
          """
           This function check the shard status in GSM
          """
          self.ocommon.log_info_message("Inside check_service_status()",self.file_name)
          #dtrname,dtrport,dtregion=self.process_director_vars()
          gsmcmd='''
            config;
            exit;
          '''.format("test")
          output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
          matched_output=re.findall("(?:Services\n)(?:.+\n)+",output)
          status=False
          if service_name:
            try:
              if self.ocommon.check_substr_match(matched_output[0],service_name):
                 status=True
              else:
                 status=False
            except:
              status=False
          else:
            reg_exp= self.service_regex()
            for key in self.ora_env_dict.keys():
               if(reg_exp.match(key)):
                  service_name,service_role=self.process_service_vars(key)
               #  match=re.search("(?i)(?m)"+service_name,matched_output)
                  try:
                    if self.ocommon.check_substr_match(matched_output[0],service_name):
                      status=True
                    else:
                      status=False
                  except:
                      status=False
          
          return(self.ocommon.check_status_value(status))

      def service_regex(self):
          """
            This function return the rgex to search the SERVICE[0-9]_PARAMS
          """
          self.ocommon.log_info_message("Inside service_regex()",self.file_name)
          return re.compile('SERVICE[0-9]+_PARAMS')
		  
      def configure_gsm_service(self,service_name,service_role):
         """
         This function configure the service creation.
         """
         self.ocommon.log_info_message("Inside configure_gsm_service()",self.file_name)
         gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
         cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
         cpasswd="HIDDEN_STRING"

         #dtrname,dtrport,dtregion=self.process_director_vars()
         self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
         gsmlogin='''{0}/bin/gdsctl'''.format(self.ora_env_dict["ORACLE_HOME"])
         gsmcmd='''
            connect {1}/{2};
            add service -service {3} -role {4};
            start service -service {3};
         exit;
         '''.format("test",cadmin,cpasswd,service_name,service_role)
         output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)

         ### Unsetting the encrypt value to None
         self.ocommon.unset_mask_str()

      ############################## GSM backup fIle function Begins Here #############################
      def gsm_backup_file(self):
          """
            This function check the gsm setup status
          """
          self.ocommon.log_info_message("Inside gsm_backup_file()",self.file_name)
          gsmdata_loc='/opt/oracle/gsmdata'
          gsmfile_loc='''{0}/network/admin'''.format(self.ora_env_dict["ORACLE_HOME"])

          if os.path.isdir(gsmdata_loc):
             msg='''Directory {0} exit'''.format(gsmdata_loc)
             self.ocommon.log_info_message(msg,self.file_name)

          cmd='''cp -r -v {0}/* {1}/'''.format(gsmfile_loc,gsmdata_loc)
          output,error,retcode=self.ocommon.execute_cmd(cmd,None,None)
          self.ocommon.check_os_err(output,error,retcode,True)

      ############### Deploy Sample Function Begins Here ##########################
      def setup_sample_schema(self):
          """
            This function deploy the sample app
          """
          s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
          passlen = 8
          passwd  =  "".join(random.sample(s,passlen )) 
          self.ocommon.log_info_message("Inside deploy_sample_schema()",self.file_name)
          reg_exp= self.catalog_regex()
          for key in self.ora_env_dict.keys():
              if(reg_exp.match(key)):
                 catalog_db,catalog_pdb,catalog_port,catalog_region,catalog_host,catalog_name,catalog_chunks,repl_type,repl_factor,repl_unit,stype,sspace,cfname=self.process_clog_vars(key)
          sqlpluslogin='''{0}/bin/sqlplus "sys/HIDDEN_STRING@{1}:{2}/{3} as sysdba"'''.format(self.ora_env_dict["ORACLE_HOME"],catalog_host,catalog_port,catalog_db)
          if self.ocommon.check_key("SAMPLE_SCHEMA",self.ora_env_dict):
             if self.ora_env_dict["SAMPLE_SCHEMA"] == 'DEPLOY':
                self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                msg='''Deploying sample schema'''
                self.ocommon.log_info_message(msg,self.file_name)
                sqlcmd='''
                 set echo on
                 set termout on
                 set time on
                 spool /tmp/create_app_schema.lst
                 REM
                 REM Connect to the Shard Catalog and Create Schema
                 REM
                 alter session enable shard ddl;
                 alter session set container={2};
                 alter session enable shard ddl;
                 create user app_schema identified by {3};
                 grant connect, resource, alter session to app_schema;
                 grant execute on dbms_crypto to app_schema;
                 grant create table, create procedure, create tablespace, create materialized view to app_schema;
                 grant unlimited tablespace to app_schema;
                 grant select_catalog_role to app_schema;
                 grant all privileges to app_schema; 
                 grant gsmadmin_role to app_schema;
                 grant dba to app_schema;
                 CREATE TABLESPACE SET tbsset1 IN SHARDSPACE shd1;
                 CREATE TABLESPACE SET tbsset2 IN SHARDSPACE shd2;
                 connect app_schema/{3}@{0}:{1}/{2}
                 alter session enable shard ddl;

                 /* Customer shard table */

                 CREATE SHARDED TABLE customer
                 ( cust_id NUMBER NOT NULL,
                  cust_passwd VARCHAR2(20) NOT NULL,
                  cust_name VARCHAR2(60) NOT NULL,
                  cust_type VARCHAR2(10) NOT NULL,
                  cust_email VARCHAR2(100) NOT NULL)
                  partitionset by list (cust_type)
                  partition by consistent hash (cust_id) partitions auto
                  (partitionset individual values ('individual') tablespace set tbsset1,
                  partitionset  business values ('business') tablespace set tbsset2
                  );
                 /* Invoice shard table */

                 CREATE SHARDED TABLE invoice 
                 ( invoice_id  NUMBER NOT NULL,
                 cust_id  NUMBER NOT NULL,
                 cust_type VARCHAR2(10) NOT NULL,
                 vendor_name VARCHAR2(60) NOT NULL,
                 balance FLOAT(10) NOT NULL,
                 total FLOAT(10) NOT NULL,    
                 status VARCHAR2(20),  
                 CONSTRAINT InvoicePK PRIMARY KEY (cust_id, invoice_id))
                 PARENT customer
                 partitionset by list (cust_type)
                 partition by consistent hash (cust_id) partitions auto
                 (partitionset individual values ('individual') tablespace set tbsset1,
                 partitionset  business values ('business') tablespace set tbsset2
                 );
                 /* Data */
                 insert into customer values (999, 'pass', 'Customer 999', 'individual', 'customer999@gmail.com');
                 insert into customer values (250251, 'pass', 'Customer 250251', 'individual', 'customer250251@yahoo.com');
                 insert into customer values (350351, 'pass', 'Customer 350351', 'individual', 'customer350351@gmail.com');
                 insert into customer values (550551, 'pass', 'Customer 550551', 'business', 'customer550551@hotmail.com');
                 insert into customer values (650651, 'pass', 'Customer 650651', 'business', 'customer650651@live.com');
                 insert into invoice values (1001, 999, 'individual', 'VendorA', 10000, 20000, 'Due');
                 insert into invoice values (1002, 999, 'individual', 'VendorB', 10000, 20000, 'Due');
                 insert into invoice values (1001, 250251, 'individual', 'VendorA', 10000, 20000, 'Due');
                 insert into invoice values (1002, 250251, 'individual', 'VendorB', 0, 10000, 'Paid');
                 insert into invoice values (1003, 250251, 'individual', 'VendorC', 14000, 15000, 'Due');
                 insert into invoice values (1001, 350351, 'individual', 'VendorD', 10000, 20000, 'Due');
                 insert into invoice values (1002, 350351, 'individual', 'VendorE', 0, 10000, 'Paid');
                 insert into invoice values (1003, 350351, 'individual', 'VendorF', 14000, 15000, 'Due');
                 insert into invoice values (1004, 350351, 'individual', 'VendorG', 12000, 15000, 'Due');
                 insert into invoice values (1001, 550551, 'business', 'VendorH', 10000, 20000, 'Due');
                 insert into invoice values (1002, 550551, 'business', 'VendorI', 0, 10000, 'Paid');
                 insert into invoice values (1003, 550551, 'business', 'VendorJ', 14000, 15000, 'Due');
                 insert into invoice values (1004, 550551, 'business', 'VendorK', 10000, 20000, 'Due');
                 insert into invoice values (1005, 550551, 'business', 'VendorL', 10000, 20000, 'Due');
                 insert into invoice values (1006, 550551, 'business', 'VendorM', 0, 10000, 'Paid');
                 insert into invoice values (1007, 550551, 'business', 'VendorN', 14000, 15000, 'Due');
                 insert into invoice values (1008, 550551, 'business', 'VendorO', 10000, 20000, 'Due');
                 insert into invoice values (1001, 650651, 'business', 'VendorT', 10000, 20000, 'Due');
                 insert into invoice values (1002, 650651, 'business', 'VendorU', 0, 10000, 'Paid');
                 insert into invoice values (1003, 650651, 'business', 'VendorV', 14000, 15000, 'Due');
                 insert into invoice values (1004, 650651, 'business', 'VendorW', 10000, 20000, 'Due');
                 insert into invoice values (1005, 650651, 'business', 'VendorX', 0, 20000, 'Paid');
                 insert into invoice values (1006, 650651, 'business', 'VendorY', 0, 30000, 'Paid');
                 insert into invoice values (1007, 650651, 'business', 'VendorZ', 0, 10000, 'Paid');
                 commit;
                 select table_name from user_tables;
                 spool off
                '''.format(catalog_host,catalog_port,catalog_pdb,passwd)
                output,error,retcode=self.ocommon.run_sqlplus(sqlpluslogin,sqlcmd,None)
                self.ocommon.log_info_message("Calling check_sql_err() to validate the sql command return status",self.file_name)
                self.ocommon.check_sql_err(output,error,retcode,None)
          ### Unsetting the encrypt value to None
                self.ocommon.unset_mask_str()

                gsmhost=self.ora_env_dict["ORACLE_HOSTNAME"]
                cadmin=self.ora_env_dict["SHARD_ADMIN_USER"]
                cpasswd="HIDDEN_STRING"
                #dtrname,dtrport,dtregion=self.process_director_vars()
                self.ocommon.set_mask_str(self.ora_env_dict["ORACLE_PWD"])
                gsmcmd='''
                  connect {1}/{2};
                  show ddl;
                  exit;
                '''.format("test",cadmin,cpasswd)
                output,error,retcode=self.ocommon.exec_gsm_cmd(gsmcmd,None,self.ora_env_dict)
          ### Unsetting the encrypt value to None
                self.ocommon.unset_mask_str()

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
          msg.append('     GSM Setup Completed                      ')
          msg.append('==============================================')

          for text in msg:
              self.ocommon.log_info_message(text,self.file_name)



      ############################### GET GSM Trace Level ###############################################
      def get_gsm_trace_level(self):
          """
           Funtion to get the GSM Trace Level
          """
          self.ocommon.log_info_message("Inside get_gsm_trace_level()",self.file_name)
          if self.ocommon.check_key("GSM_TRACE_LEVEL",self.ora_env_dict):
             gsm_trace_level = self.ora_env_dict["GSM_TRACE_LEVEL"]
             if gsm_trace_level in {'USER','ADMIN','SUPPORT','OFF'}:
                msg='''GSM Trace Level is Passed and is set to {0}'''.format(gsm_trace_level)
                self.ocommon.log_info_message(msg,self.file_name)
             else:
                self.ocommon.log_info_message("INVALID value passed for parameter GSM_TRACE_LEVEL.",self.file_name)
                self.ocommon.prog_exit("127")
          else:
             self.ocommon.log_info_message("No value passed for parameter GSM_TRACE_LEVEL. It will be set to OFF.",self.file_name)
             gsm_trace_level='OFF'
          return gsm_trace_level
