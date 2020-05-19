<!DOCTYPE html>
<html>
  <head>
    <script type="text/javascript">
    <!-- // let browser without JS support ignore code
    <?php // use this replace real function code later
    // include 'wdshow.js';
    ?>
function showRoot(str) {
  if (str == "") {
    document.getElementById("txtHint").innerHTML = "";
    return;
  } else {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        document.getElementById("txtHint").innerHTML = this.responseText;
      }
    };
    xmlhttp.open("GET","php_utils/wdshow_Root.php?q="+str,true);
    xmlhttp.send();
  }
}

    -->
    </script>
  </head>
<body>
 <!-- folder structure in MySQL: regenerate -->
 <?php include 'wddir.php';?>
 <hr>
 <?php include 'wdsearch.php';?>
 <hr>
 <?php
 //include 'wdpicture.php';
// hold for future
 //include 'wdshow.php';
?>
</body>
</html>
