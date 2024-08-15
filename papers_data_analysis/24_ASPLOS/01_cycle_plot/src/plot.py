"""Plotting Figure 0"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
from matplotlib.lines import Line2D
from math import ceil

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import plots as CPLT # noqa E402

XTICK_TILT = 29

SCALE = 5/3
ASPECT_RATIO = 1/2
X_SIZE = (2*8.45 + 0.83)*SCALE*CPLT.CM
Y_SIZE = X_SIZE*ASPECT_RATIO

font_manager.fontManager.addfont(CPLT.FONT_PATH)

APPS = ['vecadd', 'saxpy', 'sgemm', 'knn', 'sfilter', 'conv2d']
APPS = [x + '-airbender' for x in APPS]
THREADS = [8, 16, 32]
TITLES = ['vecadd\nvlen→[4:160:1.5]',
          'saxpy\nvlen→[4:160:1.5]',
          'sgemm\nZ=16\nX*Y→[4:50:0.25]',
          'knn\nvlen→[4:100:1.5]',
          'sfilter\nX*Y→[4:50:0.25]',
          'conv2d\nC=8 K=1\nX*Y→[4:50:0.25]']
HW_CONFIGS = ["1C-2c-4w-8t", "1C-4c-8w-16t", "4C-4c-8w-32t"]
AXES = ['HW: {}\nAvg Speedup'.format(x) for x in HW_CONFIGS]


def add_grid(ax, y_axis_lim):
    step = 0
    if y_axis_lim > 20:
        step = 6
    elif y_axis_lim > 15:
        step = 5
    elif y_axis_lim > 10:
        step = 4
    elif y_axis_lim > 5:
        step = 3
    else:
        step = 2
    ymax = ceil(y_axis_lim)
    ticks = range(0, ymax, step)
    ax.yaxis.set_ticks(ticks)
    ax.yaxis.grid(True)


def gen_plot(df: pd.DataFrame, plots_dir: str, figure_name: str):
    """
        Generate the plot for Figure 1
        Plots is a 3x6 grid with cycles and instruction ratio for all benchmarks
        Legend is common for all plots and is placed at the bottom of the figure
    """
    fig, axs = plt.subplots(3, 6, figsize=(X_SIZE, Y_SIZE))
    for i, app in enumerate(APPS):
        data = df[df['app'] == app]
        max_cycles_ratio = data['cycles_ratio'].max()
        max_instrs_ratio = data['instrs_ratio'].max()
        ymax = max(max_cycles_ratio, max_instrs_ratio)
        y_axis_lim = ymax + 0.05*ymax
        for j, thread in enumerate(THREADS):
            ax = axs[j, i]
            cdata = data[data['threads'] == thread]
            sns.barplot(x='kernel', y='cycles_ratio', data=cdata, ax=ax)
            sns.scatterplot(x='kernel', y='instrs_ratio', data=cdata, hue='kernel', ax=ax,
                            marker='D', legend=False, edgecolor='black')
            if j == 0:
                ax.set_title(TITLES[i])
            if i == 0:
                ax.set_ylabel(AXES[j])
            ax.set_ylim(0, y_axis_lim)
            for t in ax.get_xticklabels():
                t.set_rotation(XTICK_TILT)
            ax.set_xlabel('')
            add_grid(ax, y_axis_lim)

    # add custom legend for max instrs ratio
    legend_elements = [Line2D([0], [0], marker='D', color='w', label='Avg Instructions Reduction',
                       markerfacecolor='black', markersize=8)]
    fig.legend(handles=legend_elements, loc=8, bbox_to_anchor=(0.5, - 0.06), ncol=1)

    # change font to calibi and increase size
    for ax in axs.flat:
        for item in ([ax.xaxis.label, ax.yaxis.label]
                     + ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontname('Calibri')
            size = item.get_fontsize()
            item.set_fontsize(size * 1.2)
    plt.tight_layout()

    # Save the plot ################################################
    for fmt in CPLT.FORMATS:
        plt.savefig(os.path.join(plots_dir, figure_name + '.' + fmt),
                    bbox_inches='tight', format=fmt, pad_inches=0)
    plt.close()
