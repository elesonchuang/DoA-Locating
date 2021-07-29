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
MQTT_PATH = "test" #this is the name of topic, like temp
MQTT_PATH1 = "test1"
MQTT_PATH2 = "test2"
MQTT_PATH3 = "test3"
MQTTlist = [MQTT_PATH, MQTT_PATH1, MQTT_PATH2, MQTT_PATH3]
password = "raspberry"

ratio0 = collections.deque(maxlen=10000)#for saving RSSI ratio data 
ratio1 = collections.deque(maxlen=10000)
ratio2 = collections.deque(maxlen=10000)
ratio3 = collections.deque(maxlen=10000)
positionx = collections.deque(maxlen=10000)#for saving positioning data 
positiony = collections.deque(maxlen=10000)
angleturn2 = 0
angleturn3 = 0

def on_connect(client, userdata, flags, rc):# The callback for when the client receives a CONNECT response from the server.
    for i in range (0, N, 1):
        client.subscribe(MQTTlist[i])
        print("Connected with result code"+str(rc))
    
def reversefunc(phi):

    data2 = pd.read_excel('C:\\Users\\KOBE_NTU\\Desktop\\system gain.xlsx')
    x = np.linspace(0, 50, 51)
    y = data2.iloc[x, 2]
    f = interp1d(y, x, kind = 'linear', fill_value='extrapolate')  # radial basis function interpolator instance
    # print(f)
    di = f(phi)   # interpolated values
    # print(di)
    return di
 
def on_message(client, userdata, msg):# The callback for when a PUBLISH message is received from the server_4 anchors.
      
    if msg.topic == MQTT_PATH:
        # print(msg.topic, msg.payload)
        ratio0.append(msg.payload)
    elif msg.topic == MQTT_PATH1:
        # print(msg.topic, msg.payload)
        ratio1.append(msg.payload)
    elif msg.topic == MQTT_PATH2:
        # print(msg.topic, msg.payload)
        ratio2.append(msg.payload)
    elif msg.topic == MQTT_PATH3:
        # print(msg.topic, msg.payload)
        ratio3.append(msg.payload)

def positioning(ratio0, ratio1, ratio2, ratio3, Position, angleturn0, angleturn1, angleturn2, angleturn3, N):#positioning algoritm by pseudoinverse_4 anchors    

    answerx = []
    answery = []
    final = []

    while len(ratio0) == 0:
        time.sleep(10)
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
    # print(slope)
    # print(b)
    
    # print('anchor1=', ratio1.popleft())
    while len(ratio1) == 0:
        time.sleep(10)
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
        while len(ratio2) == 0:
            time.sleep(10)
        func2 = reversefunc(ratio2.popleft())
        if func2 > 50:
            func2 = 50
        phii2 = - func2 - angleturn2#求出Rx2對Tx角度 (100, 0)
        phi2 = func2 - angleturn2
        if angleturn2 == 90:
            phii2 = angleturn2 - func2
            phi2 = func2 - angleturn2
        # print('2')
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
        
    elif N >= 4:##WTF is this? this elif will never occur!!
        while len(ratio3) == 0:
            time.sleep(10)
        func3 = reversefunc(ratio3.popleft())
        if func > 50:
            func = 50
        phii3 = angleturn3 + func3#求出Rx1對Tx角度 (0, 0)
        phi3 = angleturn3 - func3
        print('3', func3, phii3, phi3)    
        slope3 = math.tan(math.radians(phii3))
        coss3 = math.cos(math.radians(phii3))
        slope3_1 = math.tan(math.radians(phi3))
        coss3_1 = math.cos(math.radians(phi3))
        slopearray3 = np.array([slope3,slope3_1])
        cossarray3 = np.array([coss3, coss3_1])
        b3 = Position[0][1]-slope3*Position[0][0]
        b3_1 = Position[0][1]-slope3_1*Position[0][0]
        # print(b, b_1)
        b3array = np.array([b3, b3_1])
        # print(slope)
        # print(b)    
    if N == 2:
        for k in range(2):
            for l in range(2):
                H = np.array([[-slopearray[k]*cossarray[k],cossarray[k]], [-slopearray1[l]*cossarray1[l],cossarray1[l]]])
                # print('H=',H)
                B = np.array([[barray[k]*cossarray[k]], [b1array[l]*cossarray1[l]]])
                # print('B=',B)
                answer = np.dot(scipy.linalg.pinv(H), B)
                print('answer=',answer)
                answerx.append(answer[0])
                answery.append(answer[1])
                
                d = abs((slopearray[k]*answer[0]-answer[1] + barray[k])*cossarray[k])
                d1 = abs((slopearray1[l]*answer[0]-answer[1] + b1array[l])*cossarray1[l])
                # print(d, d1, d2, d3)
                r = d / np.sqrt((slopearray[k]*cossarray[k])**2 + cossarray[k]**2, dtype = "float64")
                r1 = d1 / np.sqrt((slopearray1[l]*cossarray1[l])**2 + cossarray1[l]**2, dtype = "float64")
                rfinal = r**2 + r1**2
                final.append(rfinal)
    elif N == 3:    
        for k in range(2):
            for l in range(2):
               for m in range(2):
                    H = np.array([[-slopearray[k]*cossarray[k],cossarray[k]], [-slopearray1[l]*cossarray1[l],cossarray1[l]], [-slopearray2[m]*cossarray2[m],cossarray2[m]]])
                    # print('H=',H)
                    B = np.array([[barray[k]*cossarray[k]], [b1array[l]*cossarray1[l]], [b2array[m]*cossarray2[m]]])
                    # print('B=',B)
                    answer = np.dot(scipy.linalg.pinv(H), B)
                    print('answer=',answer)
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
    elif N == 4:
        for k in range(2):
            for l in range(2):
               for m in range(2):
                   for n in range(2):
                        H = np.array([[-slopearray[k]*cossarray[k],cossarray[k]], [-slopearray1[l]*cossarray1[l],cossarray1[l]], [-slopearray2[m]*cossarray2[m],cossarray2[m]], [-slopearray3[n]*cossarray3[n],cossarray3[n]]])
                        # print(H)
                        B = np.array([[barray[k]*cossarray[k]], [b1array[l]*cossarray1[l]], [b2array[m]*cossarray2[m]], [b3array[n]*cossarray3[n]]])
                        # print(B)
                        answer = np.dot(np.linalg.inv(np.dot(H.T, H)), np.dot(H.T, B))
                        print('answer=',answer)
                        answerx.append(answer[0])
                        answery.append(answer[1])
                        
                        d = abs(slopearray[k]*answer[0]-answer[1] + barray[k])
                        d1 = abs(slopearray1[l]*answer[0]-answer[1] + b1array[l])
                        d2 = abs(slopearray2[m]*answer[0]-answer[1] + b2array[m])
                        d3 = abs(slopearray3[n]*answer[0]-answer[1] + b3array[n])
                        # print(d, d1, d2, d3)
                        r = d / (slopearray[k]**2 + 1)**0.5
                        r1 = d1 / (slopearray1[l]**2 + 1)**0.5
                        r2 = d2 / (slopearray2[m]**2 + 1)**0.5
                        r3 = d3 / (slopearray3[n]**2 + 1)**0.5
                        rfinal = r**2 + r1**2 + r2**2 + r3**2
                        final.append(rfinal)                                  
    # residuemin = min(final)
    # print(residuemin)
    # print(final)
    index = final.index(min(final))
    print(index)
    positionx.clear()
    positiony.clear()
    print('x=', answerx[index])
    print('y=', answery[index])
    positionx.append(answerx[index])
    positiony.append(answery[index])

    return positionx, positiony

