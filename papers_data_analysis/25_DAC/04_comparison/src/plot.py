"""Plotting Core scaling"""

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
    # Remove airbender from app name
    df['app'] = df['app'].str.replace('-airbender', '')
    if False:  # Need to decomment make ratio from data analysis when True
        ow_df = df.loc[df['cores'] == 1]
        # ow_df = CDA.make_ratios(df)
        # Remove all the kernels that do not end with ssr3
        ow_df = ow_df[ow_df['kernel'].str.endswith('ssr3')]
        # Data preprocessing ########################################
        summary_df = pd.DataFrame()
        for app in ow_df['app'].unique():
            FLOPs = ow_df[ow_df['app'] == app]['flops'].sum()
            cycles = ow_df[ow_df['app'] == app]['cycles'].sum()
            speedup = ow_df[ow_df['app'] == app]['cycles_ratio'].mean()
            ired = ow_df[ow_df['app'] == app]['instrs_ratio'].mean()
            summary_df = pd.concat([summary_df, pd.DataFrame({'app': [app],
                                                              'FLOPs': [FLOPs],
                                                              'cycles': [cycles],
                                                              'speedup': [speedup],
                                                              'ired': [ired]})])
        summary_df["FLOPs/cycle"] = summary_df["FLOPs"] / summary_df["cycles"]
        print(summary_df.to_string())
        final_df = pd.DataFrame()
        FLOPs_per_cycle = summary_df['FLOPs/cycle'].mean()
        speedup = summary_df['speedup'].mean()
        ired = summary_df['ired'].mean()
        final_df = pd.concat([final_df, pd.DataFrame({'FLOPs/cycle': [FLOPs_per_cycle],
                                                      'speedup': [speedup],
                                                      'ired': [ired]})])
        print(final_df.to_string())
        exit()

    # Data preprocessing ########################################
    # Remove all the kernels except for CDEFS.BASE_KERNELS
    df = df[df['kernel'].isin(CDEFS.BASE_KERNELS.values())]
    summary_df = pd.DataFrame()
    for app in df['app'].unique():
        for cores in df['cores'].unique():
            FLOPs = df[(df['cores'] == cores) & (df['app'] == app)]['flops'].sum()
            cycles = df[(df['cores'] == cores) & (df['app'] == app)]['cycles'].sum()
            # speedup = df[(df['cores'] == cores) & (df['app'] == app)]['cycles_ratio'].mean()
            # ired = df[(df['cores'] == cores) & (df['app'] == app)]['instrs_ratio'].mean()
            summary_df = pd.concat([summary_df, pd.DataFrame({'app': [app],
                                                              'cores': [cores],
                                                              'FLOPs': [FLOPs],
                                                              'cycles': [cycles]})])
    summary_df["FLOPs/cycle"] = summary_df["FLOPs"] / summary_df["cycles"]
    print(summary_df.to_string())
    final_df = pd.DataFrame()
    for cores in df['cores'].unique():
        FLOPs_per_cycle = summary_df[summary_df['cores'] == cores]['FLOPs/cycle'].mean()
        # speedup = summary_df[summary_df['cores'] == cores]['speedup'].mean()
        # ired = summary_df[summary_df['cores'] == cores]['ired'].mean()
        final_df = pd.concat([final_df, pd.DataFrame({'cores': [cores],
                                                      'FLOPs/cycle': [FLOPs_per_cycle]})])
    final_df.sort_values(by='cores', inplace=True)
    print(final_df.to_string())
