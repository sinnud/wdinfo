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

class WdinfoUpdate(object):
    def wd2list(self, rootpath=None, dt_allow=None):
        mylist=list()
        mntname=DiskAccess().ip2mount(rootpath)
        ''' recursively find files '''
        logger.info(f"Start collecting file ({rootpath}) info...")
        stack = list()  # FIFO data-type
        stack.append(mntname)
        while(len(stack)>0):
            thisdir=stack.pop(0)
            dirlist, filelist=DiskAccess().get_dir_file_list_in_folder(thisdir=thisdir)
            for d in dirlist:
                stack.append(d)
            for f in filelist:
                status, rst=DiskAccess().file_info(thisfile=f, ipflag=True)
                if not status:
                    logger.error(f"Failed to get file info for {f}")
                    return False, None
                if datetime.strptime(rst[5], "%Y-%m-%d %H:%M:%S") <= dt_allow:
                    continue
                mystr='\t'.join(map(str, rst))
                mystr=mystr.replace('\r','') # remove \r to avoid error out
                dt_str=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                mystr=f"{mystr}\t{dt_str}"
                mylist.append(mystr)
        logger.info(f"Finished collecting file info, total {len(mylist)} files.")
        return True, mylist
        
    def list2table(self, datalist=None, tbl=None):
        psc=PostgresqlConnect(database='dbhuge')
        rst = psc.execute('set search_path=wdinfo')
        rst = psc.execute(f'drop table if exists _wdinfo_stg')
        if not psc.import_datalist(datalist=datalist, tbl='_wdinfo_stg', tbl_str=table_struct, distby='inserted_dt'):
            return False
        rst = psc.execute(f'insert into {tbl} select * from _wdinfo_stg')
        return True

    def wdinfoupd(self, thisroot=None):
        tbl=DiskAccess().fullpath2tbl(instr=thisroot)
        if tbl is None:
            return False
        psc=PostgresqlConnect(database='dbhuge')
        rst = psc.execute('set search_path=wdinfo')
        rst = psc.execute(f'select max(inserted_dt) from {tbl}')
        dt_allow = rst[0][0]
        logger.info(f"New file must have timestamp greater than '{dt_allow}'.")
        status, rst=self.wd2list(rootpath=thisroot, dt_allow=dt_allow)
        if not status:
            return False
        logger.info(f"New file number: {len(rst)}")
        status=self.list2table(datalist=rst, tbl=tbl)
        if not status:
            logger.error(f"Failed to insert data list into table {tbl}")
            return False
        
        return True

dirlist={'data243'   :'//192.168.1.243/data'
         , 'photo243':'//192.168.1.243/photos'
         , 'music243':'//192.168.1.243/music'
         , 'movie243':'//192.168.1.243/movie'
         , 'data241' :'//192.168.1.241/public/data'
         , 'photo241':'//192.168.1.241/public/photos'
         , 'music241':'//192.168.1.241/public/music'
         , 'movie241':'//192.168.1.241/public/newmovies'
        }

def main(arg=None):
    if arg is None:
        for thisroot in dirlist.values():
            if not WdinfoUpdate().wdinfoupd(thisroot=thisroot):
                return False
        return True

    namelist=arg.split()
    for name in namelist:
        thisroot=dirlist.get(name)
        if thisroot is None:
            logger.debug(f"The name {name} is not valid!")
            continue
        if not WdinfoUpdate().wdinfoupd(thisroot=thisroot):
            return False
    '''
    thisroot='//192.168.1.241/public/newmovies'
    if not WdinfoUpdate().wdinfoupd(thisroot=thisroot):
        return False
    
    thisroot='//192.168.1.241/public/photos'
    if not WdinfoUpdate().wdinfoupd(thisroot=thisroot):
        return False
    thisroot='//192.168.1.241/public/music'
    if not WdinfoUpdate().wdinfoupd(thisroot=thisroot):
        return False
    thisroot='//192.168.1.241/public/data'
    if not WdinfoUpdate().wdinfoupd(thisroot=thisroot):
        return False
    
    thisroot='//192.168.1.243/data'
    if not WdinfoUpdate().wdinfoupd(thisroot=thisroot):
        return False
    
    thisroot='//192.168.1.243/photos'
    if not WdinfoUpdate().wdinfoupd(thisroot=thisroot):
        return False
    
    thisroot='//192.168.1.243/music'
    if not WdinfoUpdate().wdinfoupd(thisroot=thisroot):
        return False
    
    thisroot='//192.168.1.243/movie'
    if not WdinfoUpdate().wdinfoupd(thisroot=thisroot):
        return False
    '''
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
