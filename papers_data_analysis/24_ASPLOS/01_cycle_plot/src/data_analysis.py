"""Module for data analysis"""

import os
import re
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


def replace_kernel_names(app: str) -> str:
    """Replace the kernel names"""
    if re.match(r".*-ssr$", app):
        return '+1xSSL'
    elif re.match(r'.*-ssr2', app):
        return '+2xSSL'
    elif re.match(r'.*-ssr3', app):
        return '+3xSSL'
    elif re.match(r'.*-loop', app):
        return 'loops'
    else:  # default
        return 'baseline'


def get_dataframe(path: str, dir_name: str) -> pd.DataFrame:
    """Get the dataframe from the root path and workload"""
    df_file = os.path.join(path, CDEFS.DF_FNAME)
    df = pd.read_feather(df_file)
    app = get_app_name(dir_name)
    df = cda.merge_for_repeat(df, app)
    df['kernel'] = df['kernel'].apply(replace_kernel_names)
    return df


def make_avg_df(df: pd.DataFrame) -> pd.DataFrame:
    """Make the average dataframe"""
    avg_df = pd.DataFrame(columns=['app', 'kernel', 'threads', 'cycles_ratio', 'instrs_ratio'])
    for app in df['app'].unique():
        for kernel in df['kernel'].unique():
            for threads in df['threads'].unique():
                if kernel == 'baseline':
                    continue
                cycle_avg = df[(df['app'] == app) & (df['kernel'] == kernel) 
                               & (df['threads'] == threads)]['cycles_ratio'].mean()
                instr_avg = df[(df['app'] == app) & (df['kernel'] == kernel) 
                               & (df['threads'] == threads)]['instrs_ratio'].mean()
                avg_df = pd.concat([avg_df, pd.DataFrame({'app': [app],
                                                          'kernel': [kernel],
                                                          'threads': [threads],
                                                          'cycles_ratio': [cycle_avg],
                                                          'instrs_ratio': [instr_avg]})])
                avg_df = avg_df.reset_index(drop=True)
    return avg_df
