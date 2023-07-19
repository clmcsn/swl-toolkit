from plots.utils import init_plot
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
import pandas as pd
import numpy as np

sns.set(style="ticks")

def gen_plot(path):
    plt.grid()
    if path:
        plt.savefig(path, dpi =300, bbox_inches = "tight")
    else:
        plt.show()
    plt.clf()

def gen_scatter_color(df, y, x, color=None, path=None, size=None, **kwargs):
    init_plot()
    rcParams['figure.figsize'] = size[0],size[1]
    x = sns.catplot( x=x, y=y, hue=color, data=df, dodge=True, jitter=True, **kwargs)
    gen_plot(path)