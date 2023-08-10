from plots.utils import init_plot
import matplotlib.pyplot as plt
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

def gen_strip_color(df, y, x, color, path=None, size=None, **kwargs):
    init_plot()
    if size : sns.set(rc={'figure.figsize': size})
    if kwargs["col"]:
        ax = sns.catplot( x=x, y=y, hue=color, data=df, dodge=True, jitter=True, **kwargs)
    else:
        ax = sns.stripplot( x=x, y=y, hue=color, data=df, dodge=False, jitter=True, **kwargs)
    #plt.setp(ax.get_xticklabels(), rotation=60, ha="right", rotation_mode="anchor")
    gen_plot(path)

def gen_strip_color_marker(df, x, y, color, marker, columns=None, path=None, size=None, **kwargs):
    init_plot()
    fig, ax = plt.subplots()
    marker_values = list(pd.unique(df[marker]))
    markers = ["o", "v", "^", "<", ">", "s", "p", "P", "*", "h", "H", "X", "D", "d"]
    for c, m in zip(marker_values, markers):
        cdf = df.loc[df[marker]==c]
        sns.stripplot(data=cdf, x=x, y=y, hue=color, marker=m, dodge=False, jitter=True, ax=ax, s=8, **kwargs)
    handles, labels = ax.get_legend_handles_labels()
    unique_legend_entries = len(list(pd.unique(df[color])))
    ax.legend(handles=handles[:unique_legend_entries], labels=labels[:unique_legend_entries], title="legend", loc='upper right')
    gen_plot(path)

def gen_strip_marker(df, x, y, marker, columns=None, path=None, size=None, **kwargs):
    init_plot()
    fig, ax = plt.subplots()
    marker_values = list(pd.unique(df[marker]))
    markers = ["o", "v", "^", "<", ">", "s", "p", "P", "*", "h", "H", "X", "D", "d"]
    for c, m in zip(marker_values, markers):
        cdf = df.loc[df[marker]==c]
        sns.stripplot(data=cdf, x=x, y=y, marker=m, dodge=False, jitter=True, ax=ax, s=8, **kwargs)
    gen_plot(path)