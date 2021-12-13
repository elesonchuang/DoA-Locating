# Import libraries
import RPi.GPIO as GPIO
import time
import csv
import numpy as np  #check if rpi has this module

import RPI_library.gura as gura
import paho.mqtt.client as receive #import library

# Open csv file
f = open('./ground_truths/ground_truth_new.csv', 'w')
writer = csv.writer(f)
total_portion = 10
each_portion = 180/total_portion
sum_signal = 10
diff_signal = 20
angle = 180
record_angle = -90
duty = angle/18 +2
writer.writerow(["Phi [deg]","SUM","DIFF","SUM-DIFF"])

# motor setup
GPIO.setmode(GPIO.BOARD) # Set GPIO numbering mode
GPIO.setup(11,GPIO.OUT)  # Set pin 11 as an output, and define as servo1 as PWM pin
servo1 = GPIO.PWM(11,50) # pin 11 for servo1, pulse 50Hz
servo1.start(0)


base_number = int(input('which base is this: '))
name = 'allen'#str(input('which Wi-Fi AP will you measure?'))
freq = gura.get_Channel('wlan0', name)
print('target wifi SSID: ', name)
print('target wifi freq: ', freq)
interface1 = gura.get_interface(base_number)['sum'] # the difference one
interface2 = gura.get_interface(base_number)['difference']       # the sum one
#interface3 = 'wlan1' # the default one
print('interfaces', interface1, interface2)

servo1.ChangeDutyCycle(duty)

while angle >= 0:
    l_signal1 = []
    l_signal2 = []
    l_r = []
    while min(len(l_signal1), len(l_signal2))<10:
        try:
            data1 = gura.get_Signal(interface1, freq, name)
            signal1 = float(data1['signal'])
            interval1 = float(data1['interval'])
            data2 = gura.get_Signal(interface2, freq, name)
            signal2 = float(data2['signal'])
            interval2 = float(data2['interval'])
            if interval1>2000 or interval2>2000 :
                print('overtime')
                continue
            print('signal1: ',signal1)
            print('signal2: ',signal2)
            r = signal1 - signal2
            print('r: ', r)
            l_signal1.append(signal1)
            l_signal2.append(signal2)
            l_r.append(r)
        except:
            pass
    '''find mean
    diff_signal = sum(l_signal1) / len(l_signal1)
    sum_signal = sum(l_signal2) / len(l_signal2)
    avg_r = sum(l_r) / len(l_r)
    '''
    #find median
    diff_signal = np.median(l_signal1)
    sum_signal = np.median(l_signal2)

    writer.writerow( [int(record_angle), sum_signal, diff_signal ,sum_signal - diff_signal] )
    #print('duty : ', duty)
    angle -= each_portion
    record_angle -= each_portion
    duty = angle/18 +2
    continue_flag = input("ready to turn to degree {} ?".format(angle))
    #servo1.ChangeDutyCycle(duty)
    print('TURNed')
    time.sleep(1)

print("Finish duty cycle")
#Clean things up at the end
servo1.ChangeDutyCycle(2 + 0)
servo1.stop()
GPIO.cleanup()
f.close()
print("Goodbye!")
