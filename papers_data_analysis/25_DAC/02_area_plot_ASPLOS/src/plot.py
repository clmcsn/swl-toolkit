"""Plotting Figure 1"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as font_manager

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import plots as CPLT # noqa E402

SCALE = 5
X_SIZE = 8.45*SCALE*CPLT.CM/3
Y_SIZE = 8.45*SCALE*CPLT.CM/6
MARKERSIZE = 9


def gen_plot(df: pd.DataFrame, plots_dir: str, figure_name: str):
    """
        Generate the plot for Figure 1
        Plots is a 3x6 grid with cycles and instruction ratio for all benchmarks
        Legend is common for all plots and is placed at the bottom of the figure
    """
    CPLT.load_font(CPLT.FONT_PATH)
    # Remove warps <8
    df = df[df['warps'] >= 8]
    fig, axs = plt.subplots(1, 2, figsize=(X_SIZE, Y_SIZE))

    sns.lineplot(x='cfg', y='area', hue='ports',
                 hue_order=[1, 2, 3, 4, 0], markers=True,
                 style='ports', style_order=[1, 2, 3, 4, 0],
                 data=df.loc[df['l3cache'] == 1], ax=axs[0],
                 palette='tab10', markersize=MARKERSIZE)
    for tick in axs[0].get_xticklabels():
        tick.set_rotation(30)
    # force y-axis to go to 1e7
    # axs[0].set_ylim(0.8*1e6, 1.15*1e7)
    # axs[0].set_yscale('log')
    # Set y-axis to have 1e6 as base
    axs[0].ticklabel_format(axis='y', style='sci', scilimits=(6, 6))
    axs[0].set_ylabel('Area (mm^2)')
    axs[0].set_xlabel('')
    axs[0].get_legend().remove()
    axs[0].grid(which='minor', linestyle=':', linewidth='0.5')
    axs[0].grid(which='major')
    axs[0].grid(axis='x', linestyle=':', linewidth='0.5')

    df = df[df['area_ratio'] != 1.0]
    sns.lineplot(x='cfg', y='area_ratio', hue='ports',
                 hue_order=[1, 2, 3, 4, 0], markers=True,
                 style='ports', style_order=[1, 2, 3, 4, 0],
                 data=df.loc[df['l3cache'] == 1], ax=axs[1],
                 palette='tab10', markersize=MARKERSIZE)
    for tick in axs[1].get_xticklabels():
        tick.set_rotation(30)
    axs[1].set_ylabel('Area Overhead (%)')
    # Add at least 4 ticks in the y-axis
    axs[1].yaxis.set_major_locator(plt.MaxNLocator(5))
    axs[1].set_xlabel('')
    axs[1].get_legend().remove()
    axs[1].grid()
    axs[1].grid(axis='x', linestyle=':', linewidth='0.5')

    # change font to calibi and increase size
    for ax in axs.flat:
        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                     ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontname('Calibri')
            size = item.get_fontsize()
            item.set_fontsize(size * 1.1)

    # add common legend
    handles, labels = axs[0].get_legend_handles_labels()
    # make handles and labels start from the third element and then the other elements
    handles = handles[4:] + handles[:3]
    labels = ["baseline", "1 port", "2 ports", "3 ports"]
    fig.legend(handles, labels, loc=8, bbox_to_anchor=(0.5, - 0.08), ncol=4)
    plt.tight_layout()

    # Save the plot ################################################
    for fmt in CPLT.FORMATS:
        plt.savefig(os.path.join(plots_dir, figure_name + '.' + fmt),
                    bbox_inches='tight', format=fmt, pad_inches=0)
    plt.close()
