# FastSLAM.


from slam_g_library import get_cylinders_from_scan, write_cylinders,\
     write_error_ellipses, get_mean, get_error_ellipse_and_heading_variance,\
     print_particles,write_scanData
from math import sin, cos, pi, atan2, sqrt, exp
import copy
import random
import socket,sys
import numpy as np
import datetime
import Pyro4
import sys,time
import MySQLdb
import json
import array
from multiprocessing import Pipe , Process
#..................................................................................
class Particle:
    def __init__(self, pose):
        self.pose = pose
        self.landmark_positions = []
        self.landmark_covariances = []
        self.landmark_counters = []       # Added: counter for each landmark.

    def number_of_landmarks(self):
        """Utility: return current number of landmarks in this particle."""
        return len(self.landmark_positions)

    @staticmethod
    def g(state, control, w):
        """State transition. This is exactly the same method as in the Kalman
           filter."""
        x, y, theta = state
        l, r = control
        if r != l:
            alpha = (r - l) / w
            rad = l/alpha
            g1 = x + (rad + w/2.)*(sin(theta+alpha) - sin(theta))
            g2 = y + (rad + w/2.)*(-cos(theta+alpha) + cos(theta))
            g3 = (theta + alpha + pi) % (2*pi) - pi
        else:
            g1 = x + l * cos(theta)
            g2 = y + l * sin(theta)
            g3 = theta
        return np.array([g1, g2, g3])

    def move(self, left, right, w):
        """Given left, right control and robot width, move the robot."""
        self.pose = self.g(self.pose, (left, right), w)

    @staticmethod
    def h(state, landmark, scanner_displacement):
        """Measurement function. Takes a (x, y, theta) state and a (x, y)
           landmark, and returns the corresponding (range, bearing)."""
        dx = landmark[0] - (state[0] + scanner_displacement * cos(state[2]))
        dy = landmark[1] - (state[1] + scanner_displacement * sin(state[2]))
        r = sqrt(dx * dx + dy * dy)
        alpha = (atan2(dy, dx) - state[2] + pi) % (2*pi) - pi
        return np.array([r, alpha])

    @staticmethod
    def dh_dlandmark(state, landmark, scanner_displacement):
        """Derivative with respect to the landmark coordinates. This is related
           to the dh_dstate function we used earlier (it is:
           -dh_dstate[0:2,0:2])."""
        theta = state[2]
        cost, sint = cos(theta), sin(theta)
        dx = landmark[0] - (state[0] + scanner_displacement * cost)
        dy = landmark[1] - (state[1] + scanner_displacement * sint)
        q = dx * dx + dy * dy
        sqrtq = sqrt(q)
        dr_dmx = dx / sqrtq
        dr_dmy = dy / sqrtq
        dalpha_dmx = -dy / q
        dalpha_dmy =  dx / q

        return np.array([[dr_dmx, dr_dmy],
                         [dalpha_dmx, dalpha_dmy]])

    def h_expected_measurement_for_landmark(self, landmark_number,
                                            scanner_displacement):
        """Returns the expected distance and bearing measurement for a given
           landmark number and the pose of this particle."""

        codinate = self.h(self.pose,self.landmark_positions[landmark_number],scanner_displacement)
        return codinate

    def H_Ql_jacobian_and_measurement_covariance_for_landmark(
        self, landmark_number, Qt_measurement_covariance, scanner_displacement):
        """Computes Jacobian H of measurement function at the particle's
           position and the landmark given by landmark_number. Also computes the
           measurement covariance matrix."""

        H = self.dh_dlandmark(self.pose,self.landmark_positions[landmark_number],scanner_displacement)
        Q_l = np.dot(np.dot(H,self.landmark_covariances[landmark_number]),H.T)+Qt_measurement_covariance

        return (H, Q_l)

    def wl_likelihood_of_correspondence(self, measurement,
                                        landmark_number,
                                        Qt_measurement_covariance,
                                        scanner_displacement):
        """For a given measurement and landmark_number, returns the likelihood
           that the measurement corresponds to the landmark."""

        delta_z = measurement - self.h_expected_measurement_for_landmark(landmark_number,scanner_displacement)
        H,Q_l = self.H_Ql_jacobian_and_measurement_covariance_for_landmark(landmark_number,Qt_measurement_covariance,scanner_displacement)
        delta_Q = np.dot(np.dot(delta_z.T,np.linalg.inv(Q_l)),delta_z)
        likelyhood = (1/(2*pi*np.sqrt(np.linalg.det(Q_l))))*np.exp((-1/2)*delta_Q)
        return likelyhood

    def compute_correspondence_likelihoods(self, measurement,
                                           number_of_landmarks,
                                           Qt_measurement_covariance,
                                           scanner_displacement):
        """For a given measurement, returns a list of all correspondence
           likelihoods (from index 0 to number_of_landmarks-1)."""
        likelihoods = []
        for i in xrange(number_of_landmarks):
            likelihoods.append(
                self.wl_likelihood_of_correspondence(
                    measurement, i, Qt_measurement_covariance,
                    scanner_displacement))
        return likelihoods
    #...................................................
    @staticmethod
    def scanner_to_world(pose, point):
        """Given a robot pose (rx, ry, heading) and a point (x, y) in the
           scanner's coordinate system, return the point's coordinates in the
           world coordinate system."""
        dx = cos(pose[2])
        dy = sin(pose[2])
        x, y = point
        return (x * dx - y * dy + pose[0], x * dy + y * dx + pose[1])
    #...................................................

    def initialize_new_landmark(self, measurement_in_scanner_system,
                                Qt_measurement_covariance,
                                scanner_displacement):
        """Given a (x, y) measurement in the scanner's system, initializes a
           new landmark and its covariance."""
        scanner_pose = (self.pose[0] + cos(self.pose[2]) * scanner_displacement,
                        self.pose[1] + sin(self.pose[2]) * scanner_displacement,
                        self.pose[2])
        codinate = self.scanner_to_world(scanner_pose,measurement_in_scanner_system)
        H = self.dh_dlandmark(scanner_pose,codinate,scanner_displacement)
        H_inverse = np.linalg.inv(H)
        Segma = np.dot(np.dot(H_inverse,Qt_measurement_covariance),H_inverse.T)

        self.landmark_positions.append(codinate)
        self.landmark_covariances.append(Segma)

    def update_landmark(self, landmark_number, measurement,
                        Qt_measurement_covariance, scanner_displacement):
        """Update a landmark's estimated position and covariance."""

        H,Q_l = self.H_Ql_jacobian_and_measurement_covariance_for_landmark(landmark_number,Qt_measurement_covariance,scanner_displacement)
        K = np.dot(self.landmark_covariances[landmark_number],np.dot(H.T,np.linalg.inv(Q_l)))
        self.landmark_positions[landmark_number]= self.landmark_positions[landmark_number] + np.dot(K,(measurement - self.h_expected_measurement_for_landmark(landmark_number,scanner_displacement)))
        self.landmark_covariances[landmark_number] = np.dot((np.eye(2) - np.dot(K,H)),self.landmark_covariances[landmark_number])


    def update_particle(self, measurement, measurement_in_scanner_system,
                        number_of_landmarks,
                        minimum_correspondence_likelihood,
                        Qt_measurement_covariance, scanner_displacement):
        """Given a measurement, computes the likelihood that it belongs to any
           of the landmarks in the particle. If there are none, or if all
           likelihoods are below the minimum_correspondence_likelihood
           threshold, add a landmark to the particle. Otherwise, update the
           (existing) landmark with the largest likelihood."""

        likelihoods = self.compute_correspondence_likelihoods(measurement,number_of_landmarks,Qt_measurement_covariance,scanner_displacement)
        if not likelihoods or \
                        max(likelihoods) < minimum_correspondence_likelihood:

            self.initialize_new_landmark(measurement_in_scanner_system, Qt_measurement_covariance, scanner_displacement)
            self.landmark_counters.append(1)
            return minimum_correspondence_likelihood

        else:

            w = max(likelihoods)
            index = likelihoods.index(w)
            self.update_landmark(index, measurement, Qt_measurement_covariance, scanner_displacement)
            # Add code to update_landmark().
            self.landmark_counters[index] = self.landmark_counters[index] + 2
            return w


    #..........................................................
    @staticmethod
    def beam_index_to_angle(i, mounting_angle=-0.06981317007977318):
        """Convert a beam index to an angle, in radians."""
        return (i - 330.0) * 0.006135923151543 + mounting_angle


    def min_max_bearing(self):
        return (self.beam_index_to_angle(0),
                self.beam_index_to_angle(660))
    #..........................................................
    def decrement_visible_landmark_counters(self, scanner_displacement):
        """Decrements the counter for every landmark which is potentially
           visible. This uses a simplified test: it is only checked if the
           bearing of the expected measurement is within the laser scanners
           range."""
        # --->>> Insert your new code here.
        min_bearing,max_bearing = self.min_max_bearing()
        for i in xrange(len(self.landmark_counters)):
            l,alpha = self.h_expected_measurement_for_landmark(i,scanner_displacement)
            if alpha >= min_bearing  and alpha <= max_bearing:
                self.landmark_counters[i] = self.landmark_counters[i] -1


    def remove_spurious_landmarks(self):
        """Remove all landmarks which have a counter less than zero."""

        landmark_pos = self.landmark_positions
        landmark_cov = self.landmark_covariances
        landmark_count = self.landmark_counters
        self.landmark_positions = []
        self.landmark_covariances = []
        self.landmark_counters = []
        for i in xrange(len(landmark_count)):
            if landmark_count[i] >= 0 :
                self.landmark_positions.append(landmark_pos[i]);
                self.landmark_covariances.append(landmark_cov[i]);
                self.landmark_counters.append(landmark_count[i]);


