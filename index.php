<!DOCTYPE html>
<html>
<body>

<h1>WD net drive 192.168.1.243 info</h1>
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
<!--form action="./php_utils/wddir_refresh.php" method="post"-->
  <input type="submit" name="Refresh" value="Refresh">
  <input type="submit" name="GoDefault" value="GoDefault"><br><br>
  <input type="submit" name="droptable" value="droptable"
	 onclick="return confirm('Are you sure you want to delete?')">
  <input type="submit" name="Analyze" value="Analyze">
</form>

</body>
</html> 
