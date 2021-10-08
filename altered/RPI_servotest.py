# Import libraries
import RPi.GPIO as GPIO
import time
import csv

import gura
import paho.mqtt.client as receive #import library

# Open csv file

total_portion = 30
each_portion = 180/total_portion
sum_signal = 10
diff_signal = 20
angle = 180
record_angle = -90
duty = angle/18 +2


# motor setup
GPIO.setmode(GPIO.BOARD) # Set GPIO numbering mode
GPIO.setup(11,GPIO.OUT)  # Set pin 11 as an output, and define as servo1 as PWM pin
servo1 = GPIO.PWM(11,50) # pin 11 for servo1, pulse 50Hz
servo1.start(0)

servo1.ChangeDutyCycle(duty)

while angle >=0:

    #print('duty : ', duty)
    angle -= each_portion
    record_angle -= each_portion
    duty = angle/18 +2
    servo1.ChangeDutyCycle(duty)
    print('TURNING')
    time.sleep(3)

print("Finish duty cycle")
#Clean things up at the end
servo1.ChangeDutyCycle(2 + 0)
servo1.stop()
GPIO.cleanup()

print("Goodbye!")
