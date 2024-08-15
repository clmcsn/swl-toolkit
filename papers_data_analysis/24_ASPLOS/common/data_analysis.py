"""Common funtions for data analysis"""

import pandas as pd
from . import defines as CDEFS


def merge_for_repeat(df: pd.DataFrame, app: str) -> pd.DataFrame:
    """Merge the dataframes for repeat runs"""
    df_repeat1 = df[df['repeat'] == 1].reset_index(drop=True)
    df_repeat2 = df[df['repeat'] == 2].reset_index(drop=True)
    df_merged = pd.merge(df_repeat1, df_repeat2, on=CDEFS.MERGE_ON[app],
                         suffixes=('_r1', '_r2'))
    # Process metrics
    df_merged['instrs'] = df_merged['instrs_r2'] - df_merged['instrs_r1']
    df_merged['cycles'] = df_merged['cycles_r2'] - df_merged['cycles_r1']
    # Merge workload size
    if "workload_size_y" in df_merged.columns:
        df_merged['workload_size'] = (df_merged['workload_size_x'] *
                                      df_merged['workload_size_y'])
    # Remove outliers ################################################
    df_merged['cycles'] = df_merged['cycles'].mask(df_merged['cycles'] <= 0).ffill()
    # Compute the ratio of instructions and cycles
    df_merged['instrs_ratio'] = 1
    df_merged['cycles_ratio'] = 1
    for ws in df_merged['workload_size'].unique():
        base_df = df_merged[(df_merged['workload_size'] == ws) &
                            (df_merged['kernel'] == CDEFS.BASE_KERNELS[app])]
        base_instrs = base_df['instrs'].values[0]
        base_cycles = base_df['cycles'].values[0]
        df_merged.loc[(df_merged['workload_size'] == ws)
                      & (df_merged['kernel'] != CDEFS.BASE_KERNELS[app]),
                      'instrs_ratio'] = base_instrs / df_merged['instrs']
        df_merged.loc[(df_merged['workload_size'] == ws)
                      & (df_merged['kernel'] != CDEFS.BASE_KERNELS[app]),
                      'cycles_ratio'] = base_cycles / df_merged['cycles']
    # Normalize workload size
    hw_norm_val = (df_merged['cores'].unique()[0] *
                   df_merged['threads'].unique()[0] *
                   df_merged['warps'].unique()[0] *
                   df_merged['clusters'].unique()[0])
    df_merged['workload_size'] = df_merged['workload_size'] / hw_norm_val
    return df_merged
