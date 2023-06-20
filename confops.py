""" File name: confops.py
Utils for Configuration file.
"""
import os
from logzero import logger
from datetime import datetime
class ConfigOps(object):
    """ Read from config file
    Get first folder we need to handle
    Update config file

    config file line start with '#' as comment and historical log with timestamp
    """
    def __init__(self,
            config_file = None,
    ):
        self.config_file = config_file
        if os.path.isfile(self.config_file):
            with open(self.config_file, 'r', encoding="utf-8") as f:
                self.config_lines = f.readlines()
        else:
            self.config_lines = []
        self.current_idx = None
    
    def init_from_dirlist(self, dirlist=None):
        """ initialize with dirlist
        """
        self.config_lines = dirlist
        self.current_idx = 1
        return dirlist[0]
    
    def get_first_folder(self):
        """ Get first non-comment line and record idx
        """
        folder = None
        for idx, line in enumerate(self.config_lines, start = 1):
            line = line.strip()
            if line.startswith('#'):
                continue
            folder = line
            self.current_idx = idx
            break
        if folder is None:
            logger.debug("Finished all folders in config file!!!")
        return folder
    
    def update_config_in_memory(self,
            comment = None,
            dirlist = None,
    ):
        """ Using dirlist to update config file in memory
        """
        new_lines = []
        for idx, line in enumerate(self.config_lines, start = 1):
            line = line.strip()
            if idx == self.current_idx:
                timestampstr = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                str_elm = f"# {line} -- folder finished {timestampstr}"
                new_lines.append(str_elm)
                if comment is None:
                    continue
                new_lines.append(comment)
            else:
                new_lines.append(line)
        if dirlist is not None:
            new_lines.extend(sorted(dirlist))
        self.config_lines = new_lines
    
    def update_to_config_file(self):
        """ update to config file
        """
        with open(self.config_file, 'w', encoding="utf-8") as f:
            f.write("\n".join(self.config_lines))
            f.write("\n")
    
    def update_config_with_dirlist(self,
            newfilecnt = None,
            updatedfilecnt = None,
            dirlist = None,
    ):
        """ Using dirlist to update config file
        """
        comment = f"# ---- synced {newfilecnt} new files and {updatedfilecnt} updated files"
        self.update_config_in_memory(
            comment = comment,
            dirlist = dirlist,
        )
        self.update_to_config_file()
