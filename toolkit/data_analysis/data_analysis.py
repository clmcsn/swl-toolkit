import os
import yaml
import pandas as pd
from typing import OrderedDict

from . import vortex_da_utils as vda
from . import utils
from .. import stream_parsing as sp
from ..util import os_utils as osu
from ..plots.trace import gen_trace_analysis, gen_time_traces
from ..plots.bar import gen_bar
from ..plots.violin import violin_plot

#TODO: 
#   - Keep track of the faulty reports in a separate df

"""
Data analysis toolkit for research experiments.
Main classes:
    DataExtractionClass: class to extract data from text experiment report.
        generic class. Methods can be inerhited and overloaded. See below for more details.
Derived classes:
    VortexPerfExtractionClass: class to extract data from Vortex performance experiment report.
        specific to vortex performance experiment reports.
    VortexTraceAnalysisClass: class to extract data from Vortex trace.
        specific to vortex trace sintax. --> obtained with stream_parsing
    VortexTracePostProcessingClass: class to reduce the data extracted from multiple experiment reports (e.g. summing performances).
        specific to vortex performance experiment reports.
    VortexComparativeAnalysisClass: class to compare the data obtained from different experiment reports (e.g. with different methodologies).
        specific to vortex performance experiment reports. Could be generalized.
"""

class DataExtractionClass():
    """
    Class to extract data from text experiment report.
    e.g.: experiment_cmd > experiment_report.txt 2>&1
                            └── extract from this file!
    Methods:
        Fixed:
            extract:
                Main method to extract data and/or inplace process the experiment result file.
                Fixed but can be overloaded.
                For every file in the path,  matching the fault_checker conditions, it:
                    1. calls the inplace_process method
                    2. calls the extracton_func method
                Finally can perform a post_extraction_func method. 
            dump_dataframe: generate feather file from extracted data.
            is_exp_faulty: check if the experiment report is faulty, applying functions from the fault_checkers list.

    Attributes:
        path (str): path to the directory where the experiment reports are stored.
        app (str): Mandatory. Application name (e.g. vecadd).
        raw_subdir (str): subdirectory where the experiment reports are stored. main directory is self.path. Default: "raw/".
        inplace_only (bool): if True, it only performs the inplace_process method. Default: False.
        yml_file (str): path to the yaml file containing the list of experiment reports to process. Default: "".

        file_list (list): list of experiment reports to process. Can be obtained automatically from the raw_subdir or from the yml_file.
        extracton_func (function): function to extract data from text experiment report.
        inplace_process (function): function to process the experiment report inplace.
        fault_checkers (list): list of functions to check if the experiment report is faulty.
        fault_handler (function): function to handle faulty experiment reports (what to do if a faulty experiment is detected).
        post_extraction_func (function): function to perform after the extraction process. (e.g. plotting or saving the extracted data)
        df (pandas.DataFrame): dataframe to store extracted data.
    """
    def __init__(self, path, app, raw_subdir="raw/", inplace_only=False, yml_file=""):
        #paths
        self.path = path if path[-1]=="/" else path + "/"
        self.raw_subdir = self.path + raw_subdir
        self.checkpoint_path = self.path + "checkpoint.feather"
        self.output_dataframe_path = self.path + "dataframe.feather"

        #base attributes
        self.app = app
        self.inplace_only = inplace_only
        self.yml_file = yml_file

        #reducing attributes
        self.file_list = []
        if os.path.isfile(self.yml_file):
            yml = yaml.load(open(self.yml_file, "r"), Loader=yaml.FullLoader)
            self.file_list = yml["obj_list"]
            self.file_list = [os.path.join(self.path, x) for x in self.file_list]
        else:
            self.file_list = [os.path.join(self.raw_subdir, x) for x in os.listdir(self.raw_subdir)]
        
        #members to be overloaded
        self.extracton_func = self.dummy_extraction
        self.inplace_process = self.dummy_inplace_process
        self.fault_checkers = []
        self.fault_handler = self.dummy_fault_handler
        self.post_extraction_func = self.dummy_post_extraction

        #data structures
        self.df = pd.DataFrame({})

    @staticmethod
    def dummy_fault_handler(fpath):
        pass

    @staticmethod
    def dummy_inplace_process(fpath):
        pass

    @staticmethod
    def dummy_extraction(fpath):
        return pd.DataFrame({})
    
    @staticmethod
    def dummy_post_extraction():
        pass
    
    def is_exp_faulty(self,fpath):
        for func in self.fault_checkers:
            ret = func(fpath)
            if ret: return ret
        return 0

    def extract(self):
        """
        Extract data from text experiment report.
        Loops over all the files in the path, matching the fault_checker conditions, and:
            1. calls the inplace_process method
            2. calls the extracton_func method
        If inplace_only is False, it concatenates the extracted dataframes.
        If a checkpoint file is present, it merges the extracted dataframe with the checkpoint dataframe.
            (the checkpoint dataframe is generated while executing the actual experiments)
        Finally can perform a post_extraction_func method.
        Notes:
        """
        #iterate over all files in the directory
        for f in self.file_list:
            r = self.is_exp_faulty(f)
            if r: 
                self.fault_handler(f)
                continue
            self.inplace_process(f)
            if (not self.inplace_only): self.df = pd.concat([self.df, self.extracton_func(f)], ignore_index=True)
        if (not self.inplace_only):
            try:
                if os.path.isfile(self.checkpoint_path):
                        self.df = pd.merge(self.df, pd.read_feather(self.checkpoint_path), on="ID")
                        print("Added experiment metadata to dataframe.")
                else: raise Exception("Checkpoint file not found.")
            except Exception as e: print("WARNING: {}".format(e))
            self.dump_dataframe()
        self.post_extraction_func()
    
    def dump_dataframe(self):
        if os.path.isfile(self.output_dataframe_path):
            print("Dataframe already present...")
            osu.make_backup(self.output_dataframe_path)
        self.df.to_feather(self.output_dataframe_path)

