from numpy.lib.function_base import angle
import paho.mqtt.client as receive #import library
import collections, time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
 
MQTT_SERVER = "192.168.50.31" #specify the broker address, it can be IP of raspberry pi or simply localhost
MQTT_PATH = "temp0" #this is the name of topic, like temp
MQTT_PATH1 = "temp1"
MQTT_PATH2 = "temp2"
MQTT_PATH3 = "temp3"
MQTTlist = [MQTT_PATH, "signal", MQTT_PATH2, MQTT_PATH3]
password = "raspberry"
N=1
sum = 0
test_mode = False
# difference-sum ratio
if test_mode == True:
    ratio0 = collections.deque([-6,7,0,-3,-6,-5,3,41,-1,-1],maxlen=1000)
    ratio1 = collections.deque([-6,7,0,-3,-6,-5,3,41,-1,-1],maxlen=1000)
    ratio2 = collections.deque([-3,-6,1,-2,1,-1,1,-5,-4,-2],maxlen=1000)
    
    ratio3 = collections.deque([],maxlen=1000)
else:
    ratio0 = collections.deque(maxlen=1000)#
    ratio1 = collections.deque(maxlen=1000)#
    ratio2 = collections.deque(maxlen=1000)#
    ratio3 = collections.deque(maxlen=1000)
    signal0 = []
    signal1 = []

#############################################################################

def on_connect(client, userdata, flags, rc):# The callback for when the client receives a CONNECT response from the server.   
    #print('MQTT connecting')
    for i in range (0, N, 1):
        client.subscribe("signal")
        print("Connected with result code "+str(rc))
 
def on_message(client, userdata, msg):# The callback for when a PUBLISH message is received from the server_4 anchors.     
    if msg.topic == "signal":
        #print(msg.topic, msg.payload)
        payload = msg.payload.decode()
        signal0.append(float(payload.split('$')[0]))
        global sum
        sum += float(payload.split('$')[0])
        #signal1.append(float(payload.split('$')[1]))

print('start listening')
client = receive.Client() #MQTT subscriber function
client.connect(MQTT_SERVER, 1883, 60)
client.on_connect = on_connect
client.on_message = on_message
client.loop_start()
while len(signal0)<100 :
    print('report signal0 len: ', len(signal0))
    #print('report signal1 len: ', len(signal1))
    time.sleep(5)

fig, axs = plt.subplots(1)
axs.boxplot(signal0)
axs.set_title('31:9b'+'  new2 average: '+ str(sum/len(signal0)))
#axs[1].boxplot(signal1)
print('average: ', sum/len(signal0))
plt.show()