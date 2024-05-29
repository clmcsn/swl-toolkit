"""Tiny script to plot cycles"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

res_root = "./scripts/outputs/ASPLOS-COMP-saxpy-im-1C2c4w8t/"
df_file = res_root + "dataframe.feather"
output_dir = res_root + "comparative_analysis/"
os.makedirs(output_dir, exist_ok=True)
#baseline = 'saxpy-ssr'

df  = pd.read_feather(df_file)
df_repeat1 = df[df['repeat'] == 1].reset_index(drop=True)
df_repeat2 = df[df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of the cycles
df = pd.merge(df_repeat1, df_repeat2, on=['dataset', 'kernel','vlen'], suffixes=('_r1', '_r2'))
df['cycles'] = df['cycles_r2'] - df['cycles_r1']
df['instrs'] = df['instrs_r2'] - df['instrs_r1']
df['dcache_bank_utilization'] = df['dcache_bank_utilization_r2']
df['dcache_bank_stalls'] = df['dcache_bank_stalls_r2'] - df['dcache_bank_stalls_r1']


df['cycle_ratio'] = 1
#plot cycles, y axis is cycles, x axis is vlen, and we have a line for each kernel
for dataset in df['dataset'].unique():
    sns.lineplot(x='vlen', y='cycles', hue='kernel', data=df[df['dataset'] == dataset])
    #add grid
    plt.grid()
    #fix y axis
    #plt.ylim(0, 10000000)
    plt.savefig(output_dir + 'cycles_'+dataset+'.svg')
    plt.clf()

    #plot instrs, y axis is instrs, x axis is vlen, and we have a line for each kernel
    sns.lineplot(x='vlen', y='instrs', hue='kernel', data=df[df['dataset'] == dataset])
    #add grid
    plt.grid()
    plt.savefig(output_dir + 'instrs_'+dataset+'.svg')
    plt.clf()

    #plot bank conflicts, y axis is bank_conflicts, x axis is vlen, and we have a line for each kernel
    sns.lineplot(x='vlen', y='dcache_bank_utilization', hue='kernel', data=df[df['dataset'] == dataset])
    #add grid
    plt.grid()
    plt.savefig(output_dir + 'dcache_bank_utilization_'+dataset+'.svg')
    plt.clf()

    
    for vlen in df[df['dataset'] == dataset]['vlen'].unique():
        base_cycles = df[(df['dataset'] == dataset) & (df['vlen'] == vlen) & (df['kernel'] == 'aggr-el-base')]['cycles'].values[0]