import gura
import paho.mqtt.client as receive #import library

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

base_number = int(input('which base is this: '))

server_list = ["192.168.50.117", "192.168.50.60", "192.168.50.229"]	
topic_list = ["temp0", "temp1", "temp2"]
MQTT_SERVER = "192.168.50.117"#server_list[base_number] #specify the broker address
MQTT_PATH = topic_list[base_number] #this is the name of topic, like temp
print('initiating base{} with IP '.format(base_number), MQTT_SERVER)
client = receive.Client()
client.connect(MQTT_SERVER, 1883, 60)
name = 'Wi-Fi'#str(input('which Wi-Fi AP will you measure?'))
freq = gura.get_Channel('wlan0', name)

print('target wifi SSID: ', name)
print('target wifi freq: ', freq)
print('current topic: ', topic_list[base_number])
interface1 = gura.get_interface(base_number)['difference'] # the difference one
interface2 = gura.get_interface(base_number)['sum']       # the sum one
#interface3 = 'wlan1' # the default one
print('interfaces', interface1, interface2)
cnt = 0
while cnt < 100:
    try:
        data1 = gura.get_Signal(interface1, freq, name)
        signal1 = float(data1['signal'])
        interval1 = float(data1['interval'])
        data2 = gura.get_Signal(interface2, freq, name)
        signal2 = float(data2['signal'])
        interval2 = float(data2['interval'])
        if interval1>2000 or interval2>2000 :
            print('overtime')
            pass
        print('signal1: ',signal1)
        print('signal2: ',signal2)
        r = signal1 - signal2
        print('r: ', r)
        client.on_message = on_message
        payload = str(r) + '$' + str(signal2)
        client.publish(MQTT_PATH, payload) # return difference/sum ratio and the sum signal strength
        client.loop_start()
        cnt = cnt + 1 
    except:
        pass
        
