"""Plotting Figure 0"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import plots as CPLT # noqa E402

SCALE = 5*8.45
X_SIZE = SCALE*CPLT.CM/3.2
Y_SIZE = SCALE*CPLT.CM/3.2
HUE_ORDER = ['saxpy', 'sgemv', 'sgemm']
LINEWIDTH = 2.5


def gen_plot(df: pd.DataFrame, plots_dir: str, figure_name: str):
    """
        Generate the plot for Figure 0
        Plots is a 3x1 grid with cicles for saxpy, sgemv, sgemm
        Legend is common for all plots and is placed at the bottom of the figure
    """
    CPLT.load_font(CPLT.FONT_PATH)
    fig, axs = plt.subplots(1, 1, figsize=(X_SIZE, Y_SIZE))

    # divide workload size of sgemv by 8 workload_size_y
    df.loc[df['kernel'] == 'sgemv', 'workload_size'] = df.loc[df['kernel'] == 'sgemv',
                                                              'workload_size'] / 8

    # Plot the data ################################################
    sns.lineplot(data=df, x='workload_size', y='cycles', hue='kernel',
                 style='kernel', hue_order=HUE_ORDER, style_order=HUE_ORDER,
                 ax=axs, linewidth=LINEWIDTH)
    axs.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    # axs.set_title('sgemm')
    axs.grid()
    axs.set_ylabel('Cycles')
    axs.set_xlabel('Thread Iterations')
    axs.get_legend().remove()

    # Add common legend ################################################
    handles, labels = axs.get_legend_handles_labels()
    fig.legend(handles, labels, loc=8,
               bbox_to_anchor=(0.5, - 0.02),
               ncol=3, fontsize='medium')

    # Change font to Calibri and increase size ################################################
    if os.path.isfile(CPLT.FONT_PATH):
        for ax in axs.flat:
            for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                         ax.get_xticklabels() + ax.get_yticklabels()):
                item.set_fontname('Calibri')
                size = item.get_fontsize()
                item.set_fontsize(size * 2)
    plt.tight_layout()

    # Save the plot ################################################
    for fmt in CPLT.FORMATS:
        plt.savefig(os.path.join(plots_dir, figure_name + '.' + fmt),
                    bbox_inches='tight', format=fmt, pad_inches=0)
    plt.close()
