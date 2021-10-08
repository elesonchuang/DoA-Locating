# Import libraries

import time
import csv

# Open csv file
f = open('new_csv.csv', 'w')
writer = csv.writer(f)
total_portion = 30
sum_signal = 10
diff_signal = 20

angle = 0
duty = angle*18 +2
writer.writerow(["Phi [deg]","SUM","DIFF","DIFF-SUM"])

while angle <= 180:
    time.sleep(0.01)
    
    print('duty cycle: ', duty)
    #writer.writerow( str(duty) + ',' + str(diff_signal) + ',' + str(sum_signal) + ',' + str(diff_signal - sum_signal) )
    
    writer.writerow( [angle, diff_signal, sum_signal ,diff_signal - sum_signal] )
    angle += 180 / total_portion
    duty = angle*18 +2

print("Finish duty cycle")

f.close()
print("Goodbye!")
