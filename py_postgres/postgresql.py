import os
import sys

import logzero
import traceback # Python error trace
from logzero import logger

import psycopg2

import time

from io import StringIO

class PostgresqlConnect(object):
    def __init__(self
        , host='localhost'
        , user='sinnud'
        , password='Jeffery45!@'
        , database='dbhuge'
        ):
        self.host=host
        self.user=user
        self.password=password
        self.dbname=database
        self.conn_string=f"host='{host}' dbname='{database}' user='{user}' password='{password}'"
        self.conn=None

    def __del__(self):
        if self.conn:
            self.conn.close()
            logger.debug(f"=== Disconnect to {self.host} with account {self.user} ===")

    def connect(self):
        self.conn = psycopg2.connect(self.conn_string)
        #self.conn.autocommit(True) # mssql
        self.conn.set_session(autocommit=True)
        #self.conn.set_client_encoding('UTF8')
        logger.debug(f"=== Connect to {self.host} using account {self.user} ===")

    def cursor(self):
        if not self.conn: # or self.conn.closed:
            self.connect()
        return self.conn.cursor()

    def execute(self, query):
        if not self.conn or self.conn.closed:
            self.connect()
        logger.debug(f'RUNNING QUERY: {query}')
        start = time.time()
        cursor = self.conn.cursor()
        cursor.execute(query)
        logger.debug(f'# ROWS AFFECTED : {cursor.rowcount}, took {time.time() - start} seconds.')
        try:
            rst = cursor.fetchall()
        except Exception as e:
            return cursor
        if len(rst)<1000:
            logger.debug(f'# RESULT : {rst}.')
        return rst        

    ''' load data into PostgreSql on localhost '''
    def local_import(self, query, file):
        if not self.conn or self.conn.closed:
            self.connect()
        logger.debug(f"Import {file} using query\n\n{query}")
        start = time.time()
        cursor = self.conn.cursor()
        try:
            cursor.copy_expert(query, file)
            logger.debug(f"Rows affected: {cursor.rowcount}, took {time.time() - start} seconds")
        except:
            logger.error(f"{traceback.format_exc()}")
            self.conn.rollback()
            return False
        return True

    def close(self):
        #if not self.conn.closed:
        logger.debug(f'====== Close {self.server} with account {self.user} ======')
        self.conn.close()

    def table_exist(self, tbl=None):
        qry=f"SELECT count(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"
        qry=f"{qry}   AND TABLE_NAME='{tbl}'"
        rst = self.execute(qry)
        if rst[0][0]==0:
            return False
        return True

    def truncate_table(self, tbl=None):
        qry=f"truncate table {tbl}"
        try:
            self.execute(qry)
            return True
        except:
            logger.error(f"{traceback.format_exc()}")
        return False

    def create_table(self, tbl=None, tbl_str=None, distby=None):
        if distby is None:
            qry=f"create table {tbl} ({tbl_str})"
        else:
            qry=f"create table {tbl} ({tbl_str}) distributed by ({distby})"
        try:
            self.execute(qry)
            return True
        except:
            logger.error(f"{traceback.format_exc()}")
        return False
       
    def create_truncate_table(self, tbl=None, tbl_str=None, distby=None):
        if self.table_exist(tbl=tbl):
            return self.truncate_table(tbl=tbl)
        return self.create_table(tbl=tbl, tbl_str=tbl_str)

    def import_datalist(self, datalist=None, tbl=None, tbl_str=None, distby=None, headerline=False):
        if not self.create_truncate_table(tbl=tbl, tbl_str=tbl_str, distby=distby):
            return False
        if headerline:
            query=f"copy {tbl} from stdin header"
        else:
            query=f"copy {tbl} from stdin"
        try:
            self.local_import(query, StringIO('\n'.join(datalist)))
            return True
        except:
            logger.error(f"{traceback.format_exc()}")
        return False

        
def main(arg=None):
    psc = PostgresqlConnect()
    rst = psc.execute('set search_path=wdinfo')
    rst = psc.execute('select count(*) from sinnud')
    rst = psc.execute('drop table sinnud')
    if not psc.create_truncate_table(tbl='sinnud', tbl_str='name text', distby='name'):
        return False
    with open('requirement.txt', 'r') as f:
        f_str=f.read()
    flist_=f_str.split('\n')
    flist=list(filter(None, flist_))
    logger.info(flist)
    if not psc.import_datalist(datalist=flist, tbl='sinnud', tbl_str='name text', distby='name', headerline=False):
        return False
    return True
if __name__ == '__main__':
    mylog=os.path.realpath(__file__).replace('.py','.log')
    if os.path.exists(mylog):
        os.remove(mylog)
    logzero.logfile(mylog)

    logger.info(f'start python code {__file__}.\n')
    if len(sys.argv)>1:
        logger.info(f"Argument: {sys.argv}")
        myarg=sys.argv
        pgmname=myarg.pop(0)
        logger.info(f"Program name:{pgmname}.")
        logger.info(f"Arguments:{myarg}.")
        rst=main(arg=' '.join(myarg))
    else:
        logger.info(f"No arguments")
        rst=main()
    if not rst:
        # record error in log such that process.py will capture it
        logger.error(f"ERROREXIT: Please check")
    logger.info(f'end python code {__file__}.\n')