<?php //logtime.php
ob_start('ob_gzhandler');
header("Access-Control-Allow-Origin: *");
if (isset($_REQUEST['ajaxcallid']))
{
    if($_REQUEST['ajaxcallid']==2)
    {
      $phparr = $_REQUEST['jsarr'];
      $tempData = html_entity_decode(stripslashes($phparr));
      $dphparr = json_decode($tempData);
      $env = $dphparr->Obstacle;
     $robot = $dphparr->RobotPostion;
      $path = $dphparr->Path;
      $data = [$robot,$path];

      $result =  shell_exec('./index.py 2>&1 '.escapeshellarg(json_encode($data)));
      #$env_1 = array_slice($env, 150, 50);
      for ($x = 0; $x < sizeof($env)/50; $x++) {
          $env_input  = array_slice($env,  $x*50 , 50);
          $result =  shell_exec('./index.py 2>&1 '.escapeshellarg(json_encode($env_input)));
        }
##$result =  shell_exec('./index.py 2>&1 '.escapeshellarg(json_encode($env_1)));
$result =  shell_exec('./index.py 2>&1 ');
echo json_encode($result);
    }
}
?>
