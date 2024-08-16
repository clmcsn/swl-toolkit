"""Main script to plot the cycle bars"""

import os
import sys
import pandas as pd

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
import common.parsers as parsers  # noqa E402
import src.data_analysis as da  # noqa E402
import src.plot as plot  # noqa E402

parser = parsers.ParserClass(os.path.dirname(__file__))

df = pd.DataFrame()
for d in os.listdir(parser.args.results_dir):
    print("Processing: ", d)
    d = os.path.join(parser.args.results_dir, d)
    if os.path.samefile(d, parser.args.plots_dir):
        continue
    app = d.split("/")[-1]
    df = pd.concat([df, da.get_dataframe(d, app)])
df = df.reset_index(drop=True)
df = da.normalize(df)

plot.gen_plot(df, parser.args.plots_dir, parser.args.figure_name)
