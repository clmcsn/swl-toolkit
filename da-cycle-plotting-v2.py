import os
import pandas as pd
import math

from util.parser import DataAnalysisParserClass
from util.launch_util import mkdir, cmd
from inputs.template import templateDict

from plots.strip import gen_strip, gen_strip_marker
from plots.utils import gen_bar_name

def log_column(x):
    r=math.log(x["local_worksize"],2)
    return r

def str_column(x, col):
    return str(x[col])

def group_hardware(x):
    r = x["warps"]*x["threads"]
    return r

def main(args, dfname="dataframe.csv"):
    parser = DataAnalysisParserClass(args)
    print("Loading dataframe...")
    DF_NAME = parser.args.res_path + dfname
    df = pd.read_csv(DF_NAME)
    string_local_worksize = "local_worksize_str"
    df[string_local_worksize] = df.apply(str_column, args=("local_worksize",), axis=1)
    df['hw_groups'] = df.apply(group_hardware, axis=1)
    df = df.loc[df['local_worksize']<64]
    PLOTS_PATH = parser.args.res_path+"plots/"
    _ = mkdir(PLOTS_PATH)

    print("Plotting cycle core grouped stripcharts...")
    PLOTS_SUB_PATH = PLOTS_PATH + "coreBased_cycleOrdered/"
    _ = mkdir(PLOTS_SUB_PATH)
    for i in list(df['cores'].unique()):
        child_df = df.loc[df['cores']==i]
        for j in list(child_df['workload_size'].unique()):
            ws_child_df = child_df.loc[child_df['workload_size']==j]
            cycle_ordered_df    = ws_child_df.sort_values(by = "local_worksize")
            PLOT_NAME = PLOTS_SUB_PATH + "core{}_coreCycle_ws{}.pdf".format(i, j)
            if not os.path.isfile(PLOT_NAME) : gen_strip_marker(df=cycle_ordered_df,
                                                         x="threads",
                                                         y="cycles",
                                                         color=string_local_worksize,
                                                         marker="warps",
                                                         path=PLOT_NAME,
                                                         palette="rocket")
    print("Plotting instr core grouped stripcharts...")
    PLOTS_SUB_PATH = PLOTS_PATH + "coreBased_instrOrdered/"
    _ = mkdir(PLOTS_SUB_PATH)
    for i in list(df['cores'].unique()):
        child_df = df.loc[df['cores']==i]
        for j in list(child_df['workload_size'].unique()):
            ws_child_df = child_df.loc[child_df['workload_size']==j]
            cycle_ordered_df    = ws_child_df.sort_values(by = "local_worksize")
            PLOT_NAME = PLOTS_SUB_PATH + "core{}_coreInstr_ws{}.pdf".format(i, j)
            if not os.path.isfile(PLOT_NAME) : gen_strip_marker(df=cycle_ordered_df,
                                                         x="threads",
                                                         y="instrs",
                                                         color=string_local_worksize,
                                                         marker="warps",
                                                         path=PLOT_NAME,
                                                         palette="rocket")    

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])