class VortexPerfExtractionClass(DataExtractionClass):
    """
    Class to extract data from Vortex performance experiment report.
    Overrides the DataExtractionClass methods.
    List of methods overriden:
        extracton_func -> vda.gen_df_from_log extracts the dataframe from the text experiment report.
        fault_checkers -> [self.check_faults_by_string] checks if the experiment report is faulty by searching if a list of strings is present in the file.
        fault_handlers -> vda.vortex_fault_handler handles faulty experiment reports.
        post_extraction_func -> self.add_extraction_feedback_to_checkpoint adds extraction metadata to the checkpoint file (e.g., info if some experiments need to be repeated).
    """
    def __init__(self,path,app):
        super(VortexPerfExtractionClass, self).__init__(    path=path,
                                                            app=app)
        self.extracton_func = vda.gen_df_from_log
        self.fault_checkers = [self.check_faults_by_string]
        self.fault_handlers = vda.vortex_fault_handler
        self.post_extraction_func = self.add_extraction_feedback_to_checkpoint

    def add_extraction_feedback_to_checkpoint(self):
        """
        Add extraction metadata to the checkpoint file.
        e.g., if one experiment had problems, marks it as faulty and needs to be repeated.
        """
        experiments_df = pd.read_feather(self.checkpoint_path)
        bad_df = self.df[self.df.isnull().any(axis=1)]
        if bad_df.empty:  print("No faulty experiments found!"); return
        
        #Handle faulty experiments
        print("Bad experiments: {}".format(len(bad_df.index)))
        bad_IDs = bad_df["ID"].values
        experiments_df.loc[experiments_df["ID"].isin(bad_IDs),"Status"] = 0
        experiments_df.loc[experiments_df["ID"].isin(bad_IDs),"Return"] = None
        osu.make_backup(self.checkpoint_path)
        experiments_df.to_feather(self.checkpoint_path)

    @staticmethod
    def check_faults_by_string(fpath, fault_str=["INVALID EXPERIMENT"]):
        """
        Check if the experiment report is faulty.
        Args:
            fpath (str): path to the experiment report.
        Returns:
            bool: True if the experiment report is faulty, False otherwise.
        """
        with open(fpath, "r") as f:
            for line in f:
                if any([x in line for x in fault_str]) : return 1
        return 0

