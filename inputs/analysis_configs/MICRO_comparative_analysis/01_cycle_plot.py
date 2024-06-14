"""Script to plot instruction ratio for different kernels"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from math import ceil, floor

#####################################################################
# Adding the freaking calibri font
import matplotlib.font_manager as font_manager

font_path = '../../calibri-font-family/calibri-regular.ttf'

font_manager.fontManager.addfont(font_path)

#####################################################################
# dirs

dir_tmpl = "./scripts/outputs/ASPLOS-COMP-{}-im-{}/"
hw_cfgs = ["1C2c4w8t", "1C4c8w16t", "4C4c8w32t"]
hw_cfgs_str = ["1C-2c-4w-8t", "1C-4c-8w-16t", "4C-4c-8w-32t"]
vecadd_dirs = [dir_tmpl.format("vecadd", hw_cfg) for hw_cfg in hw_cfgs]
sgemm_dirs = [dir_tmpl.format("sgemm", hw_cfg) for hw_cfg in hw_cfgs]
conv2d_dirs = [dir_tmpl.format("conv2d", hw_cfg) for hw_cfg in hw_cfgs]
knn_dirs = [dir_tmpl.format("knn", hw_cfg) for hw_cfg in hw_cfgs]
saxpy_dirs = [dir_tmpl.format("saxpy", hw_cfg) for hw_cfg in hw_cfgs]
sfilter_dirs = [dir_tmpl.format("sfilter", hw_cfg) for hw_cfg in hw_cfgs]

#####################################################################
# vars
kernel_names = ['loops', '+1xSSL', '+2xSSL', '+3xSSL']
hatches = ['//', 'o', 'x', '-']
xtick_tilt = 29

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

###################################################################
# vecadd df preparation

vecadd_avg_df = pd.DataFrame()
vecadd_max_instrs_ratio = pd.DataFrame()
for d in vecadd_dirs:
    d_hw_cfg = d.split('-')[-1][:-1]
    vecadd_df_file = d + "dataframe.feather"
    vecadd_baseline = 'vecadd-base'

    vecadd_df = pd.read_feather(vecadd_df_file)
    vecadd_df_repeat1 = vecadd_df[vecadd_df['repeat'] == 1].reset_index(drop=True)
    vecadd_df_repeat2 = vecadd_df[vecadd_df['repeat'] == 2].reset_index(drop=True)

    # merge the two dataframes makeing the subtract of instructions
    vecadd_df = pd.merge(vecadd_df_repeat1, vecadd_df_repeat2, on=['workload_size', 'kernel'], suffixes=('_r1', '_r2'))
    vecadd_df['cycles'] = vecadd_df['cycles_r2'] - vecadd_df['cycles_r1']
    vecadd_df['instrs'] = vecadd_df['instrs_r2'] - vecadd_df['instrs_r1']

    #sort by kernel name then workload size
    vecadd_df = vecadd_df.sort_values(by=['kernel', 'workload_size'])

    # removing outliers
    # negative values and zeros get the closes previous values with ffill
    vecadd_df['cycles'] = vecadd_df['cycles'].mask(vecadd_df['cycles'] <= 0).ffill()

    vecadd_df['cycles_ratio'] = 1
    for ws in vecadd_df['workload_size'].unique():
        vacadd_base_cycles = vecadd_df[(vecadd_df['workload_size'] == ws) & (vecadd_df['kernel'] == vecadd_baseline)]['cycles'].values[0]
        vecadd_df.loc[(vecadd_df['workload_size'] == ws) & (vecadd_df['kernel'] != vecadd_baseline), 'cycles_ratio'] = vacadd_base_cycles / vecadd_df['cycles']
        vecadd_base_instrs = vecadd_df[(vecadd_df['workload_size'] == ws) & (vecadd_df['kernel'] == vecadd_baseline)]['instrs'].values[0]
        vecadd_df.loc[(vecadd_df['workload_size'] == ws) & (vecadd_df['kernel'] != vecadd_baseline), 'instrs_ratio'] = vecadd_base_instrs / vecadd_df['instrs']

    #change kernel names
    vecadd_df['kernel'] = vecadd_df['kernel'].replace({'vecadd-ssr': '+1xSSL', 'vecadd-ssr2': '+2xSSL', 'vecadd-ssr3': '+3xSSL', 'vecadd-loop': 'loops'})

    #getting avg cycles ratio
    for k in vecadd_df['kernel'].unique():
        if k == vecadd_baseline:
            continue
        avg = vecadd_df[vecadd_df['kernel'] == k]['cycles_ratio'].mean()
        vecadd_avg_df = pd.concat([vecadd_avg_df, pd.DataFrame({'kernel': [k], 'avg_cycles_ratio': [avg], 'hw_cfg': [d_hw_cfg]})], ignore_index=True)
        instrs_max = vecadd_df[vecadd_df['kernel'] == k]['instrs_ratio'].mean()#max()
        vecadd_max_instrs_ratio = pd.concat([vecadd_max_instrs_ratio, pd.DataFrame({'kernel': [k], 'max_instrs_ratio': [instrs_max], 'hw_cfg': [d_hw_cfg]})], ignore_index=True)

#print(vecadd_avg_df)

###################################################################
# sgemm df preparation

sgemm_avg_df = pd.DataFrame()
sgemm_max_instrs_ratio = pd.DataFrame()
for d in sgemm_dirs:
    d_hw_cfg = d.split('-')[-1][:-1]
    sgemm_df_file = d + "dataframe.feather"
    sgemm_baseline = 'sgemm'

    sgemm_df = pd.read_feather(sgemm_df_file)
    sgemm_df_repeat1 = sgemm_df[sgemm_df['repeat'] == 1].reset_index(drop=True)
    sgemm_df_repeat2 = sgemm_df[sgemm_df['repeat'] == 2].reset_index(drop=True)

    # merge the two dataframes makeing the subtract of instructions
    sgemm_df = pd.merge(sgemm_df_repeat1, sgemm_df_repeat2, on=['workload_size_x', 'workload_size_y', 'kernel'], suffixes=('_r1', '_r2'))
    sgemm_df['cycles'] = sgemm_df['cycles_r2'] - sgemm_df['cycles_r1']
    sgemm_df['instrs'] = sgemm_df['instrs_r2'] - sgemm_df['instrs_r1']

    sgemm_df['workload_size'] = sgemm_df['workload_size_x'] * sgemm_df['workload_size_y'] 

    #sort by kernel name then workload size
    sgemm_df = sgemm_df.sort_values(by=['kernel', 'workload_size'])

    # removing outliers
    # negative values and zeros get the closes previous values with ffill
    sgemm_df['cycles'] = sgemm_df['cycles'].mask(sgemm_df['cycles'] <= 0).ffill()

    sgemm_df['cycles_ratio'] = 1
    for ws in sgemm_df['workload_size'].unique():
        sgemm_base_cycles = sgemm_df[(sgemm_df['workload_size'] == ws) & (sgemm_df['kernel'] == sgemm_baseline)]['cycles'].values[0]
        sgemm_df.loc[(sgemm_df['workload_size'] == ws) & (sgemm_df['kernel'] != sgemm_baseline), 'cycles_ratio'] = sgemm_base_cycles / sgemm_df['cycles']
        sgemm_base_instrs = sgemm_df[(sgemm_df['workload_size'] == ws) & (sgemm_df['kernel'] == sgemm_baseline)]['instrs'].values[0]
        sgemm_df.loc[(sgemm_df['workload_size'] == ws) & (sgemm_df['kernel'] != sgemm_baseline), 'instrs_ratio'] = sgemm_base_instrs / sgemm_df['instrs']

    #change kernel names
    sgemm_df['kernel'] = sgemm_df['kernel'].replace({'sgemm-loop': 'loops', 'sgemm-ssr': '+1xSSL', 'sgemm-ssr2': '+2xSSL', 'sgemm-ssr3': '+3xSSL'})

    #getting avg cycles ratio
    for k in sgemm_df['kernel'].unique():
        if k == sgemm_baseline:
            continue
        avg = sgemm_df[sgemm_df['kernel'] == k]['cycles_ratio'].mean()
        sgemm_avg_df = pd.concat([sgemm_avg_df, pd.DataFrame({'kernel': [k], 'avg_cycles_ratio': [avg], 'hw_cfg': [d_hw_cfg]})], ignore_index=True)
        instrs_max = sgemm_df[sgemm_df['kernel'] == k]['instrs_ratio'].mean()#max()
        sgemm_max_instrs_ratio = pd.concat([sgemm_max_instrs_ratio, pd.DataFrame({'kernel': [k], 'max_instrs_ratio': [instrs_max], 'hw_cfg': [d_hw_cfg]})], ignore_index=True)
    
#print(sgemm_avg_df)

###################################################################
# saxpy df preparation

saxpy_avg_df = pd.DataFrame()
saxpy_max_instrs_ratio = pd.DataFrame()
for d in saxpy_dirs:
    d_hw_cfg = d.split('-')[-1][:-1]
    saxpy_df_file = d + "dataframe.feather"
    saxpy_baseline = 'saxpy'

    saxpy_df = pd.read_feather(saxpy_df_file)
    saxpy_df_repeat1 = saxpy_df[saxpy_df['repeat'] == 1].reset_index(drop=True)
    saxpy_df_repeat2 = saxpy_df[saxpy_df['repeat'] == 2].reset_index(drop=True)

    # merge the two dataframes makeing the subtract of instructions
    saxpy_df = pd.merge(saxpy_df_repeat1, saxpy_df_repeat2, on=['workload_size', 'kernel'], suffixes=('_r1', '_r2'))
    saxpy_df['cycles'] = saxpy_df['cycles_r2'] - saxpy_df['cycles_r1']
    saxpy_df['instrs'] = saxpy_df['instrs_r2'] - saxpy_df['instrs_r1']

    #sort by kernel name then workload size
    saxpy_df = saxpy_df.sort_values(by=['kernel', 'workload_size'])

    # removing outliers
    # negative values and zeros get the closes previous values with ffill
    saxpy_df['cycles'] = saxpy_df['cycles'].mask(saxpy_df['cycles'] <= 0).ffill()

    saxpy_df['cycles_ratio'] = 1
    for ws in saxpy_df['workload_size'].unique():
        saxpy_base_cycles = saxpy_df[(saxpy_df['workload_size'] == ws) & (saxpy_df['kernel'] == saxpy_baseline)]['cycles'].values[0]
        saxpy_df.loc[(saxpy_df['workload_size'] == ws) & (saxpy_df['kernel'] != saxpy_baseline), 'cycles_ratio'] = saxpy_base_cycles / saxpy_df['cycles']
        saxpy_base_instrs = saxpy_df[(saxpy_df['workload_size'] == ws) & (saxpy_df['kernel'] == saxpy_baseline)]['instrs'].values[0]
        saxpy_df.loc[(saxpy_df['workload_size'] == ws) & (saxpy_df['kernel'] != saxpy_baseline), 'instrs_ratio'] = saxpy_base_instrs / saxpy_df['instrs']

    #change kernel names
    saxpy_df['kernel'] = saxpy_df['kernel'].replace({'saxpy-ssr': '+1xSSL', 'saxpy-ssr2': '+2xSSL', 'saxpy-ssr3': '+3xSSL', 'saxpy-loop': 'loops'})

    #getting avg cycles ratio
    for k in saxpy_df['kernel'].unique():
        if k == saxpy_baseline:
            continue
        avg = saxpy_df[saxpy_df['kernel'] == k]['cycles_ratio'].mean()
        saxpy_avg_df = pd.concat([saxpy_avg_df, pd.DataFrame({'kernel': [k], 'avg_cycles_ratio': [avg], 'hw_cfg': [d_hw_cfg]})], ignore_index=True)
        instrs_max = saxpy_df[saxpy_df['kernel'] == k]['instrs_ratio'].mean()#max()
        saxpy_max_instrs_ratio = pd.concat([saxpy_max_instrs_ratio, pd.DataFrame({'kernel': [k], 'max_instrs_ratio': [instrs_max], 'hw_cfg': [d_hw_cfg]})], ignore_index=True)

#print(saxpy_avg_df)

###################################################################
# knn df preparation

knn_avg_df = pd.DataFrame()
knn_max_instrs_ratio = pd.DataFrame()
for d in knn_dirs:
    d_hw_cfg = d.split('-')[-1][:-1]
    knn_df_file = d + "dataframe.feather"
    knn_baseline = 'knn-asm'

    knn_df = pd.read_feather(knn_df_file)
    knn_df_repeat1 = knn_df[knn_df['repeat'] == 1].reset_index(drop=True)
    knn_df_repeat2 = knn_df[knn_df['repeat'] == 2].reset_index(drop=True)

    # merge the two dataframes makeing the subtract of instructions
    knn_df = pd.merge(knn_df_repeat1, knn_df_repeat2, on=['workload_size', 'kernel'], suffixes=('_r1', '_r2'))
    knn_df['cycles'] = knn_df['cycles_r2'] - knn_df['cycles_r1']
    knn_df['instrs'] = knn_df['instrs_r2'] - knn_df['instrs_r1']

    #sort by kernel name then workload size
    knn_df = knn_df.sort_values(by=['kernel', 'workload_size'])

    # removing outliers
    # negative values and zeros get the closes previous values with ffill
    knn_df['cycles'] = knn_df['cycles'].mask(knn_df['cycles'] <= 0).ffill()

    knn_df['cycles_ratio'] = 1
    for ws in knn_df['workload_size'].unique():
        knn_base_cycles = knn_df[(knn_df['workload_size'] == ws) & (knn_df['kernel'] == knn_baseline)]['cycles'].values[0]
        knn_df.loc[(knn_df['workload_size'] == ws) & (knn_df['kernel'] != knn_baseline), 'cycles_ratio'] = knn_base_cycles / knn_df['cycles']
        knn_base_instrs = knn_df[(knn_df['workload_size'] == ws) & (knn_df['kernel'] == knn_baseline)]['instrs'].values[0]
        knn_df.loc[(knn_df['workload_size'] == ws) & (knn_df['kernel'] != knn_baseline), 'instrs_ratio'] = knn_base_instrs / knn_df['instrs']

    #change kernel names
    knn_df['kernel'] = knn_df['kernel'].replace({'knn-ssr': '+1xSSL', 'knn-ssr2': '+2xSSL', 'knn-ssr3': '+3xSSL', 'knn-loop': 'loops'})

    #getting avg cycles ratio
    for k in knn_df['kernel'].unique():
        if k == knn_baseline:
            continue
        avg = knn_df[knn_df['kernel'] == k]['cycles_ratio'].mean()
        knn_avg_df = pd.concat([knn_avg_df, pd.DataFrame({'kernel': [k], 'avg_cycles_ratio': [avg], 'hw_cfg': [d_hw_cfg]})], ignore_index=True)
        instrs_max = knn_df[knn_df['kernel'] == k]['instrs_ratio'].mean()#max()
        knn_max_instrs_ratio = pd.concat([knn_max_instrs_ratio, pd.DataFrame({'kernel': [k], 'max_instrs_ratio': [instrs_max], 'hw_cfg': [d_hw_cfg]})], ignore_index=True)

#print(knn_avg_df)

###################################################################
# sfilter df preparation

sfilter_avg_df = pd.DataFrame()
sfilter_max_instrs_ratio = pd.DataFrame()
for d in sfilter_dirs:
    d_hw_cfg = d.split('-')[-1][:-1]
    sfilter_df_file = d + "dataframe.feather"
    sfilter_baseline = 'sfilter'

    sfilter_df = pd.read_feather(sfilter_df_file)
    sfilter_df_repeat1 = sfilter_df[sfilter_df['repeat'] == 1].reset_index(drop=True)
    sfilter_df_repeat2 = sfilter_df[sfilter_df['repeat'] == 2].reset_index(drop=True)

    # merge the two dataframes makeing the subtract of instructions
    sfilter_df = pd.merge(sfilter_df_repeat1, sfilter_df_repeat2, on=['workload_size_y', 'kernel'], suffixes=('_r1', '_r2'))
    sfilter_df['cycles'] = sfilter_df['cycles_r2'] - sfilter_df['cycles_r1']
    sfilter_df['instrs'] = sfilter_df['instrs_r2'] - sfilter_df['instrs_r1']

    sfilter_df['workload_size'] = sfilter_df['workload_size_y'] 

    #sort by kernel name then workload size
    sfilter_df = sfilter_df.sort_values(by=['kernel', 'workload_size'])

    # removing outliers
    # negative values and zeros get the closes previous values with ffill
    sfilter_df['cycles'] = sfilter_df['cycles'].mask(sfilter_df['cycles'] <= 0).ffill()

    sfilter_df['cycles_ratio'] = 1
    for ws in sfilter_df['workload_size'].unique():
        sfilter_base_cycles = sfilter_df[(sfilter_df['workload_size'] == ws) & (sfilter_df['kernel'] == sfilter_baseline)]['cycles'].values[0]
        sfilter_df.loc[(sfilter_df['workload_size'] == ws) & (sfilter_df['kernel'] != sfilter_baseline), 'cycles_ratio'] = sfilter_base_cycles / sfilter_df['cycles']
        sfilter_base_instrs = sfilter_df[(sfilter_df['workload_size'] == ws) & (sfilter_df['kernel'] == sfilter_baseline)]['instrs'].values[0]
        sfilter_df.loc[(sfilter_df['workload_size'] == ws) & (sfilter_df['kernel'] != sfilter_baseline), 'instrs_ratio'] = sfilter_base_instrs / sfilter_df['instrs']

    #change kernel names
    sfilter_df['kernel'] = sfilter_df['kernel'].replace({'sfilter-ssr': '+1xSSL', 'sfilter-ssr2': '+2xSSL', 'sfilter-ssr3': '+3xSSL', 'sfilter-loop': 'loops'})

    #getting avg cycles ratio
    for k in sfilter_df['kernel'].unique():
        if k == sfilter_baseline:
            continue
        avg = sfilter_df[sfilter_df['kernel'] == k]['cycles_ratio'].mean()
        sfilter_avg_df = pd.concat([sfilter_avg_df, pd.DataFrame({'kernel': [k], 'avg_cycles_ratio': [avg], 'hw_cfg': [d_hw_cfg]})], ignore_index=True)
        instrs_max = sfilter_df[sfilter_df['kernel'] == k]['instrs_ratio'].mean()#max()
        sfilter_max_instrs_ratio = pd.concat([sfilter_max_instrs_ratio, pd.DataFrame({'kernel': [k], 'max_instrs_ratio': [instrs_max], 'hw_cfg': [d_hw_cfg]})], ignore_index=True)

#print(sfilter_avg_df)

###################################################################
# conv2d df preparation

conv2d_avg_df = pd.DataFrame()
conv2d_max_instrs_ratio = pd.DataFrame()
for d in conv2d_dirs:
    d_hw_cfg = d.split('-')[-1][:-1]
    conv2d_df_file = d + "dataframe.feather"
    conv2d_baseline = 'conv2d-asm'

    conv2d_df = pd.read_feather(conv2d_df_file)
    conv2d_df_repeat1 = conv2d_df[conv2d_df['repeat'] == 1].reset_index(drop=True)
    conv2d_df_repeat2 = conv2d_df[conv2d_df['repeat'] == 2].reset_index(drop=True)

    # merge the two dataframes makeing the subtract of instructions
    conv2d_df = pd.merge(conv2d_df_repeat1, conv2d_df_repeat2, on=['workload_size_x', 'workload_size_y', 'kernel'], suffixes=('_r1', '_r2'))
    conv2d_df['cycles'] = conv2d_df['cycles_r2'] - conv2d_df['cycles_r1']
    conv2d_df['instrs'] = conv2d_df['instrs_r2'] - conv2d_df['instrs_r1']

    conv2d_df['workload_size'] = conv2d_df['workload_size_x'] * conv2d_df['workload_size_y'] 

    #sort by kernel name then workload size
    conv2d_df = conv2d_df.sort_values(by=['kernel', 'workload_size'])

    # removing outliers
    # negative values and zeros get the closes previous values with ffill
    conv2d_df['cycles'] = conv2d_df['cycles'].mask(conv2d_df['cycles'] <= 0).ffill()

    conv2d_df['cycles_ratio'] = 1
    for ws in conv2d_df['workload_size'].unique():
        conv2d_base_cycles = conv2d_df[(conv2d_df['workload_size'] == ws) & (conv2d_df['kernel'] == conv2d_baseline)]['cycles'].values[0]
        conv2d_df.loc[(conv2d_df['workload_size'] == ws) & (conv2d_df['kernel'] != conv2d_baseline), 'cycles_ratio'] = conv2d_base_cycles / conv2d_df['cycles']
        conv2d_base_instrs = conv2d_df[(conv2d_df['workload_size'] == ws) & (conv2d_df['kernel'] == conv2d_baseline)]['instrs'].values[0]
        conv2d_df.loc[(conv2d_df['workload_size'] == ws) & (conv2d_df['kernel'] != conv2d_baseline), 'instrs_ratio'] = conv2d_base_instrs / conv2d_df['instrs']

    #change kernel names
    conv2d_df['kernel'] = conv2d_df['kernel'].replace({'conv2d-loop': 'loops', 'conv2d-ssr': '+1xSSL', 'conv2d-ssr2': '+2xSSL', 'conv2d-ssr3': '+3xSSL'})

    #getting avg cycles ratio
    for k in conv2d_df['kernel'].unique():
        if k == conv2d_baseline:
            continue
        avg = conv2d_df[conv2d_df['kernel'] == k]['cycles_ratio'].mean()
        conv2d_avg_df = pd.concat([conv2d_avg_df, pd.DataFrame({'kernel': [k], 'avg_cycles_ratio': [avg], 'hw_cfg': [d_hw_cfg]})], ignore_index=True)
        instrs_max = conv2d_df[conv2d_df['kernel'] == k]['instrs_ratio'].mean()
        conv2d_max_instrs_ratio = pd.concat([conv2d_max_instrs_ratio, pd.DataFrame({'kernel': [k], 'max_instrs_ratio': [instrs_max], 'hw_cfg': [d_hw_cfg]})], ignore_index=True)

###################################################################

#plotting
cm = 1/2.54  # centimeters in inches
plot_size_x = (2*8.45 +0.83)*cm
plot_size_y = plot_size_x*(11/22)
scale = 5/3
#subdividing the plot into 4 subplots

fig, axs = plt.subplots(3, 6, figsize=(plot_size_x*scale, plot_size_y*scale))

#vecadd
max_cycles_ratio = vecadd_avg_df['avg_cycles_ratio'].max()
max_instrs_ratio = vecadd_max_instrs_ratio['max_instrs_ratio'].max()
ymax = max_cycles_ratio if max_cycles_ratio > max_instrs_ratio else max_instrs_ratio
y_axis_lim = ymax + 0.05*ymax
axs[0, 0].set_title('vecadd\nvlen→[4:160:1.5]')
for i, hw_cfg in enumerate(hw_cfgs):
    vecadd_avg_df_hw = vecadd_avg_df[vecadd_avg_df['hw_cfg'] == hw_cfg]
    ax = sns.barplot(data=vecadd_avg_df_hw, x='kernel', y='avg_cycles_ratio', ax=axs[i, 0])
    #adding max instrs ratio
    max_instrs_ratio = vecadd_max_instrs_ratio[vecadd_max_instrs_ratio['hw_cfg'] == hw_cfg]
    sns.scatterplot(data=max_instrs_ratio, x='kernel', y='max_instrs_ratio', hue='kernel', ax=ax, marker='D',legend=False, edgecolor='black')

    #changing hatches
    #for j, bar in enumerate(ax.patches):
    #    bar.set_hatch(hatches[j])
    axs[i, 0].set_ylim(0, y_axis_lim)
    axs[i, 0].set_ylabel('HW: {}\nAvg Speedup'.format(hw_cfgs_str[i]))
    #tilt x axis labels
    for tick in axs[i, 0].get_xticklabels():
        tick.set_rotation(xtick_tilt)
    axs[i, 0].set_xlabel('')
    add_grid(ax, y_axis_lim)

#sapxy
max_cycles_ratio = saxpy_avg_df['avg_cycles_ratio'].max()
max_instrs_ratio = saxpy_max_instrs_ratio['max_instrs_ratio'].max()
ymax = max_cycles_ratio if max_cycles_ratio > max_instrs_ratio else max_instrs_ratio
y_axis_lim = ymax + 0.05*ymax
axs[0, 1].set_title('saxpy\nvlen→[4:160:1.5]')
for i, hw_cfg in enumerate(hw_cfgs):
    saxpy_avg_df_hw = saxpy_avg_df[saxpy_avg_df['hw_cfg'] == hw_cfg]
    ax = sns.barplot(data=saxpy_avg_df_hw, x='kernel', y='avg_cycles_ratio', ax=axs[i, 1])
    max_instrs_ratio = saxpy_max_instrs_ratio[saxpy_max_instrs_ratio['hw_cfg'] == hw_cfg]
    sns.scatterplot(data=max_instrs_ratio, x='kernel', y='max_instrs_ratio', hue='kernel', ax=ax, marker='D',legend=False, edgecolor='black')
    #changing hatches
    #for j, bar in enumerate(ax.patches):
    #    bar.set_hatch(hatches[j])
    axs[i, 1].set_ylim(0, y_axis_lim)
    axs[i, 1].set_ylabel('')
    #tilt x axis labels
    for tick in axs[i, 1].get_xticklabels():
        tick.set_rotation(xtick_tilt)
    axs[i, 1].set_xlabel('')
    add_grid(ax, y_axis_lim)

#sgemm
max_cycles_ratio = sgemm_avg_df['avg_cycles_ratio'].max()
max_instrs_ratio = sgemm_max_instrs_ratio['max_instrs_ratio'].max()
ymax = max_cycles_ratio if max_cycles_ratio > max_instrs_ratio else max_instrs_ratio
y_axis_lim = ymax + 0.05*ymax
axs[0, 2].set_title('sgemm\nZ=16\nX*Y→[4:50:0.25]')
for i, hw_cfg in enumerate(hw_cfgs):
    sgemm_avg_df_hw = sgemm_avg_df[sgemm_avg_df['hw_cfg'] == hw_cfg]
    ax = sns.barplot(data=sgemm_avg_df_hw, x='kernel', y='avg_cycles_ratio', ax=axs[i, 2])
    max_instrs_ratio = sgemm_max_instrs_ratio[sgemm_max_instrs_ratio['hw_cfg'] == hw_cfg]
    sns.scatterplot(data=max_instrs_ratio, x='kernel', y='max_instrs_ratio', hue='kernel', ax=ax, marker='D',legend=False, edgecolor='black')
    #changing hatches
    #for j, bar in enumerate(ax.patches):
    #    bar.set_hatch(hatches[j])
    axs[i, 2].set_ylim(0, y_axis_lim)
    axs[i, 2].set_ylabel('')
    #tilt x axis labels
    for tick in axs[i, 2].get_xticklabels():
        tick.set_rotation(xtick_tilt)
    axs[i, 2].set_xlabel('')
    add_grid(ax, y_axis_lim)

#knn
max_cycles_ratio = knn_avg_df['avg_cycles_ratio'].max()
max_instrs_ratio = knn_max_instrs_ratio['max_instrs_ratio'].max()
ymax = max_cycles_ratio if max_cycles_ratio > max_instrs_ratio else max_instrs_ratio
y_axis_lim = ymax + 0.05*ymax
axs[0, 3].set_title('knn\nvlen→[4:100:1.5]')
for i, hw_cfg in enumerate(hw_cfgs):
    knn_avg_df_hw = knn_avg_df[knn_avg_df['hw_cfg'] == hw_cfg]
    ax = sns.barplot(data=knn_avg_df_hw, x='kernel', y='avg_cycles_ratio', ax=axs[i, 3])
    max_instrs_ratio = knn_max_instrs_ratio[knn_max_instrs_ratio['hw_cfg'] == hw_cfg]
    sns.scatterplot(data=max_instrs_ratio, x='kernel', y='max_instrs_ratio', hue='kernel', ax=ax, marker='D',legend=False, edgecolor='black')
    #changing hatches
    #for j, bar in enumerate(ax.patches):
    #    bar.set_hatch(hatches[j])
    axs[i, 3].set_ylim(0, y_axis_lim)
    axs[i, 3].set_ylabel('')
    #tilt x axis labels
    for tick in axs[i, 3].get_xticklabels():
        tick.set_rotation(xtick_tilt)
    axs[i, 3].set_xlabel('')
    add_grid(ax, y_axis_lim)

#sfilter
max_cycles_ratio = sfilter_avg_df['avg_cycles_ratio'].max()
max_instrs_ratio = sfilter_max_instrs_ratio['max_instrs_ratio'].max()
ymax = max_cycles_ratio if max_cycles_ratio > max_instrs_ratio else max_instrs_ratio
y_axis_lim = ymax + 0.05*ymax
axs[0, 4].set_title('sfilter\nX*Y→[4:50:0.25]')
for i, hw_cfg in enumerate(hw_cfgs):
    sfilter_avg_df_hw = sfilter_avg_df[sfilter_avg_df['hw_cfg'] == hw_cfg]
    ax = sns.barplot(data=sfilter_avg_df_hw, x='kernel', y='avg_cycles_ratio', ax=axs[i, 4])
    max_instrs_ratio = sfilter_max_instrs_ratio[sfilter_max_instrs_ratio['hw_cfg'] == hw_cfg]
    sns.scatterplot(data=max_instrs_ratio, x='kernel', y='max_instrs_ratio', hue='kernel', ax=ax, marker='D',legend=False, edgecolor='black')
    #changing hatches
    #for j, bar in enumerate(ax.patches):
    #    bar.set_hatch(hatches[j])
    axs[i, 4].set_ylim(0, y_axis_lim)
    axs[i, 4].set_ylabel('')
    #tilt x axis labels
    for tick in axs[i, 4].get_xticklabels():
        tick.set_rotation(xtick_tilt)
    axs[i, 4].set_xlabel('')
    add_grid(ax, y_axis_lim)

#conv2d
max_cycles_ratio = conv2d_avg_df['avg_cycles_ratio'].max()
max_instrs_ratio = conv2d_max_instrs_ratio['max_instrs_ratio'].max()
ymax = max_cycles_ratio if max_cycles_ratio > max_instrs_ratio else max_instrs_ratio
y_axis_lim = ymax + 0.05*ymax
axs[0, 5].set_title('conv2d\nC=8 K=1\nX*Y→[4:50:0.25]')
for i, hw_cfg in enumerate(hw_cfgs):
    conv2d_avg_df_hw = conv2d_avg_df[conv2d_avg_df['hw_cfg'] == hw_cfg]
    ax = sns.barplot(data=conv2d_avg_df_hw, x='kernel', y='avg_cycles_ratio', ax=axs[i, 5])
    max_instrs_ratio = conv2d_max_instrs_ratio[conv2d_max_instrs_ratio['hw_cfg'] == hw_cfg]
    sns.scatterplot(data=max_instrs_ratio, x='kernel', y='max_instrs_ratio', hue='kernel', ax=ax, marker='D',legend=False, edgecolor='black')
    #changing hatches
    #for j, bar in enumerate(ax.patches):
    #    bar.set_hatch(hatches[j])
    axs[i, 5].set_ylim(0, y_axis_lim)
    axs[i, 5].set_ylabel('')
    #tilt x axis labels
    for tick in axs[i, 5].get_xticklabels():
        tick.set_rotation(xtick_tilt)
    axs[i, 5].set_xlabel('')
    add_grid(ax, y_axis_lim)

#add custom legend for max instrs ratio
legend_elements = [Line2D([0], [0], marker='D', color='w', label='Avg Instructions Reduciton', markerfacecolor='black', markersize=8)]
fig.legend(handles=legend_elements, loc=8, bbox_to_anchor=(0.5, - 0.06), ncol=1)


#change font to calibi and increase size
for ax in axs.flat:
    for item in ([ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontname('Calibri')
        size = item.get_fontsize()
        item.set_fontsize(size * 1.2)
        #item.set_fontsize(8*scale)

plt.tight_layout()

###################################################################
# Save the plot
output_dir = "./scripts/outputs/ASPLOS-COMP-01-cycle_plot/"
os.makedirs(output_dir, exist_ok=True)
output_file = output_dir + "05_01_CYCLE"

plt.savefig(output_file + ".pdf", format='pdf', bbox_inches='tight',pad_inches=0)