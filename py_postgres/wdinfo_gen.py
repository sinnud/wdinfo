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

class WdinfoGen(object):
    def wd2list(self, rootpath=None, debug=False):
        mylist=list()
        mntname=DiskAccess().ip2mount(rootpath)
        if debug:
            dirlist, filelist=DiskAccess().get_dir_file_list_in_folder(thisdir=mntname)
            for f in filelist:
                status, rst=DiskAccess().file_info(thisfile=f, ipflag=True)
                if not status:
                    logger.error(f"Failed to get file info for {f}")
                    return False, None
                mystr='\t'.join(map(str, rst))
                dt_str=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                mystr=f"{mystr}\t{dt_str}"
                mylist.append(mystr)
            return True, mylist
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
        rst = psc.execute(f'drop table if exists {tbl}')
        if not psc.import_datalist(datalist=datalist, tbl=tbl, tbl_str=table_struct, distby='inserted_dt'):
            return False
        return True

    def wdinfogen(self, thisroot=None, debug=False):
        status, rst=self.wd2list(rootpath=thisroot, debug=debug)
        if not status:
            logger.error(f"Failed to generate list for {thisroot}")
            return False
        datalist=rst
        status, rst=DiskAccess().ip_mount_table(instr=thisroot)
        if not status:
            logger.error(f"Failed to get table info for {thisroot}")
            return False
        thistable=rst[2]
        status=self.list2table(datalist=datalist, tbl=thistable)
        if not status:
            logger.error(f"Failed to insert data list into table {thisroot}")
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
            if not WdinfoGen().wdinfogen(thisroot=thisroot):
                return False
        return True

    namelist=arg.split()
    for name in namelist:
        thisroot=dirlist.get(name)
        if thisroot is None:
            logger.debug(f"The name {name} is not valid!")
            continue
        if not WdinfoGen().wdinfogen(thisroot=thisroot):
            return False
        
    '''    
    thisroot='//192.168.1.241/public/newmovies'
    if not WdinfoGen().wdinfogen(thisroot=thisroot):
        return False
    
    thisroot='//192.168.1.241/public/photos'
    if not WdinfoGen().wdinfogen(thisroot=thisroot):
        return False
    thisroot='//192.168.1.241/public/music'
    if not WdinfoGen().wdinfogen(thisroot=thisroot):
        return False
    thisroot='//192.168.1.241/public/data'
    if not WdinfoGen().wdinfogen(thisroot=thisroot):
        return False
    
    thisroot='//192.168.1.243/data'
    if not WdinfoGen().wdinfogen(thisroot=thisroot):
        return False
    
    thisroot='//192.168.1.243/photos'
    if not WdinfoGen().wdinfogen(thisroot=thisroot):
        return False
    thisroot='//192.168.1.243/music'
    if not WdinfoGen().wdinfogen(thisroot=thisroot):
        return False
    
    thisroot='//192.168.1.243/movie'
    if not WdinfoGen().wdinfogen(thisroot=thisroot):
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
