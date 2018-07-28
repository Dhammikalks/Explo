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
var position;

 function setup() {
  createCanvas(scanner_canvas_extents[0]+600,scanner_canvas_extents[1]);
  fill('black');
  rect(604,0,1196,600,20);
  fill('blue');
  rect(0,0,596,600,20);
  //getData()
}

function draw(){
  //background(255);
  //print("geting Data")
  getData();
 //clear();
 }
 //...................................
 function clear_window()
 {
   fill('black');
   rect(604,0,1196,600,20);
   fill('blue');
   rect(0,0,596,600,20);
 }
 //...................................
function draw_Data(data) {
  //.........clear_window
  clear_window();
  //.................................................scan_data
  var scan_data = data.data.scan_data;
  //print(scan_data);
  draw_scan = new scan_draw(scan_data,scanner_canvas_extents,scanner_range);
  draw_scan.draw();
  //.................................................cylinders
  var cylinders = data.data.cylinder_list;
  if(cylinders){
      var elipse = data.data.elipse_list;
      //print(cylinders);
      draw_cylinders = new cylinder_draw(cylinders,elipse,canvas_extents,world_extents);
      draw_cylinders.draw();
               }
  //..................................................particals
  var particals = data.data.partical_list;
  draw_partical = new partical_draw(particals,canvas_extents,world_extents);
  draw_partical.draw();
  //..................................................position
  var position = data.data.position;
  var stddv = data.data.errors;
  position = new position_draw(position,stddv,canvas_extents,world_extents);
  position.draw();
   //print(position);

}
function getData(){
  $.ajax({
                   type: "POST",
                   url: 'http://localhost/Viewer/viewer.php',
                   data: { new :1},
                   success: function(data)
                   {
                     //print(data);
                     try {
                       var obj = JSON.parse(data);
                       draw_Data(obj);
                     }
                     catch (e) {
                         //print("No new  Data !");
                     }
                     //loadJSON(data, draw_Data);
                    }

               });
  //loadJSON("results.json", draw_Data);
}
//.............................................................draw_position
function position_draw(position,stddv,canvas_extents,world_extents){
     this.position = position;
     this.canvas_extents =  canvas_extents;
     this.world_extents = world_extents;
     this.radius = 10;
     this.stddev = stddv;

 this.draw = function(){
    var pos = [this.to_world_canvas(this.position,this.canvas_extents,this.world_extents), this.position[2]];
    this.path_draw(pos,canvas_extents,world_extents,this.radius);
 }
 this.to_world_canvas = function(world_point,canvas_extents,world_extents){
       var x = int(world_point[0] / world_extents[0] * canvas_extents[0]);
       var y = int(canvas_extents[1] - 1 - world_point[1] / world_extents[1] * canvas_extents[1]);
      return [x, y];
  }
  this.path_draw = function(pos,canvas_extents,world_extents,radius){
       fill('red');
       var factor = this.canvas_extents[0] / this.world_extents[0];
       trajectroy[trajectroy.length] = pos;
       //.................................................................#direction_veriation
       var angle = min(this.stddev[3],PI);
       var point =  this.to_get_elipse_points(pos[0],pos[1],30,30,factor,-angle,angle);
       fill('gray');
       noStroke();
       beginShape();
       //.....................................
       vertex(pos[0][0],pos[0][1]);
        for(var i = 0 ; i < point.length;i++){
            vertex(point[i][0],point[i][1]);
          }
       vertex(pos[0][0],pos[0][1]);
       //.....................................
       endShape();
       //.................................................................#direction line
       stroke(0);
       line(pos[0][0],pos[0][1],pos[0][0] + cos(pos[1]) * 50,
                    pos[0][1] - sin(pos[1]) * 50);
       //.................................................................robot
       fill('red')
       ellipse(pos[0][0],pos[0][1],radius,radius);
       //.................................................................#elipse
       var point_1 = this.to_get_elipse_points( pos[0],this.stddev[0],
                    this.stddev[1]*factor,this.stddev[2]*factor,factor,0,2*PI);
        noFill();
       beginShape();
       for(var i = 0 ; i < point_1.length;i++){
           vertex(point_1[i][0],point_1[i][1]);
         }
       endShape();
       //.................................................................path
       //print(trajectroy[0][0][0]);

      stroke('black');
      //noFill();
      beginShape();
       for(var i = 0 ; i < trajectroy.length;i++){

           vertex(trajectroy[i][0][0],trajectroy[i][0][1]);
           print(trajectroy[i][0][0]);print(trajectroy[i][0][1]);


         }
       endShape();
       stroke(0);
      //.................................................................

  }
  this.to_get_elipse_points = function(center,elipse_point,radius1,radius2,factor,start_angle, end_angle){
    var points = [];
    var ax =radius1*cos(elipse_point);
    var ay = radius1*sin(elipse_point);
    var bx = - radius2*sin(elipse_point);
    var by = radius2*cos(elipse_point);
    var N_full = 40  // Number of points on full ellipse.
    var N = int(ceil((end_angle - start_angle) / (2 * PI) * N_full));
        N = max(N, 1);
    var  increment = (end_angle - start_angle) / N;
    for( var i = 0; i < (N + 1);i++){
            var a = start_angle + i * increment;
            var c = cos(a);
            var s = sin(a);
            var x = c*ax + s*bx + center[0];
            var y = - c*ay - s*by + center[1];
            points[i] = [x,y];
          }
    return points
  }
};
//.............................................................draw_partical
function partical_draw(particals,canvas_extends,world_extents){
  this.partical_list = particals;
  this.canvas_extents = canvas_extents;
  this.world_extents = world_extents;

  this.draw = function(){
    var particals = [];
    for(var i = 0; i < this.partical_list.length;i++)
    {
     particals[i] = [this.to_world_canvas(this.partical_list[i],this.canvas_extents,this.world_extents),this.partical_list[i][2]]
    }
    this.forground_draw(particals,this.canvas_extents,'red','7','8');
  }
  this.to_world_canvas = function(world_point,canvas_extents,world_extents){
    var x = int(world_point[0] / world_extents[0] * canvas_extents[0]);
    var y = int(canvas_extents[1] - 1 - world_point[1] / world_extents[1] * canvas_extents[1]);
   return [x, y];
  }
  this.forground_draw = function(particals,canvas,color,radius,vector){
     fill(color);
    for(var i = 0; i < particals.length;i++){
          ellipse(particals[i][0][0],particals[i][0][1],radius,radius);
          line(particals[i][0][0], particals[i][0][1],
                    particals[i][0][0] + cos(particals[i][1])*vector,
                    particals[i][0][1] - sin(particals[i][1])*vector);
    }
  }
  };
