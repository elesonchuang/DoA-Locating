import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import pandas as pd
import numpy as np

data2 = pd.read_csv('/Users/chenfayu/Documents/@@台灣大學電機系＿三上專題研究/演算法/DoA-Locating/altered/ground_truth_new0820-2.csv')
x = np.linspace(0, 90, 91)
print(x)
y = data2.iloc[x, 1]
print(y)
f = interp1d(x, y, kind = 'linear', fill_value='extrapolate')  # radial basis function interpolator instance


xnew = np.arange(0, 90, 2)
ynew = f(xnew)   # use interpolation function returned by `interp1d`
plt.plot(x, y, 'o', xnew, ynew, '-')
plt.show()