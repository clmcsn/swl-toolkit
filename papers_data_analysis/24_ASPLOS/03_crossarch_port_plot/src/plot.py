"""Plotting Figure 12"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as font_manager

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import plots as CPLT # noqa E402

SCALE = 5
HEIGHT = 8.45*SCALE*CPLT.CM/3
WIDTH = 0.6
ASPECT_RATIO = 10/9
FONT_SCALE = 3.5
FONT_PROPERTIES = {'family': 'Calibri', 'size': 10*FONT_SCALE}

PLOT_LABELS = {
    'cycles': 'Cycles',
    'ssr_stalls': 'SSL Stalls',
    'area_x_cycles': 'Area-Delay Product',
    'dcache_bank_stalls': 'Dcache Bank Stalls'
}

PLOT_SUFFIX = {
    'cycles': 'a',
    'ssr_stalls': 'c',
    'area_x_cycles': 'b',
    'dcache_bank_stalls': 'd'
}


def gen_plot(df: pd.DataFrame, plots_dir: str, figure_name: str):
    """
        Generate the plot for Figure 12
        Plots generates 4 different images for each metric
    """
    CPLT.load_font(CPLT.FONT_PATH)
    for metric in ['cycles', 'area_x_cycles', 'ssr_stalls', 'dcache_bank_stalls']:
        sns.catplot(x="app", y=metric, hue="dcache_ports", data=df, kind="bar",
                    height=HEIGHT, aspect=ASPECT_RATIO, width=WIDTH, legend=False)
        plt.ylabel(PLOT_LABELS[metric], FONT_PROPERTIES)
        plt.yticks(fontproperties=FONT_PROPERTIES)
        plt.xlabel('', FONT_PROPERTIES)
        plt.xticks(fontproperties=FONT_PROPERTIES, rotation=30)

        plt.grid(axis='y', linestyle='--', linewidth='0.5')
        plt.tight_layout()

        # Save the plot ################################################
        for fmt in CPLT.FORMATS:
            plt.savefig(os.path.join(plots_dir, figure_name + PLOT_SUFFIX[metric] + '.' + fmt),
                        bbox_inches='tight', format=fmt, pad_inches=0)
        plt.close()
        plt.clf()
