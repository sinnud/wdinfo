<html>
<body>

<?php
require 'common.php'; // for test_input function

if($_SERVER['REQUEST_METHOD'] == 'POST')
{
  {
    $file = test_input($_POST["picname"]);
    if(empty($file)) {
        print_r("Variable 'picture_name' is empty.<br>Go back!");
        return;
    }
    if (file_exists($file) ){
      print_r('Picture <br><img src = "' . $file .'">');
  	} else {
  	   echo "<script>alert('No WD directory file!')</script>";
  	}

  }

}

?>
</body>
</html>
