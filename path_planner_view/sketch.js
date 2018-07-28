//scanner range
var scanner_range = 2200.0;
//scanner canvas_extends
scanner_canvas_extents = [600,600];
canvas_extents = [600,600];

world_extents = [2000.0, 2000.0];
var trajectroy = [];
//temp
var draw_scan;
var draw_cylinders;
var draw_partical;
//.............................................................setup
 function setup() {
  createCanvas(scanner_canvas_extents[0],scanner_canvas_extents[1]);
  fill('black');
  rect(0,0,596,600,20);
  //getData();
 }
//.............................................................draw
function draw(){
  getData();
}
 //............................................................get_Data
function getData(){
  $.ajax({
                   type: "POST",
                   url: 'http:/localhost/planner.php',
                   data: { new :1},
                   success: function(data)
                   {
                     print(data);
                     var obj = JSON.parse(data);
                     //print(obj.data);
                     draw_Data(obj);
                     //loadJSON(data, draw_Data);
                    }

               });
  //loadJSON("results.json", draw_Data);
}
//.............................................................draw
function draw_Data(data) {
  //..................................................env
  var env = data.data.visited_nodes;
  if(env){
    var draw_env = new env_draw(env,canvas_extents,world_extents);
    draw_env.draw();
  }
  //..................................................potential
  //var env = data.data.env_nodes;
  //var draw_potential = new potential_draw(env,canvas_extents,world_extents);
  //draw_potential.draw();

  //..................................................visited
  //var visited = data.data.visited_nodes;
  //var draw_visited = new visited_draw(visited,canvas_extents,world_extents);
  //draw_visited.draw();

  //.................................................scan_data
  var path_data = data.data.path_data;
  //print(scan_data);
  var x_base = data.data.X_base;
  var y_base = data.data.y_base;

  draw_path = new path_draw(path_data,x_base,y_base);
  draw_path.draw();

  //.................................................cylinders
  var cylinders = data.data.obstacle;
  if(cylinders){
      //print(cylinders);
      draw_cylinders = new cylinder_draw(cylinders,canvas_extents,world_extents);
      draw_cylinders.draw();
               }
  //..................................................position
  var postion = data.data.position;
  var position = new position_draw(postion,canvas_extents,world_extents);
  position.draw();
  //..................................................Goal
  var g = data.data.goal;
  var g1 =split(g,'(');
  var g2 =split(g1[1],')');
  var goal =split(g2[0],',');

  var Goal = new goal_draw(goal,canvas_extents,world_extents);
  Goal.draw();
}
//.............................................................draw_goal
function goal_draw(goal,canvas_extents,world_extents){
  //this.postion = postion;
  this.canvas = canvas_extents;
  this.world = world_extents;
  this.color = [220, 30, 150];
  this.radius = 10;
  this.draw = function(){
                ellipse(goal[0]*3,goal[1]*3,this.radius,this.radius);
                }
};
//.............................................................draw_potential
function potential_draw(potential_array,canvas_extents,world_extents){
  //this.postion = postion;
  this.canvas = canvas_extents;
  this.world = world_extents;

  var v = split(potential_array,'[[');
  var v1 = split(v[1],']]');
  this.env =split(v1[0],'], [');
  this.radius = 4;
  this.array_size = [200,200];


  this.draw = function()
                {
                  for(var i = 0; i < this.array_size[0];i++){
                    var envs = split(this.env[i],',');
                    for(var j = 0; j < this.array_size[1];j++){
                      if(envs[j]>1){
                        fill([0,0,envs[j]]);
                        noStroke();
                        ellipse(i*3,canvas_extents[1]-j*3,this.radius,this.radius);
                          }
                    }
                  }
                }
};
//.............................................................draw_env
function env_draw(env_array,canvas_extents,world_extents){
  //this.postion = postion;
  this.canvas = canvas_extents;
  this.world = world_extents;

   var v = split(env_array,'[[[');
   var v1 = split(v[1],']]]');
   this.env =split(v1[0],']], [[');
   this.radius = 4;
   this.array_size = [200,200];

   this.draw = function()
                 {
                   for(var i = 0; i < this.array_size[0];i++){
                     var env_a = split(this.env[i],'], [');
                     for(var j = 0; j < this.array_size[1];j++){
                       var e = split(env_a[j],',');

                       if(e[1]>1)
                          {
                         fill([0,0,e[1]]);
                         noStroke();
                         ellipse(i*3,canvas_extents[1]-j*3,this.radius,this.radius);
                         }

                       if(e[0]>1)
                          {
                          fill([0,e[0],0]);
                          noStroke();
                          ellipse(i*3,canvas_extents[1]-j*3,this.radius,this.radius);
                           }

                     }
                   }
                 }


};
//.............................................................draw_position
function visited_draw(visited_array,canvas_extents,world_extents){
  //this.postion = postion;
  this.canvas = canvas_extents;
  this.world = world_extents;

  var v = split(visited_array,'[[');
  var v1 = split(v[1],']]');
  this.visited =split(v1[0],'], [');
  this.radius = 4;
  this.array_size = [200,200];


  this.draw = function()
                {
                  for(var i = 0; i < this.array_size[0];i++){
                    var visit = split(this.visited[i],',');
                    for(var j = 0; j < this.array_size[1];j++){
                      if(visit[j]>1){
                        fill([0,visit[j],0]);
                        noStroke();
                        ellipse(i*3,canvas_extents[1]-j*3,this.radius,this.radius);
                          }
                    }
                  }
                }
};
//.............................................................draw_position
function position_draw(postion,canvas_extents,world_extents){
  //this.postion = postion;
  this.canvas = canvas_extents;
  this.world = world_extents;
  this.color = [220, 220, 197];
  this.radius = 10;
  this.draw = function(){

                var factor = this.canvas[0] / this.world[0];
                fill(this.color);
                ellipse(postion[0]*factor, postion[1]*factor,this.radius,this.radius);
                }
};
//.............................................................draw_cylinders
function cylinder_draw(cylinders,canvas_extents,world_extents){
  this.cylinder_list = cylinders;
  this.canvas = canvas_extents;
  this.world = world_extents;

  this.draw = function(){
                var points = [];
                for(var i = 0 ; i < this.cylinder_list.length; i++){
                   points[i] = [int(this.cylinder_list[i][0]*0.3),int(this.cylinder_list[i][1]*0.3)];
                }
                var factor = this.canvas[0] / this.world[0];
                print(points);
                var point = new Points(points, this.world,[220, 35, 197],factor);
                point.draw();
                }
  this.to_world_canvas = function(world_point,canvas_extents,world_extents){
    var x = int((world_point[0] / world_extents[0]) * canvas_extents[0]);
    var y = int(canvas_extents[1] - 1 - (world_point[1] / world_extents[1]) * canvas_extents[1]);
   return [x, y];
  }
};
//..............................................................draw_points
function Points(point,world_canvas,color,factor){
  this.point_list = point;
  this. world_canvas = world_canvas;
  this.color = color;
  this.factor = factor;
  this.radius =10;
  this.draw = function(){
        for(var i = 0; i < this.point_list.length;i++)  {
            fill(this.color);
            ellipse(this.point_list[i][0], this.point_list[i][1],this.radius,this.radius);
          }
          }
  };
//.............................................................draw path
function path_draw(path_data,x_base,y_base){
  this.path = path_data
  this.draw=function(){
                  stroke('red');
                  strokeWeight(4);
                  for(var i = 1 ; i < this.path.length; i++){
                        strokeWeight(4);
                        line(this.path[i-1][0]*3, canvas_extents[1]-this.path[i-1][1]*3,this.path[i][0]*3, canvas_extents[1]-this.path[i][1]*3);
                                                          }
                  strokeWeight(1);
                  stroke(0);
                    }
};
//.............................................................mose actions
function mousePressed() {
  var x = mouseX;
  var y = mouseY;
  var new_goal = [x,y];

    $.ajax({
                     type: "POST",
                     url: 'http:/localhost/control.php',
                     data: { X_post :x,Y_post : y},
                     success: function(data)
                     {
                      print("sucess!");
                     }

                 });
}
//...............................................................
