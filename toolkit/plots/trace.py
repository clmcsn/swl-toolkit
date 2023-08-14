import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
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
    #sampling_step = math.floor(df[period_col_name].min()/2)
    #df = df.apply(lambda x: x/sampling_step if (x.name == start_col_name) or (x.name == period_col_name) else x)
    #df = df.apply(lambda x: x.apply(np.floor) if (x.name == start_col_name) or (x.name == period_col_name) else x)
    #df = df.apply(lambda x: x.astype(int) if (x.name == start_col_name) or (x.name == period_col_name) else x)
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

def gen_trace_analysis(synthetic_df, df, traces_col_name, period_col_name, start_col_name, 
                       remove_bias=True, path=None, time_span=0, max_threads=0):
    """
    synthetic_df:       synthetic dataframe -> used to generate the waveform plot
    df:                 trace dataframe     -> used to generate the accurate trace plot
    traces_col_name:    name of the column containing the trace section id
    period_col_name:    name of the column containing the period
    start_col_name:     name of the column containing the start
    path:               path to save the plot
    """
    
    """Generating plot limits for removing starting bias"""
    if remove_bias:
        start = df[start_col_name].min()
        if start > 0:
            df = df.apply(lambda x: x-start if (x.name == start_col_name) else x)

        start = synthetic_df[start_col_name].min()
        if start > 0:
            synthetic_df = synthetic_df.apply(lambda x: x-start if (x.name == start_col_name) else x)

    df["end"] = df[start_col_name].add(df[period_col_name])

    """Assigning colors to traces sections"""
    for i, t in enumerate(list(df[traces_col_name].unique())): 
        synthetic_df.loc[synthetic_df[traces_col_name] == t, "color"] = colors[i]

    _, (ax, ax1) = plt.subplots(2, figsize=(16,5), gridspec_kw={'height_ratios':[1, 3]}, sharex=True)
    
    """Making axes"""
    #X-axis (time)
    possible_ticks = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000] #time cycles
    main_ticks_count = 20

    if time_span: plot_end = time_span
    else: plot_end = df.end.max()

    if remove_bias: plot_start = 0
    else: plot_start = df.start.min()

    step = math.floor((plot_end-plot_start)/main_ticks_count)
    d = [abs(x - step) for x in possible_ticks] 
    idx = d.index(min(d))           #selecting the ticks from the most similar to the step
    step = possible_ticks[idx]      

    xticks = np.arange(plot_start, plot_end+1, step).astype(int)
    xticks_labels = xticks 
    #xticks_minor = np.arange(0, df.end.max()+1, 1)
    ax1.set_xticks(xticks)
    #ax1.set_xticks(xticks_minor, minor=True) #minor ticks not visible for now
    ax1.set_xticklabels(xticks_labels, rotation=30)
    ax1.set_xlim([0, plot_end])

    """Y grid lines"""
    ax.set_axisbelow(True)
    ax.xaxis.grid(color='gray', linestyle='dashed', which='major', alpha=0.5)
    ax1.xaxis.grid(color='gray', linestyle='dashed', which='major', alpha=0.5)

    """Adding legend for waveform plot"""
    legend_elements = [Patch(facecolor=colors[i], label=t) for i, t in enumerate(list(df[traces_col_name].unique()))]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.1, 1.0))

    """Adding the actual plots"""
    #Waveform plot
    ax.barh(y=synthetic_df[traces_col_name], width=synthetic_df[period_col_name], left=synthetic_df[start_col_name], color=synthetic_df.color, edgecolor = "none")
    #PC plot
    sns.lineplot(data=df, x=start_col_name, y="PC", ax=ax1)
    
    #plotting warp issue instructions
    df["dummy"] = [0 for _ in range(len(df))]
    offset = df["e_count"].max()/(df["warp"].max()+1)/6 #300 is the height of the minimum plot point
    df["dummy"] = df["warp"]*offset + offset #0.2 is the height of the point, 0.65 is offset from the bottom
    
    
    ax2 = ax1.twinx()   # creating a second axis
    sns.lineplot(data=df, x=start_col_name, y="e_count", ax=ax2, color="orange") #thread utilization plot (e_count=execution count)
    sns.scatterplot(data=df, x=start_col_name, y="dummy", hue="warp", ax=ax2, legend=True, edgecolor = "none")

    """Y ticks PC"""
    ax.set_yticks([]) #traces
    
    #PC
    yticks_count = 5
    yticks = np.arange( df.PC.min(), df.PC.max(), 
                        math.floor((df.PC.max()-df.PC.min())/yticks_count)).astype(int)
    yticks_labels = [hex(x-0x80000000) for x in yticks] #removing leading 0x80000000 to avoid space waste
    ax1.set_yticks(yticks)
    ax1.set_yticklabels(yticks_labels)

    """Y ticks e_count"""
    if max_threads: y_ax_limit= max_threads
    else: y_ax_limit = df.e_count.max()

    yticks = np.arange(df.e_count.min(), y_ax_limit+0.1, 1).astype(int)
    ax2.set_yticks(yticks)
    ax2.set_yticklabels(yticks)
    ax2.set_ylim([0, y_ax_limit+0.1])

    gen_plot(path)