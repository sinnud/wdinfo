<html>
<body>
<?php
require 'common.php'; // for test_input function
if($_SERVER['REQUEST_METHOD'] == 'POST')
{
  if ( isset($_POST['Refresh']) )
  {
    ?>
    <h1>Refresh WD directory list...</h1><br><br>
    <?php
    $message = exec("../scripts/wddir_refresh.py 2>&1");
    print_r($message);
  } elseif ( isset($_POST['GoDefault']) )
  {
    ?>
    <h1>Remove the new WD directory list...</h1><br><br>
    <?php
    $message = exec("../scripts/wddir_remove_new.py 2>&1");
    print_r($message);
  } elseif ( isset($_POST['droptable']) )
  {
    $folder = test_input($_POST["folder"]);
    if(empty($folder)) {
       print_r("Variable 'folder' is empty.<br>Go back!");
       return;
    }
    ?>
    <h1>Drop MySQL table wdinfo.<?php echo $folder; ?> ...</h1><br><br>
    <?php 
    $message = exec("../scripts/wddir_drop.py $folder 2>&1");
    #$message="Hello World!";
    print_r($message);

  } elseif ( isset($_POST['Analyze']) )
  {
    $folder = test_input($_POST["folder"]);
    if(empty($folder)) {
       print_r("Variable 'folder' is empty.<br>Go back!");
       return;
    }
    ?>
    <h1>Analize /mnt/<?php echo $folder; ?> into MySQL table wdinfo.<?php echo $folder; ?> ...</h1><br><br>
    <?php 
    $message = exec("../scripts/wddir_analyze.py $folder 2>&1");
    #$message="Hello World!";
    print_r($message);

  }
  
}

/*
function test_input($data) {
  $data = trim($data);
  $data = stripslashes($data);
  $data = htmlspecialchars($data);
  return $data;
}
*/
?>
</body>
</html>