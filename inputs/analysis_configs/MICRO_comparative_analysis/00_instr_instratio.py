"""Script to plot instruction ratio for different kernels"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

#####################################################################
# Adding the freaking calibri font
import matplotlib.font_manager as font_manager

font_path = '../../calibri-font-family/calibri-regular.ttf'

font_manager.fontManager.addfont(font_path)
#font_name = font_manager.FontProperties(fname=font_path)

vecadd_root = "./scripts/outputs/ASPLOS-COMP-vecadd-im-1C2c4w8t/"
sgemm_root  = "./scripts/outputs/ASPLOS-COMP-sgemm-im-1C2c4w8t/"

#####################################################################
# vecadd df preparation

vecadd_df_file = vecadd_root + "dataframe.feather"
vecadd_baseline = 'vecadd-base'

vecadd_df = pd.read_feather(vecadd_df_file)
vecadd_df_repeat1 = vecadd_df[vecadd_df['repeat'] == 1].reset_index(drop=True)
vecadd_df_repeat2 = vecadd_df[vecadd_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
vecadd_df = pd.merge(vecadd_df_repeat1, vecadd_df_repeat2, on=['workload_size', 'kernel'], suffixes=('_r1', '_r2'))
vecadd_df['instrs'] = vecadd_df['instrs_r2'] - vecadd_df['instrs_r1']

vecadd_df['instr_ratio'] = 1
for ws in vecadd_df['workload_size'].unique():
    vacadd_base_instrs = vecadd_df[(vecadd_df['workload_size'] == ws) & (vecadd_df['kernel'] == vecadd_baseline)]['instrs'].values[0]
    vecadd_df.loc[(vecadd_df['workload_size'] == ws) & (vecadd_df['kernel'] != vecadd_baseline), 'instr_ratio'] = vacadd_base_instrs / vecadd_df['instrs']

#change kernel names
vecadd_df['kernel'] = vecadd_df['kernel'].replace({'vecadd-ssr': 'loops + 1xSSL', 'vecadd-ssr2': 'loops + 2xSSL', 'vecadd-ssr3': 'loops + 3xSSL', 'vecadd-loop': 'loops', 'vecadd-base': 'baseline'})
vecadd_hue_order = ['baseline', 'loops', 'loops + 1xSSL', 'loops + 2xSSL', 'loops + 3xSSL']

#normalize workload size
norm_val = 64
vecadd_df['workload_size'] = vecadd_df['workload_size'] / norm_val

#add a column for linestyles
dashes = {
    'baseline': '',
    'loops': '--',
    'loops + 1xSSL': '-.',
    'loops + 2xSSL': ':',
    'loops + 3xSSL': ''
}


#####################################################################
# sgemm df preparation

sgemm_df_file = sgemm_root + "dataframe.feather"
sgemm_baseline = 'sgemm'

sgemm_df = pd.read_feather(sgemm_df_file)
sgemm_df_repeat1 = sgemm_df[sgemm_df['repeat'] == 1].reset_index(drop=True)
sgemm_df_repeat2 = sgemm_df[sgemm_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
sgemm_df = pd.merge(sgemm_df_repeat1, sgemm_df_repeat2, on=['workload_size_x', 'workload_size_y', 'kernel'], suffixes=('_r1', '_r2'))
sgemm_df['instrs'] = sgemm_df['instrs_r2'] - sgemm_df['instrs_r1']

sgemm_df['workload_size'] = sgemm_df['workload_size_x'] * sgemm_df['workload_size_y'] 

sgemm_df['instr_ratio'] = 1
for ws in sgemm_df['workload_size'].unique():
    sgemm_base_instrs = sgemm_df[(sgemm_df['workload_size'] == ws) & (sgemm_df['kernel'] == sgemm_baseline)]['instrs'].values[0]
    sgemm_df.loc[(sgemm_df['workload_size'] == ws) & (sgemm_df['kernel'] != sgemm_baseline), 'instr_ratio'] = sgemm_base_instrs / sgemm_df['instrs'] 

#change kernel names
sgemm_df['kernel'] = sgemm_df['kernel'].replace({'sgemm': 'baseline', 'sgemm-ssr': 'loops + 1xSSL', 'sgemm-ssr2': 'loops + 2xSSL', 'sgemm-ssr3': 'loops + 3xSSL', 'sgemm-loop': 'loops'})
sgemm_hue_order = ['baseline', 'loops', 'loops + 1xSSL', 'loops + 2xSSL', 'loops + 3xSSL']

#normalize workload size
norm_val = 64
sgemm_df['workload_size'] = sgemm_df['workload_size'] / norm_val

#####################################################################

cm = 1/2.54  # centimeters in inches
scale = 5
#subdividing the plot into 4 subplots

fig, axs = plt.subplots(2, 2, figsize=(8.45/3*cm*scale, 8.45/3.2*cm*scale))

#plot instrs, y axis is instrs, x axis is workload_size, and we have a vertical plot for each kernel
sns.lineplot(x='workload_size', y='instrs', hue='kernel', hue_order=vecadd_hue_order, style='kernel', style_order=vecadd_hue_order, data=vecadd_df, ax=axs[0, 0], linewidth=1.8)
axs[0, 0].ticklabel_format(axis='y', style='sci', scilimits=(0,0))
#plot name
axs[0, 0].set_title('vecadd')
axs[0, 0].grid()
#change axis name
axs[0, 0].set_ylabel('Instructions (#)')
axs[0, 0].set_xlabel('Thread Iterations')
#remove legend
axs[0, 0].get_legend().remove()

sns.lineplot(x='workload_size', y='instrs', hue='kernel', hue_order=sgemm_hue_order, style='kernel', style_order=sgemm_hue_order, data=sgemm_df, ax=axs[1, 0], linewidth=1.8)
#plot name
axs[1, 0].set_title('sgemm')
axs[1, 0].grid()
#change axis name
axs[1, 0].set_ylabel('Instructions (#)')
axs[1, 0].set_xlabel('Thread Iterations')
#remove legend
axs[1, 0].get_legend().remove()

#plot instr_ratio, y axis is instr_ratio, x axis is workload_size, and we have a vertical plot for each kernel
sns.lineplot(x='workload_size', y='instr_ratio', hue='kernel', hue_order=vecadd_hue_order, style='kernel', style_order=vecadd_hue_order, data=vecadd_df, ax=axs[0, 1], linewidth=1.8)
#plot name
axs[0, 1].set_title('vecadd')
axs[0, 1].grid()
#change axis name
axs[0, 1].set_ylabel('Instructions Reduction')
axs[0, 1].set_xlabel('Thread Iterations')
#remove legend
axs[0, 1].get_legend().remove()

sns.lineplot(x='workload_size', y='instr_ratio', hue='kernel', hue_order=sgemm_hue_order, style='kernel', style_order=sgemm_hue_order, data=sgemm_df, ax=axs[1, 1], linewidth=1.8)
axs[1, 1].grid()
#plot name
axs[1, 1].set_title('sgemm')
#change axis name
axs[1, 1].set_ylabel('Instructions Reduction')
axs[1, 1].set_xlabel('Thread Iterations')
#remove legend
axs[1, 1].get_legend().remove()

#add common legend
handles, labels = axs[0, 1].get_legend_handles_labels()
fig.legend(handles, labels, loc=8, bbox_to_anchor=(0.5, - 0.09), ncol=3)

#change font to calibi and increase size
for ax in axs.flat:
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontname('Calibri')
        size = item.get_fontsize()
        item.set_fontsize(size * 1.3)

plt.tight_layout()

#update spaces between subplots
#plt.subplots_adjust(hspace=0.3, wspace=0.3)

#####################################################################
# Save the plot

output_dir = "./scripts/outputs/00_instr_instratio/"
os.makedirs(output_dir, exist_ok=True)
output_file = output_dir + "05_00_INSTR"

plt.savefig(output_file + ".pdf", format='pdf', bbox_inches='tight',pad_inches=0)
plt.savefig(output_file + ".svg", format='svg', bbox_inches='tight',pad_inches=0)

