import os
import util.os_utils as osu
import util.parsers.extractor as parsers
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def gen_hw_str(x):
    return f"{x['clusters']}_{x['cores']}_{x['warps']}_{x['threads']}"

def make_perc(x, col):
    p = x["sum_0vs{}".format(col)] / x["0"] if x["sum_0vs{}".format(col)] >= 0 else x["sum_0vs{}".format(col)] / x[col]
    p = p*100 if p*100 <300 else 300
    #p = p if p > -300 else -300
    return p

#parser = parsers.ExtractorParserClass()
#with osu.cd(parser.args.output_dir):
res_path = "outputs/"
dirs = os.listdir(res_path)
dirs = [d for d in dirs if os.path.isdir(os.path.join(res_path, d))]
dirs = [os.path.join(res_path, d) for d in dirs]
dirs = [d for d in dirs if d.split("/")[-1].startswith("IISWC")]
plot_df = pd.DataFrame({})
for d in dirs:
    with osu.cd(d):
        if not os.path.isfile("dataframe.feather"): continue
        print(d)
        df = pd.read_feather("dataframe.feather")
        cdf = pd.DataFrame({})
        df["hw"] = df.apply(gen_hw_str, axis=1)
        pivot = df.pivot(index="hw", columns="local_worksize", values="cycles")
        pivot.columns = pivot.columns.map(str)
        pivot['sum_0vs1']   = pivot['1'] - pivot['0']
        pivot['sum_0vs32']  = pivot['32'] - pivot['0']
        pivot['perc_0vs1']  = pivot.apply(lambda x: make_perc(x, "1"), axis=1)
        pivot['perc_0vs32'] = pivot.apply(lambda x: make_perc(x, "32"), axis=1)
        pivot = pd.melt(pivot, value_vars=["perc_0vs1", "perc_0vs32"], id_vars=["1", "32"], var_name="local_worksize", value_name="cycles")
        name = d.split("-")[-1]
        pivot["workload"] = [ name for _ in range(len(pivot))]
        plot_df = pd.concat([plot_df, pivot])
#sorting
plot_df["workload"] = pd.Categorical(plot_df["workload"], ["vecadd", "sgemm", "sfilter", "saxpy", "nearn", "aggr", "dnn", "gcn"])
plot_df = plot_df.sort_values(by="workload")
plt.figure(figsize=(20,5))
sns.violinplot(data=plot_df, x="workload", y="cycles", hue="local_worksize", split=True, inner="stick", linewidth=0.7)
plt.savefig("plots/violin.svg", dpi=300, bbox_inches="tight")
    #for C in df["clusters"].unique().tolist():
    #    for c in df["cores"].unique().tolist():
    #        for w in df["warps"].unique().tolist():
    #            for t in df["threads"].unique().tolist():
    #                filtered_df = df.loc[(df["clusters"]==C) & (df["cores"]==c) & (df["warps"]==w) & (df["threads"]==t)]
    #                if filtered_df.empty: continue
    #                cdf["sub_1"] =  filtered_df.loc[""]
    