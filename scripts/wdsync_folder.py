#!/home/user/code/wdinfo/venv/bin/python
'''
Compare file under folder based on MySQL.wdinfo
'''
import os
import sys
import logging
import logzero
import traceback # Python error trace
from logzero import logger
import mysql.connector # test mysql connection, need pip install mysql-connector-python 
from mysql_con import MySqlConnect
from mysql_con import Pandas2MySql
import pandas as pd # import data through pandas to mysql
import glob
from datetime import datetime
import time
import shutil
from win32_setctime import setctime

''' function decorator '''
def log_dbg(func):
    def log_dbg_in(*args, **kwargs):
        begin_time=time.time()
        logger.debug(f"--- start {func.__name__} ---")
        returned_value = func(*args, **kwargs)
        duration=time.time()-begin_time
        logger.debug(f"--- end {func.__name__} used {duration} seconds ---")
        return returned_value
    return log_dbg_in

class SyncMySQL(object):
    ''' submit query to MySQL.wdinfo '''
    @log_dbg
    def MySQL_exec(self, qry=None):
        # logger.debug(f"--- in {sys._getframe().f_code.co_name} ---")
        try:
            mydb=MySqlConnect(database='wdinfo')
            rst=mydb.execute(qry)
            mydb.close()
            return True, rst
        except:
            logger.error(f"{traceback.format_exc()}")
            logger.error(f"Failed to submit: {qry}!!!")
            return False, None

    ''' check table exist in MySQL.wdinfo '''
    def table_exist(self, tbl=None):
        qry="SELECT count(*) FROM information_schema.TABLES"
        qry=f"{qry} WHERE (TABLE_SCHEMA = 'wdinfo') AND (TABLE_NAME = '{tbl}')"
        status, rst=self.MySQL_exec(qry)
        if status:
            if rst[0][0]>0:
                return True
            else:
                return False
        return False

    ''' check folder exist in 192.168.1.243 from table in MySQL.wdinfo '''
    def folder_in_243(self, folder=None):
        dirlist=list(filter(None, folder.split('/')))
        tbl=dirlist[0]
        if not self.table_exist(tbl=tbl):
            logger.error(f"For dir {folder} under 243, table {tbl} does not exist!!!")
            return False
        mydir=f"/mnt{folder}"
        qry=f"SELECT count(*) FROM {tbl} WHERE (folder = '{mydir}')"
        status, rst=self.MySQL_exec(qry)
        if status:
            if rst[0][0]>0:
                return True
            else:
                return False
        return False

    ''' check folder exist in 192.168.1.241 from table in MySQL.wdinfo '''
    def folder_in_241(self, folder=None):
        tbl='public'
        if not self.table_exist(tbl=tbl):
            logger.error(f"For dir {folder} under 241, table {tbl} does not exist!!!")
            return False
        mydir=f"/mnt/public{folder}"
        qry=f"SELECT count(*) FROM {tbl} WHERE (folder = '{mydir}')"
        status, rst=self.MySQL_exec(qry)
        if status:
            if rst[0][0]>0:
                return True
            else:
                return False
        return False

    ''' new dir in 192.168.1.243 but not in 241 from table in MySQL.wdinfo '''
    def new_folder_in_243_not_241(self, roottable=None):
        newdirs=list()
        qry=f"select a.folder from"
        qry=f"{qry} (SELECT distinct folder FROM {roottable}) as a"
        qry=f"{qry} left join (select distinct folder from public) as b"
        qry=f"{qry} on replace(a.folder,'/mnt/','/mnt/public/') = b.folder"
        qry=f"{qry} where b.folder is null"
        status, rst=self.MySQL_exec(qry)
        if not status:
            return False, None
        for idx, x in enumerate(rst, start=1):
            newdirs.append(x[0])
        return True, newdirs

    ''' same dir in 192.168.1.243 and in 241 from table in MySQL.wdinfo '''
    def same_folder_in_243_and_241(self, roottable=None):
        newdirs=list()
        qry=f"select a.folder from"
        qry=f"{qry} (SELECT distinct folder FROM {roottable}) as a"
        qry=f"{qry} inner join (select distinct folder from public) as b"
        qry=f"{qry} on replace(a.folder,'/mnt/','/mnt/public/') = b.folder"
        status, rst=self.MySQL_exec(qry)
        if not status:
            return False, None
        for idx, x in enumerate(rst, start=1):
            newdirs.append(x[0])
        return True, newdirs

    ''' get file list under new folder in 192.168.1.243 from table in MySQL.wdinfo '''
    def new_file_new_dir_243(self, folder=None):
        newfiles=list()
        dirlist=list(filter(None, folder.split('/')))
        tbl=dirlist[0]
        mydir=f"/mnt{folder}"
        qry=f"SELECT fullpath FROM {tbl}"
        qry=f"{qry} WHERE (folder = '{mydir}')"
        status, rst=self.MySQL_exec(qry)
        if not status:
            return False, None
        for idx, x in enumerate(rst, start=1):
            newfiles.append(x[0])
        return True, newfiles

    ''' get new file list under folder in 192.168.1.243 but not in 241 from table in MySQL.wdinfo '''
    def new_file_in_243_not_241(self, folder=None):
        newfiles=list()
        dirlist=list(filter(None, folder.split('/')))
        tbl243=dirlist[0]
        tbl241='public'
        mydir243=f"/mnt{folder}"
        mydir241=f"/mnt/public{folder}"
        qry=f"SELECT a.fullpath FROM {tbl243} a"
        qry=f"{qry} left join {tbl241} b"
        qry=f"{qry} on replace(a.fullpath,'/mnt','')=replace(b.fullpath,'/mnt/public','')"
        qry=f"{qry} WHERE (a.folder = '{mydir243}') and (b.folder is null)"
        status, rst=self.MySQL_exec(qry)
        if not status:
            return False, None
        for idx, x in enumerate(rst, start=1):
            newfiles.append(x[0])
        return True, newfiles

    ''' get updated file list under folder in 192.168.1.243 and in 241 from table in MySQL.wdinfo '''
    def updated_file_in_243_not_241(self, folder=None):
        newfiles=list()
        dirlist=list(filter(None, folder.split('/')))
        tbl243=dirlist[0]
        tbl241='public'
        mydir243=f"/mnt{folder}"
        mydir241=f"/mnt/public{folder}"
        qry=f"SELECT a.fullpath FROM {tbl243} a"
        qry=f"{qry} join {tbl241} b"
        qry=f"{qry} on replace(a.fullpath,'/mnt','')=replace(b.fullpath,'/mnt/public','')"
        qry=f"{qry} WHERE (a.folder = '{mydir243}') and (a.filesize <> b.filesize)"
        status, rst=self.MySQL_exec(qry)
        if not status:
            return False, None
        for idx, x in enumerate(rst, start=1):
            newfiles.append(x[0])
        return True, newfiles

    ''' giving folder, compare files (not sub-folder) in 243 and 241 based on MySQL.wdinfo tables
        If exist in 243 but not in 241, append to list
        If exist in 241 but not in 243, ignore
    '''
    def new_file_list(self, folder=None):
        if not self.folder_in_243(folder=folder):
            return False, None
        if not self.folder_in_241(folder=folder):
            logger.info(f"The dir {folder} is new (not in 241).")
            return self.new_file_new_dir_243(folder=folder)
        newfiles=list()
        dirlist=list(filter(None, folder.split('/')))
        tbl243=dirlist[0]
        tbl241='public'
        mydir243=f"/mnt{folder}"
        mydir241=f"/mnt/public{folder}"
        qry=f"SELECT count(*) FROM {tbl243} WHERE (folder = '{mydir243}')"
        status, rst=self.MySQL_exec(qry)
        if not status:
            return False, None
        logger.info(f"In 243, folder {folder} includes {rst[0][0]} data files.")
        qry=f"SELECT count(*) FROM {tbl241} WHERE (folder = '{mydir241}')"
        status, rst=self.MySQL_exec(qry)
        if not status:
            return False, None
        logger.info(f"In 241, folder {folder} includes {rst[0][0]} data files.")
        return self.new_file_in_243_not_241(folder=folder)

    ''' update table in MySQL.wdinfo using file properties '''
    @log_dbg
    def update_file_with_properties_241(self, properties=None):
        fullpath=properties[3]
        mystr=properties[3].replace("'","''")
        qry=f"delete FROM public WHERE (fullpath = '{mystr}')"
        status, rst=self.MySQL_exec(qry)
        if not status:
            return False
        qry=f"insert into public values ('0', " # index, default 0
        mystr=properties[0].replace("'","''")
        qry=f"{qry}'{mystr}', " # filename
        mystr=properties[1].replace("'","''")
        qry=f"{qry}'{mystr}', " # folder
        qry=f"{qry}'{properties[2]}', " # type
        mystr=properties[3].replace("'","''")
        qry=f"{qry}'{mystr}', " # fullpath
        qry=f"{qry}{properties[4]}, " # file size (integer)
        dtstr=properties[5].strftime("%Y-%m-%d %H:%M:%S")
        qry=f"{qry}'{dtstr}')" # timestamp
        status, rst=self.MySQL_exec(qry)
        if not status:
            return False
        return True

