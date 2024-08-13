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
        return 'hwloops + W-SSL'
    elif re.match(r'.*-ssr2', app):
        return 'hwloops + W-SSL + 1xR-SSL'
    elif re.match(r'.*-ssr3', app):
        return 'hwloops + W-SSL + 2xR-SSL'
    elif re.match(r'.*-loop', app):
        return 'hwloops (+TMLS)'
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
