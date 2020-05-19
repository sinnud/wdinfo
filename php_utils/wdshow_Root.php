<?php
// get the q parameter from URL
$q = $_REQUEST["q"];

if ($q == "/"){
  echo "Special '/' symbol typed!!!";
  return;
}
if ($q == chr(8)){
  echo "Special 'backspace' symbol typed!!!";
  return;
}
// Get MySQL connection argument
require '/home/user/.php/mysql_conf.php';
// Connect to MySQL
$con = mysqli_connect($MySQLHost,$MySQLUser,$MySQLPassword,'wdinfo');
if (!$con) {
  die('Could not connect: ' . mysqli_error($con));
}
// run SQL query
$sql="select substring_index(fullpath,'/',3) as dir";
$sql .= ", substring_index(substring_index(fullpath,'/',4),'/',-1) as f2sub";
$sql .= ", count(*) from music group by 1, 2";
$result = mysqli_query($con,$sql);
// collect output of SQL query
while($row = mysqli_fetch_array($result))
{
  $a[] = $row[1];
}
// close MySQL
mysqli_close($con);

$hint = "";

// lookup all hints from array if $q is different from ""
if ($q !== "") {
  $q = strtolower($q);
  $len=strlen($q);
  foreach($a as $name) {
    if (stristr($q, substr($name, 0, $len))) {
      if ($hint === "") {
        $hint = $name;
      } else {
        $hint .= ", $name";
      }
    }
  }
}

// Output "no suggestion" if no hint was found or output correct values
echo $hint === "" ? "no suggestion" : $hint;

?>
