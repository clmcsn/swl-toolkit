"""Module for data analysis"""

import os
import sys
import pandas as pd

from . import defines as DDEFS
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
from common import data_analysis as cda  # noqa E402
from common import defines as CDEFS  # noqa E402


def get_app_name(dir_name: str) -> str:
    """Get the application name"""
    for app in DDEFS.APP_NAMES:
        if app in dir_name:
            return app
    raise ValueError('Invalid directory name')


def add_unrolling_factor(df: pd.DataFrame, dir_name: str) -> pd.DataFrame:
    """Add the unrolling factor to the dataframe"""
    try:
        unrolling_factor = int(dir_name.split('-')[-1][1:])
    except ValueError:
        unrolling_factor = 1
    df['unrolling_factor'] = unrolling_factor
    return df


def make_ratios(df_merged: pd.DataFrame) -> pd.DataFrame:
    # Compute the ratio of instructions and cycles
    df_merged['instrs_ratio'] = 1.0
    df_merged['cycles_ratio'] = 1.0
    for app in df_merged['app'].unique():
        cdf = df_merged.loc[df_merged['app'] == app]
        for ws in cdf['workload_size'].unique():
            base_df = df_merged[(df_merged['workload_size'] == ws) &
                                (df_merged['unrolling_factor'] == 1) &
                                (df_merged['app'] == app)]
            base_instrs = base_df['instrs'].values[0]
            base_cycles = base_df['cycles'].values[0]
            df_merged.loc[(df_merged['workload_size'] == ws) &
                          (df_merged['unrolling_factor'] != 1) &
                          (df_merged['app'] == app),
                          'instrs_ratio'] = base_instrs / df_merged['instrs']
            df_merged.loc[(df_merged['workload_size'] == ws) &
                          (df_merged['unrolling_factor'] != 1) &
                          (df_merged['app'] == app),
                          'cycles_ratio'] = base_cycles / df_merged['cycles']
    return df_merged


def get_dataframe(path: str, dir_name: str) -> pd.DataFrame:
    """Get the dataframe from the root path and workload"""
    df_file = os.path.join(path, CDEFS.DF_FNAME)
    df = pd.read_feather(df_file)
    df = add_unrolling_factor(df, dir_name)
    app = get_app_name(dir_name)
    df = cda.merge_for_repeat(df, app)
    df = cda.add_flops(df, app)
    df = cda.process_workload_size(df, app)
    # df = cda.make_ratios(df, app)
    return df
