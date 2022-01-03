import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import pandas as pd
import sys
from tkinter.filedialog import askopenfilename
from tkinter import Tk, Button, BOTTOM
#import tkinter as tk
#root = Tk()
#root.withdraw()
#filepathtest = askopenfilename(parent=root,initialdir='./')
#print(filepathtest)
usage = """To run:
        python plot_ground_truth.py [ploting_index] [ploting_mode] [points]
        [ploting_index]: 1 => sum, 2 => diff, 3 => ratio
        [ploting_mode]: 0 => single_plot (default), 1 => compare
        [points]: 0 => w/o points(default), 1 => with points"""
if len(sys.argv) == 1: 
    print(usage)
    sys.exit()
###################################################
#                  input part                     #
###################################################

filepath = 'ground_truths_wo_alu_2/ground_truth_new.csv'
file2path = 'ground_truths_wo_alu/ground_truth_new.csv' # only useful when mode is 1

title_dictionary = {1:"sum", 2:"diff", 3:"ratio"}
the_one_to_plot = int(sys.argv[1]) # 1 => sum, 2 => diff, 3 => ratio
mode = title_dictionary[the_one_to_plot]

def ploting(data, option, folder):
    arr = np.array([])
    for i in range(len(y)):
        arr = np.append(arr, data[i]) #store DIFF-SUM into array
    x_axis = np.arange(0, 181, angle_portion)   #x-axis

    f = interp1d(x_axis, arr, kind = 'linear', fill_value='extrapolate')  # radial basis function interpolator instance
    value = f(x_axis)   # use interpolation function returned by `interp1d`


    plt.title(title_dictionary[the_one_to_plot])
    plt.plot(x_axis, value, linestyle='-', label = folder)
    if option:plt.plot(x_axis, value, 'o')


if len(sys.argv) == 2 or sys.argv[2] == "0":
    data = pd.read_csv(filepath)
    try:
        filename = filepath.split("/")[-1]
        folder = filepath.split("/")[0]
    except:
        filename = filepath
        folder = "./"
    print()
    print(f"ploting '{mode}' of file '{filename}' in '{folder}'.")
    print()
    ############### parameters
    data_num = len(data) #number of data
    angle_portion = 180/(data_num-1) #angle of each turn
    ###############
    
    index = np.linspace(0, data_num-1, data_num)  #to read the csv file
    y = data.iloc[index, the_one_to_plot]  #get the DIFF-SUM 

    ploting(y, True)


    plt.title(title_dictionary[the_one_to_plot])
    #plt.plot(x_axis, value, 'o', x_axis, value, '-')
    plt.show()

if sys.argv[2] == "1":
    data = pd.read_csv(filepath)
    data2 = pd.read_csv(file2path)
    try:
        filename = filepath.split("/")[-1]
        file2name = file2path.split("/")[-1]
        folder = filepath.split("/")[0]
        folder2 = file2path.split("/")[0]
    except:
        filename = filepath
        folder = "./"
        file2name = file2path
        folder2 = "./"
    if filename != file2name:
        print("unmatch filename of two file, please check if the input is correct.")
        sys.exit()
    print()
    print(f"ploting '{mode}' of file '{filename}' in '{folder}' and '{folder2}'.")
    print()
    ############### parameters
    data_num = len(data) #number of data
    angle_portion = 180/(data_num-1) #angle of each turn
    ###############
    
    index = np.linspace(0, data_num-1, data_num)  #to read the csv file
    y = data.iloc[index, the_one_to_plot]  #get the data 
    y2 = data2.iloc[index, the_one_to_plot]  #get the data of another file


    fig = plt.figure(f"{folder}__{folder2}__{mode}")
    plt.title(title_dictionary[the_one_to_plot])

    if len(sys.argv) < 4 or sys.argv[3] == "0":
        ploting(y, False, folder)
        ploting(y2, False, folder2)
    elif sys.argv[3] == "1":
        ploting(y, True, folder)
        ploting(y2, True, folder2)

    plt.legend()
    plt.show()

# def _quit():
#     root.quit()
#     root.destroy()

# button = Button(root, text='quit', command=_quit)
# button.pack(side=BOTTOM)