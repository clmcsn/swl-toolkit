"""Main script to plot the area and area overhead"""

import os
import sys
import pandas as pd

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
import common.parsers as parsers  # noqa E402
from inputs.data import area_df  # noqa E402
import src.plot as plot  # noqa E402


def make_cfg_string(row):
    # avoiding the use of f-strings for compatibility with python 3.5
    return "w{:,.0f}_t{:,.0f}".format(row['warps'], row['threads'])


parser = parsers.ParserClass(os.path.dirname(__file__))

df: pd.DataFrame = area_df
df['cfg'] = df.apply(make_cfg_string, axis=1)
plot.gen_plot(df, parser.args.plots_dir, parser.args.figure_name)
