"""Plotting Figure 0 - Motivation"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import plots as CPLT # noqa E402
from common import data_analysis as CDA # noqa E402
from common import defines as CDEFS # noqa E402
from . import defines as DEFS # noqa E402

SCALE = 5*8.45
X_SIZE = SCALE*CPLT.CM/3.2
Y_SIZE = SCALE*CPLT.CM/10
KERNEL_ORDER = ['saxpy', 'sgemv', 'sgemm', 'knn', 'sfilter', 'conv2d', 'gcn-aggr', 'mean']
KERNEL_MAPPING = {kernel: i for i, kernel in enumerate(KERNEL_ORDER)}

EXTS_ORDER = ['CFM only', 'CFM+1xDMSL', 'CFM+2xDMSL', 'CFM+3xDMSL']
EXTS_MAPPING = {ext: i for i, ext in enumerate(EXTS_ORDER)}

LINEWIDTH = 2.5


def gen_exts(row):
    if 'loop' in row['kernel'] or 'limbo' in row['kernel']:
        return 'CFM only'
    elif 'ssr3' in row['kernel']:
        return 'CFM+3xDMSL'
    elif 'ssr2' in row['kernel']:
        return 'CFM+2xDMSL'
    elif 'ssr' in row['kernel']:
        return 'CFM+1xDMSL'
    else:
        return 'base'


def gen_plot(df: pd.DataFrame, plots_dir: str, figure_name: str):
    """Generate the plot"""
    CPLT.load_font(CPLT.FONT_PATH)

    # Remove airbender from app name
    df['app'] = df['app'].str.replace('-airbender', '')
    df['app'] = df['app'].str.replace('aggr', 'gcn-aggr')

    # Data preprocessing ########################################
    summary_df = pd.DataFrame()
    for app in df['app'].unique():
        for k in df['kernel'].unique():
            if k == CDEFS.BASE_KERNELS[app]:
                continue
            FLOPs = df[(df['kernel'] == k) & (df['app'] == app)]['flops'].sum()
            cycles = df[(df['kernel'] == k) & (df['app'] == app)]['cycles'].sum()
            speedup = df[(df['kernel'] == k) & (df['app'] == app)]['cycles_ratio'].mean()
            ired = df[(df['kernel'] == k) & (df['app'] == app)]['instrs_ratio'].mean()
            summary_df = pd.concat([summary_df, pd.DataFrame({'app': [app],
                                                              'kernel': [k],
                                                              'FLOPs': [FLOPs],
                                                              'cycles': [cycles],
                                                              'speedup': [speedup],
                                                              'ired': [ired]})])
    summary_df["FLOPs/cycle"] = summary_df["FLOPs"]/summary_df["cycles"]
    summary_df["exts"] = summary_df.apply(gen_exts, axis=1)
    # Remove Nan values
    summary_df = summary_df.dropna()
    summary_df['util'] = summary_df["FLOPs/cycle"]/16*100
    # Add mean for each exts
    for ext in summary_df['exts'].unique():
        mean_speedup = summary_df[summary_df['exts'] == ext]['speedup'].mean()
        mean_ired = summary_df[summary_df['exts'] == ext]['ired'].mean()
        mean_util = summary_df[summary_df['exts'] == ext]['util'].mean()
        summary_df = pd.concat([summary_df, pd.DataFrame({'app': ['mean'],
                                                          'kernel': [ext],
                                                          'exts': [ext],
                                                          'speedup': [mean_speedup],
                                                          'ired': [mean_ired],
                                                          'util': [mean_util]})])

    # Order according to the mapping by kernel and exts
    summary_df = summary_df.sort_values(by=['kernel'], key=lambda x: x.map(KERNEL_MAPPING))
    summary_df = summary_df.sort_values(by=['exts'], key=lambda x: x.map(EXTS_MAPPING))

    # Generate the plots ########################################
    # 3 plots over the x axis for speedup, ired and util
    fig, axs = plt.subplots(1, 3, figsize=(3*X_SIZE, Y_SIZE))
    # Plots are grouped bar plots
    for i, metric in enumerate(['speedup', 'ired', 'util']):
        x_placements = np.arange(len(summary_df['app'].unique()))
        width = 0.2
        multiplier = 0
        for ext in summary_df['exts'].unique():
            ixp = x_placements.copy()
            if not ext == 'CFM only':
                ixp = np.delete(ixp, -2)
            ext_df = summary_df[summary_df['exts'] == ext]
            ext_df = ext_df.sort_values(by=['app'], key=lambda x: x.map(KERNEL_MAPPING))
            offset = width * multiplier
            _ = axs[i].bar(ixp + offset, ext_df[metric], width, label=ext)
            # rects = axs[i].bar(ixp + offset, ext_df[metric], width, label=ext)
            # axs[i].bar_label(rects, padding=3)
            multiplier += 1
        # Add labels
        axs[i].set_ylabel(DEFS.Y_LABELS[metric])
        # At least 6 y ticks, minor in between
        axs[i].yaxis.set_major_locator(plt.MaxNLocator(6))
        # Set x axis
        axs[i].set_xticks(x_placements+1.5*width)
        axs[i].set_xticklabels(KERNEL_ORDER, rotation=35)
        # Add grid
        axs[i].grid(axis='y')
    # Add legend top, center of three plots, 4 cols
    axs[0].legend(title='Extensions Used', loc='upper center', bbox_to_anchor=(1.7, 1.5), ncol=4)

    # Save the plot ################################################
    for fmt in CPLT.FORMATS:
        fig.savefig(os.path.join(plots_dir, figure_name + '.' + fmt),
                    bbox_inches='tight', format=fmt, pad_inches=0)
    plt.close()
