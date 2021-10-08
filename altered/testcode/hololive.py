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
 
MQTT_SERVER = "192.168.50.117" #specify the broker address, it can be IP of raspberry pi or simply localhost
MQTT_PATH = "temp0" #this is the name of topic, like temp
MQTT_PATH1 = "temp1"
MQTT_PATH2 = "temp2"
MQTT_PATH3 = "temp3"
MQTTlist = [MQTT_PATH, MQTT_PATH1, MQTT_PATH2, MQTT_PATH3]
password = "raspberry"

ratio0 = collections.deque([-6,7,0,-3,-6,-5,3,41,-1,-1],maxlen=1000)#collections.deque(maxlen=10000)
ratio1 = collections.deque([-6,7,0,-3,-6,-5,3,41,-1,-1],maxlen=1000)#collections.deque(maxlen=10000)
ratio2 = collections.deque([-3,-6,1,-2,1,-1,1,-5,-4,-2],maxlen=1000)#collections.deque(maxlen=10000)
ratio3 = collections.deque([],maxlen=10000)
positionx = collections.deque(maxlen=10000)#for saving positioning data 
positiony = collections.deque(maxlen=10000)
angleturn2 = 0
angleturn3 = 0

########################## inputs #############################################
N = 3
angleturn0 = 45#int(input('please input anchor0 angle turn:'))#input anchor0 angle turn
angleturn1 = 45#int(input('please input anchor1 angle turn:'))#input anchor1 angle turn
angleturn2 = 90#int(input('please input anchor2 angle turn:'))#input anchor2 angle turn

x0, y0 = (0,0)#map(float, input('please input anchor0 position:').split())#input anchor0 Position
x1, y1 = (3.6,0)#map(float, input('please input anchor1 position:').split())#input anchor1 Position
x2, y2 = (1.8,3.6)#map(float, input('please input anchor2 position:').split())#input anchor2 Position
Position = ((x0, y0), (x1, y1), (x2, y2))
print(Position)

left_BOARDER = x0
right_BOARDER = x1
lower_BOARDER = y0
upper_BOARDER = y2


#############################################################################

def on_connect(client, userdata, flags, rc):# The callback for when the client receives a CONNECT response from the server.   
    #print('MQTT connecting')
    for i in range (0, N, 1):
        client.subscribe(MQTTlist[i])
        print("Connected with result code "+str(rc))
    
def reversefunc(phi):
    #print('reversefunc')
    data2 = pd.read_excel('/Users/chenfayu/Documents/@@台灣大學電機系＿三上專題研究/演算法/DoA-Locating/ground_truth.xlsx')
    x = np.linspace(0, 50, 51)
    y = data2.iloc[x, 2]
    f = interp1d(y, x, kind = 'linear', fill_value='extrapolate')  # radial basis function interpolator instance
    di = f(phi)
    return di
 
def on_message(client, userdata, msg):# The callback for when a PUBLISH message is received from the server_4 anchors.     
    if msg.topic == MQTT_PATH:
        #print(msg.topic, msg.payload)
        ratio0.append(msg.payload)
    elif msg.topic == MQTT_PATH1:
        #print(msg.topic, msg.payload)
        ratio1.append(msg.payload)
    elif msg.topic == MQTT_PATH2:
        #print(msg.topic, msg.payload)
        ratio2.append(msg.payload)
    elif msg.topic == MQTT_PATH3:
        # print(msg.topic, msg.payload)
        ratio3.append(msg.payload)

    if len(ratio0) % 10 ==0:
        print('ratio0 len: ',len(ratio0))
    if len(ratio1) % 10 ==0:
        print('ratio1 len: ',len(ratio1))
    if len(ratio2) % 10 ==0:
        print('ratio2 len: ',len(ratio2))

