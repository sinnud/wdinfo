<html>
<html>
<head>
<style>
table {
  width: 100%;
  border-collapse: collapse;
}

table, td, th {
  border: 1px solid black;
  padding: 5px;
}

th {text-align: left;}
</style>
</head>
<body>
<?php
require 'common.php'; // for test_input function
// Get MySQL connection argument
require '/home/user/.php/mysql_conf.php';
  
   # default
	$php_d = "wdsearch_default.php";
	# refresh
	$php_r = "wdsearch_new.php";

	if (file_exists($php_r) ){
	require $php_r;
	} elseif (file_exists($php_d) ){
	require $php_d;
	} else {
	echo "<script>alert('No WD directory list file!')</script>";
	}
if($_SERVER['REQUEST_METHOD'] == 'POST')
{
    if ( isset($_POST['search']) )
    {
        $folder = test_input($_POST["dir"]);
        if(empty($folder)) {
            print_r("Variable 'folder' is empty.<br>Go back!");
            return;
        }
        $tbl = $MySQLtableWD[$folder];
        $searchstr=test_input($_POST["name"]);
        if(empty($searchstr)) {
            print_r("You can NOT search nothing!!!<br>Go back!");
            return;
        }
        // Connect to MySQL
        $con = mysqli_connect($MySQLHost,$MySQLUser,$MySQLPassword,'wdinfo');
        if (!$con) {
            die('Could not connect: ' . mysqli_error($con));
        }
        // run SQL query
        $sql="SELECT * FROM ".$tbl." where fullpath like '%".$searchstr."%' limit 5";
        echo "Debug query:<br>".$sql."<br><br><br>";
        $result = mysqli_query($con,$sql);
        // collect output of SQL query
        $sample_data="<table>
        <tr>
        <th>index</th>
        <th>filename</th>
        <th>folder</th>
        <th>file_type</th>
        <th>fullpath</th>
        <th>filesize</th>
        <th>createtime</th>
        </tr>";
        while($row = mysqli_fetch_array($result)) 
        {
            //
            $sample_data .= "<tr>";
            $sample_data .= "<td>" . $row[0] . "</td>";
            $sample_data .= "<td>" . $row['filename'] . "</td>";
            $sample_data .= "<td>" . $row['folder'] . "</td>";
            $sample_data .= "<td>" . $row['file_type'] . "</td>";
            $sample_data .= "<td>" . $row['fullpath'] . "</td>";
            $sample_data .= "<td>" . $row['filesize'] . "</td>";
            $sample_data .= "<td>" . $row['createtime'] . "</td>";
            $sample_data .= "</tr>";
        }
        $sample_data .= "</table>";
        // close MySQL
        mysqli_close($con);
        // Output "no suggestion" if no sample data was found or output correct values
        echo $sample_data === "" ? "no suggestion" : $sample_data;

    }
}
?>
</body>
</html>