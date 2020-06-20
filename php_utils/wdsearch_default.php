<?php
// PHP array according to wddir_default.php
// will be included by PHP code
// When ../scripts/wddir_refresh.py create wddir_new.php,
// it will also create wdsearch_new.php accordingly 
global $MySQLtableWD;
$MySQLtableWD = array("photos", "data", "music", "movie", "public");
?>