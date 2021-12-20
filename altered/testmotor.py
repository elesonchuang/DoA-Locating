import RPi.GPIO as GPIO

angle = 180
duty = 12
GPIO.setmode(GPIO.BOARD) # Set GPIO numbering mode
GPIO.setup(11,GPIO.OUT)  # Set pin 11 as an output, and define as servo1 as PWM pin
servo1 = GPIO.PWM(11,50) # pin 11 for servo1, pulse 50Hz
servo1.start(0)
a = "0"
total_portion = 10
each_portion = 180/total_portion
i = 0
change_times = 10
while duty > 0:
   # i+=1
    #last_angle = angle
    #angle -= each_portion
    #duty = (last_angle / 3.6 + 2) + ((angle - last_angle) / 3.6) * i / change_times
    #print(i)
    print(duty)
    servo1.ChangeDutyCycle(duty)
    duty -= 0.2
    a = str(input())
servo1.ChangeDutyCycle(2 + 0)
servo1.stop()
GPIO.cleanup()
