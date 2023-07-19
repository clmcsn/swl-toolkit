import os

from util.parser import ScriptsParserClass
from util.launch_util import mkdir, cmd
from inputs.template import templateDict
from plots.bar import gen_bar, gen_dualbar
import pandas as pd

class DataAnalysisParserClass(ScriptsParserClass):
    def __init__(self, args):
        super(DataAnalysisParserClass, self).__init__(args)
    def init_parser(self):
        self.parser.add_argument("-p", "--res_path", action="store", type=str, help="Result path")
        self.parser.add_argument("-c", "--clean", action="store_true", help="Remove plot directory")
    def set_defaults(self):
        self.parser.set_defaults(res_path=None)
    def check_args(self):
        if not os.path.isdir(self.args.res_path): raise FileNotFoundError("{} directory doesn't exixst".format(self.args.res_path))
    def reduce_args(self):
        if self.args.clean: cmd("rm -rf".format(self.args.res_path+"plots/"))

def group_experiment(x):
    r = x["cores"]*x["warps"]*x["threads"]
    return r

def gen_bar_name(df_line, param_list, template, separator="_"):
    try:
        l = []
        for p in param_list:
            l.append(template[p].format(**{p:df_line[p]}))
        return separator.join(l)
    except Exception as e: print(e)

def main(args, dfname="dataframe.csv"):
    parser = DataAnalysisParserClass(args)

    print("Loading dataframe...")
    DF_NAME = parser.args.res_path + "dataframe.csv"
    df = pd.read_csv(DF_NAME)
    df['groups'] = df.apply(group_experiment, axis=1)
    PLOTS_PATH = parser.args.res_path+"plots/"
    _ = mkdir(PLOTS_PATH)
    
    print("Plotting hardware grouped barcharts...")
    PLOTS_SUB_PATH = PLOTS_PATH + "hwBased_cycleOrdered/"
    _ = mkdir(PLOTS_SUB_PATH)
    for i in list(df['groups'].unique()):
        child_df = df.loc[df['groups']==i]
        cycle_ordered_df    = child_df.sort_values(by = 'cycles')
        #lw_ordered_df       = child_df.sort_values(by = 'local_worksize')
        cycle_ordered_df["bar_name"] = cycle_ordered_df.apply(  gen_bar_name, 
                                                                param_list=['cores', 'warps', 'threads', 'local_worksize'],
                                                                template = templateDict[child_df["app"].iloc[0]].STR,  #iloc pics one index... they will be all the same, so I pick just a random one
                                                                axis=1)
        PLOT_NAME = PLOTS_SUB_PATH + "cycle_ordered_hw{}.pdf".format(i)
        if not os.path.isfile(PLOT_NAME) : gen_bar(df=cycle_ordered_df, 
                                                    height='cycles', 
                                                    bar_names='bar_name', 
                                                    path=PLOT_NAME,
                                                    size = (16,10))

    print("Plotting min-max barchart...")
    PLOTS_SUB_PATH = PLOTS_PATH + "hwBased_minMaxCycles/"
    _ = mkdir(PLOTS_SUB_PATH)
    l = []
    for i in list(df['groups'].unique()):
        child_df = df.loc[df['groups']==i]
        m = child_df.min(axis=0)['cycles']
        M = child_df.max(axis=0)['cycles']
        l.append({'hw':i, 'min':m, 'max':M})
    hw_mM_df = pd.DataFrame(l)
    PLOT_NAME = PLOTS_SUB_PATH + "hwBased_MinMax_cycles.pdf"
    if not os.path.isfile(PLOT_NAME) : gen_dualbar(df=hw_mM_df, 
                                                    h1='max',
                                                    h2='min',
                                                    bar_names='hw', 
                                                    path=PLOT_NAME,
                                                    size = (16,10))
    
    print("Plotting core grouped barcharts...")
    PLOTS_SUB_PATH = PLOTS_PATH + "coreBased_cyclesOrdered/"
    _ = mkdir(PLOTS_SUB_PATH)
    for i in list(df['cores'].unique()):
        child_df = df.loc[df['cores']==i]
        cycle_ordered_df    = child_df.sort_values(by = 'cycles')
        cycle_ordered_df["bar_name"] = cycle_ordered_df.apply(  gen_bar_name, 
                                                                param_list=['warps', 'threads', 'local_worksize'],
                                                                template = templateDict[child_df["app"].iloc[0]].STR,
                                                                axis=1)
        PLOT_NAME = PLOTS_SUB_PATH + "core{}_coreCycle.pdf".format(i)
        if not os.path.isfile(PLOT_NAME) : gen_bar(df=cycle_ordered_df, 
                                                    height='cycles', 
                                                    bar_names='bar_name', 
                                                    path=PLOT_NAME,
                                                    size = (25,10))
    
    print("Plotting core - warps grouped barcharts...")
    PLOTS_SUB_PATH = PLOTS_PATH + "coreWarpsBased_cyclesOrdered/"
    _ = mkdir(PLOTS_SUB_PATH)
    for i in list(df['cores'].unique()):
        PLOTS_SUBSUB_PATH = PLOTS_SUB_PATH + "core{}/".format(i)
        _ = mkdir(PLOTS_SUBSUB_PATH)
        c_df = df.loc[df['cores']==i]
        for j in list(c_df['warps'].unique()):
            child_df = c_df.loc[c_df['warps']==j]
            cycle_ordered_df    = child_df.sort_values(by = 'cycles')
            cycle_ordered_df["bar_name"] = cycle_ordered_df.apply(  gen_bar_name, 
                                                                    param_list=['threads', 'local_worksize'],
                                                                    template = templateDict[child_df["app"].iloc[0]].STR, 
                                                                    axis=1)
            PLOT_NAME = PLOTS_SUBSUB_PATH + "core{}_warps{}_Cycle.pdf".format(i,j)
            if not os.path.isfile(PLOT_NAME) : gen_bar(df=cycle_ordered_df, 
                                                        height='cycles', 
                                                        bar_names='bar_name', 
                                                        path=PLOT_NAME,
                                                        size = (16,10))

    print("Plotting core - local worksize grouped barcharts...")
    PLOTS_SUB_PATH = PLOTS_PATH + "coreLworksizeBased_cyclesOrdered/"
    _ = mkdir(PLOTS_SUB_PATH)
    for i in list(df['cores'].unique()):
        PLOTS_SUBSUB_PATH = PLOTS_SUB_PATH + "core{}/".format(i)
        _ = mkdir(PLOTS_SUBSUB_PATH)
        c_df = df.loc[df['cores']==i]
        for j in list(c_df['local_worksize'].unique()):
            child_df = c_df.loc[c_df['local_worksize']==j]
            cycle_ordered_df    = child_df.sort_values(by = 'cycles')
            cycle_ordered_df["bar_name"] = cycle_ordered_df.apply(  gen_bar_name, 
                                                                    param_list=['warps', 'threads', 'groups'],
                                                                    template = templateDict[child_df["app"].iloc[0]].STR, 
                                                                    axis=1)
            PLOT_NAME = PLOTS_SUBSUB_PATH + "core{}_lw{}_Cycle.pdf".format(i,j)
            if not os.path.isfile(PLOT_NAME) : gen_bar(df=cycle_ordered_df, 
                                                        height='cycles', 
                                                        bar_names='bar_name', 
                                                        path=PLOT_NAME,
                                                        size = (16,10))

    print("Plotting core - warps grouped barcharts...")
    PLOTS_SUB_PATH = PLOTS_PATH + "coreWarpsBased_lworksizeOrdered/"
    _ = mkdir(PLOTS_SUB_PATH)
    for i in list(df['cores'].unique()):
        PLOTS_SUBSUB_PATH = PLOTS_SUB_PATH + "core{}/".format(i)
        _ = mkdir(PLOTS_SUBSUB_PATH)
        c_df = df.loc[df['cores']==i]
        for j in list(c_df['warps'].unique()):
            child_df = c_df.loc[c_df['warps']==j]
            cycle_ordered_df    = child_df.sort_values(by = 'local_worksize')
            cycle_ordered_df["bar_name"] = cycle_ordered_df.apply(  gen_bar_name, 
                                                                    param_list=['threads', 'local_worksize'],
                                                                    template = templateDict[child_df["app"].iloc[0]].STR, 
                                                                    axis=1)
            PLOT_NAME = PLOTS_SUBSUB_PATH + "core{}_warps{}_Cycle.pdf".format(i,j)
            if not os.path.isfile(PLOT_NAME) : gen_bar(df=cycle_ordered_df, 
                                                        height='cycles', 
                                                        bar_names='bar_name', 
                                                        path=PLOT_NAME,
                                                        size = (16,10))


    
if __name__ == '__main__':
    import sys
    main(sys.argv[1:])