import pandas as pd
import os
import util.os_utils as osu

output_dir = "outputs/"
rn_test_case = [
    "IISWC-COMP-rn-badd",
    "IISWC-COMP-rn-relu",
    "IISWC-COMP-rn-sgemm",
    "IISWC-COMP-rn-vecadd",
]
rn_test_case = [os.path.join(output_dir, d) for d in rn_test_case]

gcn_test_case = [
    "IISWC-COMP-gcn-badd",
    "IISWC-COMP-gcn-relu",
    "IISWC-COMP-gcn-aggr",
    "IISWC-COMP-gcn-linear",
]
gcn_test_case = [os.path.join(output_dir, d) for d in gcn_test_case]

def gen_df(l,path):
    osu.mkdir(path)
    df = pd.DataFrame({})
    for d in l:
        if df.empty: df = pd.read_feather(os.path.join(d, "dataframe.feather"))
        else:
            new_df = pd.read_feather(os.path.join(d, "dataframe.feather"))
            df = pd.merge(df, new_df, on=["clusters", "cores", "warps", "threads", "local_worksize"], suffixes=('_df1', '_df2'))
            df["cycles"] = df["cycles_df1"] + df["cycles_df2"]
            df = df[df.columns.drop(list(df.filter(regex='_df')))]
    df.to_feather(os.path.join(path, "dataframe.feather"))

gen_df(rn_test_case, "outputs/IISWC-COMP-resnet/")
gen_df(gcn_test_case, "outputs/IISWC-COMP-gcn/")