//.............................................................draw_cylinders
function cylinder_draw(cylinders,elipse,canvas_extents,world_extents){
  this.cylinder_list = cylinders;
  this.elipse_list = elipse;
  this.canvas = canvas_extents;
  this.world = world_extents;

  this.draw = function(){
                var points = [];
                for(var i = 0 ; i < this.cylinder_list.length; i++){
                   points[i] = this.to_world_canvas(this.cylinder_list[i],this.canvas,this.world);
                }
                var factor = this.canvas[0] / this.world[0];
                var point = new Points(points, this.world,[220, 35, 197],this.elipse_list,factor);
                point.draw();
                }
  this.to_world_canvas = function(world_point,canvas_extents,world_extents){
    var x = int(world_point[0] / world_extents[0] * canvas_extents[0]);
    var y = int(canvas_extents[1] - 1 - world_point[1] / world_extents[1] * canvas_extents[1]);
   return [x, y];
  }
};
//..............................................................draw_points
function Points(point,world_canvas,color,elipse,factor){
  this.point_list = point;
  this. world_canvas = world_canvas;
  this.color = color;
  this.elipse_list = elipse;
  this.factor = factor;
  this.radius = 5;

  this.draw = function(){

          for(var i = 0; i < this.point_list.length;i++)  {
            fill(this.color);
            ellipse(this.point_list[i][0], this.point_list[i][1],this.radius,this.radius);
            var point_draw = this.to_get_elipse_points(this.point_list[i],this.elipse_list[i],factor,0,2*PI);
            noFill();
            beginShape();
              for(var r = 0; r < point_draw.length; r++){
                 vertex(point_draw[r][0],point_draw[r][1]);
            }
            endShape();
          }

          for(var i = 0; i < this.point_list.length;i++)  {
          fill(this.color);
          ellipse(this.point_list[i][0], this.point_list[i][1],this.radius,this.radius);
          }

          }
//..............................................................................................
  this.to_get_elipse_points = function(center,elipse_point,factor,start_angle, end_angle){
    var points = [];
    var ax = elipse_point[1]*factor*cos(elipse_point[0]);
    var ay = elipse_point[1]*factor*sin(elipse_point[0]);
    var bx = - elipse_point[2]*factor*sin(elipse_point[0]);
    var by = elipse_point[2]*factor*cos(elipse_point[0]);
    var N_full = 40  // Number of points on full ellipse.
    var N = int(ceil((end_angle - start_angle) / (2 * PI) * N_full));
        N = max(N, 1);
    var  increment = (end_angle - start_angle) / N;
    for( var i = 0; i < (N + 1);i++){
            var a = start_angle + i * increment;
            var c = cos(a);
            var s = sin(a);
            var x = c*ax + s*bx + center[0];
            var y = - c*ay - s*by + center[1];
            points[i] = [x,y];
          }
    return points
  }
  };
