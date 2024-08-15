"""Plotting Figure 0"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import plots as CPLT # noqa E402

SCALE = 5*8.45
X_SIZE = SCALE*CPLT.CM/3
Y_SIZE = SCALE*CPLT.CM/3.2
HUE_ORDER = ['baseline', 'hwloops (+TMLS)', 'hwloops + W-SSL',
             'hwloops + W-SSL + 1xR-SSL', 'hwloops + W-SSL + 2xR-SSL']
LINEWIDTH = 1.8
font_manager.fontManager.addfont(CPLT.FONT_PATH)


def gen_plot(df: pd.DataFrame, plots_dir: str, figure_name: str):
    """
        Generate the plot for Figure 0
        Plots is a 2x2 grid with instructions and instruction ratio for vecadd and sgemm
        Legend is common for all plots and is placed at the bottom of the figure
    """
    fig, axs = plt.subplots(2, 2, figsize=(X_SIZE, Y_SIZE))
    vecadd_df = df[df['app'] == 'vecadd-airbender']
    sgemm_df = df[df['app'] == 'sgemm-airbender']

    # Plot instructions for vecadd ################################################
    sns.lineplot(ax=axs[0, 0], data=vecadd_df, x='workload_size', y='instrs',
                 hue='kernel', hue_order=HUE_ORDER, style='kernel', style_order=HUE_ORDER,
                 linewidth=LINEWIDTH)
    axs[0, 0].ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    axs[0, 0].set_title('vecadd')
    axs[0, 0].grid()
    axs[0, 0].set_ylabel('Instructions')
    axs[0, 0].set_xlabel('Thread Iterations')
    axs[0, 0].get_legend().remove()

    # Plot instructions for sgemm ################################################
    sns.lineplot(ax=axs[1, 0], data=sgemm_df, x='workload_size', y='instrs',
                 hue='kernel', hue_order=HUE_ORDER, style='kernel', style_order=HUE_ORDER,
                 linewidth=LINEWIDTH)
    axs[1, 0].set_title('sgemm')
    axs[1, 0].grid()
    axs[1, 0].set_ylabel('Instructions')
    axs[1, 0].set_xlabel('Thread Iterations')
    axs[1, 0].get_legend().remove()

    # Plot instruction ratio for vecadd ################################################
    sns.lineplot(ax=axs[0, 1], data=vecadd_df, x='workload_size', y='instrs_ratio',
                 hue='kernel', hue_order=HUE_ORDER, style='kernel', style_order=HUE_ORDER,
                 linewidth=LINEWIDTH)
    axs[0, 1].set_title('vecadd')
    axs[0, 1].grid()
    axs[0, 1].set_ylabel('Instructions Reduction')
    axs[0, 1].set_xlabel('Thread Iterations')
    axs[0, 1].get_legend().remove()

    # Plot instruction ratio for sgemm ################################################
    sns.lineplot(ax=axs[1, 1], data=sgemm_df, x='workload_size', y='instrs_ratio',
                 hue='kernel', hue_order=HUE_ORDER, style='kernel', style_order=HUE_ORDER,
                 linewidth=LINEWIDTH)
    axs[1, 1].set_title('sgemm')
    axs[1, 1].grid()
    axs[1, 1].set_ylabel('Instructions Reduction')
    axs[1, 1].set_xlabel('Thread Iterations')
    axs[1, 1].get_legend().remove()

    # Add common legend ################################################
    handles, labels = axs[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc=8, bbox_to_anchor=(0.5, - 0.17), ncol=2, fontsize='large')

    # Change font to Calibri and increase size ################################################
    for ax in axs.flat:
        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                     ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontname('Calibri')
            size = item.get_fontsize()
            item.set_fontsize(size * 1.3)
    plt.tight_layout()

    # Save the plot ################################################
    for fmt in CPLT.FORMATS:
        plt.savefig(os.path.join(plots_dir, figure_name + '.' + fmt),
                    bbox_inches='tight', format=fmt, pad_inches=0)
    plt.close()
