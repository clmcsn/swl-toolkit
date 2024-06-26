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
base_dir = "/users/micas/gsarda/vortex/vortex-KUL-fork/scripts/outputs/ASPLOS-SWIFT-vs-VORTEX"
swift_dir = "/users/micas/gsarda/vortex/vortex-KUL-fork/scripts/outputs/ASPLOS-SWIFT-ARC-COMP"
dir_tmlp = base_dir+"/{}-rm-{}"
swift_tmlp = swift_dir+"/{}-rm-1C4c8w8t"
hw_cfgs = ["2C4c8w8t", "4C4c8w8t", "8C4c8w8t"]
kernels = ["conv2d", "knn", "saxpy", "vecadd", "sfilter", "sgemm"]

areas = pd.DataFrame({
    "clusters" : [1, 2, 4, 8],
    "area" :     [ 2276699.76/1e6,  1424971.71*2/1e6,  1424971.71*4/1e6,  1424971.71*8/1e6]
})

#####################################################################
# vecadd

vecadd_df = pd.DataFrame()
for hw_cfg in hw_cfgs:
    vecadd_df_file = dir_tmlp.format("vecadd", hw_cfg) + "/dataframe.feather"
    vecadd_df = pd.concat([vecadd_df, pd.read_feather(vecadd_df_file)], ignore_index=True)

# read swift df
swift_vecadd_df = pd.read_feather(swift_tmlp.format("vecadd") + "/dataframe.feather")

# remove from swift workload size not in vecadd_df
swift_vecadd_df = swift_vecadd_df[swift_vecadd_df['workload_size'].isin(vecadd_df['workload_size'])]

#remove write_back=1 from swift_vecadd_df
swift_vecadd_df = swift_vecadd_df[swift_vecadd_df['write_back'] == 0]

# check that all workload size in vecadd_df are in swift_vecadd_df
assert len(vecadd_df[~vecadd_df['workload_size'].isin(swift_vecadd_df['workload_size'])]) == 0

# merge swift_vecadd_df with vecadd_df
vecadd_df = pd.concat([vecadd_df, swift_vecadd_df], ignore_index=True)

