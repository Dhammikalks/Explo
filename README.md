Goal:

Full stack development of naviagtional robot with online SLAM and path planner using 2D Lidar.

Robot, is containing 5 separate component working together.

    controller               - controls the 4 motors connecting to the robot according to the data coming from the control server
 
    control server           - listening to the incoming data signal from the communicator,process the data and converted to PWM signal for    the controller  

    sensor                   - sensor network containing lidar and encoders , feeding the data to the location data server

    localization data server - listening to the incoming data signal from the sensor and process them to transmitted 

     communicator            - maintaining data link between robot and server. listening to the both localization data server and control server push back and forth data

 Localization server, 

is a work as API, from the data coming from the robot,lidar and encoders, localize the robot position related to it surrounding? while mapping the surrounding? respected to the robot position . For localization API uses Kalmarn filter inside a particle filter Implementation? for localize and API treat the obstacle it pacing as Landmark of the map and position the landmark on the map according to there probability cures. Also API puses all the result and performance data to the Data base end of the each calculation cycle.

 Data base,
 
 implementation is not finish since i am not yet done with control server but up to now it keeping all the localization data, performance data and keep cursor on latest unused data for the control sever and to keep the rest of the system up to date with localization cycle. 


Viewer,

is a API for demonstrated the localization, path planing with generated map manual control panel for debug. It is paging with Data base for Live Data and also old Data as per needed 

Path Planer,

is combination of A* Algorithm and Greedy Algorithm to make the system reliable and efficient . it is rendering live map from the Data base then Algorithm work graphical manner and generate set of coordinate for robot to travel and then converted back to real world coordinate and puses back to the Data base 

Control server,

puses in the path Data from the Data base and according to the current position. it generate immediate action and puses it in to the Data link  