#.................................................................................
class FastSLAM:

    def __init__(self, initial_particles,
                 robot_width, scanner_displacement,
                 control_motion_factor, control_turn_factor,
                 measurement_distance_stddev, measurement_angle_stddev,
                 minimum_correspondence_likelihood):
        # The particles.
        self.particles = initial_particles

        # Some constants.
        self.robot_width = robot_width
        self.scanner_displacement = scanner_displacement
        self.control_motion_factor = control_motion_factor
        self.control_turn_factor = control_turn_factor
        self.measurement_distance_stddev = measurement_distance_stddev
        self.measurement_angle_stddev = measurement_angle_stddev
        self.minimum_correspondence_likelihood = \
            minimum_correspondence_likelihood
        self.last_tiks = None
        self.first_motor_ticks = True

    def predict(self, control):
        """The prediction step of the particle filter."""
        left, right = control
        left_std  = sqrt((self.control_motion_factor * left)**2 +\
                        (self.control_turn_factor * (left-right))**2)
        right_std = sqrt((self.control_motion_factor * right)**2 +\
                         (self.control_turn_factor * (left-right))**2)

        for p in self.particles:
            l = random.gauss(left, left_std)
            r = random.gauss(right, right_std)
            p.move(l, r, self.robot_width)

    def update_and_compute_weights(self, cylinders):
        """Updates all particles and returns a list of their weights."""
        Qt_measurement_covariance = \
            np.diag([self.measurement_distance_stddev**2,
                     self.measurement_angle_stddev**2])
        weights = []
        for p in self.particles:

            p.decrement_visible_landmark_counters(self.scanner_displacement)

            # Loop over all measurements.
            number_of_landmarks = p.number_of_landmarks()
            weight = 1.0
            for measurement, measurement_in_scanner_system in cylinders:
                weight *= p.update_particle(
                    measurement, measurement_in_scanner_system,
                    number_of_landmarks,
                    self.minimum_correspondence_likelihood,
                    Qt_measurement_covariance, scanner_displacement)

            # Append overall weight of this particle to weight list.
            weights.append(weight)

            # Added: remove spurious landmarks (with negative counter).
            p.remove_spurious_landmarks()

        return weights

    def resample(self, weights):
        """Return a list of particles which have been resampled, proportional
           to the given weights."""
        new_particles = []
        max_weight = max(weights)
        index = random.randint(0, len(self.particles) - 1)
        offset = 0.0
        for i in xrange(len(self.particles)):
            offset += random.uniform(0, 2.0 * max_weight)
            while offset > weights[index]:
                offset -= weights[index]
                index = (index + 1) % len(weights)
            new_particles.append(copy.deepcopy(self.particles[index]))
        return new_particles

    def correct(self, cylinders):
        """The correction step of FastSLAM."""
        # Update all particles and compute their weights.
        weights = self.update_and_compute_weights(cylinders)
        # Then resample, based on the weight array.
        self.particles = self.resample(weights)


    def get_tiks(self,motor_Data):

        ticks = (motor_Data[2],motor_Data[6])
        if self.first_motor_ticks :
            self.first_motor_ticks = False
            self.last_tiks = ticks
        self.motor_ticks = tuple([ticks[i]- self.last_tiks[i] for i in range(2)])
        self.last_tiks = ticks
        return self.motor_ticks
