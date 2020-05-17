#!/usr/bin/python3
'''
Drop table under MySQL.wdinfo schema
'''
import os
import sys
import mysql.connector # test mysql connection
from mysql_con import MySqlConnect
if len(sys.argv) != 2:
    print("Which table do you like to be dropped?")
    exit(0)
tablename=sys.argv[1]
mydb=MySqlConnect(database='wdinfo')
mycursor=mydb.cursor()
mycursor.execute(f"drop table {tablename}")
mydb.close()
phpstr=f"<br><br>Done! Please go back to the previous page..."
print(phpstr)
