<!--
included by index.php
In this module, you can:

1. refresh root folder list, or go back to default
2. drop table in MySQL according to root folder
3. analyze root folder to generate MySQL table of folder structure
-->
<h1>WD net drive 192.168.1.243/241 info: Re-Generate</h1>
  The directory structure information is stored in MySQL tables.<br>
  You can refresh table content by: drop the table, and analyze to generate the table.<br><br>
<form action="./php_utils/wddir_main.php" method="post">
<?php
# default
$php_d = "php_utils/wddir_default.php";
# refresh
$php_r = "php_utils/wddir_new.php";

if (file_exists($php_r) ){
require $php_r;
} elseif (file_exists($php_d) ){
require $php_d;
} else {
echo "<script>alert('No WD directory list file!')</script>";
}
?>
  <input type="submit" name="Refresh" value="Refresh">
  <input type="submit" name="GoDefault" value="GoDefault"><br><br>
  You can refresh the above list from the existence of root directory. <br>
  Also you can change back to the default folder list.
  <br><br>
  <input type="submit" name="droptable" value="droptable"
	 onclick="return confirm('Are you sure you want to delete?')">
  <input type="submit" name="Analyze" value="Analyze"><br><br>
</form>
