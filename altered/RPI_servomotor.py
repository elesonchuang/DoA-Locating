# Import libraries
import RPi.GPIO as GPIO
import time
import csv

import gura
import paho.mqtt.client as receive #import library

# Open csv file
f = open('ground_truth_new.csv', 'w')
writer = csv.writer(f)
total_portion = 10
each_portion = 180/total_portion
sum_signal = 10
diff_signal = 20
angle = 0
duty = angle*18 +2
writer.writerow(["Phi [deg]","SUM","DIFF","DIFF-SUM"])

# motor setup
GPIO.setmode(GPIO.BOARD) # Set GPIO numbering mode
GPIO.setup(11,GPIO.OUT)  # Set pin 11 as an output, and define as servo1 as PWM pin
servo1 = GPIO.PWM(11,50) # pin 11 for servo1, pulse 50Hz
servo1.start(0)

base_number = int(input('which base is this: '))
name = 'Wi-Fi'#str(input('which Wi-Fi AP will you measure?'))
freq = gura.get_Channel('wlan0', name)
print('target wifi SSID: ', name)
print('target wifi freq: ', freq)
interface1 = gura.get_interface(base_number)['difference'] # the difference one
interface2 = gura.get_interface(base_number)['sum']       # the sum one
#interface3 = 'wlan1' # the default one
print('interfaces', interface1, interface2)

while angle <= 180:
    l_signal1 = []
    l_signal2 = []
    l_r = []
    for i in range(10):
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
            l_signal1.append(signal1)
            l_signal2.append(signal2)
            l_r.append(r)
        except:
            pass

    diff_signal = sum(l_signal1) / len(l_signal1)
    sum_signal = sum(l_signal2) / len(l_signal2)
    avg_r = sum(l_r) / len(l_r)
    writer.writerow( [angle, diff_signal, sum_signal ,diff_signal - sum_signal] )
    #print('duty : ', duty)
    angle += each_portion
    duty = angle/18 +2
    servo1.ChangeDutyCycle(duty)
    time.sleep(1)

print("Finish duty cycle")
#Clean things up at the end
servo1.ChangeDutyCycle(2 + 0)
servo1.stop()
GPIO.cleanup()
f.close()
print("Goodbye!")
