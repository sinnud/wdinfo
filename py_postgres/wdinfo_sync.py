#!/home/user/code/wdinfo/venv/bin/python
import os
import sys

import logzero
import traceback # Python error trace
from logzero import logger

from postgresql import PostgresqlConnect
from wdaccess import DiskAccess

from datetime import datetime

table_struct="filename text, folder text, type text, fullpath text, filesize bigint, filecreate_dt timestamp, inserted_dt timestamp not null default current_timestamp"
update_clm_list="filename, folder, type, fullpath, filesize, filecreate_dt"

class WdinfoSync(object):
    ''' get new file list in tbl, not in basetbl '''
    def new_file_list(self, tbl=None, basetbl=None):
        filelist=list()
        qry=f"select a.fullpath from {tbl} a"
        qry=f"{qry} left join {basetbl} b"
        qry=f"{qry} on a.fullpath=replace(b.fullpath, '//192.168.1.241/public/', '//192.168.1.243/')"
        qry=f"{qry} where b.fullpath is null;"
        psc=PostgresqlConnect(database='dbhuge')
        psc.execute("set search_path=wdinfo")
        rst = psc.execute(qry)
        for elm in rst:
            filelist.append(elm[0])
        return filelist

    def update_file_with_properties(self, properties=None):
        fullpath=properties[3]
        mystr=properties[3].replace("'","''")
        tbl=DiskAccess().fullpath2tbl(instr=fullpath)
        if tbl is None:
            return False
        qry=f"delete FROM {tbl} WHERE (fullpath = '{mystr}')"
        psc=PostgresqlConnect(database='dbhuge')
        psc.execute("set search_path=wdinfo")
        rst = psc.execute(qry)
        qry=f"insert into {tbl} ({update_clm_list}) values ( "
        mystr=properties[0].replace("'","''")
        qry=f"{qry}'{mystr}', " # filename
        mystr=properties[1].replace("'","''")
        qry=f"{qry}'{mystr}', " # folder
        qry=f"{qry}'{properties[2]}', " # type
        mystr=properties[3].replace("'","''")
        qry=f"{qry}'{mystr}', " # fullpath
        qry=f"{qry}{properties[4]}, " # file size (integer)
        dtstr=properties[5] # .strftime("%Y-%m-%d %H:%M:%S") # already string
        qry=f"{qry}'{dtstr}')" # timestamp
        rst = psc.execute(qry)
        return True

    def filelist_sync(self, filelist=None):
        for elm in filelist: # ip based fullpath
            thisfile=DiskAccess().ip2mount(instr=elm)
            file241=thisfile.replace('/mnt/', '/mnt/public/')
            if not DiskAccess().delete_if_exist(thisfile=file241):
                logger.error(f"Failed to delete {file241}!!!")
                return False
            if not DiskAccess().copy_file(srcfile=thisfile, destfile=file241):
                logger.error(f"Failed to copy {thisfile} to  {file241}!!!")
                return False

            status, rst=DiskAccess().file_info(thisfile=file241, ipflag=True) # not /mnt, but //ip
            if status:
                logger.info(f"The file {file241} record:{rst}")
            else:
                logger.error(f"Failed to call file_info")
                return False
            if not self.update_file_with_properties(properties=rst):
                logger.error(f"Failed to update {rst}!!!")
                return False
        return True

def main(arg=None):
    tbl='music243'
    basetbl='music241'
    rst=WdinfoSync().new_file_list(tbl=tbl, basetbl=basetbl)
    logger.info(f"There exist {len(rst)} new files in {tbl} than {basetbl}.")
    if not WdinfoSync().filelist_sync(filelist=rst):
        return False
    tbl='photos243'
    basetbl='photos241'
    rst=WdinfoSync().new_file_list(tbl=tbl, basetbl=basetbl)
    logger.info(f"There exist {len(rst)} new files in {tbl} than {basetbl}.")
    if not WdinfoSync().filelist_sync(filelist=rst):
        return False
    tbl='data243'
    basetbl='data241'
    rst=WdinfoSync().new_file_list(tbl=tbl, basetbl=basetbl)
    logger.info(f"There exist {len(rst)} new files in {tbl} than {basetbl}.")
    if not WdinfoSync().filelist_sync(filelist=rst):
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