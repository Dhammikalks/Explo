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
      $data = [$robot,$path,$env];

$result =  shell_exec('python ./calculate_vectors.py 2>&1 '.escapeshellarg(json_encode($data)));
echo json_encode($result);
    }
}
?>
