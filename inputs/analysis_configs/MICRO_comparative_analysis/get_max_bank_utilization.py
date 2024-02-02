import pandas as pd

fname = "/vx/scripts/outputs/MICRO-COMP-sgemm-expl-16384/dataframe.feather"
df = pd.read_feather(fname)
a = df['dcache_bank_utilization'].max()
print("Max bank utilization: ", a)
print(df.loc[df['dcache_bank_utilization'] == a])