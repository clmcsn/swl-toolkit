"""Main script to plot the instruction"""

import os
import pandas as pd

from ..common import parsers
from . import data_analysis as da
from . import plot

parser = parsers.ParserClass()

df = pd.DataFrame()
for d in os.listdir(parser.args.results_dir):
    d = os.path.join(parser.args.results_dir, d)
    if d == parser.args.plots_dir:
        continue
    app = d.split("/")[-1]
    df = pd.concat([df, da.get_dataframe(d, app)])
df = df.reset_index(drop=True)
plot.gen_plot(df, parser.args.plots_dir)
