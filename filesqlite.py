""" File name: filesqlite.py
call mysqlite.py and fileinfo.py
Utils to store File Information into SQLite table.
"""
from logzero import logger
from mysqlite import MySqlite
from fileinfo import FileInfo

class FileInfoSqlite(object):
    """ Check file info and store to SQLite database
    Assumption:
    - One folder only. SQLite table includes file information under this folder
    - Table structure: file name, file path, file size, file timestmap, and relative path
    - Each time drop table and create one (this is slow?)
    """
    def __init__(self, db = None, ):
        self.sqlite = MySqlite(db = db)

    def table_check(self, table = None, drop_if_exist = False, table_structure = None):
        """ Check table
        if not exist, create it
        """
        tblex = self.sqlite.table_exist(table=table)
        if tblex and drop_if_exist:
            self.sqlite.drop_table(table=table)
        elif tblex:
            return
        qry = f"CREATE TABLE {table} ({table_structure});"
        self.sqlite.execute(qry)

    def staging_table_check(self, table = None, staging_table = None):
        """ Check staging table
        if exist, truncate it
        if not exist, create it based on table
        =============================================
        SQLite3: instead of `truncate table [table_name]`, use `delete from [table_name]`.
        =============================================
        SQLite3 does not provide syntax `create table new_table like existing_table`
        But provides `SELECT sql FROM sqlite_master WHERE type='table' AND name='mytable'`
        We will start from there
        "CREATE TABLE disk1 (NAME TEXT, PATH TEXT, FILESIZE TEXT, CHANGETIME TEXT, REL_NAME TEXT, updateddatetime TIMESTAMP DEFAULT (datetime('now','localtime')))"
        Remove first three words "CREATE TABLE [table_name]"
        Remove leading "(" and tailing ")"
        "NAME TEXT, PATH TEXT, FILESIZE TEXT, CHANGETIME TEXT, REL_NAME TEXT, updateddatetime TIMESTAMP DEFAULT (datetime('now','localtime'))"
        """
        tblex = self.sqlite.table_exist(table=staging_table)
        if tblex:
            qry = f"delete from {staging_table};"
        else:
            qry = f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'"
            logger.debug(qry)
            rst = self.sqlite.execute(qry)
            logger.debug(rst)
            sql_str = rst[0][0]
            data_structure = ' '.join(sql_str.split()[3:])[1:-1]
            qry = f"CREATE TABLE {staging_table} ({data_structure});"
        self.sqlite.execute(qry)

    def import_data(self, table = None, datalist = None, header = None):
        """ Import data into table
        The header argument list column name
        """
        fieldcnt = len(header.split(','))
        wildlist = ['?'] * fieldcnt
        wildstr = ', '.join(wildlist)
        qry = f"INSERT INTO {table} ({header}) VALUES({wildstr})"
        self.sqlite.import_from_datalist(query=qry, datalist=datalist)

    def compute_relname(self, table = None, prefix=None):
        """ Compute relative path for comparing
        """
        qry = f"update {table}"
        qry = f"{qry} set rel_name = replace(path, '{prefix}', '')||'/'||name"
        self.sqlite.execute(qry)

    def compute_newfiles(self, table = None, tablebase = None):
        """ Compute relative path for comparing
        """
        qry = f"select a.REL_NAME from {table} a left join {tablebase} b on a.rel_name = b.REL_NAME where b.filesize is null"
        return [x[0] for x in self.sqlite.execute(qry)]

    def compute_updatedfiles(self, table = None, tablebase = None):
        """ Compute relative path for comparing
        """
        qry = f"select a.REL_NAME from {table} a join {tablebase} b on a.rel_name = b.REL_NAME where a.filesize != b.filesize"
        return [x[0] for x in self.sqlite.execute(qry)]

    def update_staging_to_core(self, table = None, staging_table = None, key_column = None):
        """ Update staging table into core table
        Based on key_column, if record already exist in core table drop them from core table
        """
        qry = f"delete from {table} where exists (select * from {staging_table} where {table}.{key_column} = {staging_table}.{key_column})"
        self.sqlite.execute(qry)
        qry = f"insert into {table} select * from {staging_table}"
        self.sqlite.execute(qry)
