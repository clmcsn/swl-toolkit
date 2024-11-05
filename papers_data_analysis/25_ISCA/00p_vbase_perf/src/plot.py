"""Plotting Figure 0"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import plots as CPLT # noqa E402

SCALE = 5*8.45
X_SIZE = SCALE*CPLT.CM/3.2
Y_SIZE = SCALE*CPLT.CM/7
HUE_ORDER = ['saxpy', 'sgemv', 'sgemm']
LINEWIDTH = 2.5


def gen_plot(df: pd.DataFrame, plots_dir: str, figure_name: str):
    """
        Generate the plot for Figure 0
        Plots is a grouped barplot for OP/cycle for saxpy,gemv,gemm
    """
    #print(df.loc[df['workload_size'] == 'saxpy', 'FLOPs'])
    # make OPs column
    df['FLOPs'] = 1
    df.loc[df['kernel'] == 'saxpy', 'FLOPs'] = df.loc[df['kernel'] == 'saxpy', 'workload_size'] / 32
    df.loc[df['kernel'] == 'sgemv', 'FLOPs'] = df.loc[df['kernel'] == 'sgemv', 'workload_size'] / 32
    df.loc[df['kernel'] == 'sgemm', 'FLOPs'] = df.loc[df['kernel'] == 'sgemm', 'workload_size'] / 4
    summary_df = pd.DataFrame()
    for k in df['kernel'].unique():
        kernel = k
        FLOPs = df.loc[df['kernel'] == k, 'FLOPs'].sum()
        cycles = df.loc[df['kernel'] == k, 'cycles'].sum()
        summary_df = pd.concat([summary_df, pd.DataFrame({'kernel': [kernel], 'FLOPs': [FLOPs],
                                                          'cycles': [cycles/4],
                                                          'Arch': ['Vortex Baseline']})],
                               ignore_index=True)
        summary_df = pd.concat([summary_df, pd.DataFrame({'kernel': [kernel], 'FLOPs': [FLOPs],
                                                          'cycles': [cycles/8],
                                                          'Arch': ['Vortex Ideal Dual-issue']})],
                               ignore_index=True)
    summary_df['OPs/cycle'] = summary_df['FLOPs']/summary_df['cycles']*100
    # Rename column Arch to Architecture
    summary_df = summary_df.rename(columns={'Arch': 'Architecture'})
    # Order the hue
    summary_df['kernel'] = pd.Categorical(summary_df['kernel'], categories=HUE_ORDER, ordered=True)
    pivot_df = pd.pivot_table(summary_df, index='kernel', columns='Architecture',
                              values='OPs/cycle')
    arch = False
    if arch is False:
        pivot_df = pivot_df.drop(columns=['Vortex Ideal Dual-issue'])

    ax = pivot_df.plot(kind='bar')
    fig = ax.get_figure()
    fig.set_size_inches(X_SIZE, Y_SIZE)
    # Tilt x-ticks
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    # Remove x-label
    ax.set_xlabel('')
    # ax.set_xlabel('Kernel')
    ax.set_ylabel('FPU utilization (%)')
    # Add grid
    ax.grid(axis='y')
    # Add legend, top center outside the plot, two columns
    if arch is False:  # Remove the legend
        ax.get_legend().remove()
    else:
        ax.legend(loc='center', bbox_to_anchor=(0.5, 1.15), ncol=2, title='Architecture')
    # Save the plot ################################################
    for fmt in CPLT.FORMATS:
        fig.savefig(os.path.join(plots_dir, figure_name + '.' + fmt),
                    bbox_inches='tight', format=fmt, pad_inches=0)
    plt.close()
