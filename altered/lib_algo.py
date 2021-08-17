from numpy.core.records import array
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
import random

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
    line1 = Line(p1,slope1)
    line2 = Line(p2,slope2)
    GetLinePara(line1)
    GetLinePara(line2)
    d = line1.a * line2.b - line2.a * line1.b
    p=Point()
    if d == 0: # invalid point
        p.x = -50
        p.y = -50
        return p
    p.x = (line1.b * line2.c - line2.b * line1.c)*1.0 / d
    p.y = (line1.c * line2.a - line2.c * line1.a)*1.0 / d
    return p

##################################################################################################################################################

def reversefunc(r):
    #print('reversefunc')
    data = pd.read_excel('ground_truth.xlsx')
    x = np.linspace(0, 50, 51)
    y = data.iloc[x, 2]
    f = interp1d(y, x, kind = 'linear', fill_value='extrapolate')  # radial basis function interpolator instance
    di = f(r)
    #print('angle blackbox',di)
    return di

def getArray(Position, ratio, base_num, angleturn0, angleturn1, angleturn2):
    if len(ratio) == 0:
        print('base{} finished'.format(base_num))
        exit = str(input('ready to end?(Y/N) :'))
        quit()
    dp_angle = reversefunc(ratio.popleft()) # displacement angle
    if dp_angle > 50:
        #print('base', base_num, 'angle miss')
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
    
    position_x = collections.deque(maxlen=1000)#for saving positioning data
    position_y = collections.deque(maxlen=1000)
    for main_base in range(N-1): # base0 to 1 and 2
        print('mainbase:',main_base)
        for main_base_thetas in range(2):
            for other_bases in range(main_base+1,N):
                for other_base_thetas in range(2):
                    #print(Position[main_base],slopearray[main_base][main_base_thetas],Position[other_bases],slopearray[other_bases][other_base_thetas])
                    P_c = GetCrossPoint(Position[main_base],slopearray[main_base][main_base_thetas],Position[other_bases],slopearray[other_bases][other_base_thetas])

                    print('main slope',slopearray[main_base])
                    #print('other slope',slopearray[other_bases])
                    position_x.append(P_c.x)
                    position_y.append(P_c.y)
                    '''
                    if P_c.x > Position[1][0] or P_c.x < Position[0][0] or P_c.y > Position[2][1] or P_c.y < Position[0][1]:
                        pass
                    else:
                        position_x.append(P_c.x)
                        position_y.append(P_c.y)
                    '''

    return position_x, position_y

def get_far_list(ss0, ss1, ss2):
    far_list = []
    for i in range(min([len(ss0),len(ss1),len(ss2)])):
        ss_list = [ss0[i], ss1[i], ss2[i]]
        far_list.append(ss_list.index(min(ss_list)))

    return far_list

def delete_far_point(Position, far_base, position_x, position_y):
    #dropout = len(position_x) // 3 # dropout 1/3 points in (posision_x,posision_y)
    if len(position_x) > 3:
        for i in reversed(range(len(position_x))):
            d_to_0 = math.sqrt( (Position[0][0]-position_x[i])**2 + (Position[0][1]-position_y[i])**2 )
            d_to_1 = math.sqrt( (Position[1][0]-position_x[i])**2 + (Position[1][1]-position_y[i])**2 )
            d_to_2 = math.sqrt( (Position[2][0]-position_x[i])**2 + (Position[2][1]-position_y[i])**2 )
            d_list = [d_to_0, d_to_1, d_to_2]
            if d_list.index(min(d_list)) == far_base:
                position_x.pop(i)
                position_y.pop(i)
        return position_x, position_y
    else:
        return position_x, position_y
        
####################################################################################
def realtime_getArray_random(Position, ratio, base_num, angleturn0, angleturn1, angleturn2):
    slopearray = []
    angleturn_switcher={
        0: angleturn0,
        1: angleturn1,
        2: angleturn2
        #3: angleturn3
    }
    rand_int = random.randint(0,len(ratio)-1)
    dp_angle = reversefunc(ratio[rand_int]) # displacement angle
    if dp_angle > 50:
        print('base', base_num, 'angle miss')
        angle_flag = False
    else:
        angle_flag = True

    angleturn = angleturn_switcher.get(base_num,"Invalid base number")
    UpperAngleLimit = angleturn + dp_angle
    LowerAngleLimit = angleturn - dp_angle
    upperSlope = math.tan(math.radians(UpperAngleLimit))
    lowerSlope = math.tan(math.radians(LowerAngleLimit))
    slopearray += [upperSlope, lowerSlope]
    return slopearray, angle_flag

