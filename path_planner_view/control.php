<?php //logtime.php

if(isset($_POST['X_post']))
{
    $x = $_POST['X_post'];
    $y = $_POST['Y_post'];

   $pos = [$x,$y];

  $result =  shell_exec('./goal.py 2>&1  '.escapeshellarg(json_encode($pos)));
   // Do whatever you want with the $uid
echo $result;
}
?>

