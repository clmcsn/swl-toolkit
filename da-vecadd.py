import os
import pandas as pd
import numpy as np
import math

import util.parsers as parsers
import util.os_utils as osu
import inputs.template as template

import plots.strip as plots_s
import plots.line as plots_l
import plots.utils as plots_u

def log_column(x, col):
    r=math.log(x[col],2)
    return r

def group_hardware(x):
    r = x["clusters"]*x["cores"]*x["warps"]*x["threads"]
    return r

def main(args, dfname="dataframe.feather"):
    parser  = parsers.DataAnalysisParserClass(args)
    print("Loading dataframe...")
    DF_NAME = parser.args.res_path + dfname
    PLOTS_PATH = parser.args.res_path+"plots/"
    df = pd.read_feather(DF_NAME)
    # apply da metadata to dataframe
    df = df.loc[df['workload_size']>2000]
    C = [2 for _ in range(len(df))]
    df['clusters'] = C
    df['hw_groups'] = df.apply(group_hardware, axis=1)
    df['cycles_log'] = df.apply(log_column, args=("cycles",), axis=1)
    df['lw_log'] = df.apply(log_column, args=("local_worksize",), axis=1)
    df['instrs_log'] = df.apply(log_column, args=("instrs",), axis=1)
    print("Plotting cycle and IPC core grouped strip charts...")
    PLOTS_SUB_PATH = PLOTS_PATH + "core_ws_perf/"
    _ = osu.mkdir(PLOTS_SUB_PATH)
    for i in list(df['cores'].unique()):
        child_df = df.loc[df['cores']==i]
        C = child_df['clusters'].unique().tolist()[0]
        w = child_df['warps'].unique().tolist()[0]
        t = child_df['threads'].unique().tolist()[0]
        #Reports
        wss = child_df['workload_size'].unique().tolist()
        wss.sort()
        best_ls = []
        best_cycles = []
        best_teor_ls = []
        actual_cycles = []
        penalty = []
        for s in wss:
            #print(child_df.loc[child_df['workload_size']==32768].sort_values(by = "local_worksize"))
            #exit()
            best_cycles.append(child_df.loc[child_df['workload_size']==s]['cycles'].min())
            best_ls.append(child_df.loc[(child_df['workload_size']==s) & (child_df['cycles']==best_cycles[-1])]['local_worksize'].values)
            r = math.ceil(s/(C*i*w*t))
            best_teor_ls.append(r)
            actual_cycles.append(child_df.loc[(child_df['workload_size']==s) & (child_df['local_worksize']==best_teor_ls[-1])]['cycles'].values)
            penalty.append(np.round(((actual_cycles[-1] - best_cycles[-1])/best_cycles[-1]*100),decimals=1))
        for k in range(len(wss)):
            print("CORES:{} - Best local worksize for workload size {} is {} (theoretical: {})".format(i, wss[k], best_ls[k], best_teor_ls[k]))
            print("---------- Actual cycles for workload size {} is {} (theoretical: {})".format(wss[k], best_cycles[k], actual_cycles[k]))
            print("---------- Penalty for workload size {} is {}".format(wss[k], penalty[k]))

        line_df = child_df.pivot("local_worksize", "workload_size", "cycles")
        dots_df = pd.DataFrame()
        for k in range(len(wss)):
            d = pd.DataFrame({"local_worksize": best_teor_ls[k], "workload_size": wss[k], "cycles": actual_cycles[k]})
            dots_df = pd.concat([dots_df,d], ignore_index=True)
        dots_df = dots_df.pivot("local_worksize", "workload_size", "cycles")
        PLOT_NAME = PLOTS_SUB_PATH + "core{}_coreCycle_ws.svg".format(i)
        if not os.path.isfile(PLOT_NAME) : plots_l.gen_lineplot_dots(   df=line_df,
                                                                        dots=dots_df,
                                                                        x=5,
                                                                        y=6,
                                                                        #x="local_worksize",
                                                                        #y="cycles_log",
                                                                        #color="workload_size",
                                                                        #aspect=1.5,
                                                                        path=PLOT_NAME,
                                                                        palette="rocket")
        PLOT_NAME = PLOTS_SUB_PATH + "core{}_coreInstructions_ws.svg".format(i)
        #Reports
        actual_instr = []
        for k in range(len(wss)):
            actual_instr.append(child_df.loc[(child_df['workload_size']==wss[k]) & (child_df['local_worksize']==best_teor_ls[k])]['instrs'].values)
        line_df = child_df.pivot("local_worksize", "workload_size", "instrs")
        dots_df = pd.DataFrame()
        for k in range(len(wss)):
            d = pd.DataFrame({"local_worksize": best_teor_ls[k], "workload_size": wss[k], "instrs": actual_instr[k]})
            dots_df = pd.concat([dots_df,d], ignore_index=True)
        dots_df = dots_df.pivot("local_worksize", "workload_size", "instrs")
        if not os.path.isfile(PLOT_NAME) : plots_l.gen_lineplot_dots(   df=line_df,
                                                                        dots=dots_df,
                                                                        x=5,
                                                                        y=6,
                                                                        #x="local_worksize",
                                                                        #y="cycles_log",
                                                                        #color="workload_size",
                                                                        #aspect=1.5,
                                                                        path=PLOT_NAME,
                                                                        palette="rocket")
if __name__ == '__main__':
    import sys
    main(sys.argv[1:])