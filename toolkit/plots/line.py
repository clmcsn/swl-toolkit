from plots.utils import init_plot
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
import pandas as pd
import numpy as np

sns.set(style="ticks")

def gen_plot(path):
    #plt.grid()
    if path:
        plt.savefig(path, dpi =300, bbox_inches = "tight")
    else:
        plt.show()
    plt.clf()

def gen_lineplot(df, x=None, y=None, color=None, path=None, size=None, **kwargs):
    init_plot()
    rcParams['figure.figsize'] = 12,5
    ax = sns.lineplot(x=x, y=y, hue=color, data=df, **kwargs)
    ax.set(xscale='log')
    ax.set(yscale='log')
    gen_plot(path)

def gen_lineplot_dots(df, dots, x=None, y=None, color=None, path=None, **kwargs):
    init_plot()
    rcParams['figure.figsize'] = x,y
    rcParams['lines.markersize'] = 10
    _, ax = plt.subplots()
    m = []
    for i in range(len(dots.index)):
        m.append('o')
    ax = sns.lineplot(data=df, **kwargs)
    ax = sns.scatterplot(data=dots, markers=m, **kwargs)
    ax.set(xscale='log')
    ax.set(yscale='log')
    plt.grid(True,which="both",ls="--",c='lightgrey')
    gen_plot(path)