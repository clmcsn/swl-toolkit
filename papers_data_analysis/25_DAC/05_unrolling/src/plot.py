"""Plotting Unrolling"""

import os
import sys
import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import plots as CPLT # noqa E402
from common import data_analysis as CDA # noqa E402
from common import defines as CDEFS # noqa E402
from . import defines as DEFS # noqa E402
from . import data_analysis as DA # noqa E402

SCALE = 5*8.45
X_SIZE = SCALE*CPLT.CM/3.2
Y_SIZE = SCALE*CPLT.CM/9.4
KERNEL_ORDER = ['saxpy', 'sgemv', 'sgemm', 'sfilter']
KERNEL_MAPPING = {kernel: i for i, kernel in enumerate(KERNEL_ORDER)}

EXTS_ORDER = ['CFM only', 'CFM+1xDMSL', 'CFM+2xDMSL', 'CFM+3xDMSL']
EXTS_MAPPING = {ext: i for i, ext in enumerate(EXTS_ORDER)}

LINEWIDTH = 2.5


def gen_plot(df: pd.DataFrame, plots_dir: str, figure_name: str):
    """Generate the plot"""
    # rename unrolling_factor_r1 to unrolling_factor
    df.rename(columns={'unrolling_factor_r1': 'unrolling_factor'}, inplace=True)
    df = DA.make_ratios(df)
    # Remove airbender from app name
    df['app'] = df['app'].str.replace('-airbender', '')
    # Data preprocessing ########################################
    summary_df = pd.DataFrame()
    for app in df['app'].unique():
        for uf in df['unrolling_factor'].unique():
            FLOPs = df[(df['unrolling_factor'] == uf) & (df['app'] == app)]['flops'].sum()
            cycles = df[(df['unrolling_factor'] == uf) & (df['app'] == app)]['cycles'].sum()
            speedup = df[(df['unrolling_factor'] == uf) & (df['app'] == app)]['cycles_ratio'].mean()
            ired = df[(df['unrolling_factor'] == uf) & (df['app'] == app)]['instrs_ratio'].mean()
            summary_df = pd.concat([summary_df, pd.DataFrame({'app': [app],
                                                              'unrolling_factor': [uf],
                                                              'FLOPs': [FLOPs],
                                                              'cycles': [cycles],
                                                              'speedup': [speedup],
                                                              'ired': [ired]})])
    summary_df["FLOPs/cycle"] = summary_df["FLOPs"] / summary_df["cycles"]
    print(summary_df.to_string())
    final_df = pd.DataFrame()
    for uf in df['unrolling_factor'].unique():
        FLOPs_per_cycle = summary_df[summary_df['unrolling_factor'] == uf]['FLOPs/cycle'].mean()
        speedup = summary_df[summary_df['unrolling_factor'] == uf]['speedup'].mean()
        ired = summary_df[summary_df['unrolling_factor'] == uf]['ired'].mean()
        final_df = pd.concat([final_df, pd.DataFrame({'unrolling_factor': [uf],
                                                      'FLOPs/cycle': [FLOPs_per_cycle],
                                                      'speedup': [speedup],
                                                      'ired': [ired]})])
    final_df.sort_values(by='unrolling_factor', inplace=True)
    print(final_df.to_string())
