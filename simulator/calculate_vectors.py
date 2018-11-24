#!/usr/bin/env python
import sys,os,json,cv2,pickle,math
import PIL
from PIL import Image
import numpy as np
import urllib
from random import gauss

################################### build current vector range
#def calLimit(pos,sensor_range,canvas_range):
#    Xminlimit = limit(int(pos[0]),1,sensor_range,0)
#    Yminlimit = limit(int(pos[1]),1,sensor_range,0)
#    Xmaxlimit = limit(int(pos[0]),0,sensor_range,canvas_range[0])
#    Ymaxlimit = limit(int(pos[1]),0,sensor_range,canvas_range[1])
#    return [Xminlimit,Yminlimit,Xmaxlimit,Ymaxlimit]
#####################################
#def limit(vector,min_max,sensor_range,abs_limit):
#    limit = vector;
#    if(min_max): #minum range
#        if(vector - sensor_range >= abs_limit):
#            limit = vector - sensor_range
#        else:
#            limit = abs_limit
#    else:#max limit
#        if(vector + sensor_range <= abs_limit):
#            limit = vector + sensor_range
#        else:
#            limit = abs_limit
#    return limit
###################################filter out vector
#def getMetrix(limit,env):
#    vector = []
#        row = []
#        for j in xrange(limit[2]-limit[0]):
#            row.append(env[limit[0]+j][limit[1]+i])
#        vector.append(row)
#    vector = np.asarray(vector);
#    return vector
##################################
#def toImage(vector):
#    array_vector = np.asarray(vector)
#    image = Image.fromarray(array_vector, 'L')
#    return image
################################## (python open cv does not implemeted this yet )from work of mohikhsan hat off to him
def createLineIterator(P1, P2, img,intensity):


    P1X = P1[0]
    P1Y = P1[1]
    P2X = P2[0]
    P2Y = P2[1]

    #difference and absolute difference between points
    #used to calculate slope and relative location between points
    dX = P2X - P1X
    dY = P2Y - P1Y
    dXa = np.abs(dX)
    dYa = np.abs(dY)

    #predefine numpy array for output based on distance between points
    if(intensity == 1):
        itbuffer = np.empty(shape=(np.maximum(int(dYa),int(dXa)),3),dtype=np.float32)
        #define local variables for readability
        imageH = len(img)
        imageW = len(img[0])
    else:
        itbuffer = np.empty(shape=(np.maximum(dYa,dXa),2),dtype=np.float32)
    itbuffer.fill(np.nan)

    #Obtain coordinates along the line using a form of Bresenham's algorithm
    negY = P1Y > P2Y
    negX = P1X > P2X
    if P1X == P2X: #vertical line segment
        itbuffer[:,0] = P1X
        if negY:
            itbuffer[:,1] = np.arange(P1Y - 1,P1Y - dYa - 1,-1)
        else:
            itbuffer[:,1] = np.arange(P1Y+1,P1Y+dYa+1)
    elif P1Y == P2Y: #horizontal line segment
        itbuffer[:,1] = P1Y
        if negX:
            itbuffer[:,0] = np.arange(P1X-1,P1X-dXa-1,-1)
        else:
            itbuffer[:,0] = np.arange(P1X+1,P1X+dXa+1)
    else: #diagonal line segment
        steepSlope = dYa > dXa
        if steepSlope:
            slope = float(dX)/float(dY)
            if negY:
                itbuffer[:,1] = np.arange(P1Y-1,P1Y-dYa-1,-1)
            else:
                itbuffer[:,1] = np.arange(P1Y+1,P1Y+dYa+1)
            itbuffer[:,0] = (slope*(itbuffer[:,1]-P1Y)).astype(np.int) + P1X
        else:
            slope = float(dY)/float(dX)
            if negX:
                itbuffer[:,0] = np.arange(P1X-1,P1X-dXa-1,-1)
            else:
                itbuffer[:,0] = np.arange(P1X+1,P1X+dXa+1)
            itbuffer[:,1] = (slope*(itbuffer[:,0]-P1X)).astype(np.int) + P1Y

    if(intensity == 1 ):
        #Remove points outside of image
        colX = itbuffer[:,0]
        colY = itbuffer[:,1]
        itbuffer = itbuffer[(colX >= 0) & (colY >=0) & (colX<imageW) & (colY<imageH)]
        #Get intensities from img ndarray
        #itbuffer[:,2] =
        line = img[itbuffer[:,1].astype(np.uint),itbuffer[:,0].astype(np.uint)]
        itbuffer[:,2] = 0.21*line[:,0] + 0.72*line[:,1] + 0.07*line[:,2]

    return itbuffer
 #####################################################std_val
