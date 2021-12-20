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
    y_hat1_7 = lowess(y, x, frac=1/7)
    
    fig = px.scatter(df, x=df['Phi [deg]'], y=df['SUM-DIFF'], opacity=0.8, color_discrete_sequence=['black'])
    fig.add_traces(go.Scatter(x=y_hat2_3[:,0], y=y_hat2_3[:,1], name='LOWESS, frac=2/3', line=dict(color='red')))
    fig.add_traces(go.Scatter(x=y_hat2_3[:,0], y=y_hat1_5[:,1], name='LOWESS, frac=1/5', line=dict(color='orange')))
    fig.add_traces(go.Scatter(x=y_hat2_3[:,0], y=y_hat1_7[:,1], name='LOWESS, frac=1/7', line=dict(color='yellowgreen')))
    fig.update_layout(dict(plot_bgcolor = 'white'))
    fig.update_traces(marker=dict(size=3))
    fig.show() 

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