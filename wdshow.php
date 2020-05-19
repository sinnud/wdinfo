<!--
included by index.php
In this module, you can:

1. dynamically select folder and subfolder to get fullpath of one file
2.
3.
-->
<h1>WD net drive 192.168.1.243: dir and file</h1>

<!-- <form>
<select name="root" onchange="showRoot(this.value)">
  <option value="">Select a root:</option> -->
  <!-- use dynamic setting instead
  <option value="1">photos</option>
  <option value="2">data</option>
  <option value="3">music</option>
  <option value="4">movie</option>
  -->
  <?php
  /*
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
  */
	?>

  <!-- </select>
</form>
<br>

<p>Sample data: <span id="txtHint"></span></p> -->
<p><b>Start typing a name in the input field below (start with '/'):</b></p>
<form action="">
  <label for="fname">/mnt</label>
  <input type="text" id="fname" name="fname" onkeyup="showRoot(this.value)">
  <!-- <input type="text" id="fname" name="fname" onkeypress="showRoot(this.value)"> -->
</form>
<p>Suggestions: <span id="txtHint"></span></p>
</body>
</html>
