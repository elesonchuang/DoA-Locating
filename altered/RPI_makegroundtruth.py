# Import libraries
import RPi.GPIO as GPIO
import time
import csv

import RPI_library.gura as gura
import paho.mqtt.client as receive #import library

# Open csv file
f = open('./ground_truths/ground_truth_new.csv', 'w')
f_sum = open('./ground_truths/ground_truth_sum.csv', 'w')
f_diff = open('./ground_truths/ground_truth_diff.csv', 'w')
f_ratio = open('./ground_truths/ground_truth_ratio.csv', 'w')
writer = csv.writer(f)
total_portion = 90
each_portion = 180/total_portion
sum_signal = 10
diff_signal = 20
angle = 0
record_angle = -90
duty = angle/18 +2
writer.writerow(["Phi [deg]","SUM","DIFF","SUM-DIFF"])
f_sum.write("Phi [deg],data\n")
f_diff.write("Phi [deg],data\n")
f_ratio.write("Phi [deg],data\n")
# motor setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) # Set GPIO numbering mode
GPIO.setup(11,GPIO.OUT)  # Set pin 11 as an output, and define as servo1 as PWM pin
servo1 = GPIO.PWM(11,50) # pin 11 for servo1, pulse 50Hz
servo1.start(0)


base_number = int(input('which base is this: '))
name = 'EEEEEE'#str(input('which Wi-Fi AP will you measure?'))
freq = gura.get_Channel('wlan0', name)
while freq == 0:
    time.sleep(5)
    freq = gura.get_Channel('wlan0', name)
    print('target wifi SSID: ', name)
    print('target wifi freq: ', freq)
interface1 = gura.get_interface(base_number)['sum'] # the difference one
interface2 = gura.get_interface(base_number)['difference']       # the sum one
#interface3 = 'wlan1' # the default one
print('interfaces', interface1, interface2)
print('ssid:', name)
print('freq', freq)
servo1.ChangeDutyCycle(duty)

count_time = int(input("how many times to count:"))

while angle <= 180:
    l_signal1 = []
    l_signal2 = []
    l_r = []
    f_sum.write(str(int(record_angle)) )
    f_diff.write(str(int(record_angle)) )
    f_ratio.write(str(int(record_angle)) )
    while min(len(l_signal1), len(l_signal2)) < count_time:
        try:
            # sum
            data1 = gura.get_Signal(interface1, freq, name)
            signal1 = float(data1['signal'])
            interval1 = float(data1['interval'])
            # diff
            data2 = gura.get_Signal(interface2, freq, name)
            signal2 = float(data2['signal'])
            interval2 = float(data2['interval'])
            if interval1>2000 or interval2>2000 :
                print('overtime')
                continue
            print('signal1: ',signal1)
            f_sum.write("," + str(signal1))
            print('signal2: ',signal2)
            f_diff.write("," + str(signal2))
            r = signal1 - signal2
            print('r: ', r)
            f_ratio.write("," + str(int(r)))

            l_signal1.append(signal1)
            l_signal2.append(signal2)
            l_r.append(r)
        except:
            print("gura<3")

    sum_signal = sum(l_signal1) / len(l_signal1)
    diff_signal = sum(l_signal2) / len(l_signal2)
    avg_r = sum(l_r) / len(l_r)
    writer.writerow( [int(record_angle), sum_signal, diff_signal ,sum_signal - diff_signal] )
    f_sum.write("\n")
    f_diff.write("\n")
    f_ratio.write("\n")
    print('duty : ', duty)
    angle += each_portion
    record_angle += each_portion
    duty = angle/18 +2
    servo1.ChangeDutyCycle(duty)
    print('TURNING')
    # print('Please turn to %.2f degree' %angle)
    # input()
    # time.sleep(1)
    print('Now turn to %.2f degree' %angle)
print("Finish duty cycle")
#Clean things up at the end
servo1.ChangeDutyCycle(2 + 0)
servo1.stop()
GPIO.cleanup()
f.close()
f_sum.close()
f_diff.close()
f_ratio.close()
print("Goodbye!")