class DiskAccess(object):
    def file_info(self, thisfile=None):
        if not os.path.exists(thisfile):
            logger.error(f"{thisfile} does NOT exist!!!")
            return False, None
        if os.path.isdir(thisfile):
            logger.error(f"{thisfile} is directory, NOT file!!!")
            return False, None
        
        path, fn=os.path.split(thisfile)
        filename, file_extension = os.path.splitext(fn)
        st=os.stat(thisfile)
        dt_fmt=datetime.fromtimestamp(st.st_ctime)
        return True, [fn, path, file_extension[1:], thisfile, st.st_size, dt_fmt]

    def delete_if_exist(self, thisfile=None):
        if not os.path.exists(thisfile):
            return True
        if os.path.isdir(thisfile):
            logger.error(f"{thisfile} is directory!!!")
            return False
        try:
            os.remove(thisfile)
            logger.debug(f"Successfully delete {thisfile}.")
            return True
        except:
            logger.error(f"Failed deleting {thisfile}!!!")
            return False

    def rename_file(self, thisfile=None, newname=None):
        if not os.path.exists(thisfile):
            logger.error(f"{thisfile} does NOT exist!!!")
            return False
        if os.path.isdir(thisfile):
            logger.error(f"{thisfile} is directory!!!")
            return False
        try:
            os.rename(thisfile, newname)
            logger.debug(f"Successfully rename {thisfile} to {newname}.")
            return True
        except:
            logger.error(f"Failed renaming {thisfile}!!!")
            return False

    def copy_file(self, srcfile=None, destfile=None, ctime=None):
        path, fn=os.path.split(destfile)
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            #shutil.copyfile(srcfile, destfile)
            shutil.copy2(srcfile, destfile)
            if ctime is not None and os.name == 'nt':
                setctime(destfile,ctime)
            logger.debug(f"Successfully copy {srcfile} to {destfile}.")
            return True
        except:
            logger.error(f"{traceback.format_exc()}")
            logger.error(f"Failed to copy {srcfile} to {destfile}!!!")
            self.delete_if_exist(thisfile=destfile) # in case partially copied
            return False
        
