import paho.mqtt.client as receive #import library
import numpy as np
import math
import collections, time
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
from scipy.interpolate import interp1d
import scipy
 
MQTT_SERVER = "192.168.50.117" #specify the broker address, it can be IP of raspberry pi or simply localhost
MQTT_PATH = "temp0" #this is the name of topic, like temp
MQTT_PATH1 = "temp1"
MQTT_PATH2 = "temp2"
MQTT_PATH3 = "temp3"
MQTTlist = [MQTT_PATH, MQTT_PATH1, MQTT_PATH2, MQTT_PATH3]
password = "raspberry"

ratio0 = collections.deque([-6,7,0,-3,-6,-5,3,41,-1,-1],maxlen=10000)#collections.deque(maxlen=10000)
ratio1 = collections.deque([26,26,28,30,32,30,30,26,32,22],maxlen=10000)#collections.deque(maxlen=10000)
ratio2 = collections.deque([-3,-6,1,-2,1,-1,1,-5,-4,-2],maxlen=10000)#collections.deque(maxlen=10000)
ratio3 = collections.deque([],maxlen=10000)
positionx = collections.deque(maxlen=10000)#for saving positioning data 
positiony = collections.deque(maxlen=10000)
angleturn2 = 0
angleturn3 = 0

########################## inputs #############################################
N = 3
angleturn0 = 0#int(input('please input anchor0 angle turn:'))#input anchor0 angle turn
angleturn1 = 0#int(input('please input anchor1 angle turn:'))#input anchor1 angle turn
angleturn2 = 0#int(input('please input anchor2 angle turn:'))#input anchor2 angle turn

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
    print('MQTT connecting')
    for i in range (0, N, 1):
        client.subscribe(MQTTlist[i])
        print("Connected with result code "+str(rc))
    
def reversefunc(phi):
    print('reversefunc')
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

