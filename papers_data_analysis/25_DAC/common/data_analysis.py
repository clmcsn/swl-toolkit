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
    for metric in CDEFS.METRICS:
        df_merged[metric] = CDEFS.METRIC_RED_FUNC[metric](df_merged[metric + '_r2'], df_merged[metric + '_r1'])
        # Remove outliers
        df_merged[metric] = df_merged[metric].mask(df_merged[metric] <= 0).ffill()
    return df_merged

def add_flops(df: pd.DataFrame, app: str) -> pd.DataFrame:
    """Add the FLOPS column"""
    df['flops'] = 0
    match app:
        case "aggr":
            for g in df['dataset'].unique():
                df.loc[df['dataset'] == g, 'flops'] = CDEFS.GRAPH_LINKS[g] * df['vlen']
        case "conv2d":
            df['flops'] = df['out_channels'] * df['in_channels'] * df['workload_size_x'] * df['workload_size_y'] * 9
        case "sgemm":
            df['flops'] = df['workload_size_x'] * df['workload_size_y'] * df['workload_size_z']
        case "sgemv":
            df['flops'] = df['workload_size_x'] * df['workload_size_y']
        case "sfilter":
            df['flops'] = df['workload_size_x'] * df['workload_size_y'] * 9
        case "vecadd":
            df['flops'] = df['workload_size']
        case "saxpy":
            df['flops'] = df['workload_size']
        case "knn":
            df['flops'] = df['workload_size'] * 4
    return df

def process_workload_size(df_merged: pd.DataFrame, app) -> pd.DataFrame:
    # Merge workload size
    if "workload_size_y" in df_merged.columns and app != "sgemv":
        df_merged['workload_size'] = (df_merged['workload_size_x'] *
                                      df_merged['workload_size_y'])
    if app == "sgemv":
        df_merged['workload_size'] = df_merged['workload_size_x']
    # df_merged = df_merged.sort_values(by=['kernel', 'workload_size'])
    return df_merged

def make_ratios(df_merged: pd.DataFrame, app: str) -> pd.DataFrame:
    # Compute the ratio of instructions and cycles
    df_merged['instrs_ratio'] = 1.0
    df_merged['cycles_ratio'] = 1.0
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
    return df_merged
    
def norm_hardware(df_merged: pd.DataFrame) -> pd.DataFrame:
    # Normalize workload size
    hw_norm_val = (df_merged['cores'].unique()[0] *
                   df_merged['threads'].unique()[0] *
                   df_merged['warps'].unique()[0] *
                   df_merged['clusters'].unique()[0])
    df_merged['workload_size'] = df_merged['workload_size'] / hw_norm_val
    return df_merged

def make_avg(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Make the average of the metric"""
    # Add a new row: kernel = 'avg', metric = average of the metric of all kernels
    avg = df[metric].mean()
    df = pd.concat([df, pd.DataFrame({'kernel': ['mean'], metric: [avg]})])
    return df
