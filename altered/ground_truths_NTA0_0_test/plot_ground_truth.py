import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import pandas as pd
import sys
data = pd.read_csv('ground_truth_new.csv')
############### parameters
data_num = len(data) #number of data
angle_portion = 180/(data_num-1) #angle of each turn
###############

index = np.linspace(0, data_num-1, data_num)  #to read the csv file
y = data.iloc[index, int(sys.argv[1])]  #get the DIFF-SUM 

arr = np.array([])
for i in range(len(y)):
    arr = np.append(arr, y[i]) #store DIFF-SUM into array
x_axis = np.arange(0, 181, angle_portion)   #x-axis

f = interp1d(x_axis, arr, kind = 'linear', fill_value='extrapolate')  # radial basis function interpolator instance
value = f(x_axis)   # use interpolation function returned by `interp1d`

plt.plot(x_axis, value, 'o', x_axis, value, '-')
plt.show()