vecadd_df_repeat1 = vecadd_df[vecadd_df['repeat'] == 1].reset_index(drop=True)
vecadd_df_repeat2 = vecadd_df[vecadd_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
vecadd_df = pd.merge(vecadd_df_repeat1, vecadd_df_repeat2, on=['workload_size', 'threads', 'warps', 'dcache_ports','clusters', 'cores', 'write_back', 'app'], suffixes=('_r1', '_r2'))
vecadd_df['instrs'] = vecadd_df['instrs_r2'] - vecadd_df['instrs_r1']
vecadd_df['cycles'] = vecadd_df['cycles_r2'] - vecadd_df['cycles_r1']

#add cycle/area metric based on clusters
for c in vecadd_df['clusters'].unique():
    area = areas[areas['clusters'] == c]['area'].values[0]
    vecadd_df.loc[vecadd_df['clusters'] == c, 'area_eff'] = vecadd_df[vecadd_df['clusters'] == c]['cycles'] * area

#####################################################################
# knn

knn_df = pd.DataFrame()
for hw_cfg in hw_cfgs:
    knn_df_file = dir_tmlp.format("knn", hw_cfg) + "/dataframe.feather"
    knn_df = pd.concat([knn_df, pd.read_feather(knn_df_file)], ignore_index=True)

# read swift df
swift_knn_df = pd.read_feather(swift_tmlp.format("knn") + "/dataframe.feather")

# remove from swift workload size not in knn_df
swift_knn_df = swift_knn_df[swift_knn_df['workload_size'].isin(knn_df['workload_size'])]

#remove write_back=1 from swift_knn_df
swift_knn_df = swift_knn_df[swift_knn_df['write_back'] == 0]

# check that all workload size in knn_df are in swift_knn_df
assert len(knn_df[~knn_df['workload_size'].isin(swift_knn_df['workload_size'])]) == 0

# merge swift_knn_df with knn_df
knn_df = pd.concat([knn_df, swift_knn_df], ignore_index=True)

knn_df_repeat1 = knn_df[knn_df['repeat'] == 1].reset_index(drop=True)
knn_df_repeat2 = knn_df[knn_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
knn_df = pd.merge(knn_df_repeat1, knn_df_repeat2, on=['workload_size', 'threads', 'warps', 'dcache_ports','clusters', 'cores', 'write_back', 'app'], suffixes=('_r1', '_r2'))

knn_df['instrs'] = knn_df['instrs_r2'] - knn_df['instrs_r1']
knn_df['cycles'] = knn_df['cycles_r2'] - knn_df['cycles_r1']

#add cycle/area metric based on clusters

for c in knn_df['clusters'].unique():
    area = areas[areas['clusters'] == c]['area'].values[0]
    knn_df.loc[knn_df['clusters'] == c, 'area_eff'] = knn_df[knn_df['clusters'] == c]['cycles'] * area

#####################################################################
# saxpy

saxpy_df = pd.DataFrame()
for hw_cfg in hw_cfgs:
    saxpy_df_file = dir_tmlp.format("saxpy", hw_cfg) + "/dataframe.feather"
    saxpy_df = pd.concat([saxpy_df, pd.read_feather(saxpy_df_file)], ignore_index=True)

# read swift df
swift_saxpy_df = pd.read_feather(swift_tmlp.format("saxpy") + "/dataframe.feather")

# remove from swift workload size not in saxpy_df
swift_saxpy_df = swift_saxpy_df[swift_saxpy_df['workload_size'].isin(saxpy_df['workload_size'])]

#remove write_back=1 from swift_saxpy_df
swift_saxpy_df = swift_saxpy_df[swift_saxpy_df['write_back'] == 0]

# check that all workload size in saxpy_df are in swift_saxpy_df
assert len(saxpy_df[~saxpy_df['workload_size'].isin(swift_saxpy_df['workload_size'])]) == 0

# merge swift_saxpy_df with saxpy_df
saxpy_df = pd.concat([saxpy_df, swift_saxpy_df], ignore_index=True)

saxpy_df_repeat1 = saxpy_df[saxpy_df['repeat'] == 1].reset_index(drop=True)
saxpy_df_repeat2 = saxpy_df[saxpy_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
saxpy_df = pd.merge(saxpy_df_repeat1, saxpy_df_repeat2, on=['workload_size', 'threads', 'warps', 'dcache_ports','clusters', 'cores', 'write_back', 'app'], suffixes=('_r1', '_r2'))

saxpy_df['instrs'] = saxpy_df['instrs_r2'] - saxpy_df['instrs_r1']
saxpy_df['cycles'] = saxpy_df['cycles_r2'] - saxpy_df['cycles_r1']

#add cycle/area metric based on clusters

for c in saxpy_df['clusters'].unique():
    area = areas[areas['clusters'] == c]['area'].values[0]
    saxpy_df.loc[saxpy_df['clusters'] == c, 'area_eff'] = saxpy_df[saxpy_df['clusters'] == c]['cycles'] * area

#####################################################################
# sfilter

sfilter_df = pd.DataFrame()
for hw_cfg in hw_cfgs:
    sfilter_df_file = dir_tmlp.format("sfilter", hw_cfg) + "/dataframe.feather"
    sfilter_df = pd.concat([sfilter_df, pd.read_feather(sfilter_df_file)], ignore_index=True)

# read swift df
swift_sfilter_df = pd.read_feather(swift_tmlp.format("sfilter") + "/dataframe.feather")

# remove from swift workload size not in sfilter_df
swift_sfilter_df = swift_sfilter_df[swift_sfilter_df['workload_size_y'].isin(sfilter_df['workload_size_y'])]

#remove write_back=1 from swift_sfilter_df
swift_sfilter_df = swift_sfilter_df[swift_sfilter_df['write_back'] == 0]

# check that all workload size in sfilter_df are in swift_sfilter_df
assert len(sfilter_df[~sfilter_df['workload_size_y'].isin(swift_sfilter_df['workload_size_y'])]) == 0

# merge swift_sfilter_df with sfilter_df
sfilter_df = pd.concat([sfilter_df, swift_sfilter_df], ignore_index=True)

sfilter_df_repeat1 = sfilter_df[sfilter_df['repeat'] == 1].reset_index(drop=True)
sfilter_df_repeat2 = sfilter_df[sfilter_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
sfilter_df = pd.merge(sfilter_df_repeat1, sfilter_df_repeat2, on=['workload_size_y', 'workload_size_x','threads', 'warps', 'dcache_ports','clusters', 'cores', 'write_back', 'app'], suffixes=('_r1', '_r2'))

sfilter_df['instrs'] = sfilter_df['instrs_r2'] - sfilter_df['instrs_r1']
sfilter_df['cycles'] = sfilter_df['cycles_r2'] - sfilter_df['cycles_r1']

sfilter_df['workload_size'] = sfilter_df['workload_size_x'] * sfilter_df['workload_size_y']


#add cycle/area metric based on clusters

for c in sfilter_df['clusters'].unique():
    area = areas[areas['clusters'] == c]['area'].values[0]
    sfilter_df.loc[sfilter_df['clusters'] == c, 'area_eff'] = sfilter_df[sfilter_df['clusters'] == c]['cycles'] * area

#####################################################################
# sgemm

sgemm_df = pd.DataFrame()
for hw_cfg in hw_cfgs:
    sgemm_df_file = dir_tmlp.format("sgemm", hw_cfg) + "/dataframe.feather"
    sgemm_df = pd.concat([sgemm_df, pd.read_feather(sgemm_df_file)], ignore_index=True)

# read swift df
swift_sgemm_df = pd.read_feather(swift_tmlp.format("sgemm") + "/dataframe.feather")

# remove from swift workload size not in sgemm_df
swift_sgemm_df = swift_sgemm_df[swift_sgemm_df['workload_size_y'].isin(sgemm_df['workload_size_y'])]

#remove write_back=1 from swift_sgemm_df
swift_sgemm_df = swift_sgemm_df[swift_sgemm_df['write_back'] == 0]

# check that all workload size in sgemm_df are in swift_sgemm_df
assert len(sgemm_df[~sgemm_df['workload_size_y'].isin(swift_sgemm_df['workload_size_y'])]) == 0

# merge swift_sgemm_df with sgemm_df
sgemm_df = pd.concat([sgemm_df, swift_sgemm_df], ignore_index=True)

sgemm_df_repeat1 = sgemm_df[sgemm_df['repeat'] == 1].reset_index(drop=True)
sgemm_df_repeat2 = sgemm_df[sgemm_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
sgemm_df = pd.merge(sgemm_df_repeat1, sgemm_df_repeat2, on=['workload_size_y', 'workload_size_x', 'threads', 'warps', 'dcache_ports','clusters', 'cores', 'write_back', 'app'], suffixes=('_r1', '_r2'))

# add instrs and cycles
sgemm_df['instrs'] = sgemm_df['instrs_r2'] - sgemm_df['instrs_r1']
sgemm_df['cycles'] = sgemm_df['cycles_r2'] - sgemm_df['cycles_r1']

sgemm_df['workload_size'] = sgemm_df['workload_size_y'] * sgemm_df['workload_size_x']

#add cycle/area metric based on clusters

for c in sgemm_df['clusters'].unique():
    area = areas[areas['clusters'] == c]['area'].values[0]
    sgemm_df.loc[sgemm_df['clusters'] == c, 'area_eff'] = sgemm_df[sgemm_df['clusters'] == c]['cycles'] * area

#####################################################################
# conv2d

conv2d_df = pd.DataFrame()
for hw_cfg in hw_cfgs:
    conv2d_df_file = dir_tmlp.format("conv2d", hw_cfg) + "/dataframe.feather"
    conv2d_df = pd.concat([conv2d_df, pd.read_feather(conv2d_df_file)], ignore_index=True)

# read swift df
swift_conv2d_df = pd.read_feather(swift_tmlp.format("conv2d") + "/dataframe.feather")

# remove from swift workload size not in conv2d_df
swift_conv2d_df = swift_conv2d_df[swift_conv2d_df['workload_size_y'].isin(conv2d_df['workload_size_y'])]

#remove write_back=1 from swift_conv2d_df
swift_conv2d_df = swift_conv2d_df[swift_conv2d_df['write_back'] == 0]

# check that all workload size in conv2d_df are in swift_conv2d_df
assert len(conv2d_df[~conv2d_df['workload_size_y'].isin(swift_conv2d_df['workload_size_y'])]) == 0

# merge swift_conv2d_df with conv2d_df
conv2d_df = pd.concat([conv2d_df, swift_conv2d_df], ignore_index=True)

conv2d_df_repeat1 = conv2d_df[conv2d_df['repeat'] == 1].reset_index(drop=True)
conv2d_df_repeat2 = conv2d_df[conv2d_df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of instructions
conv2d_df = pd.merge(conv2d_df_repeat1, conv2d_df_repeat2, on=['workload_size_y', 'workload_size_x', 'out_channels', 'in_channels', 'threads', 'warps', 'dcache_ports','clusters', 'cores', 'write_back', 'app'], suffixes=('_r1', '_r2'))

# add instrs and cycles
conv2d_df['instrs'] = conv2d_df['instrs_r2'] - conv2d_df['instrs_r1']
conv2d_df['cycles'] = conv2d_df['cycles_r2'] - conv2d_df['cycles_r1']

conv2d_df['workload_size'] = conv2d_df['workload_size_x'] * conv2d_df['workload_size_y'] * conv2d_df['out_channels'] * conv2d_df['in_channels'] / conv2d_df['threads']

#add cycle/area metric based on clusters

for c in conv2d_df['clusters'].unique():
    area = areas[areas['clusters'] == c]['area'].values[0]
    conv2d_df.loc[conv2d_df['clusters'] == c, 'area_eff'] = conv2d_df[conv2d_df['clusters'] == c]['cycles'] * area
####################################################################

# merge all dataframes into one with columns app, clusters, cycles (avg), area_eff (avg)
df = pd.DataFrame(columns=['app', 'clusters', 'cycles', 'area_eff'])

avg_df = pd.DataFrame(columns=['app', 'clusters', 'cycles', 'area_eff'])
for df_ in [vecadd_df, knn_df, saxpy_df, sfilter_df, sgemm_df, conv2d_df]:
    for c in df_['clusters'].unique():
        avg_cycles = df_[df_['clusters'] == c]['cycles'].mean()
        avg_area_eff = df_[df_['clusters'] == c]['area_eff'].mean()
        avg_df = pd.concat([avg_df, pd.DataFrame({'app' : [df_['app'].unique()[0]], 'clusters' : [c], 'cycles' : [avg_cycles], 'area_eff' : [avg_area_eff]})], ignore_index=True)

#print(avg_df.to_string())

#####################################################################
# Now we can plot

# Plotting

cm = 1/2.54  # centimeters in inches
scale = 5
#subdividing the plot into 4 subplots

hatches = ['//', '..', 'xx']
font_incr = 3.5
fontproperties = {'family': 'Calibri', 'size': 10*font_incr}
aspectR=3
y_axis_str = 1e2
font_incr = 3.5
fontproperties = {'family': 'Calibri', 'size': 10*font_incr}

y_lim = avg_df['cycles'].max() * 1.1

g = sns.catplot(x='app', y='cycles', hue='clusters', data=avg_df, kind='bar', height=8.45/3*cm*scale, aspect=aspectR, width=0.6, legend=False)

plt.yscale('log')
plt.ylim(1e2, y_lim)
#remove '-airbender' from app names
plt.xticks(ticks=range(6), labels=[app.replace('-airbender', '') for app in avg_df['app'].unique()])
plt.xticks(rotation=30)
plt.xlabel('')

for item in ([g.ax.xaxis.label, g.ax.yaxis.label] +
             g.ax.get_xticklabels() + g.ax.get_yticklabels()):
    item.set_fontname('Calibri')
    size = item.get_fontsize()
    item.set_fontsize(size*font_incr)

plt.tight_layout()

output_dir = base_dir + "/plotss"
os.makedirs(output_dir, exist_ok=True)
output_file = output_dir + "/cycles"

plt.savefig(output_file + ".pdf", format='pdf', bbox_inches='tight')
plt.savefig(output_file + ".svg", format='svg', bbox_inches='tight')

plt.close()
plt.clf()

#####################################################################

y_lim = avg_df['area_eff'].max() * 1.1

g = sns.catplot(x='app', y='area_eff', hue='clusters', data=avg_df, kind='bar', height=8.45/3*cm*scale, aspect=aspectR, width=0.6, legend=False)

plt.legend(title='Clusters', loc='upper left', ncol=4, prop=fontproperties,title_fontproperties=fontproperties)

plt.yscale('log')
plt.ylabel('Area x Latency (mm^2*cycles)')
plt.ylim(1e2*5, y_lim)

#remove '-airbender' from app names
plt.xticks(ticks=range(6), labels=[app.replace('-airbender', '') for app in avg_df['app'].unique()])
plt.xticks(rotation=30)
plt.xlabel('')

for item in ([g.ax.xaxis.label, g.ax.yaxis.label] +
                g.ax.get_xticklabels() + g.ax.get_yticklabels()):
        item.set_fontname('Calibri')
        size = item.get_fontsize()
        item.set_fontsize(size*font_incr)

plt.tight_layout()

output_dir = base_dir + "/plotss"
os.makedirs(output_dir, exist_ok=True)
output_file = output_dir + "/area_eff"

plt.savefig(output_file + ".pdf", format='pdf', bbox_inches='tight')
plt.savefig(output_file + ".svg", format='svg', bbox_inches='tight')

