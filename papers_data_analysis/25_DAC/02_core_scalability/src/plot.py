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
Y_SIZE = SCALE*CPLT.CM/3.2
KERNEL_ORDER = ['saxpy', 'sgemv', 'sgemm', 'knn', 'sfilter', 'conv2d', 'gcn-aggr', 'mean']
KERNEL_MAPPING = {kernel: i for i, kernel in enumerate(KERNEL_ORDER)}

EXTS_ORDER = ['CFM only', 'CFM+1xDMSL', 'CFM+2xDMSL', 'CFM+3xDMSL']
EXTS_MAPPING = {ext: i for i, ext in enumerate(EXTS_ORDER)}

LINEWIDTH = 2.5


def gen_plot(df: pd.DataFrame, plots_dir: str, figure_name: str):
    """Generate the plot"""
    CPLT.load_font(CPLT.FONT_PATH)

    # Remove airbender from app name
    df['app'] = df['app'].str.replace('-airbender', '')
    # Remove all kernels that are base kernels
    df = df[~df['kernel'].isin(CDEFS.BASE_KERNELS.values())]
    # Data preprocessing ########################################
    summary_df = pd.DataFrame()
    # Makeing speedup summary df, app is at this stage only for debug purposes
    for app in df['app'].unique():
        for t in df['threads'].unique():
            for w in df['warps'].unique():
                speedup = df[(df['threads'] == t) &
                             (df['warps'] == w) &
                             (df['app'] == app)]['cycles_ratio'].mean()
                summary_df = pd.concat([summary_df, pd.DataFrame({'app': [app],
                                                                  'threads': [t],
                                                                  'warps': [w],
                                                                  'speedup': [speedup]})])
    # print(summary_df.to_string())  # for debug purposes
    final_df = pd.DataFrame()
    for t in df['threads'].unique():
        for w in df['warps'].unique():
            speedup = summary_df[(summary_df['threads'] == t) &
                                 (summary_df['warps'] == w)]['speedup'].mean()
            final_df = pd.concat([final_df, pd.DataFrame({'threads': [t],
                                                          't_coord': [t/16],
                                                          'warps': [w],
                                                          'w_coord': [w/8],
                                                          'speedup': [speedup]})])
    # order the final_df
    final_df = final_df.sort_values(by=['threads', 'warps'])
    # print(final_df.to_string())  # for debug purposes
    # Plotting 3D bar plot ##################################################
    fig = plt.figure(figsize=(X_SIZE, Y_SIZE))
    ax = fig.add_subplot(111, projection='3d')
    ax.bar3d(final_df['w_coord'], final_df['t_coord'], np.zeros_like(final_df['speedup']),
             0.9, 0.9, final_df['speedup'], shade=False, edgecolor='black')
    ax.set_xlabel('Warps')
    ax.set_ylabel('Threads')
    ax.set_zlabel('Speedup')
    ax.set_xticks([1.5, 2.5])
    ax.set_xticklabels([16, 32])
    ax.set_yticks([1.5, 2.5])
    ax.set_yticklabels([8, 16])
    ax.grid(True)
    ax.view_init(30, 120)
    ax.set_box_aspect(aspect=None, zoom=0.8)

    # Save the plot ################################################
    for fmt in CPLT.FORMATS:
        fig.savefig(os.path.join(plots_dir, figure_name + '.' + fmt),
                    bbox_inches='tight', format=fmt, pad_inches=0)
    plt.close()