def randmize(mean,std_dev):
    return gauss(mean,std_dev)
#####################################################
def calLastpixel(postion,sensor_range,canvas_range,angle):
    current_pose  = [sensor_range,sensor_range]
    x = int(postion[0] - sensor_range*np.cos(np.deg2rad(angle)))
    y = int(postion[1] - sensor_range*np.sin(np.deg2rad(angle)))
    if(x < 0):
        x = 0;
    if(y < 0):
        y = 0;
    if(x > canvas_range[0]):
        x = canvas_range[0]
    if(y > canvas_range[1]):
        y = canvas_range[1]
    return (x,y)
 ######################################################
def calScanerRays(postion,sensor_range,canvas_range,env,sensor_stdv):
    ray_ends = []
    for i in range(360):
        end = calLastpixel(postion,sensor_range,canvas_range,i)
        end = (end[0],end[1])
        pixelset = createLineIterator(postion, end, env,1)
        ray_end = distance(end,postion);
        for i in range(len(pixelset)): # find if there is any obstacle inbetween
            if(pixelset[i][2] > 250):
                ray_end = distance([pixelset[i][0],pixelset[i][1]],postion);
                break
        ray_end = randmize(ray_end,sensor_stdv)
        ray_ends.append(int(round(ray_end)))
    return ray_ends
#######################################################
def distance(p1,p2):
    [X1,Y1] = p1
    [X2,Y2] = p2
    d = int(math.sqrt((X1-X2)**2+(Y1-Y2)**2))
    return d
########################################################
def getPath(path):
    fullPath = []
    image = 0;
    for i in range(len(path)-1):
        codinate = createLineIterator(path[i], path[i+1],i,0)
        codinate.tolist().pop()
        fullPath.extend(codinate.tolist())
    return fullPath
########################################################
def get_vector(path,angle):
    pos_vectors  = []
    for i in range(len(path)):
        if i == 0:
            x = path[i][0]
            y = path[i][1]
            theta = angle
        else:
            x = path[i][0]
            y = path[i][1]
            theta = math.atan2((path[i][1]-path[i-1][1]),(path[i][0]-path[i-1][0]))
        pos_vectors.append([x,y,theta])
    return pos_vectors
########################################################
def sensor(ray_ends,postion):
    distances = []
    for i in range(len(ray_ends)):
        distances.append(distance(ray_ends[i],postion))
    return distances
#######################################################
class robot:
    def __init__(self,robotWidth,robotLenght,wheelRadius,encoderticks):
        self.width = robotWidth;
        self.lenght = robotLenght;
        self.wheel_radius = wheelRadius;
        self.tickcount = encoderticks;
        self.count_left = 0
        self.count_right = 0
        self.postion = [0,0,0];
        self.wheellength = math.pi*2*self.wheel_radius
        self.ticks_per_lenth = self.tickcount/self.wheellength

    def init_pos(self,pos):
        self.postion = pos

    def run(self,next_pos):
        [x,y,theta] = self.postion
        [xn,yn,thetan] = next_pos
        if(theta == thetan):
            count = abs((xn-x)/np.cos(theta))*self.ticks_per_lenth
            self.count_left += int(count)
            self.count_right += int(count)
        else:
            alpha = (thetan - theta + math.pi )% (2*math.pi) - math.pi
            rad = ((xn -x)/(np.sin(thetan) - np.sin(theta)))-(self.width/2.)
            l = rad*alpha
            r = self.width*alpha + l
            self.count_left += int(abs(l))
            self.count_right += int(abs(r))
        self.postion = next_pos

    def tickcount_left(self):
        return self.count_left;

    def tickcount_right(self):
        return self.count_right;
########################################################
if __name__ == '__main__':
    #getting the data set from the php
    sensor_range = 50;
    sensor_stdv = 0.5;
    canvas_range = [700,700];
    env = [];
    initPos = [];
    path = [];
    sensor_rays = [];
    if(len(sys.argv)>= 1):
        data = json.loads(sys.argv[1])
        initPos = data[0];
        path = data[1];
        env = data[2]['imageData'];
        #.......................
        resp = urllib.urlopen(env);
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = np.asarray(image)
        #.......................
        fullpath = getPath(path)
        pos_vectors = get_vector(fullpath,0.0)
        distance_array = [];
    bot = robot(10,15,5,100);
    bot.init_pos(pos_vectors[0])
    tick_counts = []
    for i in range(len(pos_vectors)):
        bot.run(pos_vectors[i])
        tick_counts.append([bot.tickcount_left(),bot.tickcount_right()])
        rays = calScanerRays(fullpath[i],sensor_range,canvas_range,image,sensor_stdv)
        sensor_rays.append(rays);
    print(tick_counts)
    ########################################################
