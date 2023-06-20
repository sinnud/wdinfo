""" test code: test_fs.py
Test FileSqlite class
Like to have updatedatetime as additional
"""
from logzero import logger
import traceback
from fileinfo import FileInfo
from filesqlite import FileInfoSqlite

def main():
    logger.info("Start working...")
    db = '/home/family/wdinfo.sqlite/wddata.db'
    table = 'disk1'
    tbl_str_list = ['NAME', 'PATH', 'FILESIZE', 'CHANGETIME', 'REL_NAME']
    table_structure=' TEXT, '.join(tbl_str_list)
    table_structure = f"{table_structure} TEXT"
    # table_structure = f"{table_structure}, updateddatetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    table_structure = f"{table_structure}, updateddatetime TIMESTAMP DEFAULT (datetime('now','localtime'))"
    table_header=', '.join(tbl_str_list[:-1])

    wd_dir = "/mnt/music/hulusi"
    prefix = "/mnt"
    fis = FileInfoSqlite(db = db)
    try:
        fis.table_check(table=table,
                   drop_if_exist=True,
                   table_structure=table_structure,
                   )
        dirlist, filelist = FileInfo().get_dir_file_list_in_folder(thisdir=wd_dir)
        datalist=[]
        for f in filelist:
            status, f_info = FileInfo().file_info(thisfile=f)
            if not status:
                logger.error(f"Failed to get file info for '{f}'")
                exit()
            data = tuple(f_info) # use tuple considering `sqlite3.executemany` format
            datalist.append(data)
        logger.debug(f"Got dir info of {wd_dir} into list.")
        fis.import_data(table=table, datalist=datalist, header=table_header)
        logger.debug(f"SQLite: {table} imported")
        fis.compute_relname(table=table, prefix=prefix)
        logger.debug(f"SQLite: {table} rel name")
    
    except:
        logger.error(f"{traceback.format_exc()}")

def main_updated_recent():
    from wdinfo import WdInfo
    wi = WdInfo(db = '/home/family/wdinfo.sqlite/wddata.db')
    rst = wi.updated_recent(table='disk1')
    logger.info(rst)

def main_update_test():
    from wdinfo import WdInfo
    wi = WdInfo(db = '/home/family/wdinfo.sqlite/wddata.db')
    rst = wi.sqlite_update(table = 'wd_movie',
                           filedir = '/mnt/movie',
                           prefix = '/mnt'
                           )

if __name__ == '__main__':
    #main()
    #main_updated_recent()
    main_update_test()
