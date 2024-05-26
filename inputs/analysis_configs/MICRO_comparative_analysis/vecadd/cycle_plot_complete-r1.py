"""Tiny script to plot cycles"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

res_root = "./scripts/outputs/ASPLOS-COMP-vecadd-im-1C1c4w4t/"
df_file = res_root + "dataframe.feather"
output_dir = res_root + "comparative_analysis/"
os.makedirs(output_dir, exist_ok=True)
#baseline = 'vecadd-ssr'

df  = pd.read_feather(df_file)
df_repeat1 = df[df['repeat'] == 1].reset_index(drop=True)
df_repeat2 = df[df['repeat'] == 2].reset_index(drop=True)

# merge the two dataframes makeing the subtract of the cycles
df = pd.merge(df_repeat1, df_repeat2, on=['workload_size', 'kernel'], suffixes=('_r1', '_r2'))
df['cycles'] = df['cycles_r2'] - df['cycles_r1']
df['instrs'] = df['instrs_r2'] - df['instrs_r1']
df['dcache_bank_utilization'] = df['dcache_bank_utilization_r2']
df['dcache_bank_stalls'] = df['dcache_bank_stalls_r2'] - df['dcache_bank_stalls_r1']


#substitute cycles < 0 with 0
df.loc[df['cycles'] < 0, 'cycles'] = 0
#plot cycles, y axis is cycles, x axis is workload_size, and we have a line for each kernel
sns.lineplot(x='workload_size', y='cycles', hue='kernel', data=df)
#add grid
plt.grid()
#fix y axis
#plt.ylim(0, 10000000)
plt.savefig(output_dir + 'cycles.svg')

plt.clf()

#plot instrs, y axis is instrs, x axis is workload_size, and we have a line for each kernel
sns.lineplot(x='workload_size', y='instrs', hue='kernel', data=df)
#add grid
plt.grid()
plt.savefig(output_dir + 'instrs.svg')

plt.clf()

#plot bank conflicts, y axis is bank_conflicts, x axis is workload_size, and we have a line for each kernel
sns.lineplot(x='workload_size', y='dcache_bank_utilization', hue='kernel', data=df)
#add grid
plt.grid()
plt.savefig(output_dir + 'dcache_bank_utilization.svg')

plt.clf()

#plot cycles - bank conflicts, y axis is cycles - bank_conflicts, x axis is workload_size, and we have a line for each kernel
df['cycles_bank_stalls'] = df['cycles'] - (df['dcache_bank_stalls'])
sns.lineplot(x='workload_size', y='cycles_bank_stalls', hue='kernel', data=df)
#add grid
plt.grid()
plt.savefig(output_dir + 'cycles_bank.svg')

plt.clf()

#plot stalls
sns.lineplot(x='workload_size', y='dcache_bank_stalls', hue='kernel', data=df)
#add grid
plt.grid()
plt.savefig(output_dir + 'dcache_bank_stalls.svg')

plt.clf()

df['cycle_ratio'] = 1
#plot cycle ratio vecadd-base/others
for ws in df['workload_size'].unique():
    vecadd_base_cycles = df[(df['kernel'] == 'vecadd-base') & (df['workload_size'] == ws)]['cycles'].values[0]
    df.loc[(df['kernel'] != 'vecadd-base') & (df['workload_size'] == ws), 'cycle_ratio'] = vecadd_base_cycles / df[(df['kernel'] != 'vecadd-base') & (df['workload_size'] == ws)]['cycles'] 
sns.lineplot(x='workload_size', y='cycle_ratio', hue='kernel', data=df)
#add grid
plt.grid()
#fix y axis
plt.ylim(0, 20)
plt.savefig(output_dir + 'cycle_ratio.svg')

plt.clf()

#plot instrs ratio
df['instr_ratio'] = 1
for ws in df['workload_size'].unique():
    vecadd_base_instrs = df[(df['kernel'] == 'vecadd-base') & (df['workload_size'] == ws)]['instrs'].values[0]
    df.loc[(df['kernel'] != 'vecadd-base') & (df['workload_size'] == ws), 'instr_ratio'] =  vecadd_base_instrs / df[(df['kernel'] != 'vecadd-base') & (df['workload_size'] == ws)]['instrs']
sns.lineplot(x='workload_size', y='instr_ratio', hue='kernel', data=df)
#add grid
plt.grid()
plt.savefig(output_dir + 'instr_ratio.svg')

plt.clf()