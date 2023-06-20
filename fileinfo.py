""" File name: fileinfo.py
Utils for File Information, like file name, path, size, create datetime.
"""
import os
import glob
from datetime import datetime
class FileInfo(object):
    """ Create file information
    """
    def get_dir_file_list_in_folder(self, thisdir=None):
        """ Just list sub-folders and files at current folder
        Do not work recursively
        """
        dirlist=list()
        filelist=list()
        checklist=glob.glob(f"{thisdir}/*")
        for elm in checklist:
            if os.path.isdir(elm):
                dirlist.append(elm)
            else:
                filelist.append(elm)
        return dirlist, filelist

    def file_info(self, thisfile=None):
        """ Get file size and timestamp
        """
        if not os.path.exists(thisfile):
            logger.error(f"{thisfile} does NOT exist!!!")
            return False, None
        if os.path.isdir(thisfile):
            logger.error(f"{thisfile} is directory, NOT file!!!")
            return False, None
        
        path, fn=os.path.split(thisfile)
        st=os.stat(thisfile)
        dt=datetime.fromtimestamp(st.st_ctime)
        dt_fmt=dt.strftime("%Y-%m-%d %H:%M:%S")
        return True, [fn, path, str(st.st_size), dt_fmt]
