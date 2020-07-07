#!/home/user/code/wdinfo/venv/bin/python
import os
import sys
import logging
import logzero
import traceback # Python error trace
from logzero import logger

import glob
from datetime import datetime
import time
import shutil


'''
//192.168.1.243/music     /mnt/music     music243
//192.168.1.243/photos    /mnt/photos    photos243
//192.168.1.243/data      /mnt/data      data243
//192.168.1.243/movie     /mnt/movie     movie243

//192.168.1.241/public    /mnt/public

//192.168.1.241/public/music     /mnt/public/music     music241
//192.168.1.241/public/photos    /mnt/public/photos    photos241
//192.168.1.241/public/data      /mnt/public/data      data241
//192.168.1.241/public/newmovies /mnt/public/newmovies movie241
'''
class DiskAccess(object):
    def ip_mount_table(self, instr=None):
        if '//192.168.1.243/music' in instr:
            return True, [instr, instr.replace('//192.168.1.243/', '/mnt/'), 'music243']
        elif '//192.168.1.243/photos' in instr:
            return True, [instr, instr.replace('//192.168.1.243/', '/mnt/'), 'photos243']
        elif '//192.168.1.243/data' in instr:
            return True, [instr, instr.replace('//192.168.1.243/', '/mnt/'), 'data243']
        elif '//192.168.1.243/movie' in instr:
            return True, [instr, instr.replace('//192.168.1.243/', '/mnt/'), 'movie243']
        elif '//192.168.1.241/public/music' in instr:
            return True, [instr, instr.replace('//192.168.1.241/', '/mnt/'), 'music241']
        elif '//192.168.1.241/public/photos' in instr:
            return True, [instr, instr.replace('//192.168.1.241/', '/mnt/'), 'photos241']
        elif '//192.168.1.241/public/data' in instr:
            return True, [instr, instr.replace('//192.168.1.241/', '/mnt/'), 'data241']
        elif '//192.168.1.241/public/newmovies' in instr:
            return True, [instr, instr.replace('//192.168.1.241/', '/mnt/'), 'movie241']
        elif '//mnt/music' in instr:
            return True, [instr, instr.replace('/mnt/', '//192.168.1.243/'), instr, 'music243']
        elif '//mnt/photos' in instr:
            return True, [instr, instr.replace('/mnt/', '//192.168.1.243/'), instr, 'photos243']
        elif '//mnt/data' in instr:
            return True, [instr, instr.replace('/mnt/', '//192.168.1.243/'), instr, 'data243']
        elif '//mnt/movie' in instr:
            return True, [instr, instr.replace('/mnt/', '//192.168.1.243/'), instr, 'movie243']
        elif '//mnt/public/music' in instr:
            return True, [instr, instr.replace('/mnt/', '//192.168.1.241/'), instr, 'music241']
        elif '//mnt/public/photos' in instr:
            return True, [instr, instr.replace('/mnt/', '//192.168.1.241/'), instr, 'photos241']
        elif '//mnt/public/data' in instr:
            return True, [instr, instr.replace('/mnt/', '//192.168.1.241/'), instr, 'data241']
        elif '//mnt/public/newmovies' in instr:
            return True, [instr, instr.replace('/mnt/', '//192.168.1.241/'), instr, 'movie241']
        else:
            return False, None

    def ip2mount(self, instr=None):
        if '//192.168.1.243' in instr:
            return instr.replace('//192.168.1.243/', '/mnt/')
        else:
            return instr.replace('//192.168.1.241/', '/mnt/')

    def mount2ip(self, instr=None):
        if '/mnt/public' in instr:
            return instr.replace('/mnt/','//192.168.1.241/')
        else:
            return instr.replace('/mnt/','//192.168.1.243/')

    def fullpath2tbl(self, instr=None):
        status, rst=self.ip_mount_table(instr=instr)
        if not status:
            return None
        return rst[2]

    def get_dir_file_list_in_folder(self, thisdir=None, ipflag=False):
        dirlist=list()
        filelist=list()
        checklist=glob.glob(f"{thisdir}/*")
        for elm in checklist:
            if os.path.isdir(elm) and ipflag:
                dirlist.append(self.mount2ip(elm))
            elif os.path.isdir(elm):
                dirlist.append(elm)
            elif ipflag:
                filelist.append(self.mount2ip(elm))
            else:
                filelist.append(elm)
        return dirlist, filelist

    def file_info(self, thisfile=None, ipflag=False):
        if not os.path.exists(thisfile):
            logger.error(f"{thisfile} does NOT exist!!!")
            return False, None
        if os.path.isdir(thisfile):
            logger.error(f"{thisfile} is directory, NOT file!!!")
            return False, None
        
        path, fn=os.path.split(thisfile)
        filename, file_extension = os.path.splitext(fn)
        st=os.stat(thisfile)
        dt=datetime.fromtimestamp(st.st_ctime)
        dt_fmt=dt.strftime("%Y-%m-%d %H:%M:%S")
        if ipflag:
            return True, [fn, self.mount2ip(path), file_extension[1:], self.mount2ip(thisfile), st.st_size, dt_fmt]
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
            #if ctime is not None and os.name == 'nt':
            #    setctime(destfile,ctime)
            logger.debug(f"Successfully copy {srcfile} to {destfile}.")
            return True
        except:
            logger.error(f"{traceback.format_exc()}")
            logger.error(f"Failed to copy {srcfile} to {destfile}!!!")
            self.delete_if_exist(thisfile=destfile) # in case partially copied
            return False

def main(arg=None):
    testfile='//192.168.1.243/music/findfriend.mp3'
    mountname=DiskAccess().ip2mount(testfile)
    status, rst=DiskAccess().file_info(thisfile=mountname, ipflag=True)
    if not status:
        logger.error(f"Failed to get file information for {testfile}!!!")
        return False
    logger.info(f"File {testfile} with info {rst}")
    testdir='//192.168.1.243/music'
    mountname=DiskAccess().ip2mount(testdir)
    dirs, files=DiskAccess().get_dir_file_list_in_folder(thisdir=mountname, ipflag=True)
    mystr='\n'.join(dirs)
    logger.info(f"Under {testdir} there exist {len(dirs)} sub folders: {mystr}")
    mystr='\n'.join(files)
    logger.info(f"Under {testdir} there exist {len(files)} files: {mystr}")
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