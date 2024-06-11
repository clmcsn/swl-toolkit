"""Script to plot comparison plots for different architectures"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

#####################################################################
# Adding the freaking calibri font
import matplotlib.font_manager as font_manager

font_path = '../../calibri-font-family/calibri-regular.ttf'

font_manager.fontManager.addfont(font_path)

#####################################################################
# dirs
base_dir = "/users/micas/gsarda/vortex/vortex-KUL-fork/scripts/outputs/ASPLOS-SWIFT-ARC-COMP"
dir_tmlp = base_dir+"/{}-rm-{}"
hw_cfgs = ["1C4c8w8t", "1C4c8w16t", "1C4c8w32t"]
kernels = ["conv2d", "knn", "saxpy", "vecadd", "sfilter", "sgemm"]

#####################################################################
# df preparation

vecadd_df = pd.DataFrame()
for hw_cfg in hw_cfgs:
    vecadd_df_file = dir_tmlp.format("vecadd", hw_cfg) + "/dataframe.feather"
    vecadd_df = pd.concat([vecadd_df, pd.read_feather(vecadd_df_file)])

vecadd_df_repeat1 = vecadd_df[vecadd_df['repeat'] == 1].reset_index(drop=True)
vecadd_df_repeat2 = vecadd_df[vecadd_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
vecadd_df = pd.merge(vecadd_df_repeat1, vecadd_df_repeat2, on=['workload_size', 'threads', 'warps', 'dcache_ports','clusters', 'cores', 'write_back'], suffixes=('_r1', '_r2'))
vecadd_df['instrs'] = vecadd_df['instrs_r2'] - vecadd_df['instrs_r1']
vecadd_df['cycles'] = vecadd_df['cycles_r2'] - vecadd_df['cycles_r1']

#make workload size relative to threads
vecadd_df['workload_size'] = vecadd_df['workload_size'] / vecadd_df['threads']

# plot cycles and instructions
#plotting
cm = 1/2.54  # centimeters in inches
plot_size_x = (2*8.45 +0.83)*cm
plot_size_y = plot_size_x*(6/2)
scale = 5/3

fig, axs = plt.subplots(6, 2, figsize=(plot_size_x*scale, plot_size_y*scale))

sns.lineplot(data=vecadd_df.loc[vecadd_df['write_back']== 0], x='workload_size', y='instrs', hue='threads', style='threads', ax=axs[0, 0])
sns.lineplot(data=vecadd_df.loc[vecadd_df['write_back']== 0], x='workload_size', y='cycles', hue='threads', style='threads', ax=axs[1, 0])
sns.lineplot(data=vecadd_df.loc[vecadd_df['write_back']== 1], x='workload_size', y='instrs', hue='threads', style='threads', ax=axs[0, 1])
sns.lineplot(data=vecadd_df.loc[vecadd_df['write_back']== 1], x='workload_size', y='cycles', hue='threads', style='threads', ax=axs[1, 1])

#####################################################################
# Save the plot
#plt.tight_layout()
output_dir = base_dir + "/plots"
os.makedirs(output_dir, exist_ok=True)
plt.savefig(output_dir + "/vecadd_instr_cycles.pdf", format='pdf')
plt.savefig(output_dir + "/vecadd_instr_cycles.svg", format='svg')