def positioning(ratio0, ratio1, ratio2, ratio3, Position, angleturn0, angleturn1, angleturn2, angleturn3, N):#positioning algoritm by pseudoinverse_4 anchors    
    print('inside positioning')

    answerx = []
    answery = []
    final = []

    if len(ratio0) == 0:
        print('base0 finished')
        exit = str(input('ready to end?(Y/N) :'))
    func = reversefunc(ratio0.popleft())
    if func > 50:
        func = 50
    phii = angleturn0 + func#求出Rx1對Tx角度 (0, 0)
    phi = angleturn0 - func
    print('0', func, phii, phi)    
    slope = math.tan(math.radians(phii))
    coss = math.cos(math.radians(phii))
    slope_1 = math.tan(math.radians(phi))
    coss_1 = math.cos(math.radians(phi))
    slopearray = np.array([slope,slope_1])
    cossarray = np.array([coss, coss_1])
    b = Position[0][1]-slope*Position[0][0]
    b_1 = Position[0][1]-slope_1*Position[0][0]
    # print(b, b_1)
    barray = np.array([b, b_1])

    if len(ratio1) == 0:
        print('base1 finished')
        exit = str(input('ready to end?(Y/N) :'))
    func1 = reversefunc(ratio1.popleft())
    if func1 > 50:
        func1 = 50
    phii1 = - func1 - angleturn1#求出Rx2對Tx角度 (100, 0)
    phi1 = func1 - angleturn1
    # print('1')
    print('1', func1, phii1, phi1)
    slope1 = math.tan(math.radians(phii1))
    coss1 = math.cos(math.radians(phii1))
    slope1_1 = math.tan(math.radians(phi1))
    coss1_1 = math.cos(math.radians(phi1))
    slopearray1 = np.array([slope1,slope1_1])
    cossarray1 = np.array([coss1, coss1_1])
    # print(slope1)
    b1 = Position[1][1]-slope1*Position[1][0]
    b1_1 = Position[1][1]-slope1_1*Position[1][0]
    # print(b1, b1_1)
    b1array = np.array([b1, b1_1])
    
    if N >= 3:
        if len(ratio2) == 0:
            print('base2 finished')
            exit = str(input('ready to end?(Y/N) :'))
        func2 = reversefunc(ratio2.popleft())
        if func2 > 50:
            func2 = 50
        phii2 = - func2 - angleturn2#求出Rx2對Tx角度 (100, 0)
        phi2 = func2 - angleturn2
        if angleturn2 == 90:
            phii2 = angleturn2 - func2
            phi2 = func2 - angleturn2
        print('2', func2, phii2, phi2)
        slope2 = math.tan(math.radians(phii2))
        coss2 = math.cos(math.radians(phii2))
        slope2_1 = math.tan(math.radians(phi2))
        coss2_1 = math.cos(math.radians(phi2))
        slopearray2 = np.array([slope2,slope2_1])
        cossarray2 = np.array([coss2, coss2_1])
        # print(slope2)
        b2 = Position[2][1] - slope2*Position[2][0]
        b2_1 = Position[2][1] - slope2_1*Position[2][0]
        # print(b2, b2_1)
        b2array = np.array([b2, b2_1])
        # print(b2)
  
    if N == 3:    
        for k in range(2):
            for l in range(2):
               for m in range(2):
                    H = np.array([[-slopearray[k]*cossarray[k],cossarray[k]], [-slopearray1[l]*cossarray1[l],cossarray1[l]], [-slopearray2[m]*cossarray2[m],cossarray2[m]]])
                    # print('H=',H)
                    B = np.array([[barray[k]*cossarray[k]], [b1array[l]*cossarray1[l]], [b2array[m]*cossarray2[m]]])
                    # print('B=',B)
                    answer = np.dot(scipy.linalg.pinv(H), B)
                    #print('answer=',answer)
                    answerx.append(answer[0])
                    answery.append(answer[1])
                    
                    d = abs((slopearray[k]*answer[0]-answer[1] + barray[k])*cossarray[k])
                    d1 = abs((slopearray1[l]*answer[0]-answer[1] + b1array[l])*cossarray1[l])
                    d2 = abs((slopearray2[m]*answer[0]-answer[1] + b2array[m])*cossarray2[m])
                    # print(d, d1, d2, d3)
                    r = d / np.sqrt((slopearray[k]*cossarray[k])**2 + cossarray[k]**2, dtype = "float64")
                    r1 = d1 / np.sqrt((slopearray1[l]*cossarray1[l])**2 + cossarray1[l]**2, dtype = "float64")
                    r2 = d2 / np.sqrt((slopearray2[m]*cossarray2[m])**2 + cossarray2[m]**2, dtype = "float64")
                    rfinal = r**2 + r1**2 + r2**2
                    final.append(rfinal)

    index = final.index(min(final))
    #print('index: ', index)
    positionx.clear()
    positiony.clear()
    print('x= ', answerx[index])
    print('y= ', answery[index])
    positionx.append(answerx[index])
    positiony.append(answery[index])

    return positionx, positiony

def animation(i):#animation fuction for positioning
    print('inside animation')
    positionx, positiony = positioning(ratio0, ratio1, ratio2, ratio3, Position, angleturn0, angleturn1, angleturn2, angleturn3, N)
    if len(positionx) > 0 and len(positiony) > 0:
        x = positionx.popleft()
        y = positiony.popleft()
        plt.scatter(x, y, s = 60, marker = '.', color = 'red', alpha = 1) 
        '''
        if (x > right_BOARDER):
            right_BOARDER = x
        elif (x < left_BOARDER):
            left_BOARDER = x
        if (y > upper_BOARDER):
            upper_BOARDER = x
        elif (y < lower_BOARDER):
            lower_BOARDER = x
        '''

        # with open(r'C:\Users\KOBE_NTU\Desktop\定位_2.csv', 'a') as csvw:
        #     csvw.write( '%f'%x + ','+ '%f'%y +','+'\n')    
    else:
        print('into sleep 10')
        time.sleep(10)

print('Start animate function !')

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