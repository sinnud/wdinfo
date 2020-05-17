#!/usr/bin/python3
'''
Analyze folder structure into table under MySQL.wdinfo schema
'''
import os
import sys
import logzero
import traceback # Python error trace
from logzero import logger
import mysql.connector # test mysql connection
from mysql_con import MySqlConnect
from mysql_con import Pandas2MySql
import pandas as pd # import data through pandas to mysql
import glob
from datetime import datetime

def get_photo_info_pd(folder=None):
    datalist=list()
    stack = list()  # FIFO data-type
    stack.append(folder)
    while(len(stack)>0):
        thisdir=stack.pop(0)
        logger.info(f"Go through folder {thisdir}...")
        filelist=glob.glob(f"{thisdir}/*")
        for idx, file in enumerate(sorted(filelist), start=1):
            if os.path.isdir(file):
                logger.info(f"Folder {file} need to go through...({idx})")
                stack.append(file)
            elif os.path.isfile(file):
                path, fn=os.path.split(file)
                filename, file_extension = os.path.splitext(fn)
                st=os.stat(file)
                dt_fmt=datetime.fromtimestamp(st.st_ctime)
                datalist.append([fn, path, file_extension[1:], file, st.st_size, dt_fmt])
            else:
                logger.info(f"Not file or folder: {file}...({idx})")
    return pd.DataFrame(datalist)

if len(sys.argv) != 2:
    print("Which table do you like to be truncated?")
    exit(0)
tablename=sys.argv[1]
mydb=MySqlConnect(database='wdinfo')
mycursor=mydb.cursor()
qry="SELECT count(*) FROM information_schema.TABLES"
qry=f"{qry} WHERE (TABLE_SCHEMA = 'wdinfo') AND (TABLE_NAME = '{tablename}')"
mycursor.execute(qry)
stopflag=0
for idx, x in enumerate(mycursor, start=1):
    if idx == 1 and x[0] > 0:
        logger.info(f"{idx}: {x}")
        phpstr=f"Table wdinfo.{tablename} exists!!!"
        stopflag=1
mydb.close()
if stopflag == 1:
    phpstr=f"{phpstr}<br><br>Please go back to the previous page..."
    print(phpstr)
    exit(0)
mypd=get_photo_info_pd(folder=f"/mnt/{tablename}")
mypd.columns=['filename', 'folder', 'file_type', 'fullpath', 'filesize', 'createtime']
p2d=Pandas2MySql(pd=mypd, database='wdinfo')
p2d.pdimport(tablename)
p2d.close()
phpstr=f"<br><br>Done! Please go back to the previous page..."
print(phpstr)

