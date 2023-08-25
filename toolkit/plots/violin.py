from .utils import init_plot

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def gen_plot(path):
    plt.grid()
    if path:
        plt.savefig(path, dpi =300, bbox_inches = "tight")
    else:
        plt.show()
    plt.clf()

def violin_plot(data, x, y, hue=None, path=None, size=None, split=False):
    init_plot()
    if size: plt.figure(figsize=size)
    data = data.loc[data[y]<=4]
    sns.violinplot(data=data, x=x, y=y, hue=hue, split=split,cut=0)
    #plt.ylim(0, 4)
    #plt.yscale("log")
    gen_plot(path)
