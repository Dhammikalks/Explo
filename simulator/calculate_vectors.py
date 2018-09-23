#!/usr/bin/env python3
import sys,json,cv2
from PIL import Image
import numpy as np
#getting the data set from the php
sensor_range = 50;
canvas_range = [700,700];
env = [];
initPos = [];
path = [];

####################################data from php
try:
   pos = json.loads( sys.argv[1]);
   env = pos[0];
   initPos = pos[1];
   path  = pos[2];

except:
   print(sys.exc_info()))
   sys.exit(1)
################################### build current vector range
def calLimit(pos,sensor_range,canvas_range):
    Xminlimit = limit(pos[0],1,sensor_range,0)
    Yminlimit = limit(pos[1],1,sensor_range,0)
    Xmaxlimit = limit(pos[0],0,sensor_range,canvas_range[0])
    Ymaxlimit = limit(pos[1],0,sensor_range,canvas_range[1])
    return [Xminlimit,Xminlimit,Xmaxlimit,Ymaxlimit]
#####################################
def limit(vector,min_max,sensor_range,abs_limit):
    limit = vector;
    if(min_max): #minum range
        if(vector - sensor_range >= abs_limit):
            limit = vector - sensor_range
        else:
            limit = abs_limit
    else:#max limit
        if(vector + sensor_range =< abs_limit):
            limit = vector + sensor_range
        else:
            limit = abs_limit
    return limit
###################################filter out vector
def getMetrix(limit,env):
    vector = []
    for i in xrange(limit[3]-limit[1]):
        row = []
        for y in xrange(limit[2]-limit[0]):
            row.push(env[limit[1]+i][limit[0]+j])
        vector.push(row)
    return vector
##################################
def toImage(vector):
    array_vector = np.asarray(vector)
    image = Image.fromarray(array_vector, 'L')
    return image
################################## (python open cv does not implemeted this yet )from work of mohikhsan hat off to him
def createLineIterator(P1, P2, img,intensity):
    """
    Produces and array that consists of the coordinates and intensities of each pixel in a line between two points

    Parameters:
        -P1: a numpy array that consists of the coordinate of the first point (x,y)
        -P2: a numpy array that consists of the coordinate of the second point (x,y)
        -img: the image being processed

    Returns:
        -it: a numpy array that consists of the coordinates and intensities of each pixel in the radii (shape: [numPixels, 3], row = [x,y,intensity])
    """

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
       itbuffer = np.empty(shape=(np.maximum(dYa,dXa),3),dtype=np.float32)
       #define local variables for readability
       imageH = img.shape[0]
       imageW = img.shape[1]
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
           slope = dY.astype(np.float32)/dX.astype(np.float32)
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
       itbuffer[:,2] = img[itbuffer[:,1].astype(np.uint),itbuffer[:,0].astype(np.uint)]

   return itbuffer
 #####################################################
 def calLastpixel(sensor_range,ange):
     current_pose  = [sensor_range,sensor_range]
     x = int(current_pose[0] - sensor_range*np.cos(np.deg2rad(angle)))
     y = int(current_pose[1] - sensor_range*np.sin(np.deg2rad(angle)))
     return (x,y)
 ######################################################
def calScanerRays(postion,sensor_range,canvas_range,env):
    limit = calLimit(postion,sensor_range,canvas_range)
    vector = getMetrix(limit,env);
    img = toImage(vector);
    ray_ends = []
    for i in xrange(360):
        end = calLastpixel(sensor_range,i):
        pixelset = createLineIterator(postion, end, img,1):
        ray_end = end
        for i in xrange(len(pixelset)): # find if there is any obstacle inbetween
            if(pixelset[2] == 255):
                ray_end = [pixelset[0],pixelset[1]]
                break
        ray_ends.push(ray_end)
    return ray_ends
#######################################################
def distance(p1,p2):
    [X1,Y1] = p1
    [X2,Y2] = p2
    d = math.sqrt((X1-X2)**2+(Y1-Y2)**2)
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
