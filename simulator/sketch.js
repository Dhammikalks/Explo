environment_extends = [700,700];
scanner_range = 2200.0;
var obstacle = [];
var path = [];
var env = [];
var robot_postion = [0,0];
colorValue = 0;
var old_mX = 0;
var old_mY = 0;
var oldp_mX = 0;
var oldp_mY = 0;
var value = 0;
var path_done = 0;
var simulation = 0;
var Save_ = 0;
var env_builded = 0;
var env_data =  [];
function setup(){
  createCanvas(environment_extends[0], environment_extends[1]);
    background(0);
}
function draw()
{
stroke(255);
if (mouseIsPressed == true ){
  if(robot_postion[0]  ==  0  && robot_postion[1] == 0) {
   if(mouseX != old_mX || mouseY != old_mY)
      {
        obstacle[obstacle.length] = [mouseX, mouseY];
        //line(mouseX, mouseY, pmouseX, pmouseY);
        old_mX = mouseX;
        old_mY = mouseY;
      }

 }
 else {  // drawpath
   if(!path_done){
   if(oldp_mX == 0 && oldp_mY == 0)
   {
   oldp_mX = robot_postion[0];
   oldp_mY = robot_postion[1];
   path[path.length] = [oldp_mX,oldp_mY];

    }
 if(mouseX != oldp_mX || mouseY != oldp_mY)
      {
        path[path.length] = [mouseX, mouseY]
        //line(mouseX, mouseY, pmouseX, pmouseY);
        stroke(255, 204, 0);
        line(oldp_mX,oldp_mY,mouseX,mouseY);
        oldp_mX = mouseX;
        oldp_mY = mouseY;

      }
    }
      }
}
      fill(255);
      beginShape();
      for(i = 0; i < obstacle.length;i++){
        vertex(obstacle[i][0],obstacle[i][1]);
      }
    endShape();

}

function keyTyped() {

    if ( key == 'n')
      {
      obstacle = [];
      }
    if( key == 'd'){
      env = loadFrames('jpg'); // coustom p5.js lib
      env_builded = 1;
  }
  if (key == 'r' && env_builded == 1 && robot_postion[0]  ==  0  && robot_postion[1] == 0){
    fill('red');
       robot_postion = [mouseX,mouseY];
       ellipse(robot_postion[0],robot_postion[1],20,20);
  }
  if(key == 'p' && path_done == 0){
    //print(path);
    fill('rgb(0,255,0)');
    ellipse(oldp_mX,oldp_mY,20,20);
    path_done = 1;
  }
  if(key == 's' && path_done == 1 && simulation == 0 && (robot_postion[0]  !=  0 || robot_postion[1] != 0) )
  {
    var Data = {
       "Obstacle" : env[0],
       "RobotPostion": robot_postion,
       "Path": path
    };

    alert(Data);
    Data_json= JSON.stringify(Data);

    $.ajax({
              type: "POST",
              url: 'http:/localhost/simulator/data.php',
              dataType: "json",
              data: {ajaxcallid: '2', jsarr: Data_json},
                     success: function(out)
                     {
                      print("sucess!");
                      print(out);
                     }

    });
    simulation = 1;
    Save_ = 1
  }
  if(key == 'v' && simulation == 1)
  {

  }
}