class VortexTraceAnalysisClass(DataExtractionClass):
    """
    Class to analyze data from Vortex trace.
    List of methods overriden:
        extracton_func -> does not extract data from the text experiment report.
        fault_checkers -> [self.is_not_db, self.check_empty_database, self.check_coherent_assembly] checks if the experiment report is faulty.
        inplace_process -> self.trace_analysis performs the actual analysis.

    """
    def __init__(self,path,app,yml_file=""):
        """
        Class to extract data from Vortex trace.
        Args:
            path (str): path to the directory where the experiment dataframes (obtained with stream_parsing) are stored.
            app (str): Mandatory. Application name (e.g. vecadd).
        """
        super(VortexTraceAnalysisClass, self).__init__( path=path,
                                                        app=app,
                                                        inplace_only=True)
        
        self.yml_file = yml_file

        #Making default yml file
        input_path = os.getcwd() + "/inputs/kernels_assembly/" + self.app + "/" 
        self.configs = {"synth_pivot": "func",
                        "kernel_key" : "",
                        "dotdump_path": input_path + self.app + ".dump",
                        "code_sections_path": input_path + "sections.yml",
                        "plot": "",
                        "overhead_key": "",
                        "zoomed_plot_keys": [],
                        "sections_to_drop": [],
                        "roofline_tag": ""}

        if self.yml_file:
            if os.path.isfile(self.yml_file): 
                self.configs = yaml.load(open(self.yml_file, "r"), Loader=yaml.FullLoader)

        #Getting the PC tag section map and the dotdump path
        self.ref_code_df = self.gen_ref_code_df()
        self.iter_ref_code_df = pd.DataFrame({})

        self.code_sections = self.gen_code_map(self.configs["code_sections_path"])

        #Setting up the class functions
        self.extracton_func = self.dummy_extraction
        self.inplace_process = self.trace_analysis
        self.fault_checkers = [self.is_not_db, self.check_empty_database, self.check_coherent_assembly]

        #Initializing the class members
        self.iter_df = pd.DataFrame({})
        self.iter_fname = "" 

    def gen_ref_code_df(self):
        if self.configs["kernel_key"]:
            ret = {}
            for k in self.configs["dotdump_path"].keys():
                if not os.path.isfile(self.configs["dotdump_path"][k]): raise Exception("Dotdump file {} not found!".format(self.configs["dotdump_path"][k]))
                ret[k] = sp.DotDumpRISCVParsingClass(  output_path=self.path,
                                                        dump_file=self.configs["dotdump_path"][k]).get_df()
        else:
            if not os.path.isfile(self.configs["dotdump_path"]): raise Exception("Dotdump file not found!")
            ret = sp.DotDumpRISCVParsingClass(  output_path=self.path,
                                                dump_file=self.configs["dotdump_path"]).get_df()
        return ret

    # ------------------------ FAULT CHECKERS ------------------- #
    @staticmethod
    def is_not_db(fpath):
        if fpath[-8:] == ".feather": return False
        else: return True

    def check_empty_database(self, fpath):
        print("Checking database...")
        r = False
        try:
            self.iter_df = pd.read_feather(fpath)
        except:
            r = True
        if self.iter_df.empty: r = True
        else: r = False
        if not r: 
            self.iter_fname = fpath
            print("Database looks OK!")
        else: print("Database is empty!")
        return r

    def check_coherent_assembly(self, fpath):
        """
        Check if the assembly is coherent with the code sections map file.
        This needs to be written by hand to tag PCs with the corresponding code section.
        """
        def get_ref_code_df(ref_code_df, fpath):
            if type(ref_code_df) == dict:
                for k in ref_code_df.keys():
                    if "_"+k+"_" in fpath: return ref_code_df[k]
            else: return ref_code_df

        r = False
        self.iter_ref_code_df = get_ref_code_df(self.ref_code_df, fpath)
        print("Checking assembly coherence...")
        instr_df = self.iter_df[['PC-id','instr']]
        if not instr_df.isin(iter_ref_code_df).all().all(): r = False
        else: r = True
        if not r: print("Assembly looks OK!")
        else: print("ERROR: Assembly is not coherent!")
        return r

    # ---------------------------------------------------------- #
    # ------------------------ PLOTS --------------------------- #

    @staticmethod
    def plot_complete_trace(sdf,df, path, ID, sections_key, sections=[]):
        _ = osu.cmd("mkdir -p {}".format(path + "plots/"))
        for c in list(df["core"].unique()):
            if not sections: sections = list(df[sections_key].unique()) 
            child_df = df.loc[(df["core"]==c) & (df[sections_key].isin(sections))]   #["workload_distr","kernel_call_init","kernel_call_init_inner","kernel"]))]
            child_sdf = sdf.loc[(sdf["core"]==c) & (sdf[sections_key].isin(sections))]   #["workload_distr","kernel_call_init","kernel_call_init_inner","kernel"]))]
            if child_df.empty: continue
            gen_trace_analysis( df=child_df ,synthetic_df=child_sdf, traces_col_name=sections_key, 
                                period_col_name="total-exec-time", start_col_name="schedule-stmp", 
                                path=path + "plots/{}_c{}.svg".format(ID,c))
        

    @staticmethod
    def plot_time_traces(df, path, ID, section_key, sections=[]):
        _ = osu.cmd("mkdir -p {}".format(path + "plots/"))
        for c in list(df["core"].unique()):
            child_df = df.loc[(df["core"]==c) & (df[section_key].isin(sections))]   #["workload_distr","kernel_call_init","kernel_call_init_inner","kernel"]))]
            if child_df.empty: continue
            gen_time_traces(    df=child_df, traces_col_name=section_key, 
                                period_col_name="total-exec-time", start_col_name="schedule-stmp", 
                                path=path + "plots/{}_CORE{}.svg".format(ID,c))

    # ---------------------------------------------------------- #
    # ---------------------------- UTILS ----------------------- #

    @staticmethod
    def get_exec_count(x):
        return x["tmask"].count("1")        

    @staticmethod
    def extract_last_cycle(df):
        df["end"] = df["schedule-stmp"].add(df["total-exec-time"])
        last_cycle = df["end"].max()
        return last_cycle

    @staticmethod
    def extract_section_execution_time(df, section_name, section_value):
        child_df = df.loc[df[section_name]==section_value]
        total = child_df["total-exec-time"].sum()
        return int(total)

    @staticmethod
    def extract_section_instruction_count(df, section_name, section_value):
        child_df = df.loc[df[section_name]==section_value]
        total = child_df["event_count"].sum()
        return int(total)
    
    @staticmethod
    def extract_section_thread_instruction_count(df, section_name, section_value):
        child_df = df.loc[df[section_name]==section_value]
        total = child_df["thread_event_count"].sum()
        return int(total)

    @staticmethod
    def extract_info_dict(df, over, overhead_key=""):
        info = {}
        info["last-commit"] = int(VortexTraceAnalysisClass.extract_last_cycle(df))
        d = {}
        de = {}
        dte = {}
        for s in df[over].unique():
            d[s] = VortexTraceAnalysisClass.extract_section_execution_time(df, section_name=over, section_value=s)
            de[s] = VortexTraceAnalysisClass.extract_section_instruction_count(df, section_name=over, section_value=s)
            dte[s] = VortexTraceAnalysisClass.extract_section_thread_instruction_count(df, section_name=over, section_value=s)
        info["section-exec-time"] = d
        info["section-exec-count"] = de
        info["section-thread-exec-count"] = dte
        info["total-exec-count"] = int(df["event_count"].sum())
        info["total-thread-exec-count"] = int(df["thread_event_count"].sum())
        if overhead_key: info["overhead"] = float((info["last-commit"] - info["section-exec-time"][overhead_key]*info["section-exec-count"][overhead_key]/info["section-thread-exec-count"][overhead_key]) / info["last-commit"] * 100)
        return info
    
    @staticmethod
    def gen_code_map(code_sections_fname: str) -> dict:
        """
        Generate a code map (lookup table) from a yaml file.
        Args:
            code_sections_fname (str): path to the yaml file containing the code sections.
        Returns:
            dict: code map. Dictionary with keys = code instruction PC names and values = list of code section addresses.
        """
        if not os.path.isfile(code_sections_fname):
            print("Code sections file not found!")
            return {}
        
        code_sections = yaml.load(open(code_sections_fname, "r"), Loader=yaml.FullLoader)
        code_map = {}
        #Generating a list of PC addresses for each code section
        for s in code_sections.keys():
            code_map[s] = []
            for e in code_sections[s]:
                if type(e) == int: code_map[s].append(e)
                elif type(e) == list: code_map[s].extend(e)
                elif type(e) == str: 
                    ee = e.split(":")
                    code_map[s].extend(range(int(ee[0],base=16),int(ee[1],base=16)+1,4))
        
        #Generating program boundaries
        vmin = 0x80000000
        vmax = vmin
        for s in code_map.keys():
            vmax = max(vmax, max(code_map[s])) #getting the max value of the code map

        #Generating the reverse code map -> key = PC address, value = code section name
        ret_code_map = {}
        for i in range(vmin,vmax+1):
            for s in code_map.keys():
                if i in code_map[s]:
                    ret_code_map[i] = s
                    break
        return ret_code_map
    
    @staticmethod
    def gen_func_code_map(dot_dump_fname: str) -> pd.DataFrame:
        return sp.DotDumpRISCVParsingClass(  output_path="", 
                                                dump_file=dot_dump_fname).get_df()