def realtime_getArray(Position, ratio, base_num, angleturn0, angleturn1, angleturn2):
    slopearray = []
    angleturn_switcher={
        0: angleturn0,
        1: angleturn1,
        2: angleturn2
        #3: angleturn3
    }
    angle_flag = True
    for i in range(len(ratio)):
        dp_angle = reversefunc(ratio[i]) # displacement angle
        if angle_flag == True:
            if dp_angle > 50:
                #print('base', base_num, 'angle miss')
                angle_flag = False
            else:
                angle_flag = True

        angleturn = angleturn_switcher.get(base_num,"Invalid base number")
        UpperAngleLimit = angleturn + dp_angle
        LowerAngleLimit = angleturn - dp_angle
        upperSlope = math.tan(math.radians(UpperAngleLimit))
        lowerSlope = math.tan(math.radians(LowerAngleLimit))
        slopearray += [upperSlope, lowerSlope]
    print('end')
    return slopearray, angle_flag

def realtime_positioning(Position, ratio0, ratio1, ratio2, ratio3, angleturn0, angleturn1, angleturn2, angleturn3, N, padding):   
    slopearray0, angle_flag0 = realtime_getArray(Position, ratio0, 0, angleturn0, angleturn1, angleturn2)
    slopearray1, angle_flag1 = realtime_getArray(Position, ratio1, 1, angleturn0, angleturn1, angleturn2)
    slopearray2, angle_flag2 = realtime_getArray(Position, ratio2, 2, angleturn0, angleturn1, angleturn2)
    '''
    if angle_flag0 == False or angle_flag1 == False or angle_flag2 == False:
        print('angle out of range')
        return [],[]
    '''
    position_x = collections.deque(maxlen=10000)
    position_y = collections.deque(maxlen=10000)
    print('in')
    for count_0 in range(len(slopearray0)):
        for count_1 in range(len(slopearray1)):
            for count_2 in range(len(slopearray2)):
                position_x_add, position_y_add = GetCrossPoint_byslope(Position, slopearray0[count_0], slopearray1[count_1], slopearray2[count_2], N)
                position_x += position_x_add
                position_y += position_y_add
                print(position_y_add)
                print(position_x_add)
    print(position_x)
    return position_x, position_y 

def realtime_positioning_random(Position, ratio0, ratio1, ratio2, ratio3, angleturn0, angleturn1, angleturn2, angleturn3, N, padding):#positioning algoritm by pseudoinverse_4 anchors    
    slopearray0, angle_flag0 = realtime_getArray_random(Position, ratio0, 0, angleturn0, angleturn1, angleturn2)
    slopearray1, angle_flag1 = realtime_getArray_random(Position, ratio1, 1, angleturn0, angleturn1, angleturn2)
    slopearray2, angle_flag2 = realtime_getArray_random(Position, ratio2, 2, angleturn0, angleturn1, angleturn2)
    slopearray = [slopearray0, slopearray1, slopearray2]
    '''
    if angle_flag0 == False or angle_flag1 == False or angle_flag2 == False:
        print('angle out of range (>50)')
        return [],[]
    '''
    
    position_x = collections.deque(maxlen=1000)#for saving positioning data
    position_y = collections.deque(maxlen=1000)
    for main_base in range(N-1): # base0 to 1 and 2
        for main_base_thetas in range(2):
            for other_bases in range(main_base+1,N):
                for other_base_thetas in range(2):
                    #print(Position[main_base],slopearray[main_base][main_base_thetas],Position[other_bases],slopearray[other_bases][other_base_thetas])
                    P_c = GetCrossPoint(Position[main_base],slopearray[main_base][main_base_thetas],Position[other_bases],slopearray[other_bases][other_base_thetas])
                    position_x.append(P_c.x)
                    position_y.append(P_c.y)
                    '''
                    if P_c.x > Position[1][0] or P_c.x < Position[0][0] or P_c.y > Position[2][1] or P_c.y < Position[0][1]:
                        pass
                    else:
                        position_x.append(P_c.x)
                        position_y.append(P_c.y)
                    '''

    return position_x, position_y

def GetCrossPoint_byslope(Position, slope0, slope1, slope2, N):
    slopearray = [slope0, slope1, slope2]
    position_x_add = collections.deque(maxlen=1000)
    position_y_add = collections.deque(maxlen=1000)
    for main_base in range(N-1):
        for other_bases in range(main_base+1,N):
            P_c = GetCrossPoint(Position[main_base],slopearray[main_base],Position[other_bases],slopearray[other_bases])
            if P_c.x > Position[1][0] or P_c.x < Position[0][0] or P_c.y > Position[2][1] or P_c.y < Position[0][1]:
                pass
            else:
                position_x_add.append(P_c.x)
                position_y_add.append(P_c.y)
    return position_x_add, position_y_add