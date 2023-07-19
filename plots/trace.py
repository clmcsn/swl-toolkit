import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import da.util as util
import math
from matplotlib.patches import Patch

def gen_plot(path):
    if path:
        plt.savefig(path, dpi =300, bbox_inches = "tight")
    else:
        plt.show()
    plt.clf()
    
colors = ["blue", "red", "green", "yellow", "orange", "purple", "pink", "brown", "gray", "olive", "cyan", "magenta"]

def gen_time_traces(df, traces_col_name, period_col_name, start_col_name, path=None):
    #https://gist.github.com/Thiagobc23/ad0f228dd8a6b1c9a9e148f17de5b4b0

    #scaling
    sampling_step = math.floor(df[period_col_name].min()/2)
    df = df.apply(lambda x: x/sampling_step if (x.name == start_col_name) or (x.name == period_col_name) else x)
    df = df.apply(lambda x: x.apply(np.floor) if (x.name == start_col_name) or (x.name == period_col_name) else x)
    df = df.apply(lambda x: x.astype(int) if (x.name == start_col_name) or (x.name == period_col_name) else x)
    df["end"] = df[start_col_name].add(df[period_col_name])

    for i, t in enumerate(list(df[traces_col_name].unique())): 
        df.loc[df[traces_col_name] == t, "color"] = colors[i]

    fig, (ax, ax1) = plt.subplots(2, figsize=(16,6), gridspec_kw={'height_ratios':[6, 1]})
    ax.barh(df[traces_col_name], df[period_col_name], left=df[start_col_name], color=df.color)
    
    #for idx, row in df.iterrows():
    #    ax.text(row[period_col_name]+0.1, idx, f"{int(row.end*100)}%", va='center', alpha=0.8)
    #    ax.text(row.start_num-0.1, idx, row.Task, va='center', ha='right', alpha=0.8)

    # grid lines
    ax.set_axisbelow(True)
    ax.xaxis.grid(color='gray', linestyle='dashed', alpha=0.2, which='both')

    # ticks
    xticks = np.arange(0, df.end.max()+1, math.floor(df.end.max()/40))
    xticks_labels = xticks * sampling_step
    xticks_minor = np.arange(0, df.end.max()+1, 1)
    ax.set_xticks(xticks)
    ax.set_xticks(xticks_minor, minor=True)
    ax.set_xticklabels(xticks_labels, rotation=30)
    ax.set_yticks([])

    # remove spines
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['left'].set_position(('outward', 10))
    ax.spines['top'].set_visible(False)

    legend_elements = [Patch(facecolor=colors[i], label=t) for i, t in enumerate(list(df[traces_col_name].unique()))]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.1, 1.0))

    # clean second axis
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.set_xticks([])
    ax1.set_yticks([])

    gen_plot(path)