# ----------------------------------------------------------- #
# ------------------------ MAIN FUNCTIONS ------------------- #

    @staticmethod
    def make_synthesis(df: pd.DataFrame, df_ID: str, configs: dict, path: str ="") -> pd.DataFrame:
        print("Total number of events {}: {}".format(df_ID,len(df)))

        #Generating the synthesis dataframe
        over = configs["synth_pivot"]
        overhead_key = configs["overhead_key"]
        plot = configs["plot"]
        zoomed_plot_keys = configs["zoomed_plot_keys"]

        synthesis_df = pd.DataFrame({})
        for c in list(df["core"].unique()):
            for s in list(df[over].unique()):
                child_df = df.loc[(df["core"]==c) & (df[over]==s)]
                if child_df.empty: continue
                #extracting the fused events
                events = utils.TimeSeriesClass( ID="{}_{}".format(c,s),
                                                events=child_df,
                                                period_col_name="total-exec-time",
                                                start_col_name="schedule-stmp").make_synthesis()
                events_len = len(events)
                events["core"] = [c]*events_len
                events[over] = [s]*events_len
                synthesis_df = pd.concat([synthesis_df, events], ignore_index=True)

        if path:
            print("Saving synthesis dataframe:{}".format(path))
            synthesis_df.to_feather(path+df_ID+".feather")
            yaml.dump(VortexTraceAnalysisClass.extract_info_dict(synthesis_df, over, overhead_key), open(path+df_ID+".yml", "w"))
            if plot:
                print("Generating synthesis plot:{}".format(path))
                #sdf,df, path, ID, sections=[]):
                if plot=='complete':
                    VortexTraceAnalysisClass.plot_complete_trace(  sdf=synthesis_df, df=df, 
                                                                        path=path, ID= df_ID, sections_key=over)
                    if zoomed_plot_keys: VortexTraceAnalysisClass.plot_complete_trace(  sdf=synthesis_df, df=df, 
                                                                                        path=path, ID=df_ID+"_ZOOM",
                                                                                        sections_key=over, 
                                                                                        sections=zoomed_plot_keys)
                elif plot=='time':
                    VortexTraceAnalysisClass.plot_time_traces(  df=synthesis_df, 
                                                                        path=path, ID=df_ID)
                    VortexTraceAnalysisClass.plot_time_traces(  df=synthesis_df, 
                                                                        path=path, ID=df_ID+"_ZOOM", 
                                                                        sections=["workload_distr","kernel_call_init","kernel_call_init_inner","kernel","kernel_loops_bookkeeping","kernel_memory_addressing"])
        return synthesis_df

    @staticmethod
    def make_roofline(df, df_ID, configs, path="", plot=False):
        sections_to_drop = configs["sections_to_drop"]
        over = configs["synth_pivot"]

        roofline_df = pd.DataFrame({})
        for c in list(df["core"].unique()):
            for w in list(df["warp"].unique()):
                child_df = df.loc[(df["core"]==c) & (df["warp"]==w)]
                saved_time = 0
                child_df = child_df.sort_values(by="eID")
                child_df.reset_index(drop=True, inplace=True)
                iterations = len(child_df)
                for i in range(iterations):
                    if child_df.loc[i][over] in sections_to_drop:
                        # need to avoid the last iteration
                        if i!=iterations-1: saved_time += child_df.loc[i+1]["schedule-stmp"] - child_df.loc[i]["schedule-stmp"]
                        child_df = child_df.drop(i)
                    else:
                        child_df.loc[i, "schedule-stmp"] = child_df.loc[i]["schedule-stmp"] - saved_time
                        #time = child_df.loc[i]["schedule-stmp"]
                elen = len(child_df)
                child_df["core"] = [c]*elen
                child_df["warp"] = [w]*elen
                roofline_df = pd.concat([roofline_df, child_df], ignore_index=True)
        if path:
            roofline_df.to_feather(path+df_ID+".feather")
            VortexTraceAnalysisClass.make_synthesis(roofline_df, df_ID, configs, path)

    def trace_analysis(self, fpath):
        del fpath #not used

        #Preprocessing the dataframe self.iter_df
        #----------Add code sections
        def get_code_section(x):
            try:
                return self.code_sections[x["PC"]]
            except:
                return "fini"
        if self.code_sections: self.iter_df["code_section"]    = self.iter_df.apply(get_code_section, axis=1)
        #----------Add function names
        self.iter_df = pd.merge(self.iter_df, self.iter_ref_code_df.drop("instr",axis=1), on="PC-id", how="left")
        #----------Add active threads
        self.iter_df["e_count"]         = self.iter_df.apply(self.get_exec_count, axis=1)

        #Making the analysis result path
        stripped_df_name = self.iter_fname.split("/")[-1].split(".")[0]
        output_path = self.path + stripped_df_name + "/"
        _ = osu.cmd("mkdir -p {}".format(output_path))

        #Generating the synthesis dataframe
        self.make_synthesis(self.iter_df, 
                            df_ID=stripped_df_name+"-SYN",
                            path=output_path,
                            configs=self.configs)
        if self.configs["sections_to_drop"]: self.make_roofline(self.iter_df,
                                                                df_ID=stripped_df_name+self.configs["roofline_tag"],
                                                                path=output_path,
                                                                configs=self.configs["sections_to_drop"])
        