#......................................................................

def connect():
    sql_data = {}
    sql_data_file ="./sql.data"
    sql = open(sql_data_file,"r")
    for l in sql:
        data = l.split(":")
        sql_data[data[0]]= data[1].strip()
    con = MySQLdb.connect(host=sql_data["host"], user=sql_data["user"], passwd=sql_data["passwd"], db=sql_data["db"])
    try:

        cur = con.cursor()
        #query = "INSERT INTO SLAM(Time_stamp_big ,Scan_data ,Partical_pos ,Errors , Cylinders ,Error_elipses ,Time_Stamp_end ,Opration_time) values(\"gjfig\",\"fhgh\",\"gfdhg\",\"dhdh\",\"hhg\",\"fghfh\",\"dgdg\",2)"
        #cur.execute(query)
        con.commit()
        # data = cur.fetchall()e
    except MySQLdb.Error, e:
        print(e)
        if con:
            con.rollback()
    return con
#........................................................................
def SQL_CMD(con,query):
    cur = con.cursor()
    cur.execute(query)
    con.commit()
#.......................................................
#.......................................................data processing and storing
def insert_Data_to_DataBase(conn):
    data = []
    con  = connect()
    data = conn.recv()
    #........................
    #........................
    query_1 = "INSERT INTO SLAM(Scan_data , position, Partical_pos ,Errors , Cylinders ,Error_elipses) values('"+data[1]+"' ,'"+data[2]+"','"+data[3]+"','"+data[4]+"','"+data[5]+"','"+data[6]+"')"
    query_2 = "INSERT INTO performance(Time_Stamp_begining ,Time_Stamp_end ,Opration_time) values('"+data[0]+"','"+data[7]+"','"+data[8]+"')"
    query_3 = "INSERT INTO Data_ref(is_New ) values('"+str(1)+"')"
    SQL_CMD(con, query_1)
    SQL_CMD(con,query_2)
    SQL_CMD(con,query_3)
    #print data
    #return 0
