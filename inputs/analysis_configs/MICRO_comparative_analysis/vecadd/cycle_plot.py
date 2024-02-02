"""Tiny script to plot cycles"""
import math
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df_file = "/vx/scripts/outputs/MICRO-COMP-vecadd-limbo-prova/dataframe.feather"
output_dir = "/vx/scripts/outputs/MICRO-COMP-vecadd-limbo-prova/comparative_analysis/"

df  = pd.read_feather(df_file)
cdf = df.groupby('workload_size').apply(lambda x: (x.loc[x['kernel'] == 'vecadd', 'cycles'].iloc[0] - x.loc[x['kernel'] == 'vecadd-limbo', 'cycles'].iloc[0]) * 100 / x.loc[x['kernel'] == 'vecadd', 'cycles'].iloc[0])
cdf = cdf.reset_index()
cdf.columns = ['workload_size', 'cycles']
ndf = df.groupby('workload_size').apply(
        lambda x: (x.loc[x['kernel'] == 'vecadd-limbo', 'dcache_read_hit_ratio'].iloc[0])).reset_index()
ndf.columns = ['workload_size', 'dcache_read_hit_ratio']
cdf = cdf.merge(ndf, on='workload_size')
cdf['folding'] = ((cdf['workload_size'].astype(int) + 1) / 16).astype(int)
cdf['marks'] = [x for x in range(0, len(cdf['folding'].unique()))]

ax1 = sns.lineplot(x='marks', y='cycles', data=cdf)
ax2 = ax1.twinx()
ax2 = sns.lineplot(x='marks', y='dcache_read_hit_ratio', data=cdf, ax=ax2, color='red')
ax1.set(xlabel='Folding', ylabel='Latency gain (%)')
ax2.set(ylabel='Dcache read hit ratio (%)')
ax1.set_xticks(range(0, len(cdf['folding'].unique())))
ax1.set_xticklabels(cdf['folding'].unique())

# changing the size ratio of the plot
ax1.figure.set_size_inches(10, 5)
plt.savefig(output_dir + 'cycles.svg')

plt.clf()

# Making instrs plot
cdf = df.groupby('workload_size').apply(lambda x: (x.loc[x['kernel'] == 'vecadd', 'instrs'].iloc[0] - x.loc[x['kernel'] == 'vecadd-limbo', 'instrs'].iloc[0]) * 100 / x.loc[x['kernel'] == 'vecadd', 'instrs'].iloc[0])
cdf = cdf.reset_index()
cdf.columns = ['workload_size', 'instrs']
cdf['folding'] = ((cdf['workload_size'].astype(int) + 1) / 16).astype(int)
cdf['marks'] = [x for x in range(0, len(cdf['folding'].unique()))]

ax1 = sns.lineplot(x='marks', y='instrs', data=cdf)
ax1.set(xlabel='Folding', ylabel='Instrs gain (%)')
ax1.set_xticks(range(0, len(cdf['folding'].unique())))
ax1.set_xticklabels(cdf['folding'].unique())
plt.savefig(output_dir + 'instrs.svg')
