###########################################################################
# DATE: 2021.12.23
# REQUIREMENT: this file has to be put in a directory with following files in it
#               1. ground_truth_ratio.csv
#               2. ground_truth_reweight.csv (can be generated by this code)
###########################################################################


import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import pandas as pd
import sys
import csv
import statistics
import plotly.graph_objects as go
import plotly.express as px
import statsmodels.api as sm
from scipy.signal import savgol_filter

###########################################################################
################ generate reweight file  ##################################
###########################################################################
def OUTPUT_writter(weighted_power):
    output = open('ground_truth_reweight.csv', 'w')
    writer = csv.writer(output)
    writer.writerow(["Phi [deg]","SUM-DIFF"])

    with open('ground_truth_ratio.csv', newline='') as input:
        reader = csv.reader(input)
        input_data = list(reader)
        input_data=input_data[1:]
    for i in range(len(input_data)):
        #input_data[i]=input_data[i][1:]
        input_data[i]=np.array(input_data[i]).astype(np.float)
        STD=statistics.pstdev(input_data[i])
        writer.writerow( [input_data[i][0], reweight_generator(input_data[i][1:], weighted_power, STD)] )
    
def reweight_generator(input_list, weighted_power, STD): 
    total_weight=0
    weighted_sum=0
    ratio_mean = sum(input_list) / len(input_list)
    for each in input_list:
        #difference = abs(each-ratio_mean)
        difference = abs(each-ratio_mean)/STD
        if(difference==0):
            weight=1
        else:
            weight = 1/(difference**weighted_power)
        weighted_sum+=each*weight
        total_weight+=weight
    return weighted_sum/total_weight

###########################################################################
################ plot it out  #############################################
###########################################################################
def CSV_plotter(data):
    data_num = len(data) #number of data
    angle_portion = 180/(data_num-1) #angle of each turn
    index = np.linspace(0, data_num-1, data_num)  #to read the csv file
    y = data.iloc[index, 1]  #get the DIFF-SUM 
    arr = np.array([])
    for i in range(len(y)):
        arr = np.append(arr, y[i]) #store DIFF-SUM into array
    x_axis = np.arange(0, 181, angle_portion)   #x-axis

    f = interp1d(x_axis, arr, kind = 'linear', fill_value='extrapolate')  # radial basis function interpolator instance
    value = f(x_axis)   # use interpolation function returned by `interp1d`
    plt.plot(x_axis, value, 'o', x_axis, value, '-')
    plt.show()

###########################################################################
################ Lowess filter  ###########################################
###########################################################################
def LOWESS_filter():
    df = pd.read_csv('ground_truth_reweight.csv', encoding='utf-8')

    lowess = sm.nonparametric.lowess
    x=df['Phi [deg]'].values 
    y=df['SUM-DIFF'].values
    y_hat2_3 = lowess(y, x) # note, default frac=2/3
    y_hat1_5 = lowess(y, x, frac=1/5)
    y_hat1_4 = lowess(y, x, frac=1/4)
    y_hat1_7 = lowess(y, x, frac=1/7)
    print(test_monotonic(y_hat1_4))
    print(get_LOWESS_degree_by_ratio(y_hat1_4, -3))
    
    if(input('DO YOU WANT TO PLOT THE FILTERED RESULT? (y/n)')=='y'):
        fig = px.scatter(df, x=df['Phi [deg]'], y=df['SUM-DIFF'], opacity=0.8, color_discrete_sequence=['black'])
        fig.add_traces(go.Scatter(x=y_hat2_3[:,0], y=y_hat2_3[:,1], name='LOWESS, frac=2/3', line=dict(color='red')))
        fig.add_traces(go.Scatter(x=y_hat2_3[:,0], y=y_hat1_4[:,1], name='LOWESS, frac=1/4', line=dict(color='orange')))
        fig.add_traces(go.Scatter(x=y_hat2_3[:,0], y=y_hat1_7[:,1], name='LOWESS, frac=1/7', line=dict(color='yellowgreen')))
        fig.update_layout(dict(plot_bgcolor = 'white'))
        fig.update_traces(marker=dict(size=3))
        fig.show() 

def get_LOWESS_degree_by_ratio(filtered_data, ratio):
    if(test_monotonic(filtered_data)==False):
        print("!! the data is not monotonic !!")
        return
    min_data=10
    for i in range(len(filtered_data)-1):
        if filtered_data[i][1] < min_data:
            min_data = filtered_data[i][1]
        if min(filtered_data[i][1], filtered_data[i+1][1])<ratio and ratio<max(filtered_data[i][1], filtered_data[i+1][1]):
            return interpolator(filtered_data, i, i+1, ratio)
    print("!! no data found !!")
    if ratio <= min_data:
        return 0

def interpolator(data, index1, index2, ratio): # returns degree (float)
    return data[index1][0] + (ratio-data[index1][1])/(data[index2][1]-data[index1][1])

def test_monotonic(input):  # for lowess filter
    peak_num=0
    for i in range(1,len(input)-1):
        if (input[i+1][1]<input[i][1] and input[i-1][1]<input[i][1]) or (input[i+1][1]>input[i][1] and input[i-1][1]>input[i][1]):  # if there is a peak
            peak_num+=1
    if peak_num!=1:
        return False
    else:
        return True

###########################################################################
################ Savitzky-Golay filter  ###################################
###########################################################################
def SAVGOL_filter():
    df = pd.read_csv('ground_truth_reweight.csv', encoding='utf-8')
    x=df['Phi [deg]'].values 
    y=df['SUM-DIFF'].values
    y_filtered = savgol_filter(y, 49, 3)
    fig = plt.figure()
    ax = fig.subplots()
    p = ax.plot(x, y, '-*', color="orange")
    p, = ax.plot(x, y_filtered, 'g')
    plt.subplots_adjust(bottom=0.25)
    plt.show()

###########################################################################
################ main function  ###########################################
###########################################################################
def main():
    weighted_power=2 #power multiplied to the weight
    if(input("DO YOU WANT TO GENERATE A NEW WEIGHTED FILE? (y/n)")=="y"):
        print("START GENERATION: weighted_power= ",weighted_power )
        OUTPUT_writter(weighted_power)
    #CSV_plotter(pd.read_csv('ground_truth_reweight.csv'))
    chosen_filter=input("WHICH FILTER WHOULD YOU WANT TO APPLY?\n  [1]Lowess filter\n  [2]Savitzky-Golay filter\n YOUR CHOICE: ")
    if chosen_filter=="1":
        LOWESS_filter()
    elif chosen_filter=="2":
        SAVGOL_filter()

main()