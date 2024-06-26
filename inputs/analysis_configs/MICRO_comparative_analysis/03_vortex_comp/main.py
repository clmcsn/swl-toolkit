"""Script to plot comparison plots for different architectures"""

import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
import seaborn as sns

import generic_functions as gf

#####################################################################
# Adding the freaking calibri font
import matplotlib.font_manager as font_manager

font_path = '../../calibri-font-family/calibri-regular.ttf'

font_manager.fontManager.addfont(font_path)

#####################################################################
# dirs
base_dir = "/users/micas/gsarda/vortex/vortex-KUL-fork/scripts/outputs/05-SWIFTvsVORTEX/"

dfs = {}
for d in os.listdir(base_dir):
    if (d == "plots"):
        continue
    benchmark = d.split("/")[-1].split("-")[1]
    hw_arch = d.split("/")[-1].split("-")[-1]
    d = base_dir + d
    dfs[benchmark] = pd.concat([dfs[benchmark], gf.gen_df(d, benchmark)]) if benchmark in dfs else gf.gen_df(d, benchmark)

sum_df = pd.DataFrame()
for b in dfs.keys():
    sum_df = pd.concat([sum_df,gf.make_summary_df(dfs[b])], ignore_index=True)

benchmark_order = ['vecadd', 'saxpy', 'sgemm', 'knn', 'sfilter', 'conv2d']
sum_df['order'] = 0
for i, b in enumerate(benchmark_order):
    sum_df.loc[sum_df['app'] == b, 'order'] = i
sum_df = sum_df.sort_values(by='order')

# plot 4 gouped bar plots

cm = 1/2.54  # centimeters in inches
scale = 5
#subdividing the plot into 4 subplots

hatches = ['//', '..', 'xx']
aspectR=3
y_axis_str = 1e2
font_incr = 3.5
fontproperties = {'family': 'Calibri', 'size': 10*font_incr}


plot_labels = {
    'cycles': 'Cycles',
    'ssr_stalls': 'SSL Stalls',
    'cycle_area': 'Cycle-Area Product',
    'dcache_bank_utilization': 'Cache Bank Utilization',
    'dcache_bank_stalls': 'Dcache Bank Stalls'
}

for m in ['cycles', 'ssr_stalls', 'cycle_area', 'dcache_bank_utilization', 'dcache_bank_stalls']:
    g = sns.catplot(x="app", y=m, hue="clusters", data=sum_df, kind="bar", height=8.45/3*cm*scale, aspect=aspectR, width=0.6, legend=False)

    plt.ylabel(plot_labels[m], fontproperties)
    plt.yticks(fontproperties=fontproperties)
    plt.xlabel("", fontproperties)
    #tilt x-axis labels
    #plt.xticks(rotation=30)
    plt.xticks(fontproperties=fontproperties)

    if m == 'dcache_bank_utilization':
        plt.ylim(0, 100)
    if m == 'dcache_bank_utilization':
        plt.legend(title='Clusters', loc='upper center', bbox_to_anchor=(0.5, 0.5), ncol=4, prop=fontproperties,title_fontproperties=fontproperties)

    plt.grid(axis='y', linestyle='--', linewidth=0.5)
    plt.tight_layout()

    output_path = base_dir + "/plots/"
    os.makedirs(output_path, exist_ok=True)
    g.savefig(output_path + m + ".pdf", format='pdf')
    g.savefig(output_path + m + ".svg", format='svg')
    plt.close()
    plt.clf()


# same as above but plotting only saxpy, sgemm, sfilter and knn

# plot 4 gouped bar plots
