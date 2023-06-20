""" File name: filesync.py
Utils for File Sync, like copy file from source to target.
"""
from logzero import logger
from confops import ConfigOps
from filesqlite import FileInfoSqlite
class FileSync(object):
    """ Copy files
    """
    def __init__(self,
            config_file = None,
            waittime = None,
            src_tbl = 'disk1',
            src_prefix = r'\\wdmycloud',
            tgt_tbl = 'disk2',
            tgt_prefix = r'\\192.168.86.104\Public',
            table_structure = None,
            table_header = None,
    ):
        self.config_file = config_file
        self.waittime = waittime
        self.src_tbl = src_tbl
        self.src_prefix = src_prefix
        self.tgt_tbl = tgt_tbl
        self.tgt_prefix = tgt_prefix
        self.table_structure = table_structure
        self.table_header = table_header
        self.dirlist = None

    def folder_sync(self, db = None):
        """ Sync folder and all sub-folders using config file
        """
        co = ConfigOps(config_file=self.config_file)
        rel_dir = co.get_first_folder()
        while rel_dir is not None:
            newfilecnt, updatedfilecnt, dirlist = self.one_folder_sync(db=db, rel_dir=rel_dir)
            co.update_config_with_dirlist(newfilecnt=newfilecnt, updatedfilecnt=updatedfilecnt, dirlist=dirlist)
            co = ConfigOps(config_file=self.config_file)
            rel_dir = co.get_first_folder()

    def one_folder_sync(self, db = None, rel_dir = None):
        """ Sync one filder from config file
        """
        fis = FileInfoSqlite(db=db)
        fis.table_check(table=self.src_tbl, drop_if_exist=True,
            table_structure=self.table_structure)
        logger.debug(f"SQLite: prepared table {self.tgt_tbl}.")
        fis.table_check(table=self.tgt_tbl, drop_if_exist=True,
            table_structure=self.table_structure)
        logger.debug(f"SQLite: prepared table {self.tgt_tbl}.")

        src_dir = f"{self.src_prefix}{rel_dir}"
        datalist = self.dir_info(filedir=src_dir, store_src_dirlist = True)
        logger.debug(f"Got dir info of {src_dir} into list.")
        fis.import_data(table=self.src_tbl, datalist=datalist, header=self.table_header)
        logger.debug(f"SQLite: {self.src_tbl} imported")
        fis.compute_relname(table=self.src_tbl, prefix=self.src_prefix)
        logger.debug(f"SQLite: {self.src_tbl} rel name")
        
        tgt_dir = f"{self.tgt_prefix}{rel_dir}"
        if not os.path.isdir(tgt_dir):
            rst = self.target_create_folder(new_folder=tgt_dir)
            if not rst:
                logger.error(f"You stop creating target folder!!!")
                exit(1)
        datalist = self.dir_info(filedir=tgt_dir)
        logger.debug(f"Got dir info of {tgt_dir} into list.")
        fis.import_data(table=self.tgt_tbl, datalist=datalist, header=self.table_header)
        logger.debug(f"SQLite: {self.tgt_tbl} imported")
        fis.compute_relname(table=self.tgt_tbl, prefix=self.tgt_prefix)
        logger.debug(f"SQLite: {self.tgt_tbl} rel name")

        fl=fis.compute_newfiles(table=self.src_tbl, tablebase=self.tgt_tbl)
        str_fl = '\n'.join(fl)
        logger.debug(f"New files: {str_fl}")
        self.copy_file_in_list(filelist=fl, source_prefix=self.src_prefix, target_prefix=self.tgt_prefix)
        logger.debug(f"Synced new files.")
        newfilecnt = len(fl)

        fl=fis.compute_updatedfiles(table=self.src_tbl, tablebase=self.tgt_tbl)
        str_fl = '\n'.join(fl)
        logger.debug(f"Updated files: {str_fl}")
        self.copy_file_in_list(filelist=fl, source_prefix=self.src_prefix, target_prefix=self.tgt_prefix)
        logger.debug(f"Synced updated files.")
        updatedfilecnt = len(fl)

        return newfilecnt, updatedfilecnt, self.dirlist

    def promptcall(self):
        """ prompt with timeout
        """
        if self.waittime is None:
            return True
        try:
            y_or_n = inputimeout(prompt=f'[Create folder(Y, N)] (default Y wait for {self.waittime} seconds) >> ', timeout=self.waittime)
        except TimeoutOccurred:
            y_or_n = 'Y'
        if y_or_n == 'Y':
            return True
        return False

    def dir_info(self, filedir = None, store_src_dirlist = False):
        """ Get directory file information
        """
        dirlist, filelist = FileInfo().get_dir_file_list_in_folder(thisdir=filedir)
        if store_src_dirlist:
            self.dirlist = [x.replace(self.src_prefix, '') for x in dirlist]
        datalist=[]
        for f in filelist:
            status, f_info = FileInfo().file_info(thisfile=f)
            if not status:
                logger.error(f"Failed to get file info for '{f}'")
                exit()
            data = tuple(f_info) # use tuple considering `sqlite3.executemany` format
            datalist.append(data)
        return datalist

    def copy_file_in_list(self, filelist = None, source_prefix = None, target_prefix = None):
        """ Add prefix to each file and copy
        """
        for f in filelist:
            logger.debug(f"Sync {f}...")
            src = f"{source_prefix}{f}"
            tgt = f"{target_prefix}{f}"
            shutil.copy2(src, tgt)

    def target_create_folder(self, new_folder=None):
        """ Create target folder
        """
        if not self.promptcall():
            logger.debug(f"Do not create folder '{new_folder}'!!!")
            return False
        logger.debug(f"Start creating folder '{new_folder}'...")
        os.makedirs(new_folder, exist_ok=True)
        return True
