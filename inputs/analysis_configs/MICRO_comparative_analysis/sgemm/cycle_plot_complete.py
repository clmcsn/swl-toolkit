"""Tiny script to plot cycles"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

res_root = "./scripts/outputs/MICRO-COMP-sgemm-idealmem-mhws/"
df_file = res_root + "dataframe.feather"
output_dir = res_root + "comparative_analysis/"
baseline = 'sgemm'
os.makedirs(output_dir, exist_ok=True)
#baseline = 'vecadd-ssr'

df  = pd.read_feather(df_file)
#workload size as workload_size_x*workload_size_y
df['workload_size'] = df['workload_size_x'] * df['workload_size_y']
#plot cycles, y axis is cycles, x axis is workload_size, and we have a line for each kernel
sns.lineplot(x='workload_size', y='cycles', hue='kernel', data=df)
#add grid
plt.grid()
plt.ylim(0, 20000000)
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
    vecadd_base_cycles = df[(df['kernel'] == baseline) & (df['workload_size'] == ws)]['cycles'].values[0]
    df.loc[(df['kernel'] != baseline) & (df['workload_size'] == ws), 'cycle_ratio'] = vecadd_base_cycles / df[(df['kernel'] != baseline) & (df['workload_size'] == ws)]['cycles'] 
sns.lineplot(x='workload_size', y='cycle_ratio', hue='kernel', data=df)
#add grid
plt.grid()
plt.ylim(0, 22)
plt.savefig(output_dir + 'cycle_ratio.svg')

plt.clf()

#plot instrs ratio
df['instr_ratio'] = 1
for ws in df['workload_size'].unique():
    vecadd_base_instrs = df[(df['kernel'] == baseline) & (df['workload_size'] == ws)]['instrs'].values[0]
    df.loc[(df['kernel'] != baseline) & (df['workload_size'] == ws), 'instr_ratio'] =  vecadd_base_instrs / df[(df['kernel'] != baseline) & (df['workload_size'] == ws)]['instrs']
sns.lineplot(x='workload_size', y='instr_ratio', hue='kernel', data=df)
#add grid
plt.grid()
plt.savefig(output_dir + 'instr_ratio.svg')

plt.clf()
