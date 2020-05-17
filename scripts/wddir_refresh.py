#!/usr/bin/env python3
'''
Default under /mnt, we have sub-folders photos, data, music, and movie.
This code will refresh the folder list under /mnt
Create ../php_utils/wddir_new.php file for future use
'''
import os
import sys
import glob
# get sub folder list
dirlist=list()
for fi, fn in enumerate(glob.glob(f'/mnt/*'), start=1):
    if os.path.isdir(fn):
        dirlist.append(os.path.basename(fn))
        
# create/rewrite ../php_utils/wddir_new.php file
with open("../php_utils/wddir_new.php", 'w') as f:
    f.write("<b>Choose the folder you like to analysize...</b><br><br>\n")
    for elm in sorted(dirlist):
        f.write(f'<input type="radio" name="folder" value="{elm}">{elm}\n')

# create/rewrite ../php_utils/wdsearch_new.php file
mystr="', '".join(sorted(dirlist))
mystr=f"<?php\nglobal $MySQLtableWD;\n$MySQLtableWD = array('{mystr}');\n?>"
with open("../php_utils/wdsearch_new.php", 'w') as f:
    f.write(mystr)
print(f"Done! Please go back to the previous page...")
