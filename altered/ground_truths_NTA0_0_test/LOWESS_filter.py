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

LOWESS_filter()