"""Tiny script to plot cycles"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

df_file = "./scripts/outputs/MICRO-COMP-vecadd-ssr/dataframe.feather"
output_dir = "./scripts/outputs/MICRO-COMP-vecadd-ssr/comparative_analysis/"
os.makedirs(output_dir, exist_ok=True)
#baseline = 'vecadd-ssr'

df  = pd.read_feather(df_file)
#plot cycles, y axis is cycles, x axis is workload_size, and we have a line for each kernel
sns.lineplot(x='workload_size', y='cycles', hue='kernel', data=df)
#add grid
plt.grid()
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