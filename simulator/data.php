<?php //logtime.php
header("Access-Control-Allow-Origin: *");

if(isset($_POST['Obstacle']))
{
    $env = $_POST['Obstacle'];
    $robot = $_POST['RobotPostion'];
    $paths = $_POST['Path'];

    define("DB_HOST",'localhost');
    define('DB_USERNAME','root');
    define('DB_PASSWORD','DUKS1992');
    define('DB_NAME','ROBOT');

    $conn =new mysqli(DB_HOST,DB_USERNAME, DB_PASSWORD,DB_NAME);

    if(!$conn){
die("Connection failed".$conn->error);
    }
    $query = "INSERT INTO Simulator (Env, RobotPos, Paths ) values( '".$env."', '".$robot."', '".$paths."')";
    mysql_query($query) or die(mysql_error());

}
?>
