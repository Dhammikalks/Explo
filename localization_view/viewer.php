<?php
//seting header to json
//header('Content-Type: aplication/json');
header("Access-Control-Allow-Origin: *");
if(isset($_POST['new']))
{
    $n = $_POST['new'];
    if($n) // asking for new data
	{
  //database
	define("DB_HOST",'localhost');
	define('DB_USERNAME','root');
	define('DB_PASSWORD','DUKS1992');
	define('DB_NAME','ROBOT');

	//get connection
	$conn =new mysqli(DB_HOST,DB_USERNAME, DB_PASSWORD,DB_NAME);

	if(!$conn){
		die("Connection failed".$conn->error);
          }
	//echo "Connected successfully\n";

	//check the is there a new data is in the database
	$query = sprintf("SELECT * FROM Data_ref WHERE is_New = '1' LIMIT 1");

	$result = mysqli_fetch_array($conn->query($query));
	//get the new data
	if($result){
	  	$query_data = sprintf("SELECT * FROM SLAM WHERE No = $result[0]");
	  	$result_data = mysqli_fetch_array($conn->query($query_data));

          //data_con
	  		$data_con = array();

	  	// scan data.............................................
	  	$scan_data = array_map('intval',  explode(',',trim($result_data[1],'[]')));
	  	//print join(',', $scan_data);
	  	//$data_con[] = $scan_data;

	  	//position...............................................
	  	$position = array_map('floatval',explode(',',trim($result_data[2],'[]')));
          //print join(',',$position);
	  		//$data_con[] = $position;

          //partical_list..........................................
	  		$partical = explode('), (',trim($result_data[3],'[()]'));
	  	$partical_list = array();
          foreach($partical as $data)
					{
          	$partical_list[] = array_map('floatval',explode(',',$data));
	 	 	}
	  	//print json_encode($partical_list);
	  	//$data_con[] = $partical_list;

	  	//errors.................................................
	  	$errors = array_map('floatval',explode(',',trim($result_data[4],'()')));
	  	//print join(',',$errors);
    	//$data_con[] = $errors;
          //cylinders..............................................
	  		$cylinders = explode('], [',trim($result_data[5],'[[]]'));
	  	$cylinder_list = array();
          foreach($cylinders as $data)
					{
          	$cylinder_list[] = array_map('floatval',explode(',',$data));
	 	 	}
          //print json_encode($cylinder_list);
          //$data_con[] = $cylinder_list;
          //elipse.................................................
          $elipse = explode('), (',trim($result_data[6],'[()]'));
	  		$elipse_list = array();
          foreach($elipse as $data)
					{
          	$elipse_list[] = array_map('floatval',explode(',',$data));
	 			}
          //.......................................................
	  		//$data_con[] = $elipse_list;
	  	#print json_encode();
          //................creating json object...................
					$data_con = array('scan_data'=>$scan_data,
														'position'=>$position,
														'partical_list'=>$partical_list,
														'errors'=>$errors,
														'cylinder_list'=>$cylinder_list,
														'elipse_list'=>$elipse_list
													);
		//.......................................................
	  //if(file_exists('results.json')) unlink('results.json');

    //$fp = fopen('results.json', 'w');
	  //fwrite($fp, json_encode(array("data"=>$data_con)));
    // fclose($fp);
		$data= json_encode(array("data"=>$data_con));
		echo $data;

	  $quary2 = sprintf("UPDATE Data_ref SET is_New = '0' WHERE No = $result[0]");
	  $conn->query($quary2);

    //.......................................................set_index
    $index = $result[0];
    $result =  shell_exec('./index.py 2>&1  '.escapeshellarg($index));
    //.......................................................
	       }
else	{
	sleep(0.5);
	}
}
}

?>