def dir_sync(mydir=None):
    status, thislist=SyncMySQL().new_file_list(folder=mydir)
    if status:
        filestr='\n'.join(thislist)
        logger.info(f"For dir {mydir}, we have {len(thislist)} new files:\n{filestr}")
    else:
        logger.error(f"Failed to call new_file_list")
        return False
    for thisfile in thislist:
        status, rst=DiskAccess().file_info(thisfile=thisfile)
        if status:
            logger.info(f"The file {thisfile} record:{rst}")
        else:
            logger.error(f"Failed to call file_info")
            return False
        file241=thisfile.replace('/mnt/', '/mnt/public/')
        if not DiskAccess().delete_if_exist(thisfile=file241):
            logger.error(f"Failed to delete {file241}!!!")
            return False
        if not DiskAccess().copy_file(srcfile=thisfile, destfile=file241, ctime=rst[5]):
            logger.error(f"Failed to copy {thisfile} to  {file241}!!!")
            return False

        status, rst=DiskAccess().file_info(thisfile=file241)
        if status:
            logger.info(f"The file {file241} record:{rst}")
        else:
            logger.error(f"Failed to call file_info")
            return False
        if not SyncMySQL().update_file_with_properties_241(properties=rst):
            logger.error(f"Failed to update {rst}!!!")
            return False
    return True

''' main function '''
@log_dbg
def main():
    
    mytable='data'
    checkonly=False
    logger.info(f"test SyncMySQL().new_folder_in_243_not_241()...")
    status, dirlist=SyncMySQL().new_folder_in_243_not_241(roottable=mytable)
    if status:
        dirstr='\n'.join(sorted(dirlist))
        logger.info(f"New folder {len(dirlist)} includes:\n{dirstr}")
        logger.info(len(dirlist))
    if checkonly:
        return True
    for elm in sorted(dirlist):
        mydir=elm.replace('/mnt','')
        sqmydir=mydir.replace("'","''")
        logger.info(f"test sync {mydir}...")
        if not dir_sync(mydir=sqmydir):
            logger.error(f"Failed to sync {mydir}!!!")
            return False
    logger.info(f"test SyncMySQL().same_folder_in_243_and_241()...")
    status, dirlist=SyncMySQL().same_folder_in_243_and_241(roottable=mytable)
    if status:
        dirstr='\n'.join(sorted(dirlist))
        logger.info(f"Same folder {len(dirlist)} includes:\n{dirstr}")
    for elm in sorted(dirlist):
        mydir=elm.replace('/mnt','')
        sqmydir=mydir.replace("'","''")
        logger.info(f"test sync {mydir}...")
        if not dir_sync(mydir=sqmydir):
            logger.error(f"Failed to sync {mydir}!!!")
            return False
    '''
    mydir="/music/children/Harry Potter and the Sorcerer's Stone by J. K. Rowling"
    sqmydir=mydir.replace("'","''")
    logger.info(f"test sync {mydir}...")
    if not dir_sync(mydir=sqmydir):
        logger.error(f"Failed to sync {mydir}!!!")
        return False
    '''
    return True

if __name__ == '__main__':
    logger.info(f"Start python code file {__file__}.")
    if len(sys.argv)>1 and 'nodebug' in sys.argv:
        logzero.loglevel(logging.INFO)
    if not main():
        logger.error(f"Failed to call main")
        exit(1)
    logger.info(f"Success running python code file {__file__}.")