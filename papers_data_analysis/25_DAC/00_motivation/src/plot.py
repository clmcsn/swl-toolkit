"""Plotting Figure 0 - Motivation"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import plots as CPLT # noqa E402
from common import data_analysis as CDA # noqa E402

SCALE = 5*8.45
X_SIZE = SCALE*CPLT.CM/3.2
Y_SIZE = SCALE*CPLT.CM/10
HUE_ORDER = ['saxpy', 'sgemv', 'sgemm', 'knn', 'sfilter', 'conv2d', 'gcn-aggr']
MAPPING = {kernel: i for i, kernel in enumerate(HUE_ORDER)}
LINEWIDTH = 2.5

def gen_plot(df: pd.DataFrame, plots_dir: str, figure_name: str):
    """Generate the plot"""
    CPLT.load_font(CPLT.FONT_PATH)
    summary_df = pd.DataFrame()
    for k in df['kernel'].unique():
        FLOPs = df[df['kernel'] == k]['flops'].sum()
        cycles = df[df['kernel'] == k]['cycles'].sum()
        summary_df = pd.concat([summary_df, pd.DataFrame({'kernel': [k], 'FLOPs': [FLOPs], 'cycles': [cycles]})])
    summary_df["FLOPs/cycle"] = summary_df["FLOPs"]/summary_df["cycles"]
    summary_df = CDA.make_avg(summary_df, 'FLOPs/cycle')
    summary_df["util"] = summary_df["FLOPs/cycle"]/16*100
    # change aggr to gcn-aggr
    summary_df['kernel'] = summary_df['kernel'].replace('aggr', 'gcn-aggr')
    # Sort the dataframe by kernel names according to HUE_ORDER
    key = summary_df['kernel'].map(MAPPING)
    summary_df = summary_df.iloc[key.argsort()]
    # Plot ################################################
    ax = summary_df.plot.bar(x='kernel', y='util', legend=False, figsize=(X_SIZE, Y_SIZE))
    ax.set_ylabel('% Peak Perf.')
    ax.set_xlabel('')
    ax.grid(axis='y')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, horizontalalignment='center')

    fig = ax.get_figure()
    # Save the plot ################################################
    for fmt in CPLT.FORMATS:
        fig.savefig(os.path.join(plots_dir, figure_name + '.' + fmt),
                    bbox_inches='tight', format=fmt, pad_inches=0)
    plt.close()