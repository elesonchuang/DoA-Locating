from GetSignal import *
import paho.mqtt.client as receive #import library

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

base_number = int(input('which base is this: '))

server_list = ["192.168.50.117", "192.168.50.60", "192.168.50.229"]	
path_list = ["temp0", "temp1", "temp2"]
MQTT_SERVER = server_list[base_number] #specify the broker address
MQTT_PATH = path_list[base_number] #this is the name of topic, like temp
print('initiating base{} with IP '.format(base_number), MQTT_SERVER)
client = receive.Client()
client.connect(MQTT_SERVER, 1883, 60)
name = 'Wi-Fi'#str(input('which Wi-Fi AP will you measure?'))
freq = '2437'#channel 6
print('target wifi SSID: ', name)
print('target wifi freq: ', freq)
interface1 = 'wlan0'
interface2 = 'wlan2'
interface3 = 'wlan1' # the default one
cnt = 0
while cnt < 100:
    signal1 = get_Signal(interface1, freq, name)
    signal2 = get_Signal(interface2, freq, name)
    signal3 = get_Signal(interface3, freq, name)
    print('signal1: ',signal1)
    print('signal2: ',signal2) 
    print('signal3: ',signal3) 
    client.on_message = on_message
    client.publish(MQTT_PATH, r)
    client.loop_start()
    cnt = cnt + 1 