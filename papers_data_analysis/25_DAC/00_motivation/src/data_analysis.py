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


def keep_only_base_kernel(df: pd.DataFrame, app: str) -> pd.DataFrame:
    """Keep only the base kernel"""
    base_kernel = CDEFS.BASE_KERNELS[app]
    # replace the kernel name with the base kernel name
    df['kernel'] = df['kernel'].replace(base_kernel, app)
    return df[df['kernel'] == app]

def get_dataframe(path: str, dir_name: str) -> pd.DataFrame:
    """Get the dataframe from the root path and workload"""
    df_file = os.path.join(path, CDEFS.DF_FNAME)
    df = pd.read_feather(df_file)
    app = get_app_name(dir_name)
    df = keep_only_base_kernel(df, app)
    df = cda.merge_for_repeat(df, app)
    df = cda.add_flops(df, app)
    df = cda.process_workload_size(df, app)

    return df