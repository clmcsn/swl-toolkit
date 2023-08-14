import pandas as pd
import os
import yaml

from . import vortex_da_utils as vda
from . import utils
from .. import stream_parsing as sp
from ..util import os_utils as osu
from ..plots.trace import gen_trace_analysis, gen_time_traces

#TODO: 
#   - Keep track of the faulty reports in a separate df

class DataExtractionClass():
    """
    Class to extract data from text experiment report.
    e.g.: experiment_cmd > experiment_report.txt 2>&1

    Methods:
        extract: extract data from text experiment report.
        gen_csv: generate csv file from extracted data.

    Attributes:
        path (str): path to the directory where the experiment reports are stored.
        extracton_func (function): function to extract data from text experiment report.
        df (pandas.DataFrame): dataframe to store extracted data.
        fault_str ([str,list]): string to indicate that the experiment is faulty. Default: "Error".
    """
    def __init__(self, path, app, raw_subdir="raw/", inplace_only=False):
        #paths
        self.path = path if path[-1]=="/" else path + "/"
        self.raw_subdir = self.path + raw_subdir
        self.checkpoint_path = self.path + "checkpoint.feather"
        self.output_dataframe_path = self.path + "dataframe.feather"

        #base attributes
        self.app = app
        self.inplace_only = inplace_only
        
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
        print("Faulty experiment: {}".format(fpath))

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
        Args:
            subdir (str): subdirectory where the experiment reports are stored. main directory is self.path. Default: "raw/".
            export (bool): if True, it exports the experiment to a CSV file. Default: True.
            **kwargs: keyword arguments to pass to gen_csv method. See gen_csv method for more details.
        """
        #iterate over all files in the directory
        for f in (os.path.join(self.raw_subdir, x) for x in os.listdir(self.raw_subdir)):
            r = self.is_exp_faulty(f)
            if r: 
                self.fault_handler(f)
                continue
            self.inplace_process(f)
            if (not self.inplace_only): self.df = pd.concat([self.df, self.extracton_func(f)], ignore_index=True)
        if (not self.inplace_only):
            if os.path.isfile(self.checkpoint_path):
                print("Adding experiment metadata to dataframe...")
                self.df = pd.merge(self.df, pd.read_feather(self.checkpoint_path), on="ID")
            else: raise Exception("Checkpoint file not found.")
            self.dump_dataframe()
        self.post_extraction_func()
    
    def dump_dataframe(self):
        if os.path.isfile(self.output_dataframe_path):
            print("Dataframe already present...")
            osu.make_backup(self.output_dataframe_path)
        self.df.to_feather(self.output_dataframe_path)

class VortexPerfExtractionClass(DataExtractionClass):
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
    def __init__(self,path,app):
        """
        Class to extract data from Vortex trace.
        Args:
            path (str): path to the directory where the experiment dataframes (obtained with stream_parsing) are stored.
            app (str): Mandatory. Application name (e.g. vecadd).
        """
        super(VortexTraceAnalysisClass, self).__init__(    path=path,
                                                            app=app,
                                                            inplace_only=True)
        self.extracton_func = self.dummy_extraction
        self.inplace_process = self.trace_analysis
        self.fault_checkers = [self.is_not_db, self.check_empty_database, self.check_coherent_assembly]
        self.fault_handlers = self.dummy_fault_handler

        #Following line works only if script is run from the project root directory
        input_path = os.getcwd() + "/inputs/kernel_assembly/" + self.app + "/" 
        self.dotdump_path = input_path + self.app + ".dump"
        self.code_sections = self.gen_code_map(input_path + "sections.yml")
        self.iter_df = pd.DataFrame({})
        self.iter_fname = ""

    @staticmethod
    def gen_code_map(code_sections_fname: str) -> dict:
        """
        Generate a code map (lookup table) from a yaml file.
        Args:
            code_sections_fname (str): path to the yaml file containing the code sections.
        Returns:
            dict: code map. Dictionary with keys = code instruction PC names and values = list of code section addresses.
        """
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
        r = False
        print("Checking assembly coherence...")
        ref_code_df = sp.DotDumpRISCVParsingClass(  output_path=self.path,
                                                    dump_file=self.dotdump_path).get_df()
        instr_df = self.iter_df[['PC-id','instr']]
        if not instr_df.isin(ref_code_df).all().all(): r = False
        else: r = True
        if not r: print("Assembly looks OK!")
        else: print("ERROR: Assembly is not coherent!")
        return r

    # ---------------------------------------------------------- #
    # ------------------------ PLOTS --------------------------- #

    @staticmethod
    def plot_complete_trace_plot(sdf,df, path, ID, sections=[]):
        _ = osu.cmd("mkdir -p {}".format(path + "plots/"))
        for c in list(df["core"].unique()):
            if not sections: sections = list(df["code_section"].unique()) 
            child_df = df.loc[(df["core"]==c) & (df["code_section"].isin(sections))]   #["workload_distr","kernel_call_init","kernel_call_init_inner","kernel"]))]
            child_sdf = sdf.loc[(sdf["core"]==c) & (sdf["code_section"].isin(sections))]   #["workload_distr","kernel_call_init","kernel_call_init_inner","kernel"]))]
            if child_df.empty: continue
            gen_trace_analysis( df=child_df ,synthetic_df=child_sdf, traces_col_name="code_section", 
                                period_col_name="total-exec-time", start_col_name="schedule-stmp", 
                                path=path + "plots/{}_c{}.svg".format(ID,c))

    @staticmethod
    def plot_time_traces(df, path, ID, sections=[]):
        _ = osu.cmd("mkdir -p {}".format(path + "plots/"))
        for c in list(df["core"].unique()):
            child_df = df.loc[(df["core"]==c) & (df["code_section"].isin(sections))]   #["workload_distr","kernel_call_init","kernel_call_init_inner","kernel"]))]
            if child_df.empty: continue
            gen_time_traces(    df=child_df, traces_col_name="code_section", 
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
    def extract_section_execution_time(df, section):
        child_df = df.loc[df["code_section"]==section]
        total = child_df["total-exec-time"].sum()
        return int(total)

    @staticmethod
    def extract_section_instruction_count(df, section):
        child_df = df.loc[df["code_section"]==section]
        total = child_df["event_count"].sum()
        return int(total)
    
    @staticmethod
    def extract_section_thread_instruction_count(df, section):
        child_df = df.loc[df["code_section"]==section]
        total = child_df["thread_event_count"].sum()
        return int(total)

    @staticmethod
    def extract_info_dict(df):
        info = {}
        info["last-commit"] = VortexTraceAnalysisClass.extract_last_cycle(df)
        d = {}
        de = {}
        dte = {}
        for s in df["code_section"].unique():
            d[s] = VortexTraceAnalysisClass.extract_section_execution_time(df, s)
            de[s] = VortexTraceAnalysisClass.extract_section_instruction_count(df, s)
            dte[s] = VortexTraceAnalysisClass.extract_section_thread_instruction_count(df, s)
        info["section-exec-time"] = d
        info["section-exec-count"] = de
        info["section-thread-exec-count"] = dte
        info["total-exec-count"] = int(df["event_count"].sum())
        info["total-thread-exec-count"] = int(df["thread_event_count"].sum())
        info["overhead"] = (info["last-commit"] - info["section-exec-time"]["kernel"]*info["section-exec-count"]["kernel"]/info["section-thread-exec-count"]["kernel"]) / info["last-commit"] * 100
        return info
    
# ----------------------------------------------------------- #
# ------------------------ MAIN FUNCTIONS ------------------- #

    @staticmethod
    def make_synthesis(df, df_ID, path="", plot=True):
        print("Total number of events {}: {}".format(df_ID,len(df)))
        synthesis_df = pd.DataFrame({})
        for c in list(df["core"].unique()):
            for s in list(df["code_section"].unique()):
                child_df = df.loc[(df["core"]==c) & (df["code_section"]==s)]
                if child_df.empty: continue
                #extracting the fused events
                events = utils.TimeSeriesClass(  ID="{}_{}".format(c,s),
                                                events=child_df,
                                                period_col_name="total-exec-time",
                                                start_col_name="schedule-stmp").make_synthesis()
                events_len = len(events)
                events["core"] = [c]*events_len
                events["code_section"] = [s]*events_len
                synthesis_df = pd.concat([synthesis_df, events], ignore_index=True)

        if path:
            print("Saving synthesis dataframe:{}".format(path))
            synthesis_df.to_feather(path+df_ID+".feather")
            yaml.dump(VortexTraceAnalysisClass.extract_info_dict(synthesis_df), open(path+df_ID+".yml", "w"))
        if plot:
            print("Generating synthesis plot:{}".format(path))
            #sdf,df, path, ID, sections=[]):
            VortexTraceAnalysisClass.plot_complete_trace_plot(  sdf=synthesis_df, df=df, 
                                                                path=path, ID= df_ID)
            VortexTraceAnalysisClass.plot_complete_trace_plot(  sdf=synthesis_df, df=df, 
                                                                path=path, ID=df_ID+"_ZOOM", 
                                                                sections=["workload_distr","kernel_call_init","kernel_call_init_inner","kernel","kernel_loops_bookkeeping","kernel_memory_addressing"])

    @staticmethod
    def make_roofline(df, sections_to_drop:list, df_ID, path="", plot=False):
        roofline_df = pd.DataFrame({})
        for c in list(df["core"].unique()):
            for w in list(df["warp"].unique()):
                child_df = df.loc[(df["core"]==c) & (df["warp"]==w)]
                saved_time = 0
                child_df = child_df.sort_values(by="eID")
                child_df.reset_index(drop=True, inplace=True)
                iterations = len(child_df)
                for i in range(iterations):
                    if child_df.loc[i]["code_section"] in sections_to_drop:
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
        if plot:
            VortexTraceAnalysisClass.make_synthesis(roofline_df, df_ID, path)

    def trace_analysis(self, fpath):
        #Add code section
        def get_code_section(x):
            try:
                return self.code_sections[x["PC"]]
            except:
                return "fini"
        self.iter_df["code_section"]    = self.iter_df.apply(get_code_section, axis=1)
        self.iter_df["e_count"]         = self.iter_df.apply(self.get_exec_count, axis=1)

        stripped_df_name = self.iter_fname.split("/")[-1].split(".")[0]
        output_path = self.path + stripped_df_name + "/"
        _ = osu.cmd("mkdir -p {}".format(output_path))
        self.make_synthesis(self.iter_df, df_ID=stripped_df_name+"-SYN", path=output_path, plot=True)
        self.make_roofline(self.iter_df, sections_to_drop=["kernel_loops_bookkeeping","kernel_memory_addressing"], 
                           df_ID=stripped_df_name+"-SSR-FREP", path=output_path, plot=True)

class VortexTracePostProcessingClass(DataExtractionClass):
    def __init__(self,path,app):
        super(VortexTracePostProcessingClass, self).__init__(   path=path,
                                                                app=app)
        self.mode = "REDUCTION"
        self.extracton_func = self.trace_postprocessing
        self.post_extraction_func = self.post_extraction
        self.fault_str = ["INVALID EXPERIMENT"]
        self.fault_checkers = [self.is_not_yml_file]
        self.fault_handlers = self.dummy_fault_handler
        self.iter_dict = {}
        self.iter_fname = ""
    
    def is_not_yml_file(self, fpath):
        if fpath.endswith(".yml"):
            self.iter_dict = yaml.load(open(fpath, "r"), Loader=yaml.FullLoader)
            self.iter_fname = fpath
            return False
        return True

    @staticmethod
    def dummy_fault_handler(fpath):
        pass

    @staticmethod
    def plot_bars(d, path, df_ID):
        _ = cmd("mkdir -p {}".format(path + "plots/"),verbose=False)
        for k in d["section-exec-time"].keys():
            d["section-exec-time"][k] = d["section-exec-time"][k]/(d["section-thread-exec-count"][k]/d["section-exec-count"][k])
        df = pd.DataFrame(d["section-exec-time"], index=[0])
        df = df.apply(lambda x: x/d["last-commit"]*100, axis=1)
        df = df.melt(var_name="section", value_name="period")
        gen_bar(df, "period", "section", path=path + "plots/" + df_ID + ".svg")

    def trace_postprocessing(self, fpath):
        ID_string = fpath.split("/")[-1].split(".")[0]
        if "roof" in fpath: ID_plot = ID_string + ".roof"
        else: ID_plot = ID_string + ".AS_IS"
        plot_path = "/".join(fpath.split("/")[:-2]) + "/"
        VortexTracePostProcessingClass.plot_bars(self.iter_dict, plot_path, ID_plot)
        d = {"ID": ID_string}
        d["roof"] = True if "roof" in fpath else False
        d["overhead"] = self.iter_dict["overhead"]
        d["last-commit"] = self.iter_dict["last-commit"]
        d["total-exec-count"] = self.iter_dict["total-exec-count"]
        d["total-thread-exec-count"] = self.iter_dict["total-thread-exec-count"]
        return d

    def post_extraction(self):
        plot_path = "/".join(self.iter_fname.split("/")[:-2]) + "/plots/"
        #print dual bar
        gen_bar(self.df.sort_values(by="ID"), height="last-commit", bar_names="ID", hue="roof", path=plot_path + "savings_cycles.svg", log=True)
        gen_bar(self.df.sort_values(by="ID"), height="total-exec-count", bar_names="ID", hue="roof", path=plot_path + "savings_instr_issue.svg", log=True)
        gen_bar(self.df.sort_values(by="ID"), height="total-thread-exec-count", bar_names="ID", hue="roof", path=plot_path + "savings_instr_exec.svg", log=True)

        for i in list(self.df["roof"].unique()):
            child_df = self.df.loc[self.df["roof"]==i]
            gen_bar(child_df.sort_values(by="ID"), height="overhead", bar_names="ID", path=plot_path + "overhead{}.svg".format("_root" if i else ""))
        #df = pd.DataFrame({})
        #for i in range(len(df)):
        #    df.loc[i, "overhead"] = self.db.loc[i]["overhead"]
        #    df.loc[i, "ID"] = self.db.loc[i]["ID"]
        #    if self.db.loc[i]["roof"]:
        #        df.loc[i, "last-commit-roof"] = self.db.loc[i]["last-commit"]
        #    else:
        #        df.loc[i, "last-commit"] = self.db.loc[i]["last-commit"]
        
extractorsDict = {"vortex-run": VortexPerfExtractionClass,
                  "vortex-tan": VortexTraceAnalysisClass,
                  "vortex-tpp": VortexTracePostProcessingClass,}