def animation(i):#animation fuction for positioning
    positionx, positiony = positioning(ratio0, ratio1, ratio2, ratio3, Position, angleturn0, angleturn1, angleturn2, angleturn3, N)
    if len(positionx) > 0 and len(positiony) > 0:
        x = positionx.popleft()
        y = positiony.popleft()
        plt.scatter(x, y, s = 60, marker = '.', color = 'red', alpha = 1) 
        # with open(r'C:\Users\KOBE_NTU\Desktop\定位_2.csv', 'a') as csvw:
        #     csvw.write( '%f'%x + ','+ '%f'%y +','+'\n')    
    else:
        time.sleep(10)

N = int(input('please input numbers of Anchors:'))#input numbers of Anchors
while N > 4 or N < 2: ##WTF is this?
    N = int(input('please input numbers of Anchors again:'))

angleturn0 = int(input('please input anchor0 angle turn:'))#input anchor0 angle turn
angleturn1 = int(input('please input anchor1 angle turn:'))#input anchor1 angle turn
if N >= 3:
    angleturn2 = int(input('please input anchor2 angle turn:'))#input anchor2 angle turn
elif N >= 4: ##WTF is this? this elif will never occur!!
    angleturn3 = int(input('please input anchor3 angle turn:'))#input anchor3 angle turn     
x0, y0 = map(int, input('please input anchor0 position:').split())#input anchor0 Position
x1, y1 = map(float, input('please input anchor1 position:').split())#input anchor1 Position
if N >= 3:
    x2, y2 = map(float, input('please input anchor2 position:').split())#input anchor2 Position
elif N >= 4: ##WTF is this? this elif will never occur!!
    x3, y3 = map(float, input('please input anchor3 position:').split())#input anchor3 Position 
Position = ((x0, y0), (x1, y1))
if N == 3: 
    Position = ((x0, y0), (x1, y1), (x2, y2))
elif N == 4: 
    Position = ((x0, y0), (x1, y1), (x2, y2), (x3, y3))
print(Position)

client = receive.Client()#MQTT subscriber function
client.connect(MQTT_SERVER, 1883, 60)
client.on_connect = on_connect
client.on_message = on_message
client.loop_start()
 
fig = plt.figure()
if N == 2:
    ax = plt.axes(xlim=(0, x1), ylim=(0, x1))
elif N >= 3:
    ax = plt.axes(xlim=(0, x1), ylim=(0, y2))
print('Start animate function !')
ani = FuncAnimation(fig, animation, interval=5) 
time.sleep(5)

plt.scatter(y1/2, y1/2, s = 60, marker = '+', color = 'black', alpha = 1)
plt.scatter(Position[0][0], Position[0][1], s = 400, marker = '*')
plt.scatter(Position[1][0], Position[1][1], s = 400, marker = '*')
if N >= 3:
    plt.scatter(Position[2][0], Position[2][1], s = 400, marker = '*')
elif N >= 4:##WTF is this? this elif will never occur!!
    plt.scatter(Position[3][0], Position[3][1], s = 400, marker = '*')
plt.gca().set_aspect('equal', adjustable='box')
plt.grid()
plt.xlabel('X(M)')
plt.ylabel('Y(M)')


