from numpy.lib.function_base import angle
import paho.mqtt.client as receive #import library
import numpy as np
import math
import collections, time
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
from pandas.core.indexes import base
from scipy.interpolate import interp1d
import scipy

class Point(object):
    x = 0
    y = 0
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Line(object):
    def __init__(self, p, slope):
        self.p = p
        self.slope = slope

def GetLinePara(line):
    # ax + by = c
    line.a = -line.slope
    line.b = 1
    line.c = line.p.y - int(line.slope) * line.p.x

def GetCrossPoint(base1pos,slope1,base2pos,slope2):
    p1 = Point(base1pos[0],base1pos[1])
    p2 = Point(base2pos[0],base2pos[1])
    line1, line2 = Line(p1,slope1), Line(p2,slope2)
    GetLinePara(line1)
    GetLinePara(line2)
    d = line1.a * line2.b - line2.a * line1.b
    p=Point()
    if d == 0:
        p.x = -50
        p.y = -50
        return p
    p.x = (line1.b * line2.c - line2.b * line1.c)*1.0 / d
    p.y = (line1.c * line2.a - line2.c * line1.a)*1.0 / d
    return p

##################################################################################################################################################

def reversefunc(phi):
    #print('reversefunc')
    data2 = pd.read_excel('ground_truth.xlsx')
    x = np.linspace(0, 50, 51)
    y = data2.iloc[x, 2]
    f = interp1d(y, x, kind = 'linear', fill_value='extrapolate')  # radial basis function interpolator instance
    di = f(phi)
    #print('angle blackbox',di)
    return di

def getArray(Position, ratio, base_num, angleturn0, angleturn1, angleturn2):
    if len(ratio) == 0:
        print('base{} finished'.format(base_num))
        exit = str(input('ready to end?(Y/N) :'))
        quit()
    dp_angle = reversefunc(ratio.popleft()) # displacement angle
    if dp_angle > 50:
        print('base', base_num, 'angle miss')
        angle_flag = False
        return ([], angle_flag)
    else:
        angle_flag = True
    
    angleturn_switcher={
        0: angleturn0,
        1: angleturn1,
        2: angleturn2
        #3: angleturn3
    }
    angleturn = angleturn_switcher.get(base_num,"Invalid base number")

    UpperAngleLimit_switcher={
        0: angleturn + dp_angle,
        1: -angleturn - dp_angle,
        2: -angleturn - dp_angle
        #3: angleturn + dp_angle
    }
    LowerAngleLimit_switcher={
        0: angleturn - dp_angle,
        1: -angleturn + dp_angle,
        2: -angleturn + dp_angle
        #3: angleturn + dp_angle
    }
    UpperAngleLimit = angleturn + dp_angle#UpperAngleLimit_switcher.get(base_num,"Invalid upper angle limit")
    LowerAngleLimit = angleturn - dp_angle#LowerAngleLimit_switcher.get(base_num,"Invalid lower angle limit")
    '''
    if base_num == 2 and angleturn2 == 90:
            UpperAngleLimit = angleturn2 - dp_angle
            LowerAngleLimit = dp_angle - angleturn2
    '''
    
    upperSlope = math.tan(math.radians(UpperAngleLimit))
    lowerSlope = math.tan(math.radians(LowerAngleLimit))
    slopearray = np.array([upperSlope,lowerSlope])

    return slopearray, angle_flag

def positioning(Position, ratio0, ratio1, ratio2, ratio3, angleturn0, angleturn1, angleturn2, angleturn3, N, padding):#positioning algoritm by pseudoinverse_4 anchors    
    slopearray0, angle_flag0 = getArray(Position, ratio0, 0, angleturn0, angleturn1, angleturn2)
    slopearray1, angle_flag1 = getArray(Position, ratio1, 1, angleturn0, angleturn1, angleturn2)
    slopearray2, angle_flag2 = getArray(Position, ratio2, 2, angleturn0, angleturn1, angleturn2)
    slopearray = [slopearray0, slopearray1, slopearray2]
    if angle_flag0 == False or angle_flag1 == False or angle_flag2 == False:
        print('angle out of range')
        return [],[]
    
    positionx = collections.deque(maxlen=1000)#for saving positioning data
    positiony = collections.deque(maxlen=1000)
    for main_base in range(N-1): # base0 to 1 and 2
        for main_base_thetas in range(2):
            for other_bases in range(main_base+1,N):
                for other_base_thetas in range(2):
                    #print(Position[main_base],slopearray[main_base][main_base_thetas],Position[other_bases],slopearray[other_bases][other_base_thetas])
                    P_c = GetCrossPoint(Position[main_base],slopearray[main_base][main_base_thetas],Position[other_bases],slopearray[other_bases][other_base_thetas])
                    if P_c.x > Position[1][0] or P_c.x < Position[0][0] or P_c.y > Position[2][1] or P_c.y < Position[0][1]:
                        pass
                    else:
                        positionx.append(P_c.x)
                        positiony.append(P_c.y)

    return positionx, positiony


