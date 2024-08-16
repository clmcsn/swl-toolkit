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


def make_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Make the summary dataframe"""
    port_number = df['dcache_ports'].unique()[0]
    area = DDEFS.AREA[DDEFS.AREA['dcache_ports'] == port_number]['area'].values[0]
    sdf = pd.DataFrame({
        "app": [df['app'].unique()[0]],
        "dcache_ports": [port_number],
        "cycles": [df['cycles'].mean()],
        "area_x_cycles": [df['cycles'].mean() * area],
        "ssr_stalls": [df['ssr_stalls'].mean()],
        "dcache_bank_stalls": [df['dcache_bank_stalls'].mean()],
    })
    return sdf


def get_dataframe(path: str, dir_name: str) -> pd.DataFrame:
    """Get the dataframe from the root path and workload"""
    df_file = os.path.join(path, CDEFS.DF_FNAME)
    df = pd.read_feather(df_file)
    app = get_app_name(dir_name)
    df = cda.merge_for_repeat(df, app, ratio=False)
    df = df.sort_values(by=['dcache_ports', 'workload_size']).reset_index(drop=True)
    # remove _airbender form app name
    df['app'] = df['app'].str.replace('-airbender', '')
    if df['app'].unique()[0] == 'saxpy':
        print(df)
    df = make_summary(df)
    return df


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize data across ports"""
    for app in df['app'].unique():
        # normalize over maximum across all ports
        df.loc[df['app'] == app, 'cycles'] = df[df['app'] == app]['cycles'] / \
            df[df['app'] == app]['cycles'].max()
        df.loc[df['app'] == app, 'ssr_stalls'] = df[df['app'] == app]['ssr_stalls'] / \
            df[df['app'] == app]['ssr_stalls'].max()
        df.loc[df['app'] == app, 'dcache_bank_stalls'] = df[df['app'] == app]['dcache_bank_stalls']\
            / df[df['app'] == app]['dcache_bank_stalls'].max()
        df.loc[df['app'] == app, 'area_x_cycles'] = df[df['app'] == app]['area_x_cycles'] / \
            df[df['app'] == app]['area_x_cycles'].max()

    benchmark_order = ['vecadd', 'saxpy', 'sgemm', 'knn', 'sfilter', 'conv2d']
    df['order'] = 0
    for i, b in enumerate(benchmark_order):
        df.loc[df['app'] == b, 'order'] = i
    df = df.sort_values(by='order')
    return df