def getArray(ratio, base_num, angleturn0, angleturn1, angleturn2):
    if len(ratio) == 0:
        print('base{} finished'.format(base_num))
        exit = str(input('ready to end?(Y/N) :'))
        quit()
    dp_angle = reversefunc(ratio.popleft()) # displacement angle
    if dp_angle > 50:
        print('base', base_num, 'angle miss')
        angle_flag = False
        return ([], [], [], angle_flag)
    else:
        angle_flag = True
    
    angleturn_switcher={
        0: angleturn0,
        1: angleturn1,
        2: angleturn2,
        3: angleturn3
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
    UpperAngleLimit = UpperAngleLimit_switcher.get(base_num,"Invalid upper angle limit")
    LowerAngleLimit = LowerAngleLimit_switcher.get(base_num,"Invalid lower angle limit")
    if base_num == 2 and angleturn2 == 90:
            UpperAngleLimit = angleturn2 - dp_angle
            LowerAngleLimit = dp_angle - angleturn2
    
    upperSlope = math.tan(math.radians(UpperAngleLimit))
    lowerSlope = math.tan(math.radians(LowerAngleLimit))
    upperCos = math.cos(math.radians(UpperAngleLimit))
    lowerCos = math.cos(math.radians(LowerAngleLimit))
    slopearray = np.array([upperSlope,lowerSlope])
    cossarray = np.array([upperCos,lowerCos])
    b_1 = Position[base_num][1] - upperSlope*Position[base_num][0]
    b_2 = Position[base_num][1] - lowerSlope*Position[base_num][0]
    barray = np.array([b_1, b_2])

    return (slopearray, cossarray, barray, angle_flag)    

def positioning(ratio0, ratio1, ratio2, ratio3, Position, angleturn0, angleturn1, angleturn2, angleturn3, N):#positioning algoritm by pseudoinverse_4 anchors    

    answerx = []
    answery = []
    final = []
    slopearray0, cossarray0, b0array, angle_flag0= getArray(ratio0, 0, angleturn0, angleturn1, angleturn2)
    slopearray1, cossarray1, b1array, angle_flag1= getArray(ratio1, 1, angleturn0, angleturn1, angleturn2)
    slopearray2, cossarray2, b2array, angle_flag2= getArray(ratio2, 2, angleturn0, angleturn1, angleturn2)
    if angle_flag0 == False or angle_flag1 == False or angle_flag2 == False:
        return [], []

    if N == 3:    
        for k in range(2):
            for l in range(2):
               for m in range(2):
                    H = np.array([[-slopearray0[k]*cossarray0[k],cossarray0[k]], [-slopearray1[l]*cossarray1[l],cossarray1[l]], [-slopearray2[m]*cossarray2[m],cossarray2[m]]])
                    # print('H=',H)
                    B = np.array([[b0array[k]*cossarray0[k]], [b1array[l]*cossarray1[l]], [b2array[m]*cossarray2[m]]])
                    # print('B=',B)
                    answer = np.dot(scipy.linalg.pinv(H), B)
                    #print('answer=',answer)
                    answerx.append(answer[0])
                    answery.append(answer[1])
                    
                    d = abs((slopearray0[k]*answer[0]-answer[1] + b0array[k])*cossarray0[k])
                    d1 = abs((slopearray1[l]*answer[0]-answer[1] + b1array[l])*cossarray1[l])
                    d2 = abs((slopearray2[m]*answer[0]-answer[1] + b2array[m])*cossarray2[m])
                    # print(d, d1, d2, d3)
                    r = d / np.sqrt((slopearray0[k]*cossarray0[k])**2 + cossarray0[k]**2, dtype = "float64")
                    r1 = d1 / np.sqrt((slopearray1[l]*cossarray1[l])**2 + cossarray1[l]**2, dtype = "float64")
                    r2 = d2 / np.sqrt((slopearray2[m]*cossarray2[m])**2 + cossarray2[m]**2, dtype = "float64")
                    rfinal = r**2 + r1**2 + r2**2
                    final.append(rfinal)

    #index = final.index(min(final))
    #print('index: ', index)
    positionx.clear()
    positiony.clear()
    #print('x= ', answerx[index])
    #print('y= ', answery[index])
    for i in range(len(final)):
        positionx.append(answerx[i])
        positiony.append(answery[i])

    return positionx, positiony

def animation(i):#animation fuction for positioning
    positionx, positiony = positioning(ratio0, ratio1, ratio2, ratio3, Position, angleturn0, angleturn1, angleturn2, angleturn3, N)
    while len(positionx) > 0 and len(positiony) > 0:
        x = positionx.popleft()
        y = positiony.popleft()
        global total_x
        global total_y
        global total_n
        total_x += x
        total_y += y
        total_n += 1
        plt.scatter(total_x/total_n, total_y/total_n, s = 60, marker = '.', color = 'black', alpha = 1)
        plt.scatter(x, y, s = 60, marker = '.', color = 'red', alpha = 1) 

        # with open(r'C:\Users\KOBE_NTU\Desktop\定位_2.csv', 'a') as csvw:
        #     csvw.write( '%f'%x + ','+ '%f'%y +','+'\n')    
    #else:
        #print('angle not good')
    #    pass
'''
client = receive.Client()#MQTT subscriber function
client.connect(MQTT_SERVER, 1883, 60)
client.on_connect = on_connect
client.on_message = on_message
client.loop_start()
'''
while len(ratio0)+len(ratio1)+len(ratio2)<27:
    print('report ratio0 len: ', len(ratio0))
    print('report ratio1 len: ', len(ratio1))
    print('report ratio2 len: ', len(ratio2))
    time.sleep(10)

print('Start animate function !')
total_x = 0
total_y = 0
total_n = 0

fig = plt.figure()
#ax = plt.axes(xlim=(0, x1), ylim=(0, y2))
ax = plt.axes(xlim=(left_BOARDER-20, right_BOARDER+20), ylim=(lower_BOARDER-20, upper_BOARDER+20))
ani = FuncAnimation(fig, animation, interval=5) 
time.sleep(5)

plt.scatter(y1/2, y1/2, s = 60, marker = '+', color = 'black', alpha = 1)

######## draw base location ########
plt.scatter(Position[0][0], Position[0][1], s = 400, marker = '*')
plt.scatter(Position[1][0], Position[1][1], s = 400, marker = '*')
plt.scatter(Position[2][0], Position[2][1], s = 400, marker = '*')
plt.gca().set_aspect('equal', adjustable='box')
plt.grid()
plt.xlabel('X(M)')
plt.ylabel('Y(M)')
plt.show()