
import numpy as np
from mpmath import *
mp.pretty = True


def init_coveriance(bound_angle,obstacle_distance,sensor_angular_resolution):
    return (1/9)*np.array([[(cot(bound_angle)*obstacle_distance*sensor_angular_resolution)**2, 0],[0, (cot(bound_angle)*obstacle_distance)**2]])

def init_obstacle_pose(obstacle_distance):
    return np.array([obstacle_distance, 0])

def sensor_model(sensor_angular_resolution):
    return np.array([[1 ,sensor_angular_resolution],[ 0 , 1 ]])

def sensor_measurement_model():
    return np.array([ 1 , 0 ]).transpose()

def sensor_model_noise_coveriance(model_noise_variance):
    return (model_noise_variance)**2*np.array([[1 , 0], [0 , 1]])

def sensor_measurement_model_noise_coveriance(measurement_noise_variance):
    return measurement_noise_variance**2

def detect_ruptures_breakouts(scan_data, bound_angle,sensor_angular_resolution,model_noise_variance,measurement_noise_variance,scanner_max_range):
    current_scan_point = 0
    breakout_point_index = 0
    breakout_points= [False]*len(scan_data)
    rupture_points = [False]*len(scan_data)
    for n in range(len(scan_data)):
        if scan_data[n] >= scanner_max_range:
            rupture_points[n] = True;
        else:
            if current_scan_point == breakout_point_index:
                #print(scan_data[n])
                current_obstacle_pose = init_obstacle_pose(scan_data[n])
                current_coveriance = init_coveriance(bound_angle,scan_data[n],sensor_angular_resolution)
            else:
                predict_obstacle_pose = current_obstacle_pose
                predict_coveriance = np.add(np.dot(np.dot(sensor_model(sensor_angular_resolution),current_coveriance),sensor_measurement_model().transpose()),sensor_model_noise_coveriance(model_noise_variance))
                Vn = scan_data[n] - np.dot(sensor_measurement_model(),predict_obstacle_pose)
                Sn = np.add(np.dot(np.dot(sensor_measurement_model(),predict_coveriance),sensor_measurement_model().transpose()),sensor_measurement_model_noise_coveriance(measurement_noise_variance))
                if Vn*Vn/Sn >= 3.89 :
                    breakout_points[n] = True
                    breakout_points[n-1] = True
                    breakout_point_index = n
                    current_scan_point = n - 1
                else:
                    Kn = np.dot(predict_coveriance,sensor_measurement_model())*(1/Sn)
                    current_obstacle_pose = predict_obstacle_pose+ Kn*Vn
                    current_coveriance= predict_coveriance - np.dot(np.dot(Kn,sensor_measurement_model()),predict_coveriance)
            current_scan_point += 1
    return [breakout_points,rupture_points]

def get_lines(scan_data,breakout_points,rupture_points, line_down_limit,robot_pose):
    lines = []
    break_point = 0
    current_point  = 0
    while current_point < range(len(scan_data)):
        start_point =  break_point
        current_point = start_point + 1
        if current_point >= len(scan_data):
            break
        while breakout_points[current_point] == False and rupture_points[current_point] == False:
            current_point += 1
            if current_point >= len(scan_data):
                break
        break_point = current_point
        if (current_point - start_point +1 ) > line_down_limit:
            #print(scan_data[start_point:current_point])
            line = extract_line(scan_data[start_point:current_point],start_point,robot_pose)
            lines.append(line)
    return lines


def get_scan_point_codinate(robot_pose,point_polor):
    return [robot_pose[0] + float(point_polor[0])*float(cos(robot_pose[2] + point_polor[1])),robot_pose[1] + float(point_polor[0])*float(sin(robot_pose[2] + point_polor[1]))]

def extract_line(point_segment,start_index,robot_pose):
    [x,y,alpha] = whight_pose(point_segment,start_index,robot_pose)
    #p = "weighted position ->> x = %s,y, = %s alpha = %s " % (x,y,alpha)
    #print(p)
    [Sxx,Syy,Sxy] = point_veriations([x,y],point_segment,start_index,robot_pose)
    rq = x*cos(alpha) + y*sin(alpha)
    alpha = (1/2)*atan2(-2*Sxy,(Syy - Sxx))
    return [rq, alpha]

def point_veriations( whighted_coordinate, point_segment,start_index, robot_pose):
    [Sxx,Syy,Sxy] = [0,0,0]
    for i in range(len(point_segment)):
        [Sxx,Syy,Sxy] = [Sxx+(get_scan_point_codinate(robot_pose,[point_segment[i],sensor_start_angle-(start_index + i )*sensor_angular_resolution])[0] -whighted_coordinate[0])**2, Syy + (get_scan_point_codinate(robot_pose,[point_segment[i],sensor_start_angle-(start_index + i)*sensor_angular_resolution])[1]-whighted_coordinate[1])**2 \
            ,Sxy + ( get_scan_point_codinate(robot_pose,[point_segment[i],sensor_start_angle-(start_index +i)*sensor_angular_resolution])[0] -whighted_coordinate[0])*(get_scan_point_codinate(robot_pose,[point_segment[i],sensor_start_angle-(start_index + i)*sensor_angular_resolution])[1]-whighted_coordinate[1])]
    return [Sxx,Syy,Sxy]

def whight_pose(point_segment,index,robot_pose):
    obs_pose = [0 , 0]
    num_points = 0
    for i in range(len(point_segment)):
        num_points += 1
        obs_pose = np.add(obs_pose , get_scan_point_codinate(robot_pose,[point_segment[i],sensor_start_angle-index*sensor_angular_resolution]))
    obs_pose = [obs_pose[0]/num_points,obs_pose[1]/num_points]
    beta = atan2(obs_pose[1],obs_pose[0])
    return [obs_pose[0],obs_pose[1],beta]

def line_coveriance(scan_variance,line_pose):
    alpha = atan2(y,x)
    return (scan_variance)**2*np.array([[cos(alpha)**2, cos(alpha)*sin(alpha)],[cos(alpha)*sin(alpha), sin(alpha)**2]])

if __name__ == '__main__':
    sensor_start_angle = 135.25
    scan_data ="./scan_data"
    scan = open(scan_data,"r")
    scans_data = (scan.read()).split(",")
    #print(len(scans_data))
    scans = []
    for l in range(len(scans_data)):
	scans.append(float(scans_data[l]))

    bound_angle = pi*10/180
    sensor_angular_resolution = pi*(360/1081)/180
    model_noise_variance = 0.1
    measurement_noise_variance = 0.05
    scanner_max_range = 30.0
    [breakout_points, rupture_points] = detect_ruptures_breakouts(scans,bound_angle,sensor_angular_resolution,model_noise_variance,measurement_noise_variance,scanner_max_range)
    print("breakout_points -->   "),
    print(len(breakout_points))
    print("rupture_points -->    "),
    print(len(rupture_points))
    lines = get_lines(scans,breakout_points,rupture_points, 4,[6.19999990761,7.14285708964,0.0])
    print(lines)
