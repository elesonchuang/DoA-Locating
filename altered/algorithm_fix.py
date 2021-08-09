from numpy.lib.function_base import angle
import paho.mqtt.client as receive #import library
import collections, time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import lib_algo
 
MQTT_SERVER = "192.168.50.117" #specify the broker address, it can be IP of raspberry pi or simply localhost
MQTT_PATH = "temp0" #this is the name of topic, like temp
MQTT_PATH1 = "temp1"
MQTT_PATH2 = "temp2"
MQTT_PATH3 = "temp3"
MQTTlist = [MQTT_PATH, MQTT_PATH1, MQTT_PATH2, MQTT_PATH3]
password = "raspberry"

test_mode = True#False
# difference-sum ratio
if test_mode == True:
    ratio0 = collections.deque([-6,7,0,-3,-6,-5,3,41,-1,-1],maxlen=1000)#
    ratio1 = collections.deque([-6,7,0,-3,-6,-5,3,41,-1,-1],maxlen=1000)#
    ratio2 = collections.deque([-3,-6,1,-2,1,-1,1,-5,-4,-2],maxlen=1000)#
    ratio3 = collections.deque([],maxlen=1000)
else:
    ratio0 = collections.deque(maxlen=1000)#
    ratio1 = collections.deque(maxlen=1000)#
    ratio2 = collections.deque(maxlen=1000)#
    ratio3 = collections.deque(maxlen=1000)
# sum signal strength
ss0 = collections.deque(maxlen=1000)
ss1 = collections.deque(maxlen=1000)
ss2 = collections.deque(maxlen=1000)

position_x = collections.deque(maxlen=1000)#for saving positioning data 
position_y = collections.deque(maxlen=1000)
angleturn2 = 0
angleturn3 = 0
padding = 5

########################## inputs #############################################
N = 3
angleturn0 = 45#int(input('please input anchor0 angle turn:'))#input anchor0 angle turn
angleturn1 = 45#180-50#int(input('please input anchor1 angle turn:'))#input anchor1 angle turn
angleturn2 = 270#360-80#int(input('please input anchor2 angle turn:'))#input anchor2 angle turn

x0, y0 = (0,0)#map(float, input('please input anchor0 position:').split())#input anchor0 Position
x1, y1 = (3.6,0)#map(float, input('please input anchor1 position:').split())#input anchor1 Position
x2, y2 = (1.8,3.6)#map(float, input('please input anchor2 position:').split())#input anchor2 Position
Position = ((x0, y0), (x1, y1), (x2, y2))
print(Position)

left_BOARDER = x0
right_BOARDER = x1
lower_BOARDER = y0
upper_BOARDER = y2

test_flag = 0
#############################################################################

def on_connect(client, userdata, flags, rc):# The callback for when the client receives a CONNECT response from the server.   
    #print('MQTT connecting')
    for i in range (0, N, 1):
        client.subscribe(MQTTlist[i])
        print("Connected with result code "+str(rc))
 
def on_message(client, userdata, msg):# The callback for when a PUBLISH message is received from the server_4 anchors.     
    if msg.topic == MQTT_PATH:
        #print(msg.topic, msg.payload)
        payload = msg.payload.decode()
        ratio0.append(float(payload.split('$')[0]))
        ss0.append(float(payload.split('$')[1]))
    elif msg.topic == MQTT_PATH1:
        #print(msg.topic, msg.payload)
        payload = msg.payload.decode()
        ratio1.append(float(payload.split('$')[0]))
        ss1.append(float(payload.split('$')[1]))
    elif msg.topic == MQTT_PATH2:
        #print(msg.topic, msg.payload)
        payload = msg.payload.decode() 
        ratio2.append(float(payload.split('$')[0]))
        ss2.append(float(payload.split('$')[1]))
    elif msg.topic == MQTT_PATH3:
        # print(msg.topic, msg.payload)
        ratio3.append(msg.payload[0])

def animation(i):#animation fuction for positioning
    position_x, position_y = lib_algo.positioning(Position, ratio0, ratio1, ratio2, ratio3, angleturn0, angleturn1, angleturn2, angleturn3, N, padding)
    #position_x, position_y = lib_algo.delete_far_point(Position, far_list[i], position_x, position_y)
    global test_flag
    while len(position_x) > 0 and len(position_y) > 0 :#and test_flag==0:
        x = position_x.popleft()
        y = position_y.popleft()
        plt.scatter(x, y, s = 60, marker = '.', color = 'red', alpha = 1) 
    test_flag += 1

def realtime_animation(i):#animation fuction for positioning
    position_x, position_y = lib_algo.realtime_positioning_random(Position, ratio0, ratio1, ratio2, ratio3, angleturn0, angleturn1, angleturn2, angleturn3, N, padding)
    #position_x, position_y = lib_algo.delete_far_point(Position, far_list[i], position_x, position_y)
    global test_flag
    while len(position_x) > 0 and len(position_y) > 0 :#and test_flag==0:
        x = position_x.popleft()
        y = position_y.popleft()
        plt.scatter(x, y, s = 60, marker = '.', color = 'red', alpha = 1) 
    test_flag += 1
    
if test_mode == True:
    print('running under testing mode')
else:
    print('start listening')
    client = receive.Client() #MQTT subscriber function
    client.connect(MQTT_SERVER, 1883, 60)
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_start()

total_x = 0
total_y = 0
total_n = 0

fig = plt.figure()
ax = plt.axes(xlim=(left_BOARDER-1, right_BOARDER+1), ylim=(lower_BOARDER-1, upper_BOARDER+1))
plt.scatter(y1/2, y1/2, s = 60, marker = '+', color = 'black', alpha = 1)
plt.scatter(Position[0][0], Position[0][1], s = 400, marker = '*')
plt.scatter(Position[1][0], Position[1][1], s = 400, marker = '*')
plt.scatter(Position[2][0], Position[2][1], s = 400, marker = '*')

while len(ratio0)+len(ratio1)+len(ratio2)<31:
    print('report ratio0 len: ', len(ratio0))
    print('report ratio1 len: ', len(ratio1))
    print('report ratio2 len: ', len(ratio2))
    far_list = lib_algo.get_far_list(ss0, ss1, ss2)
    print('Start animate function !')
    
    ani = FuncAnimation(fig, realtime_animation, interval=5) 
    plt.show()
   
    time.sleep(5)

ani = FuncAnimation(fig, realtime_animation, interval=5)
time.sleep(1)
plt.gca().set_aspect('equal', adjustable='box')
plt.grid()
plt.xlabel('X(M)')
plt.ylabel('Y(M)')
plt.show()