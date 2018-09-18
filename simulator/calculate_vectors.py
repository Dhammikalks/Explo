#!/usr/bin/env python3
import sys,json
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
