import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import csv

#print(dataframe)

with open('ground_truth_ratio.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)
data=data[1:]


for i in range(len(data)):
    data[i]=data[i][1:]
    data[i]=np.array(data[i]).astype(np.float)

fig, ax = plt.subplots()
ax.boxplot(data)
plt.show()