class VortexTracePostProcessingClass(DataExtractionClass):
    """
    Class to post process the trace analysis data.
    VortexTraceAnalysisClass needs to be run before to do the inplace analysis.
    List of methods overriden:
        extracton_func -> self.trace_postprocessing extracts the informations from the yml file produced by the VortexTraceAnalysisClass.
        fault_checkers -> [self.is_not_exp_dir] checks if the directory is an experiment directory.
        post_extraction_func -> self.post_extraction plots the extracted data.
    """
    def __init__(self,path,app):
        super(VortexTracePostProcessingClass, self).__init__(   path=path,
                                                                app=app,
                                                                raw_subdir="")
        self.extracton_func = self.trace_postprocessing
        self.post_extraction_func = self.post_extraction
        self.fault_checkers = [self.is_not_exp_dir]

    @staticmethod
    def is_not_exp_dir(fpath):
        if not os.path.isdir(fpath): return True
        if not fpath.split("/")[-1][0].isdigit(): return True
        return False
    
    @staticmethod
    def plot_bars(d, path, df_ID):
        plot_path = path + "/plots/"
        _ = osu.cmd("mkdir -p {}".format(plot_path),verbose=False)
        for k in d["section-exec-time"].keys():
            #Normalizing the execution time by the avg number of threads executing the section
            d["section-exec-time"][k] = d["section-exec-time"][k]/(d["section-thread-exec-count"][k]/d["section-exec-count"][k])
        df = pd.DataFrame(d["section-exec-time"], index=[0])
        df = df.apply(lambda x: x/d["last-commit"]*100, axis=1)
        df = df.melt(var_name="section", value_name="period")
        gen_bar(df, "period", "section", path=plot_path + df_ID + "-section-breakdown.svg")

    def trace_postprocessing(self, fpath):
        files = osu.get_files(fpath, extension=".yml")
        print("Found {} files".format(len(files)))
        df = pd.DataFrame({})
        for f in files:
            print(f)
            ID_string = f.split(".")[0]
            tag = "-".join(ID_string.split("-")[1:])
            with open(fpath+"/"+f, "r") as yf:    d = yaml.load(yf, Loader=yaml.FullLoader)
            VortexTracePostProcessingClass.plot_bars(d, fpath, ID_string)
            #need to drop the break-down dictionaries}
            itd = {"ID": ID_string}
            itd["tag"] = tag if tag else "BASELINE"
            itd["overhead"] = d["overhead"]
            itd["last-commit"] = d["last-commit"]
            itd["total-exec-count"] = d["total-exec-count"]
            itd["total-thread-exec-count"] = d["total-thread-exec-count"]
            df = pd.concat([df, pd.DataFrame(itd,index=[0])], ignore_index=True)
        return df

    def post_extraction(self):
        plot_path = self.path + "/plots/"
        _ = osu.cmd("mkdir -p {}".format(plot_path))
        #print dual bar
        gen_bar(self.df.sort_values(by="ID"), height="last-commit", bar_names="ID", hue="tag", path=plot_path + "savings_cycles.svg", log=True)
        gen_bar(self.df.sort_values(by="ID"), height="total-exec-count", bar_names="ID", hue="tag", path=plot_path + "savings_instr_issue.svg", log=True)
        gen_bar(self.df.sort_values(by="ID"), height="total-thread-exec-count", bar_names="ID", hue="tag", path=plot_path + "savings_instr_exec.svg", log=True)

        for i in list(self.df["tag"].unique()):
            child_df = self.df.loc[self.df["tag"]==i]
            gen_bar(child_df.sort_values(by="ID"), height="overhead", bar_names="ID", path=plot_path + "overhead{}.svg".format("-"+i if i else ""))
        
