""" File name: wdinfo.py
Interface to web app
"""
import os
from datetime import datetime, timedelta
from logzero import logger
import traceback
from mysqlite import MySqlite
from fileinfo import FileInfo
from filesqlite import FileInfoSqlite
from confops import ConfigOps

class WdInfo(object):
    ''' This App basic config '''
    def __init__(self,
                 db = '/home/family/wdinfo.sqlite/wddata.db',
                 config_file = '/home/family/wdinfo.sqlite/wdinfo.workdirlist',
                 ):
        self.db = db
        self.sqlite = None
        self.tbl_str_list = ['NAME', 'PATH', 'FILESIZE', 'CHANGETIME', 'REL_NAME']
        table_structure=' TEXT, '.join(self.tbl_str_list)
        table_structure = f"{table_structure} TEXT"
        self.table_structure = f"{table_structure}, updateddatetime TIMESTAMP DEFAULT (datetime('now','localtime'))"
        self.table_header=', '.join(self.tbl_str_list[:-1])
        self.prefix = None
        self.co = ConfigOps(config_file = config_file)
        self.fis = FileInfoSqlite(db = self.db)

    def sqlite_db_exist(self):
        if os.path.isfile(self.db):
            return True
        return False

    def sqlite_table_exist(self, table=None):
        try:
            self.sqlite = MySqlite(db = self.db)
            return self.sqlite.table_exist(table = table)
        except:
            logger.error(f"{traceback.format_exc()}")
            return False

    def sqlite_one_record(self, table=None):
        try:
            self.sqlite = MySqlite(db = self.db)
            qry = f"select * from {table} limit 1"
            return self.sqlite.execute_outhead(qry)
        except:
            logger.error(f"{traceback.format_exc()}")
            return (None, None)

    def updated_recent(self,
                      table=None,
                      retention_day=7,
                      ):
        """ check if updated in retention_day
        If yes, no need to update it again
        """
        if not self.sqlite_db_exist():
            return False # new DB
        if not self.sqlite_table_exist(table=table):
            return False # new table
        try:
            self.sqlite = MySqlite(db = self.db)
            qry = f"select count(*) from {table}"
            rst = self.sqlite.execute(qry)
            if rst[0][0] == 0:
                logger.info(f"Table '{table}' is empty.")
                return False
            qry = f"select max(updateddatetime) from {table}"
            rst = self.sqlite.execute(qry)
            dbts = datetime.strptime(rst[0][0], "%Y-%m-%d %H:%M:%S")
            # logger.debug(dbts)
            ini_now = datetime.now()
            retention_ts = ini_now - timedelta(days = retention_day)
            if dbts > retention_ts:
                logger.info(f"The table '{table}' was updated at '{dbts}'. No need to update now.")
                return True
        except:
            logger.error(f"{traceback.format_exc()}")
            return True # not continue
        return False

    def sqlite_update_1dir(self,
                           table=None,
                           filedir=None,
                           prefix=None,
                           ):
        """ update one folder
        """
        dirlist, filelist = FileInfo().get_dir_file_list_in_folder(thisdir=filedir)
        comment = f"# ---- import {len(filelist)} records into '{table}'"
        logger.debug(f"Update with file count:\n{comment}")
        self.co.update_config_in_memory(comment=comment, dirlist=dirlist)
        datalist=[]
        for f in filelist:
            status, f_info = FileInfo().file_info(thisfile=f)
            if not status:
                logger.error(f"Failed to get file info for '{f}'")
                exit()
            data = tuple(f_info) # use tuple considering `sqlite3.executemany` format
            datalist.append(data)
        staging_table = f"{table}_stg"
        # logger.debug(f"{table=} and {staging_table=}")
        self.fis.staging_table_check(table = table, staging_table = staging_table)
        self.fis.import_data(table = staging_table, datalist = datalist, header = self.table_header)
        self.fis.compute_relname(table=staging_table, prefix=self.prefix)
        self.fis.update_staging_to_core(table = table, staging_table = staging_table, key_column = 'REL_NAME')

    def sqlite_update(self,
                      table=None,
                      filedir=None,
                      prefix=None,
                      retention_day=7,
                      ):
        ''' Update table using filedir
        If updated in retention_day, do not update
        Otherwise, cleanup, create from filedir
        '''
        if self.updated_recent(table=table, retention_day=retention_day):
            logger.info(f"Table '{table}' has already been updated in {retention_day} days...")
            return
        self.prefix = prefix
        self.fis.table_check(table=table,
                   # drop_if_exist=True,
                   table_structure=self.table_structure,
                   )
        rel_dir = self.co.init_from_dirlist(dirlist=[filedir])
        while rel_dir is not None:
            logger.info(f"Working on '{rel_dir}'...")
            self.sqlite_update_1dir(table=table, filedir=rel_dir, prefix=self.prefix)
            rel_dir = self.co.get_first_folder()
        self.co.update_to_config_file()
        