//.............................................................draw scan

function scan_draw(scan_data,scanner_canvas_extents,scanner_range){
   this.scan_data = scan_data;
   this.scanner_canvas_extents = scanner_canvas_extents;
   this.scanner_range = scanner_range;

  this.draw=function(){
    var ploygon_x = [];
    var ploygon_y = [];

    plo_b = this.to_sensor_canvas([0,0], this.scanner_canvas_extents, this.scanner_range);

    ploygon_x[0] = plo_b[0];
    ploygon_x[0] = plo_b[1];

    for(var i = 1; i <= this.scan_data.length;i++){
      var angle = this.beam_index_to_angle(i-1)
      var x = this.scan_data[i] * cos(angle)
      var y = this.scan_data[i] * sin(angle)
       var ploy = this.to_sensor_canvas([x,y], this.scanner_canvas_extents, this.scanner_range);
       ploygon_x[i] = ploy[0];
       ploygon_y[i] = ploy[1];
    }
    plo_e = this.to_sensor_canvas([0,0], this.scanner_canvas_extents, this.scanner_range);
      ploygon_x[this.scan_data.length] = plo_b[0];
      ploygon_x[this.scan_data.length] = plo_b[1];
    this.forground_draw(ploygon_x,ploygon_y);
    this.background_draw();
  }
  this.forground_draw =function(polygon_x,polygon_y){
    var pol = polygon_x;
         fill('blue');
         stroke('blue');
         beginShape();
         for(var i = 0 ; i < pol.length; i++){
           vertex(polygon_x[i]+600,polygon_y[i]);
            vertex(polygon_x[i]+600,polygon_y[i]);
            vertex(this.scanner_canvas_extents[0]/2+600, this.scanner_canvas_extents[1]/2);
         }
         endShape(CLOSE);
         stroke(0);
  }
  this.to_sensor_canvas=function(sensor_point,canvas_extends,scanner_range){
    //convert scanner point canvas sensor_point
    var scale_v = canvas_extends[0]/(2*scanner_range);
    var x = int(canvas_extends[0]/2 - sensor_point[1]*scale_v);
    var y = int(canvas_extends[1]/2 - 1 - sensor_point[0]*scale_v);
    return [x,y];
  }

  this.beam_index_to_angle=function(i){
    var mounting_angle = -0.06981317007977318;
    return (i - 330.0) * 0.006135923151543 + mounting_angle;
  }
  this.background_draw = function()
  {
    fill(0);
    stroke('white')
    line(this.scanner_canvas_extents[0]/2+600, this.scanner_canvas_extents[1]/2,
          this.scanner_canvas_extents[0]/2+600, 20);
    text('X',this.scanner_canvas_extents[0]/2+600 + 10, 20);
    line(this.scanner_canvas_extents[0]/2+600, this.scanner_canvas_extents[1]/2,
            20+600, this.scanner_canvas_extents[1]/2);
    text( 'Y',20+600, this.scanner_canvas_extents[1]/2 - 10);
    fill(150);
    ellipse(this.scanner_canvas_extents[0]/2+600, this.scanner_canvas_extents[1]/2,40, 40);
    stroke(0);
  }
};
//...............................................................
