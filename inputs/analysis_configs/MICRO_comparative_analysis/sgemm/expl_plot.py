"""Tiny script to plot cycles"""
import math
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df_file = "/vx/scripts/outputs/MICRO-COMP-sgemm-expl/dataframe.feather"
output_dir = "/vx/scripts/outputs/MICRO-COMP-sgemm-expl/comparative_analysis/"

df  = pd.read_feather(df_file)
df['workload_size'] = df.apply(lambda x: 'x'+ str(x['workload_size_x']) + '_y' + str(x['workload_size_y']) + '_z' + str(x['workload_size_z']), axis=1)
cdf = df.groupby('workload_size').apply(lambda x: (x.loc[x['kernel'] == 'sgemm', 'cycles'].iloc[0] - x.loc[x['kernel'] == 'sgemm-limbo', 'cycles'].iloc[0]) * 100 / x.loc[x['kernel'] == 'sgemm', 'cycles'].iloc[0])
cdf = cdf.reset_index()
cdf.columns = ['workload_size', 'cycles']
#ndf = df.groupby('workload_size').apply(
#        lambda x: (x.loc[x['kernel'] == 'sgemm-limbo', 'dcache_read_hit_ratio'].iloc[0])).reset_index()
#ndf.columns = ['workload_size', 'dcache_read_hit_ratio']
#cdf = cdf.merge(ndf, on='workload_size')
ndf = df.groupby('workload_size').apply(
        lambda x: (x.loc[x['kernel'] == 'sgemm-limbo', 'dcache_bank_utilization'].iloc[0])).reset_index()
ndf.columns = ['workload_size', 'dcache_bank_utilization']
cdf = cdf.merge(ndf, on='workload_size')
#add ID here
ndf = df.groupby('workload_size').apply(
        lambda x: (x.loc[x['kernel'] == 'sgemm-limbo', 'ID'].iloc[0])).reset_index()
ndf.columns = ['workload_size', 'ID']
cdf = cdf.merge(ndf, on='workload_size')

ax1 = sns.lineplot(x='ID', y='cycles', data=cdf)
ax2 = ax1.twinx()
ax2 = sns.lineplot(x='ID', y='dcache_bank_utilization', data=cdf, ax=ax2, color='red')
ax1.figure.set_size_inches(80, 6)
plt.savefig(output_dir + 'cycles.svg')
plt.clf()

#printing average cycles for z values
cdf = df.groupby('workload_size').apply(lambda x: (x.loc[x['kernel'] == 'sgemm', 'cycles'].iloc[0] - x.loc[x['kernel'] == 'sgemm-limbo', 'cycles'].iloc[0]) * 100 / x.loc[x['kernel'] == 'sgemm', 'cycles'].iloc[0])
cdf = cdf.reset_index()
cdf.columns = ['workload_size', 'cycles']
ndf = df.groupby('workload_size').apply(
        lambda x: (x.loc[x['kernel'] == 'sgemm-limbo', 'workload_size_z'].iloc[0])).reset_index()
ndf.columns = ['workload_size', 'z']
cdf = cdf.merge(ndf, on='workload_size')
cdf = cdf.groupby('z')['cycles'].mean()
ax1 = sns.lineplot(x=cdf.index, y=cdf.values)
ax1.figure.set_size_inches(10, 5)
plt.savefig(output_dir + 'cycles_z.svg')
plt.clf()

#printing average cycles for x values
cdf = df.groupby('workload_size').apply(lambda x: (x.loc[x['kernel'] == 'sgemm', 'cycles'].iloc[0] - x.loc[x['kernel'] == 'sgemm-limbo', 'cycles'].iloc[0]) * 100 / x.loc[x['kernel'] == 'sgemm', 'cycles'].iloc[0])
cdf = cdf.reset_index()
cdf.columns = ['workload_size', 'cycles']
ndf = df.groupby('workload_size').apply(
        lambda x: (x.loc[x['kernel'] == 'sgemm-limbo', 'workload_size_x'].iloc[0])).reset_index()
ndf.columns = ['workload_size', 'x']
cdf = cdf.merge(ndf, on='workload_size')
cdf = cdf.groupby('x')['cycles'].mean()
ax1 = sns.lineplot(x=cdf.index, y=cdf.values)
ax1.figure.set_size_inches(10, 5)
plt.savefig(output_dir + 'cycles_x.svg')
plt.clf()

#printing average cycles for y values
cdf = df.groupby('workload_size').apply(lambda x: (x.loc[x['kernel'] == 'sgemm', 'cycles'].iloc[0] - x.loc[x['kernel'] == 'sgemm-limbo', 'cycles'].iloc[0]) * 100 / x.loc[x['kernel'] == 'sgemm', 'cycles'].iloc[0])
cdf = cdf.reset_index()
cdf.columns = ['workload_size', 'cycles']
ndf = df.groupby('workload_size').apply(
        lambda x: (x.loc[x['kernel'] == 'sgemm-limbo', 'workload_size_y'].iloc[0])).reset_index()
ndf.columns = ['workload_size', 'y']
cdf = cdf.merge(ndf, on='workload_size')
cdf = cdf.groupby('y')['cycles'].mean()
ax1 = sns.lineplot(x=cdf.index, y=cdf.values)
ax1.figure.set_size_inches(10, 5)
plt.savefig(output_dir + 'cycles_y.svg')
plt.clf()

#cdf['folding'] = ((cdf['workload_size'].astype(int) + 1) / 16).astype(int)
#cdf['marks'] = [x for x in range(0, len(cdf['folding'].unique()))]
#
#ax1 = sns.lineplot(x='marks', y='cycles', data=cdf)
#ax2 = ax1.twinx()
#ax2 = sns.lineplot(x='marks', y='dcache_read_hit_ratio', data=cdf, ax=ax2, color='red')
#ax2 = sns.lineplot(x='marks', y='dcache_bank_utilization', data=cdf, ax=ax2, color='green')
#ax1.set(xlabel='Folding', ylabel='Latency gain (%)')
#ax2.set(ylabel='Dcache read hit ratio (%)')
#ax1.set_xticks(range(0, len(cdf['folding'].unique())))
#ax1.set_xticklabels(cdf['folding'].unique())
#
## changing the size ratio of the plot
#ax1.figure.set_size_inches(10, 5)
#plt.savefig(output_dir + 'cycles.svg')
#
#plt.clf()
#
## Making instrs plot
#cdf = df.groupby('workload_size').apply(lambda x: (x.loc[x['kernel'] == 'sgemm', 'instrs'].iloc[0] - x.loc[x['kernel'] == 'sgemm-limbo', 'instrs'].iloc[0]) * 100 / x.loc[x['kernel'] == 'sgemm', 'instrs'].iloc[0])
#cdf = cdf.reset_index()
#cdf.columns = ['workload_size', 'instrs']
#cdf['folding'] = ((cdf['workload_size'].astype(int) + 1) / 16).astype(int)
#cdf['marks'] = [x for x in range(0, len(cdf['folding'].unique()))]
#
#ax1 = sns.lineplot(x='marks', y='instrs', data=cdf)
#ax1.set(xlabel='Folding', ylabel='Instrs gain (%)')
#ax1.set_xticks(range(0, len(cdf['folding'].unique())))
#ax1.set_xticklabels(cdf['folding'].unique())
#plt.savefig(output_dir + 'instrs.svg')
