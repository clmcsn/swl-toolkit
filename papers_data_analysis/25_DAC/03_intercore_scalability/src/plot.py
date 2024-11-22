"""Plotting Figure 0 - Motivation"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import plots as CPLT # noqa E402
from common import data_analysis as CDA # noqa E402
from common import defines as CDEFS # noqa E402
from . import defines as DEFS # noqa E402

SCALE = 5*8.45
X_SIZE = SCALE*CPLT.CM/6
Y_SIZE = SCALE*CPLT.CM/6
MARKERSIZE = 9
KERNEL_ORDER = ['saxpy', 'sgemv', 'sgemm', 'knn', 'sfilter', 'conv2d', 'gcn-aggr', 'mean']
KERNEL_MAPPING = {kernel: i for i, kernel in enumerate(KERNEL_ORDER)}

EXTS_ORDER = ['CFM only', 'CFM+1xDMSL', 'CFM+2xDMSL', 'CFM+3xDMSL']
EXTS_MAPPING = {ext: i for i, ext in enumerate(EXTS_ORDER)}

LINEWIDTH = 2.5


def gen_intercore_df(df: pd.DataFrame) -> pd.DataFrame:
    # Data preprocessing for inter-core scalability ########################################
    # Remove all cores that are > 1 and dcache_banks <=128
    df = df[(df['kernel'].str.endswith('ssr3')) |
            (df['kernel'].isin(CDEFS.BASE_KERNELS.values()))]
    cdf = df[df['cores'] == 1 & (df['dcache_banks'] <= 128)]
    # remove warps <8
    cdf = cdf[(cdf['warps'] >= 8) & (cdf['threads'] > 8)]
    summary_df = pd.DataFrame()
    # Makeing speedup summary df, app is at this stage only for debug purposes
    for k in cdf['kernel'].unique():
        for t in cdf['threads'].unique():
            for w in cdf['warps'].unique():
                speedup = cdf[(cdf['threads'] == t) &
                              (cdf['warps'] == w) &
                              (cdf['kernel'] == k)]['cycles_ratio'].mean()
                FLOPs = cdf[(cdf['threads'] == t) &
                            (cdf['warps'] == w) &
                            (cdf['kernel'] == k)]['flops'].sum()
                cycles = cdf[(cdf['threads'] == t) &
                             (cdf['warps'] == w) &
                             (cdf['kernel'] == k)]['cycles'].sum()
                is_base_kernel = k in CDEFS.BASE_KERNELS.values()
                summary_df = pd.concat([summary_df, pd.DataFrame({'kernel': [k],
                                                                  'threads': [t],
                                                                  'warps': [w],
                                                                  'speedup': [speedup],
                                                                  'FLOPs': [FLOPs],
                                                                  'cycles': [cycles],
                                                                  'is_base': [is_base_kernel]})])
    summary_df['FLOP/cycle'] = summary_df['FLOPs']/summary_df['cycles']
    print(summary_df.to_string())  # for debug purposes
    final_df = pd.DataFrame()
    for is_b in summary_df['is_base'].unique():
        for t in summary_df['threads'].unique():
            for w in summary_df['warps'].unique():
                speedup = summary_df[(summary_df['threads'] == t) &
                                     (summary_df['warps'] == w) &
                                     (summary_df['is_base'] == is_b)]['speedup'].mean()
                FLOP_cyc = summary_df[(summary_df['threads'] == t) &
                                      (summary_df['warps'] == w) &
                                      (summary_df['is_base'] == is_b)]['FLOP/cycle'].mean()
                final_df = pd.concat([final_df, pd.DataFrame({'threads': [t],
                                                              'warps': [w],
                                                              'cfg':
                                                              ['w{:,.0f}_t{:,.0f}'.format(w, t)],
                                                              'is_base': [is_b],
                                                              'speedup': [speedup],
                                                              'FLOP/cycle': [FLOP_cyc]})])
    # order the final_df
    final_df = final_df.sort_values(by=['threads', 'warps'])
    # rename is_base==1 to base
    final_df['is_base'] = final_df['is_base'].apply(lambda x: 'baseline' if x else 'CFM+3xDMSL')
    final_df['perf_ratio'] = 1
    for w in final_df['warps'].unique():
        for t in final_df['threads'].unique():
            base_perf = final_df[(final_df['threads'] == t) &
                                 (final_df['warps'] == w) &
                                 (final_df['is_base'] == 'baseline')]['FLOP/cycle'].values[0]
            perf = final_df[(final_df['threads'] == t) &
                            (final_df['warps'] == w) &
                            (final_df['is_base'] == 'CFM+3xDMSL')]['FLOP/cycle'].values[0]
            final_df.loc[(final_df['threads'] == t) &
                         (final_df['warps'] == w) &
                         (final_df['is_base'] == 'CFM+3xDMSL'), 'perf_ratio'] = perf/base_perf
    print(final_df.to_string())  # for debug purposes
    return final_df


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
    # df = df[~df['kernel'].isin(CDEFS.BASE_KERNELS.values())]
    ic_df = gen_intercore_df(df.copy())

    fig = plt.figure(figsize=(X_SIZE, Y_SIZE))
    # Plotting line plot ##################################################
    ax = fig.add_subplot(111)
    sns.lineplot(x='cfg', y='FLOP/cycle', hue='is_base', markers=True, style='is_base',
                 data=ic_df, ax=ax, palette='tab10', markersize=MARKERSIZE)
    for tick in ax.get_xticklabels():
        tick.set_rotation(30)
    ax.set_ylabel('FLOP/cycle')
    ax.set_xlabel('')
    ax.get_legend().remove()
    ax.grid(which='minor', linestyle=':', linewidth='0.5')
    ax.grid(which='major')
    ax.grid(axis='x', linestyle=':', linewidth='0.5')

    # Add second y-axis for speedup (right) ########################################
    ax2 = ax.twinx()
    sns.lineplot(x='cfg', y='perf_ratio', markers=True, style='is_base', hue='is_base',
                 style_order=['yo', 'yo2', 'CFM+3xDMSL'], hue_order=['yo', 'yo2', 'CFM+3xDMSL'],
                 data=ic_df[ic_df['is_base'] == 'CFM+3xDMSL'], ax=ax2, palette='tab10',
                 markersize=MARKERSIZE, linestyle='--')
    ax2.set_ylabel('Performance Ratio')
    # set y axis limits
    ax2.set_ylim(3.8, 7.4)
    # Make both axes have the same number of ticks
    ax2.yaxis.set_major_locator(plt.MaxNLocator(5))
    ax.yaxis.set_major_locator(plt.MaxNLocator(5))
    ax2.get_legend().remove()

    # Save the plot ################################################
    for fmt in CPLT.FORMATS:
        plt.savefig(os.path.join(plots_dir, figure_name + '.' + fmt),
                    bbox_inches='tight', format=fmt, pad_inches=0)
    plt.close()