#........................................................
#......................................................................
if __name__ == '__main__':
    # Robot constants.
    robot_data = {}
    robot_data_file ="./robot.variable"
    sql = open(robot_data_file,"r")
    for l in sql:
        data = l.split(":")
        robot_data[data[0]]= data[1].strip()

    scanner_displacement =float(robot_data['scanner_displacement'])
    ticks_to_mm = float(robot_data['ticks_to_mm'])
    robot_width = float(robot_data['robot_width'])

    # Cylinder extraction and matching constants.
    minimum_valid_distance = float(robot_data['minimum_valid_distance'])
    depth_jump = float(robot_data['depth_jump'])
    cylinder_offset = float(robot_data['cylinder_offset'])

    # Filter constants.
    control_motion_factor = float(robot_data['control_motion_factor'])  # Error in motor control.
    control_turn_factor = float(robot_data['control_turn_factor'])  # Additional error due to slip when turning.
    measurement_distance_stddev = float(robot_data['measurement_distance_stddev'])  # Distance measurement error of cylinders.
    measurement_angle_stddev = float(robot_data['measurement_angle_stddev'])/ 180.0 * pi  # Angle measurement error.
    minimum_correspondence_likelihood = float(robot_data['minimum_correspondence_likelihood'])  # Min likelihood of correspondence.
    #..............................perpomances variable

    time_start = 0;
    time_finish = 0;

    ##############..............................Pyro4 elements

    robot = Pyro4.Proxy("PYRONAME:example.robot")  # use name server object lookup uri shortcut
    con =connect()
    #############..............................
    # Generate initial particles. Each particle is (x, y, theta).
    number_of_particles = int (robot_data['number_of_particles'])
    start_state = np.array([float(robot_data['start_x']), float(robot_data['start_y']), float(robot_data['start_angle']) / 180.0 * pi])
    initial_particles = [copy.copy(Particle(start_state))
                         for _ in xrange(number_of_particles)]

    # Setup filter.
    fs = FastSLAM(initial_particles,
                  robot_width, scanner_displacement,
                  control_motion_factor, control_turn_factor,
                  measurement_distance_stddev,
                  measurement_angle_stddev,
                  minimum_correspondence_likelihood)

    # Loop over all motor tick records.
    # This is the FastSLAM filter loop, with prediction and correction.
    f = open("slam_log.txt", "w")
    try :
        #...................................
        print "ROBOT server: "
        print "[1] step mode [2] continuous mode "
        print "please enter the running mode"
        mode = 0
        while (1):
            mode = input('please enter the running mode : ')
            if mode == 1:
                mode = 1;
                break
            elif mode == 2:
                mode = 2
                break;

            else:
                print "please enter correct mode "
        #...................................
        while True:

            if robot.is_avilable():
                print "new cycle......";
                data_encode = robot.get_DataEncode();
                data_scan = robot.get_DataScan();
                robot.false_avilable()

                #...........................
                time_start = datetime.datetime.now()
                splited_encodedata = data_encode.split()
                spilted_scandata   = data_scan.split()
                #...........................
                encode = splited_encodedata[2:14]
                encode_data = []
                encode_data.append('M')
                for i in range(len(encode)):
                    encode_data.append(int(encode[i]))
                #...........................
                scan = spilted_scandata[2:]
                scan_data = []
                #scan_data.append('S')
                for i in range(len(scan)):
                    scan_data.append(int(scan[i]))
                #.................................
                write_scanData(f,"S",scan_data)
                #...........................perdict
                print "predicting the postions......\n";
                #..................................
                control = map(lambda x: x * ticks_to_mm, fs.get_tiks(encode_data))
                fs.predict(control)
                #...........................
                print "correcting ....\n"
                #...........................correct
                cylinders = get_cylinders_from_scan(scan_data,depth_jump,minimum_valid_distance,cylinder_offset)
                fs.correct(cylinders)
                # ..................................
                #................................... data representation
                #output particles
                print_particles(fs.particles,f)
                # Output state estimated from all particles.
                mean = get_mean(fs.particles)
                print >> f, "F %.0f %.0f %.3f" % \
                        (mean[0] + scanner_displacement * cos(mean[2]),
                         mean[1] + scanner_displacement * sin(mean[2]),
                         mean[2])

                # Output error ellipse and standard deviation of heading.
                errors = get_error_ellipse_and_heading_variance(fs.particles, mean)
                print >> f, "E %.3f %.0f %.0f %.3f" % errors

                # Output landmarks of particle which is closest to the mean position.
                output_particle = min([
                                      (np.linalg.norm(mean[0:2] - fs.particles[i].pose[0:2]), i)
                                      for i in xrange(len(fs.particles))])[1]
                # Write estimates of landmarks.

                write_cylinders(f, "W C",
                            fs.particles[output_particle].landmark_positions)
                # Write covariance matrices.

                error_eclipse = write_error_ellipses(f, "W E",
                                 fs.particles[output_particle].landmark_covariances)

                time_finish = datetime.datetime.now()

                #................................
                process_time = time_finish - time_start
                #print process_time.microseconds/1E6
                #.................................
                posed = []
                for i in fs.particles:
                    posed.append(tuple(i.pose))
                #.................................
                landmark_pos = []
                landmark_cov = []

                landmark_pos = [np.asarray(i).tolist() for i in fs.particles[output_particle].landmark_positions]
                #landmark_cov = [np.asarray(i).tolist() for i in fs.particles[output_particle].landmark_covariances]
                #print landmark_pos
                data =[str(time_start),str(scan_data),str(np.asarray(mean).tolist()),str(posed) ,str(
                    errors) ,str(landmark_pos),str(error_eclipse),str(time_finish), str(
                    process_time.microseconds / 1E6)]
                #.................................
                print "cycle ends \n"
                perent_con,child_con = Pipe()
                p = Process(target=insert_Data_to_DataBase , args=(child_con,))
                p.start()
                perent_con.send(data)
                p.join()
                print "Data added to data base\n"
                #.................................
            if(mode == 1):
                raw_input('press Enter for next cycle...')
        f.close()
            #...................................
    except KeyboardInterrupt:
        f.close()
        sys.exit(2)