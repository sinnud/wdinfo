<!--
included by index.php
In this module, you can:

1. search file from MySQL table instead of File Explorer
-->
<h1>WD net drive 192.168.1.243: search</h1>
Type phase you like to search, choose folder (table) you like to search from:<br><br>
<form action="php_utils/wdsearch_show.php" method="post">
Name: <input type="text" name="name">
from: <select name="dir">
  <option value="">Select a folder:</option>
  <!-- use dynamic setting instead
  <option value="1">photos</option>
  <option value="2">data</option>
  <option value="3">music</option>
  <option value="4">movie</option>
  -->
  <?php
  
   # default
	$php_d = "php_utils/wdsearch_default.php";
	# refresh
	$php_r = "php_utils/wdsearch_new.php";

	if (file_exists($php_r) ){
	require $php_r;
	} elseif (file_exists($php_d) ){
	require $php_d;
	} else {
	echo "<script>alert('No WD directory list file!')</script>";
	}
	for($i = 0; $i < count($MySQLtableWD); $i++ ){
		echo '<option value="' . $i . '">' . $MySQLtableWD[$i] . '</option>';
	}
	?>
  </select>
<input type="submit" name="search" value="Search">
</form>
