import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import pandas as pd
import numpy as np

data2 = pd.read_csv('../ground_truth.csv')
x = np.linspace(0, 50, 51)
y = data2.iloc[x, 3]
f = interp1d(x, y, kind = 'linear', fill_value='extrapolate')  # radial basis function interpolator instance

xnew = np.arange(0, 60, 0.5)
ynew = f(xnew)   # use interpolation function returned by `interp1d`
plt.plot(x, y, 'o', xnew, ynew, '-')
plt.show()