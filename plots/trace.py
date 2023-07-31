import matplotlib.pyplot as plt
import seaborn as sns
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

    #remove t0 bias
    start = df[start_col_name].min()
    if start > 0:
        df = df.apply(lambda x: x-start if (x.name == start_col_name) else x)

    #scaling
    sampling_step = math.floor(df[period_col_name].min()/2)
    df = df.apply(lambda x: x/sampling_step if (x.name == start_col_name) or (x.name == period_col_name) else x)
    df = df.apply(lambda x: x.apply(np.floor) if (x.name == start_col_name) or (x.name == period_col_name) else x)
    df = df.apply(lambda x: x.astype(int) if (x.name == start_col_name) or (x.name == period_col_name) else x)
    df["end"] = df[start_col_name].add(df[period_col_name])

    for i, t in enumerate(list(df[traces_col_name].unique())): 
        df.loc[df[traces_col_name] == t, "color"] = colors[i]

    fig, (ax, ax1) = plt.subplots(2, figsize=(16,6), gridspec_kw={'height_ratios':[6, 1]})
    ax.barh(df[traces_col_name], df[period_col_name], left=df[start_col_name], color=df.color, edgecolor = "none")
    
    #for idx, row in df.iterrows():
    #    ax.text(row[period_col_name]+0.1, idx, f"{int(row.end*100)}%", va='center', alpha=0.8)
    #    ax.text(row.start_num-0.1, idx, row.Task, va='center', ha='right', alpha=0.8)

    # grid lines
    ax.set_axisbelow(True)
    #ax.xaxis.grid(color='gray', linestyle='dashed', alpha=0.5, which='both')
    ax.xaxis.grid(color='gray', linestyle='dashed', which='major', alpha=0.5)

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

def gen_trace_analysis(sdf, df, traces_col_name, period_col_name, start_col_name, path=None):
    
    start = df[start_col_name].min()
    if start > 0:
        df = df.apply(lambda x: x-start if (x.name == start_col_name) else x)

    start = sdf[start_col_name].min()
    if start > 0:
        sdf = sdf.apply(lambda x: x-start if (x.name == start_col_name) else x)

    #scaling
    #sampling_step = math.floor(df[period_col_name].min()/2)
    #df = df.apply(lambda x: x/sampling_step if (x.name == start_col_name) or (x.name == period_col_name) else x)
    #df = df.apply(lambda x: x.apply(np.floor) if (x.name == start_col_name) or (x.name == period_col_name) else x)
    #df = df.apply(lambda x: x.astype(int) if (x.name == start_col_name) or (x.name == period_col_name) else x)
    df["end"] = df[start_col_name].add(df[period_col_name])

    for i, t in enumerate(list(df[traces_col_name].unique())): 
        df.loc[df[traces_col_name] == t, "color"] = colors[i]

    fig, (ax, ax1) = plt.subplots(2, figsize=(16,5), gridspec_kw={'height_ratios':[1, 3]}, sharex=True)
    
    # ticks
    #X-axis
    possible_ticks = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    #step = math.floor(df.end.max()/20)
    step = math.floor(9000/20)
    d = [abs(x - step) for x in possible_ticks]
    idx = d.index(min(d))
    step = possible_ticks[idx]

    #xticks = np.arange(0, df.end.max()+1, step).astype(int)
    xticks = np.arange(0, 9000+1, step).astype(int)
    xticks_labels = xticks #* sampling_step
    xticks_minor = np.arange(0, df.end.max()+1, 1)
    ax1.set_xticks(xticks)
    #ax1.set_xticks(xticks_minor, minor=True) #minor ticks not visible for now
    ax1.set_xticklabels(xticks_labels, rotation=30)
    ax1.set_xlim([0, 9000])

    ax.barh(df[traces_col_name], df[period_col_name], left=df[start_col_name], color=df.color, edgecolor = "none")
    sns.lineplot(data=sdf, x=start_col_name, y="PC", ax=ax1)

    
    #for idx, row in df.iterrows():
    #    ax.text(row[period_col_name]+0.1, idx, f"{int(row.end*100)}%", va='center', alpha=0.8)
    #    ax.text(row.start_num-0.1, idx, row.Task, va='center', ha='right', alpha=0.8)

    # grid lines
    ax.set_axisbelow(True)
    #ax.xaxis.grid(color='gray', linestyle='dashed', alpha=0.5, which='both')
    ax.xaxis.grid(color='gray', linestyle='dashed', which='major', alpha=0.5)
    ax1.xaxis.grid(color='gray', linestyle='dashed', which='major', alpha=0.5)
    ax1.yaxis.grid(color='gray', linestyle='dashed', which='major', alpha=0.5)


    ####X-axis
   

    #Y-axis
    #traces
    ax.set_yticks([])

    #PC
    yticks = np.arange(sdf.PC.min()-300, sdf.PC.max(), math.floor((sdf.PC.max()-sdf.PC.min())/5)).astype(int)
    yticks_labels = [hex(x-0x80000000) for x in yticks]
    #print(yticks_labels)
    ax1.set_yticks(yticks)
    ax1.set_yticklabels(yticks_labels)

    # remove spines
    #ax.spines['right'].set_visible(False)
    #ax.spines['left'].set_visible(False)
    #ax.spines['left'].set_position(('outward', 10))
    #ax.spines['top'].set_visible(False)

    legend_elements = [Patch(facecolor=colors[i], label=t) for i, t in enumerate(list(df[traces_col_name].unique()))]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.1, 1.0))
    
    ax2 = ax1.twinx()
    sns.lineplot(data=sdf, x=start_col_name, y="e_count", ax=ax2)
    sdf["dummy"] = [0 for _ in range(len(sdf))]
    sdf["dummy"] = sdf["warp"]*0.2+0.65
    sns.scatterplot(data=sdf, x=start_col_name, y="dummy", hue="warp", ax=ax2, legend=True, edgecolor = "none")
    
    #TMASK
    #yticks = np.arange(sdf.e_count.min(), sdf.e_count.max()+1, 1).astype(int)
    yticks = np.arange(sdf.e_count.min(), 4+0.1, 1).astype(int)
    #yticks_labels = [hex(x) for x in yticks]
    ax2.set_yticks(yticks)
    ax2.set_yticklabels(yticks)
    ax2.set_ylim([0, 4.1])

    # clean second axis
    #ax1.spines['right'].set_visible(False)
    #ax1.spines['left'].set_visible(False)
    #ax1.spines['top'].set_visible(False)
    #ax1.spines['bottom'].set_visible(False)
    #ax1.set_xticks([])
    #ax1.set_yticks([])

    gen_plot(path)