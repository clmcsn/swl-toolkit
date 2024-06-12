"""Script to plot comparison plots for different architectures"""

import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
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

# vecadd_df preparation
vecadd_df = pd.DataFrame()
for hw_cfg in hw_cfgs:
    vecadd_df_file = dir_tmlp.format("vecadd", hw_cfg) + "/dataframe.feather"
    vecadd_df = pd.concat([vecadd_df, pd.read_feather(vecadd_df_file)])

vecadd_df_repeat1 = vecadd_df[vecadd_df['repeat'] == 1].reset_index(drop=True)
vecadd_df_repeat2 = vecadd_df[vecadd_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
vecadd_df = pd.merge(vecadd_df_repeat1, vecadd_df_repeat2, on=['workload_size', 'threads', 'warps', 'dcache_ports','clusters', 'cores', 'write_back', 'app'], suffixes=('_r1', '_r2'))
vecadd_df['instrs'] = vecadd_df['instrs_r2'] - vecadd_df['instrs_r1']
vecadd_df['cycles'] = vecadd_df['cycles_r2'] - vecadd_df['cycles_r1']
vecadd_df['dcache_bank_stalls'] = (vecadd_df['dcache_bank_stalls_r2'] - vecadd_df['dcache_bank_stalls_r1'])
vecadd_df['ssr_stalls'] = (vecadd_df['ssr_stalls_r2'] - vecadd_df['ssr_stalls_r1']) / vecadd_df['warps']

#make workload size relative to threads
vecadd_df['workload_size'] = vecadd_df['workload_size'] / vecadd_df['threads']

vecadd_df = vecadd_df.sort_values(by=['threads', 'workload_size'])
# removing outliers
# negative values and zeros get the closes previous values with ffill
vecadd_df['cycles'] = vecadd_df['cycles'].mask(vecadd_df['cycles'] <= 0).ffill()
vecadd_df['dcache_bank_stalls'] = vecadd_df['dcache_bank_stalls'].mask(vecadd_df['dcache_bank_stalls'] < 0).ffill()
vecadd_df['ssr_stalls'] = vecadd_df['ssr_stalls'].mask(vecadd_df['ssr_stalls'] < 0).ffill()

# saxpy_df preparation
saxpy_df = pd.DataFrame()
for hw_cfg in hw_cfgs:
    saxpy_df_file = dir_tmlp.format("saxpy", hw_cfg) + "/dataframe.feather"
    saxpy_df = pd.concat([saxpy_df, pd.read_feather(saxpy_df_file)])

saxpy_df_repeat1 = saxpy_df[saxpy_df['repeat'] == 1].reset_index(drop=True)
saxpy_df_repeat2 = saxpy_df[saxpy_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
saxpy_df = pd.merge(saxpy_df_repeat1, saxpy_df_repeat2, on=['workload_size', 'threads', 'warps', 'dcache_ports','clusters', 'cores', 'write_back', 'app'], suffixes=('_r1', '_r2'))
saxpy_df['instrs'] = saxpy_df['instrs_r2'] - saxpy_df['instrs_r1']
saxpy_df['cycles'] = saxpy_df['cycles_r2'] #- saxpy_df['cycles_r1']
saxpy_df['dcache_bank_stalls'] = saxpy_df['dcache_bank_stalls_r2'] - saxpy_df['dcache_bank_stalls_r1']
saxpy_df['ssr_stalls'] = (saxpy_df['ssr_stalls_r2'] - saxpy_df['ssr_stalls_r1']) / saxpy_df['warps']

#make workload size relative to threads
saxpy_df['workload_size'] = saxpy_df['workload_size'] / saxpy_df['threads']

saxpy_df = saxpy_df.sort_values(by=['threads', 'workload_size'])
# removing outliers
# negative values and zeros get the closes previous values with ffill
saxpy_df['cycles'] = saxpy_df['cycles'].mask(saxpy_df['cycles'] <= 0).ffill()
saxpy_df['dcache_bank_stalls'] = saxpy_df['dcache_bank_stalls'].mask(saxpy_df['dcache_bank_stalls'] < 0).ffill()
saxpy_df['ssr_stalls'] = saxpy_df['ssr_stalls'].mask(saxpy_df['ssr_stalls'] < 0).ffill()

# sgemm_df preparation
sgemm_df = pd.DataFrame()
for hw_cfg in hw_cfgs:
    sgemm_df_file = dir_tmlp.format("sgemm", hw_cfg) + "/dataframe.feather"
    sgemm_df = pd.concat([sgemm_df, pd.read_feather(sgemm_df_file)])

sgemm_df_repeat1 = sgemm_df[sgemm_df['repeat'] == 1].reset_index(drop=True)
sgemm_df_repeat2 = sgemm_df[sgemm_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
sgemm_df = pd.merge(sgemm_df_repeat1, sgemm_df_repeat2, on=['workload_size_x', 'workload_size_y', 'threads', 'warps', 'dcache_ports','clusters', 'cores', 'write_back', 'app'], suffixes=('_r1', '_r2'))
sgemm_df['instrs'] = sgemm_df['instrs_r2'] - sgemm_df['instrs_r1']
sgemm_df['cycles'] = sgemm_df['cycles_r2'] - sgemm_df['cycles_r1']
sgemm_df['dcache_bank_stalls'] = (sgemm_df['dcache_bank_stalls_r2'] - sgemm_df['dcache_bank_stalls_r1'])
sgemm_df['ssr_stalls'] = (sgemm_df['ssr_stalls_r2'] - sgemm_df['ssr_stalls_r1']) / sgemm_df['warps']

#make workload size relative to threads
sgemm_df['workload_size'] = sgemm_df['workload_size_y'] * sgemm_df['workload_size_x'] / sgemm_df['threads']

sgemm_df = sgemm_df.sort_values(by=['threads', 'workload_size'])
# removing outliers
# negative values and zeros get the closes previous values with ffill
sgemm_df['cycles'] = sgemm_df['cycles'].mask(sgemm_df['cycles'] <= 0).ffill()
sgemm_df['dcache_bank_stalls'] = sgemm_df['dcache_bank_stalls'].mask(sgemm_df['dcache_bank_stalls'] < 0).ffill()
sgemm_df['ssr_stalls'] = sgemm_df['ssr_stalls'].mask(sgemm_df['ssr_stalls'] < 0).ffill()

# knn_df preparation
knn_df = pd.DataFrame()
for hw_cfg in hw_cfgs:
    knn_df_file = dir_tmlp.format("knn", hw_cfg) + "/dataframe.feather"
    knn_df = pd.concat([knn_df, pd.read_feather(knn_df_file)])

knn_df_repeat1 = knn_df[knn_df['repeat'] == 1].reset_index(drop=True)
knn_df_repeat2 = knn_df[knn_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
knn_df = pd.merge(knn_df_repeat1, knn_df_repeat2, on=['workload_size', 'threads', 'warps', 'dcache_ports','clusters', 'cores', 'write_back','app'], suffixes=('_r1', '_r2'))
knn_df['instrs'] = knn_df['instrs_r2'] - knn_df['instrs_r1']
knn_df['cycles'] = knn_df['cycles_r2'] - knn_df['cycles_r1']
knn_df['dcache_bank_stalls'] = knn_df['dcache_bank_stalls_r2'] - knn_df['dcache_bank_stalls_r1']
knn_df['ssr_stalls'] = (knn_df['ssr_stalls_r2'] - knn_df['ssr_stalls_r1']) / knn_df['warps']

# removing outliers
# negative values and zeros get the closes previous values with ffill
knn_df['cycles'] = knn_df['cycles'].mask(knn_df['cycles'] <= 0).ffill()
knn_df['dcache_bank_stalls'] = knn_df['dcache_bank_stalls'].mask(knn_df['dcache_bank_stalls'] < 0).ffill()
knn_df['ssr_stalls'] = knn_df['ssr_stalls'].mask(knn_df['ssr_stalls'] < 0).ffill()

#drop all _r2 and _r1 columns also the others
#knn_df = knn_df.drop(columns=[col for col in knn_df.columns if '_r1' in col or '_r2' in col])
#print(knn_df.to_string())
#make workload size relative to threads
#knn_df['workload_size'] = knn_df['workload_size'] / knn_df['threads']

knn_df = knn_df.sort_values(by=['threads', 'workload_size'])

# sfilter_df preparation
sfilter_df = pd.DataFrame()
for hw_cfg in hw_cfgs:
    sfilter_df_file = dir_tmlp.format("sfilter", hw_cfg) + "/dataframe.feather"
    sfilter_df = pd.concat([sfilter_df, pd.read_feather(sfilter_df_file)])

sfilter_df_repeat1 = sfilter_df[sfilter_df['repeat'] == 1].reset_index(drop=True)
sfilter_df_repeat2 = sfilter_df[sfilter_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
sfilter_df = pd.merge(sfilter_df_repeat1, sfilter_df_repeat2, on=['workload_size_x', 'workload_size_y', 'threads', 'warps', 'dcache_ports','clusters', 'cores', 'write_back','app'], suffixes=('_r1', '_r2'))
sfilter_df['instrs'] = sfilter_df['instrs_r2'] - sfilter_df['instrs_r1']
sfilter_df['cycles'] = sfilter_df['cycles_r2'] - sfilter_df['cycles_r1']
sfilter_df['dcache_bank_stalls'] = sfilter_df['dcache_bank_stalls_r2'] - sfilter_df['dcache_bank_stalls_r1']
sfilter_df['ssr_stalls'] = (sfilter_df['ssr_stalls_r2'] - sfilter_df['ssr_stalls_r1']) / sfilter_df['warps']

#make workload size relative to threads
sfilter_df['workload_size'] = sfilter_df['workload_size_x'] * sfilter_df['workload_size_y'] / sfilter_df['threads']

sfilter_df = sfilter_df.sort_values(by=['threads', 'workload_size'])
# removing outliers
# negative values and zeros get the closes previous values with ffill
sfilter_df['cycles'] = sfilter_df['cycles'].mask(sfilter_df['cycles'] <= 0).ffill()
sfilter_df['dcache_bank_stalls'] = sfilter_df['dcache_bank_stalls'].mask(sfilter_df['dcache_bank_stalls'] < 0).ffill()
sfilter_df['ssr_stalls'] = sfilter_df['ssr_stalls'].mask(sfilter_df['ssr_stalls'] < 0).ffill()

# conv2d_df preparation
conv2d_df = pd.DataFrame()
for hw_cfg in hw_cfgs:
    conv2d_df_file = dir_tmlp.format("conv2d", hw_cfg) + "/dataframe.feather"
    conv2d_df = pd.concat([conv2d_df, pd.read_feather(conv2d_df_file)])

conv2d_df_repeat1 = conv2d_df[conv2d_df['repeat'] == 1].reset_index(drop=True)
conv2d_df_repeat2 = conv2d_df[conv2d_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
conv2d_df = pd.merge(conv2d_df_repeat1, conv2d_df_repeat2, on=['workload_size_x', 'workload_size_y', 'out_channels', 'in_channels', 'threads', 'warps', 'dcache_ports','clusters', 'cores', 'write_back', 'app'], suffixes=('_r1', '_r2'))
conv2d_df['instrs'] = conv2d_df['instrs_r2'] - conv2d_df['instrs_r1']
conv2d_df['cycles'] = conv2d_df['cycles_r2'] - conv2d_df['cycles_r1']
conv2d_df['dcache_bank_stalls'] = conv2d_df['dcache_bank_stalls_r2'] - conv2d_df['dcache_bank_stalls_r1']
conv2d_df['ssr_stalls'] = (conv2d_df['ssr_stalls_r2'] - conv2d_df['ssr_stalls_r1']) / conv2d_df['warps']

#make workload size relative to threads
conv2d_df['workload_size'] = conv2d_df['workload_size_x'] * conv2d_df['workload_size_y'] * conv2d_df['out_channels'] * conv2d_df['in_channels'] / conv2d_df['threads']

conv2d_df = conv2d_df.sort_values(by=['threads', 'workload_size'])
# removing outliers
# negative values and zeros get the closes previous values with ffill
conv2d_df['cycles'] = conv2d_df['cycles'].mask(conv2d_df['cycles'] <= 0).ffill()
conv2d_df['dcache_bank_stalls'] = conv2d_df['dcache_bank_stalls'].mask(conv2d_df['dcache_bank_stalls'] < 0).ffill()
conv2d_df['ssr_stalls'] = conv2d_df['ssr_stalls'].mask(conv2d_df['ssr_stalls'] < 0).ffill()

#####################################################################
# making summary dataframes

df = pd.DataFrame()
for kernel_df in [vecadd_df, saxpy_df, sgemm_df, knn_df, sfilter_df, conv2d_df]:
    for wb in  kernel_df['write_back'].unique():
        for t in kernel_df['threads'].unique():
            #print(kernel_df.loc[kernel_df['write_back'] == wb])
            #print(kernel_df.loc[kernel_df['threads'] == t])
            #print(kernel_df.loc[(kernel_df['write_back'] == wb) & (kernel_df['threads'] == t)])
            df = pd.concat([df, pd.DataFrame({  'app'                   : kernel_df['app'].unique(), 
                                                'threads'               : [t],
                                                'write_back'            : [wb],
                                                'cycles'                : [kernel_df.loc[(kernel_df['write_back'] == wb) & (kernel_df['threads'] == t)]['cycles'].mean()],
                                                'dcache_bank_stalls'    : [kernel_df.loc[(kernel_df['write_back'] == wb) & (kernel_df['threads'] == t)]['dcache_bank_stalls'].mean()],
                                                'ssr_stalls'            : [kernel_df.loc[(kernel_df['write_back'] == wb) & (kernel_df['threads'] == t)]['ssr_stalls'].mean()],
                                                'instrs'                : [kernel_df.loc[(kernel_df['write_back'] == wb) & (kernel_df['threads'] == t)]['instrs'].mean()]
            })])
#print(df)
#####################################################################
# plot cycles and dcache_bank_stalls
#plotting

cm = 1/2.54  # centimeters in inches
scale = 5
#subdividing the plot into 4 subplots

fontproperties = {'family': 'Calibri', 'size': 16}
hatches = ['//', '..', 'xx']
aspectR=2.4

#fig, axs = plt.subplots(1,1,figsize=(8.45/3*cm*scale, 8.45/2.5*cm*scale))

y_lim = df['cycles'].max()

g = sns.catplot(data=df.loc[df['write_back']==0], x='app', y='cycles', hue='threads', kind='bar', height=8.45/3*cm*scale, aspect=aspectR, width=0.6, legend=False)

#add legend on the top
#lg = plt.legend(title='Threads', loc='upper center', bbox_to_anchor=(0.5, 1), ncol=3, prop=fontproperties,title_fontproperties=fontproperties)

#add grid
g.ax.grid(axis='x', linestyle='--', linewidth=0.5)
g.ax.grid(axis='y')
#g.ax.grid(axis='y', which='minor', linestyle=':', linewidth=0.5)

#y axis log scale
plt.yscale('log')
plt.ylim(1, y_lim)
plt.ylabel('Cycles')
#remove '-airbender' from app names
plt.xticks(ticks=range(6), labels=[app.replace('-airbender', '') for app in df['app'].unique()])
plt.xlabel('')
#x axis tilt
plt.xticks(rotation=30)

for item in ([g.ax.xaxis.label, g.ax.yaxis.label] +
             g.ax.get_xticklabels() + g.ax.get_yticklabels()):
    item.set_fontname('Calibri')
    size = item.get_fontsize()
    item.set_fontsize(size*1.7)

plt.tight_layout()

output_dir = base_dir + "/plots"
os.makedirs(output_dir, exist_ok=True)

plt.savefig(output_dir + "/cycles_SMEM.pdf", format='pdf')
plt.savefig(output_dir + "/cycles_SMEM.svg", format='svg')

plt.close()
plt.clf()

g =sns.catplot(data=df.loc[df['write_back']==1], x='app', y='cycles', hue='threads', kind='bar', height=8.45/3*cm*scale, aspect=aspectR, width=0.6, legend=False)

#add legend on the top
plt.legend(title='Threads', loc='upper center', bbox_to_anchor=(0.5, 1), ncol=3, prop=fontproperties, title_fontproperties=fontproperties)
#y axis log scale
plt.yscale('log')
plt.ylim(1, y_lim)
plt.ylabel('Cycles')
#remove '-airbender' from app names
plt.xticks(ticks=range(6), labels=[app.replace('-airbender', '') for app in df['app'].unique()])
plt.xlabel('')
#x axis tilt
plt.xticks(rotation=30)

for item in ([g.ax.xaxis.label, g.ax.yaxis.label] +
             g.ax.get_xticklabels() + g.ax.get_yticklabels()):
    item.set_fontname('Calibri')
    size = item.get_fontsize()
    item.set_fontsize(size*1.7)

plt.tight_layout()

output_dir = base_dir + "/plots"
os.makedirs(output_dir, exist_ok=True)

plt.savefig(output_dir + "/cycles_noSMEM.pdf", format='pdf')
plt.savefig(output_dir + "/cycles_noSMEM.svg", format='svg')

plt.close()
plt.clf()

y_lim = df['dcache_bank_stalls'].max()
dcache_bank_stalls = y_lim

df['dcache_bank_stalls_norm'] = df['dcache_bank_stalls'] / df['threads']
g = sns.catplot(data=df.loc[df['write_back']==0], x='app', y='dcache_bank_stalls', hue='threads', kind='bar', height=8.45/3*cm*scale, aspect=aspectR, width=0.6, legend=False)
#add dcache stalls normalized to thread as scatterplot, increase marker size
sns.scatterplot(data=df.loc[df['write_back']==0], x='app', y='dcache_bank_stalls_norm', hue='threads', style='threads', ax=g.ax, s=150, palette='tab10')

#add grid
plt.grid(axis='x', linestyle='--', linewidth=0.5)
plt.grid(axis='y')
#plt.grid(axis='y', which='minor', linestyle=':', linewidth=0.5)


#add legend on the top
plt.legend(title='Threads', loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3, prop=fontproperties,title_fontproperties=fontproperties)
#y axis log scale
plt.yscale('log')
plt.ylim(1, y_lim)
plt.ylabel('DCache Bank Stalls')
#remove '-airbender' from app names
plt.xlabel('')
plt.xticks(ticks=range(6), labels=[app.replace('-airbender', '') for app in df['app'].unique()])
#x axis tilt
plt.xticks(rotation=30)

for item in ([g.ax.xaxis.label, g.ax.yaxis.label] +
             g.ax.get_xticklabels() + g.ax.get_yticklabels()):
    item.set_fontname('Calibri')
    size = item.get_fontsize()
    item.set_fontsize(size*1.7)

plt.tight_layout()

output_dir = base_dir + "/plots"
os.makedirs(output_dir, exist_ok=True)

plt.savefig(output_dir + "/dcache_bank_stalls_SMEM.pdf", format='pdf')
plt.savefig(output_dir + "/dcache_bank_stalls_SMEM.svg", format='svg')

plt.close()
plt.clf()

g = sns.catplot(data=df.loc[df['write_back']==1], x='app', y='dcache_bank_stalls', hue='threads', kind='bar', height=8.45/3*cm*scale, aspect=aspectR, width=0.6, legend_out=True)

#add legend on the top
plt.legend(title='Threads', loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3, prop=fontproperties,title_fontproperties=fontproperties)
#y axis log scale
plt.yscale('log')
plt.ylim(1, y_lim)
plt.ylabel('Dcache Bank Stalls')
#remove '-airbender' from app names
plt.xticks(ticks=range(6), labels=[app.replace('-airbender', '') for app in df['app'].unique()])
plt.xlabel('')
#x axis tilt
plt.xticks(rotation=30)

for item in ([g.ax.xaxis.label, g.ax.yaxis.label] +
             g.ax.get_xticklabels() + g.ax.get_yticklabels()):
    item.set_fontname('Calibri')
    size = item.get_fontsize()
    item.set_fontsize(size*1.7)

plt.tight_layout()

output_dir = base_dir + "/plots"
os.makedirs(output_dir, exist_ok=True)

plt.savefig(output_dir + "/dcache_bank_stalls_noSMEM.pdf", format='pdf')
plt.savefig(output_dir + "/dcache_bank_stalls_noSMEM.svg", format='svg')

plt.close()
plt.clf()

y_lim = dcache_bank_stalls

g = sns.catplot(data=df.loc[df['write_back']==0], x='app', y='ssr_stalls', hue='threads', kind='bar', height=8.45/3*cm*scale, aspect=aspectR, width=0.6, legend=False)

#add grid
plt.grid(axis='x', linestyle='--', linewidth=0.5)
plt.grid(axis='y')
#plt.grid(axis='y', which='minor', linestyle=':', linewidth=0.5)

#add legend on the top
#plt.legend(title='Threads', loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3, prop=fontproperties,title_fontproperties=fontproperties)

#y axis log scale
plt.yscale('log')
plt.ylim(1, y_lim)
plt.ylabel('SSR Stalls')
#remove '-airbender' from app names
plt.xlabel('')
plt.xticks(ticks=range(6), labels=[app.replace('-airbender', '') for app in df['app'].unique()])
#x axis tilt
plt.xticks(rotation=30)

for item in ([g.ax.xaxis.label, g.ax.yaxis.label] +
                g.ax.get_xticklabels() + g.ax.get_yticklabels()):
        item.set_fontname('Calibri')
        size = item.get_fontsize()
        item.set_fontsize(size*1.7)

plt.tight_layout()

output_dir = base_dir + "/plots"
os.makedirs(output_dir, exist_ok=True)

plt.savefig(output_dir + "/ssr_stalls_SMEM.pdf", format='pdf')
plt.savefig(output_dir + "/ssr_stalls_SMEM.svg", format='svg')

plt.close()
plt.clf()
