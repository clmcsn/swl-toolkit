"""Plotting Figure 0 - Motivation"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

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


def gen_outercore_df(df: pd.DataFrame) -> pd.DataFrame:
    # Data preprocessing for core scalability ########################################
    # Remove all dcache_banks <=128
    cdf = df[df['dcache_banks'] > 128]
    # Remove all kernels that don't end with '-ssr3
    cdf = cdf[cdf['kernel'].str.endswith('-ssr3')]
    summary_df = pd.DataFrame()
    # Makeing speedup summary df, app is at this stage only for debug purposes
    for app in cdf['app'].unique():
        for c in cdf['cores'].unique():
            speedup = cdf[(cdf['cores'] == c) &
                          (cdf['app'] == app)]['cycles_ratio'].mean()
            summary_df = pd.concat([summary_df, pd.DataFrame({'app': [app],
                                                              'cores': [c],
                                                              'speedup': [speedup]})])
    print(summary_df.to_string())  # for debug purposes
    core_df = pd.DataFrame()
    for c in summary_df['cores'].unique():
        speedup = summary_df[summary_df['cores'] == c]['speedup'].mean()
        core_df = pd.concat([core_df, pd.DataFrame({'cores': [c],
                                                    'speedup': [speedup]})])
    # order the core_df
    core_df = core_df.sort_values(by=['cores'])
    print(core_df.to_string())  # for debug purposes
    return core_df


def gen_plot(df: pd.DataFrame, plots_dir: str, figure_name: str):
    """Generate the plot"""
    CPLT.load_font(CPLT.FONT_PATH)

    # Remove airbender from app name
    # print all cycles_ratio and workload size value for saxpy-ssr3 kernel
    # remove cycle_ratios > 100
    df = df[df['cycles_ratio'] <= 100]
    df['cores'] = df['cores']*df['clusters']
    df['app'] = df['app'].str.replace('-airbender', '')
    # Remove all kernels that are base kernels
    df = df[~df['kernel'].isin(CDEFS.BASE_KERNELS.values())]
    soc_df = gen_outercore_df(df)
    # remove nan values rows
    soc_df = soc_df.dropna()
    fig = plt.figure(figsize=(X_SIZE, Y_SIZE))
    # Plotting bar plot with soc_df ########################################
    ax2 = fig.add_subplot(111)
    # plot a bar per core
    soc_df['c_coord'] = 0
    for i, c in enumerate(soc_df['cores'].unique()):
        soc_df.loc[soc_df['cores'] == c, 'c_coord'] = i
    ax2.bar(soc_df['c_coord'], soc_df['speedup'])
    ax2.set_xlabel('Cores')
    # set labels for x-axis as number of cores
    ax2.set_xticks(range(len(soc_df['cores'].unique())))
    ax2.set_xticklabels(soc_df['cores'].unique())
    ax2.set_ylabel('Speedup')
    ax2.set_title('Multi-core scalability')
    # Add bar values ################################################
    for i in range(len(soc_df)):
        ax2.text(soc_df['c_coord'].iloc[i], soc_df['speedup'].iloc[i],
                 '%.1f' % soc_df['speedup'].iloc[i], color='black',
                 fontsize=12, ha='center', va='bottom', fontweight='bold')
    # Add grid ################################################
    ax2.grid(axis='y')

    # Save the plot ################################################
    for fmt in CPLT.FORMATS:
        fig.savefig(os.path.join(plots_dir, figure_name + '2.' + fmt),
                    bbox_inches='tight', format=fmt, pad_inches=0)
    plt.close()
