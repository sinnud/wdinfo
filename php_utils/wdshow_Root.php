<?php
/*
// get the q parameter from URL
// $q = $_REQUEST["q"]; // https://www.w3schools.com/php/php_ajax_php.asp
$q = intval($_GET['q']);
// Get MySQL connection argument
require '/home/user/.php/mysql_conf.php';
// Connect to MySQL
$con = mysqli_connect($MySQLHost,$MySQLUser,$MySQLPassword,'wdinfo');
if (!$con) {
  die('Could not connect: ' . mysqli_error($con));
}
// run SQL query
$sql="SELECT folder, count(*) FROM ".$q." group by 1 order by 1 limit 5";
$result = mysqli_query($con,$sql);
// collect output of SQL query
$sample_data="";
while($row = mysqli_fetch_array($result)) 
{
  $sample_data .= row[0] . ":" . "row[1]" . "<br>";
}
// close MySQL
mysqli_close($con);
// Output "no suggestion" if no sample data was found or output correct values
// echo $sample_data === "" ? "no suggestion" : $sample_data;
*/
echo "no suggestion";
?>
