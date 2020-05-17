#!/usr/bin/env python3
'''
Default under /mnt, we have sub-folders photos, data, music, and movie.
This code will delete ../php_utils/wddir_new.php file for going to default
'''
import os
import sys
newfile="../php_utils/wddir_new.php"
if os.path.exists(newfile):
    os.remove(newfile)
print(f"Done! Please go back to the previous page...")