class VortexExperimentReductionClass(DataExtractionClass):
    """
    Class to reduce the data extracted from the experiment reports.
    Args:
        path (str): path to the directory where the experiment dataframes (obtained with stream_parsing) are stored.
        app (str): Mandatory. Application name (e.g. resnet). Resulting reduced dataframe will have the specified 'app' as tag.

    Attributes:
        aggregated_cols (dict, can be overridden in child class): 
            dictionary with keys = column names and values = aggregation functions.
        derived_cols (dict, can be overridden in child class):
            dictionary with keys = column names and values = functions to derive the column from aggregated ones.
    """
    def __init__(self, path, app, yml_file):
        super(VortexExperimentReductionClass, self).__init__(   path=path,
                                                                app=app,
                                                                raw_subdir="",
                                                                yml_file=yml_file)
        assert os.path.isfile(self.yml_file), "YAML file not found!"
        yml = yaml.load(open(self.yml_file, "r"), Loader=yaml.FullLoader)
        # setting up the attributes from the yaml file
        self.common_df_cols = yml["merge_on"]
        self.path = self.path + yml["output_dir"]
        _ = osu.cmd("mkdir -p {}".format(self.path))
        self.output_dataframe_path = self.path + "dataframe.feather"
        
        self.aggregated_cols = vda.aggregated_cols_dict
        self.derived_cols = vda.derived_cols_dict
        
        self.extracton_func = self.data_collection
        self.post_extraction_func = self.post_extraction

    def data_collection(self, fpath):
        df = pd.read_feather(fpath + "/dataframe.feather")
        return df
    
    def post_extraction(self):
        self.df = self.df.groupby(by=self.common_df_cols).agg(self.aggregated_cols)
        for k in self.derived_cols.keys():
            self.df[k] = self.df.apply(self.derived_cols[k], axis=1)
        self.df.reset_index(inplace=True)
        self.df["app"] = self.app
        self.df.to_feather(self.output_dataframe_path)

