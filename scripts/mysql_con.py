import os
import sys

import logzero
import traceback # Python error trace
from logzero import logger

import mysql.connector # test mysql connection
import time

from sqlalchemy import create_engine

class Pandas2MySql(object):
    def __init__(self, pd=None
                 , host="localhost", user="sinnud", passwd="Jeffery45!@"
                 , database="test"):
        self.pd=pd
        self.host=host
        self.user=user
        self.passwd=passwd
        self.database=database
        self.conn=None
        self.con_string=f"mysql+pymysql://{user}:{passwd}@{host}/{database}"

    def connect(self):
        sqlEngine = create_engine(self.con_string, pool_recycle=3600)
        self.conn = sqlEngine.connect()

    def pdimport(self, tbl=None):
        if self.conn is None:
            self.connect()
        self.pd.to_sql(tbl, self.conn, if_exists='fail')

    def close(self):
        self.conn.close()


class MySqlConnect(object):
    def __init__(self, host="localhost", user="sinnud", passwd="Jeffery45!@"
                    , database="test", allow_local_infile=True):
        self.host=host
        self.user=user
        self.passwd=passwd
        self.database=database
        self.conn = None
        self.allow_local_infile=allow_local_infile
        # logger.debug(f'====== Connect to {host}.{database} using account {user} ======')

    def connect(self):
        self.conn = mysql.connector.connect(host=self.host
                                            , user=self.user
                                            , passwd=self.passwd
                                            , database=self.database
                                            , allow_local_infile=self.allow_local_infile)
        # self.conn.set_session(autocommit = True) # postgresql
        self.conn.autocommit = True
        cursor = self.conn.cursor()
        cursor.execute(f'USE {self.database}')
        logger.debug(f'====== Connect to {self.host}.{self.database} using account {self.user} ======')

    def cursor(self):
        if not self.conn: # or self.conn.closed:
            self.connect()
        return self.conn.cursor()

    def execute(self, query):
        if not self.conn: # or self.conn.closed:
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

    ''' load data into MySql on localhost '''
    def local_import(self, file, tbl):
        thisquery = f"LOAD DATA LOCAL INFILE '{file}'"
        thisquery = f"{thisquery}\n INTO TABLE {tbl}"
        thisquery = f"{thisquery}\n FIELDS TERMINATED BY ','"
        qt = '"'
        thisquery = f"{thisquery}\n ENCLOSED BY '{qt}'"
        nl = '\\n'
        thisquery = f"{thisquery}\n LINES TERMINATED BY '{nl}'"
        return self.execute(thisquery)

    def close(self):
        #if not self.conn.closed:
        logger.debug(f'====== Close {self.host}.{self.database} using account {self.user} ======')
        self.conn.close()

def main():
    logger.debug("Start main... (connect to MySql)")
    mydb=MySqlConnect()
    logger.debug("Start query...")
    result=mydb.execute("select count(*) from photo_info")
    logger.debug("Log result...")
    logger.info(result)
    logger.debug("Close...")
    mydb.close()
    return True

if __name__ == '__main__':
    mylog=os.path.realpath(__file__).replace('.py','.log')
    #mylog=f"{config.WORKDIR}/{mylog}"
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
