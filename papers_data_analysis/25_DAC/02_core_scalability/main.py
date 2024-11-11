"""Main script to plot the instruction"""

import os
import sys
import pandas as pd

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
import common.parsers as parsers  # noqa E402
import common.utils as utils  # noqa E402
import src.data_analysis as da  # noqa E402
import src.plot as plot  # noqa E402

parser = parsers.ParserClass(os.path.dirname(__file__))

res_dirs = utils.get_result_dirs(os.path.dirname(__file__))
# get the full path
res_dirs = [os.path.join(parser.args.results_dir, d) for d in res_dirs]
# remove the plots directory
res_dirs = [d for d in res_dirs if not os.path.samefile(d, parser.args.plots_dir)]

df = pd.DataFrame()
for d in res_dirs:
    print("Processing directory: {}".format(d))
    app = d.split("/")[-1]
    df = pd.concat([df, da.get_dataframe(d, app)])  # df are here processed
df = df.reset_index(drop=True)
plot.gen_plot(df, parser.args.plots_dir, parser.args.figure_name)