class VortexComparativeAnalysisClass(DataExtractionClass):
    def __init__(self, path, app, yml_file, plot=True):
        super(VortexComparativeAnalysisClass, self).__init__(   path=path,
                                                                app=app,
                                                                raw_subdir="",
                                                                yml_file=yml_file)
        assert os.path.isfile(self.yml_file), "YAML file not found!"
        yml = yaml.load(open(self.yml_file, "r"), Loader=yaml.FullLoader)
        self.plot = plot

        #making output directory
        self.path = self.path + yml["output_dir"]
        _ = osu.cmd("mkdir -p {}".format(self.path))
        self.output_dataframe_path = self.path + "/dataframe.feather"

        # setting up the attributes from the yaml file
        self.common_df_cols = yml["merge_on"]
        self.col_to_compare = yml["col_to_compare"]
        self.value_to_compare = yml["value_to_compare"]
        self.col_ref_value = yml["col_ref_value"]

        self.extracton_func = self.data_collection
        self.post_extraction_func = self.post_extraction

    def data_collection(self, fpath):
        df = pd.read_feather(fpath + "/dataframe.feather")
        if "resnet" in fpath:
            df["app"] = "resnet"
        elif "gcn" in fpath:
            df["app"] = "gcn"
        elif df["app"].unique() == "gcnSynth":
            df["app"] = "aggr"
        return df
    
    @staticmethod
    def get_cmp_val(cols, ref_value):
        ref_index = cols.index(ref_value)
        index = 0 if ref_index else 1
        return cols[index]

    @staticmethod
    def make_perc(x, cols, ref_value):
        ref_index = cols.index(ref_value)
        index = 0 if ref_index else 1
        p = x[cols[index]] - x[cols[ref_index]]
        r = p/x[cols[index]] if p>0 else p/x[cols[ref_index]]
        r *= 100
        return r
    
    @staticmethod
    def make_comparison(x, cols, ref_value):
        ref_index = cols.index(ref_value)
        index = 0 if ref_index else 1
        p = x[cols[index]]/x[cols[ref_index]]
        return p

    @staticmethod
    def gen_str_ID(x, cols):
        return "-".join([str(x[c]) for c in cols])


    def post_extraction(self):
        dfs = []
        #make as many dataframes as the number of values to compare
        for lws in self.df[self.col_to_compare].unique():
            if lws == self.col_ref_value: continue
            dfs.append(self.df.loc[(self.df[self.col_to_compare].isin([lws,self.col_ref_value]))])

        #pivot the dataframes to make the comparison (%)
        for i in range(len(dfs)):
            dfs[i].reset_index(inplace=True)
            dfs[i] = dfs[i].pivot(index=self.common_df_cols, columns=self.col_to_compare, values=self.value_to_compare)
            cols = dfs[i].columns.tolist()
            dfs[i]["%"] = dfs[i].apply(self.make_comparison, axis=1, cols=cols, ref_value=self.col_ref_value) ##### here you can change the data analysis class
            dfs[i][self.col_to_compare] = [self.get_cmp_val(cols, self.col_ref_value)]*len(dfs[i].index)

        #merge the dataframes
        df = pd.DataFrame({})
        for i in range(len(dfs)):
            dfs[i].reset_index(inplace=True) #resetting the index to have the common columns (in the index) as columns
            df = pd.concat([df, dfs[i]], ignore_index=True)

        #sorting the dataframe
        sort_list = [""]*len(self.file_list)
        for app in df["app"].unique():
            for i, f in enumerate(self.file_list):
                if app in f: sort_list[i] = app
        df["app"] = pd.Categorical(df["app"], sort_list)
        df.sort_values(by=["app"], inplace=True)

        #saving the dataframe
        df.reset_index(inplace=True)
        df.columns = df.columns.map(str)
        df.to_feather(self.output_dataframe_path)

        #generating analytics
        df["str_ID"] = df.apply(self.gen_str_ID, axis=1, cols=self.common_df_cols) #generating a string ID for each row
        for app in df["app"].unique():
            d = OrderedDict({})
            res_dir = self.path + "/" + app + "/"
            _ = osu.cmd("mkdir -p {}".format(res_dir))
            for comp in df[self.col_to_compare].unique():
                file_name = self.col_to_compare + "_" + str(comp)
                cdf = df.loc[(df["app"]==app) & (df[self.col_to_compare]==comp)]
                cdf = cdf.sort_values(by="%", ascending=True)
                d["Max Loss"] = float(cdf["%"].min())
                d["Avg"] = float(cdf["%"].mean())
                d["Avg Loss"] = float(cdf.loc[(df["%"]<1)]["%"].mean())
                d["Avg Gain"] = float(cdf.loc[(df["%"]>1)]["%"].mean())
                d["Equal"] = len(cdf.loc[(df["%"]==1)]["%"].index)
                d["Worse"] = len(cdf.loc[(df["%"]<1)]["%"].index)
                d["Worst"] = dict(zip(cdf.loc[(df["%"]<0)]["str_ID"],cdf.loc[(df["%"]<0)]["%"].astype(float)))
                yaml.dump(d, open(res_dir + file_name + ".yml", "w"))
                try:
                    gen_bar(cdf.loc[(df["%"]<0)], height="%", bar_names="str_ID", 
                                path=res_dir + file_name + ".svg")
                except:
                    print("No negative values found for {}".format(file_name))

        if self.plot:
            #plotting
            plot_path = self.path + "/_plots/"
            _ = osu.cmd("mkdir -p {}".format(plot_path))
            violin_plot(df, x="app", y="%", hue=self.col_to_compare, path=plot_path + "violin.svg", size=(20,5), split=True)
        
"""
Need to specify one of the possible strings below to select the correct class.
"""
extractorsDict = {"vortex-run": VortexPerfExtractionClass,
                  "vortex-tan": VortexTraceAnalysisClass,
                  "vortex-tpp": VortexTracePostProcessingClass,
                  "vortex-red": VortexExperimentReductionClass,
                  "vortex-cmp": VortexComparativeAnalysisClass}
