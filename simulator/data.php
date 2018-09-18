<?php //logtime.php
header("Access-Control-Allow-Origin: *");

if(isset($_POST['Obstacle']))
{
    $env = $_POST['Obstacle'];
    $robot = $_POST['RobotPostion'];
    $paths = $_POST['Path'];

$data = [$env,$robot,$paths];
$result =  shell_exec('./calculate_vectors.py 2>&1  '.escapeshellarg(json_encode($data)));
}
?>
