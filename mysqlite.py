""" File name: mysqlite.py
Utils for SQLite
"""
from logzero import logger
import sqlite3

class MySqlite(object):
    """ Interface to SQLite
    """
    def __init__(self,
    db = None,
    ):
        self.db = db
        self.conn = None

    def __repr__(self):
        """ It could be represented
        """
        return f"SQLite: Database='{self.db}'"

    def __del__(self):
        """ destruction
        """
        if self.conn:
            self.conn.close()
            logger.debug(f"Connection to database '{self.db}' closed")

    def connect(self):
        """ Connect with auto commit
        """
        # self.conn = sqlite3.connect(self.db, autocommit=True)
        self.conn = sqlite3.connect(self.db, isolation_level=None)
        logger.debug(f"Connect to SQLite database '{self.db}'...")

    def execute(self, query):
        """ execute query
        return array instead of cursor
        """
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query)
        try:
            rst = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            return cursor
        # logger.debug(f"Result length: {len(rst)}")
        return rst

    def execute_outhead(self, query):
        """ execute query
        return array instead of cursor
        """
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query)
        try:
            head = [x[0] for x in cursor.description]
            rst = cursor.fetchall()
            return (head, rst)
        except Exception as e:
            logger.error(e)
            return (None, None)

    def tables(self):
        """ List tables in database
        """
        qry = '''
        SELECT name FROM sqlite_schema
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        '''
        return [x[0] for x in self.execute(qry)]

    def drop_table(self, table = None):
        """ List tables in database
        """
        qry = f'DROP TABLE {table}'
        self.execute(qry)

    def table_exist(self, table = None):
        """ List tables in database
        """
        qry = f'''
        SELECT name FROM sqlite_schema
        WHERE type = 'table'
        AND name = '{table}'
        '''
        if len(self.execute(qry)) == 0:
            return False
        else:
            return True

    def import_from_datalist(self, query, datalist):
        """ import data list into table using query
        Sample query is: "INSERT INTO person (name, age) VALUES(?, ?)"
        """
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute("BEGIN TRANSACTION;")
        cursor.executemany(query, datalist)
        cursor.execute("COMMIT;")
