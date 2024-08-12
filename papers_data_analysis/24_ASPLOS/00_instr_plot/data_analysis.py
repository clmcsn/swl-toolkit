"""Module for data analysis"""

import os
import re
import pandas as pd

from ..common import data_analysis as cda
from ..common import defines as CDEFS


def replace_kernel_names(app: str) -> str:
    """Replace the kernel names"""
    match app:
        case re.match(r".*-ssr", app):
            return 'hwloops + W-SSL'
        case re.match(r'*-ssr2', app):
            return 'hwloops + W-SSL + 1xR-SSL'
        case re.match(r'*-ssr3', app):
            return 'hwloops + W-SSL + 2xR-SSL'
        case re.match(r'.*-loop', app):
            return 'hwloops (+TMLS)'
        case _:  # default
            return 'baseline'


def get_dataframe(path: str, app: str) -> pd.DataFrame:
    """Get the dataframe from the root path and workload"""
    df_file = os.path.join(path, CDEFS.DF_FNAME)
    df = pd.read_feather(df_file)
    df = cda.merge_for_repeat(df, app)
    df['kernel'] = df['kernel'].apply(replace_kernel_names)
    return df
