import pandas as pd
import os
import glob
import yaml

import inputs.vortex_da_utils as vda
import src.stream_parsing as sp

import da.util as util
from util.os_utils import cmd

from plots.trace import gen_time_traces
from plots.bar import gen_bar

#TODO: 
#   - Keep track of the faulty reports in a separate df
#   - Add a way to report the type of fault

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
    def __init__(self, path, app):
        self.path = path if path[-1]=="/" else path + "/"
        self.checkpoint_path = self.path + "checkpoint.feather"
        self.app = app
        self.extracton_func = self.dummy_extraction
        self.fault_checkers = []
        self.fault_handlers = self.dummy_fault_handler
        self.fault_str = [""] # needs to be a list of strings
        self.mode = "REDUCTION"
        self.post_extraction_func = self.dummy_post_extraction
        # Check if dataframe already exists, if so, loads it
        #TODO this is useless rn! Either make it useful or remove it
        if os.path.isfile(self.path + "dataframe.feather"):
            #print("Dataframe found. Loading dataframe...")
            #self.df = pd.read_feather(self.path + "dataframe.feather")
            self.df = pd.DataFrame({})
        else: self.df = pd.DataFrame({})

    @staticmethod
    def dummy_fault_handler(fpath):
        print("Faulty experiment: {}".format(fpath))

    @staticmethod
    def inplace_extract(fpath):
        pass

    @staticmethod
    def dummy_extraction(fpath):
        return {}
    
    @staticmethod
    def dummy_post_extraction():
        pass

    def check_faults_by_string(self,fpath):
        """
        Check if the experiment report is faulty.
        Args:
            fpath (str): path to the experiment report.
        Returns:
            bool: True if the experiment report is faulty, False otherwise.
        """
        with open(fpath, "r") as f:
            for line in f:
                if any([x in line for x in self.fault_str]) : return True
        return False
    
    def is_exp_faulty(self,fpath):
        for func in self.fault_checkers:
            if func(fpath): return True
        return False

    def extract(self, subdir="raw/", export=True, **kwargs):
        """
        Extract data from text experiment report.
        Args:
            subdir (str): subdirectory where the experiment reports are stored. main directory is self.path. Default: "raw/".
            export (bool): if True, it exports the experiment to a CSV file. Default: True.
            **kwargs: keyword arguments to pass to gen_csv method. See gen_csv method for more details.
        """
        fpath = self.path + subdir
        l = []
        #iterate over all files in the directory
        for f in (os.path.join(fpath, x) for x in os.listdir(fpath)):
            #print("Extracting data from {}...".format(f))
            if self.is_exp_faulty(f): 
                self.fault_handlers(f)
                continue
            if self.mode=="SINGLE":      self.inplace_extract(f)
            elif self.mode=="REDUCTION": l.append(self.extracton_func(f))
            else: raise Exception("Invalid mode.")
        
        if self.mode=="REDUCTION":
            new_df = pd.DataFrame(data=l)
            if self.df.empty: self.df = new_df
            else: self.df = pd.concat([self.df, new_df], ignore_index=True)

            #if os.path.isfile(self.checkpoint_path):
            #    print("Adding experiment metadata to dataframe...")
            #    self.df = pd.merge(self.df, pd.read_feather(self.checkpoint_path), on="ID")
            #else: raise Exception("Checkpoint file not found.")

            if export: self.dump_dataframe(**kwargs)
        
            self.post_extraction_func()

    def add_extraction_metadata_to_checkpoint(self):
        #TODO: what if it loads??? This might brake the checkpoint file
        """
        Add extraction metadata to the checkpoint file.
        """
        exp_df = pd.read_feather(self.checkpoint_path)
        bad_df = self.df[self.df.isnull().any(axis=1)]
        if bad_df.empty: print("No faulty experiments found!")
        else:
            #TODO add a way to report the type of fault
            print("Bad experiments: {}".format(len(bad_df)))
            for i in bad_df["ID"].values.tolist():
                exp_df.loc[exp_df["ID"] == i,"Status"] = 0
                exp_df.loc[exp_df["ID"] == i,"Return"] = None
            print("Exporting corrected checkpoint file...")
            exp_df.to_feather(self.checkpoint_path)
    
    def dump_dataframe(self, name="dataframe.feather"):
        self.df.to_feather(self.path+name)
        #print(self.df)

class VortexPerfExtractionClass(DataExtractionClass):
    def __init__(self,path,app):
        super(VortexPerfExtractionClass, self).__init__(    path=path,
                                                            app=app)
        self.extracton_func = vda.gen_dict_from_log
        self.fault_str = ["INVALID EXPERIMENT"]
        self.fault_checkers = [self.check_faults_by_string]
        self.fault_handlers = vda.vortex_fault_handler
        self.assembly_reference_file = os.getcwd() + "/inputs/kernel_assembly/" + self.app + "/" + self.app + ".dump"

class VortexTraceAnalysisClass(DataExtractionClass):
    def __init__(self,path,app):
        super(VortexTraceAnalysisClass, self).__init__(    path=path,
                                                            app=app)
        self.mode = "SINGLE"
        self.extracton_func = self.dummy_extraction
        self.inplace_extract = self.trace_postprocessing
        self.fault_str = ["INVALID EXPERIMENT"]
        self.fault_checkers = [self.is_not_db, self.check_empty_database, self.check_coherent_assembly]
        self.fault_handlers = self.dummy_fault_handler

        input_path = os.getcwd() + "/inputs/kernel_assembly/" + self.app + "/" 
        self.dotdump_path = input_path + self.app + ".dump"
        self.code_sections = self.gen_code_map(input_path + "sections.yml")
        self.iter_df = pd.DataFrame({})
        self.iter_fname = ""

    @staticmethod
    def gen_code_map(code_sections_fname):
        code_sections = yaml.load(open(code_sections_fname, "r"), Loader=yaml.FullLoader)
        code_map = {}
        for s in code_sections.keys():
            code_map[s] = []
            for e in code_sections[s]:
                if type(e) == int: code_map[s].append(e)
                elif type(e) == list: code_map[s].extend(e)
                elif type(e) == str: 
                    ee = e.split(":")
                    code_map[s].extend(range(int(ee[0],base=16),int(ee[1],base=16)+1,4))
        vmax = 0
        for s in code_map.keys():
            vmax = max(vmax, max(code_map[s])) #getting the max value of the code map
        
        vmin = 0x80000000

        ret_code_map = {}
        for i in range(vmin,vmax+1):
            for s in code_map.keys():
                if i in code_map[s]:
                    ret_code_map[i] = s
                    break
        return ret_code_map   

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
    
    @staticmethod

    @staticmethod
    def plot_traces(df, path, ID):
        _ = cmd("mkdir -p {}".format(path + "plots/"))
        for c in list(df["core"].unique()):
            for w in list(df["warp"].unique()):
                child_df = df.loc[(df["core"]==c) & (df["warp"]==w)]
                if child_df.empty: continue
                gen_time_traces(    df=child_df, traces_col_name="code_section", 
                                    period_col_name="total-exec-time", start_col_name="schedule-stmp", 
                                    path=path + "plots/{}_c{}_w{}.svg".format(ID,c,w))

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

    @staticmethod
    def make_synthesis(df, df_ID, path="", plot=False):
        print("Total number of events {}: {}".format(df_ID,len(df)))
        synthesis_df = pd.DataFrame({})
        for c in list(df["core"].unique()):
            for w in list(df["warp"].unique()):
                for s in list(df["code_section"].unique()):
                    child_df = df.loc[(df["core"]==c) & (df["warp"]==w) & (df["code_section"]==s)]
                    if child_df.empty: continue
                    events = util.TimeSeriesClass(  ID="{}_{}_{}".format(c,w,s), 
                                                    events=child_df, 
                                                    period_col_name="total-exec-time", 
                                                    start_col_name="schedule-stmp").make_synthesis()
                    events_len = len(events)
                    events["core"] = [c]*events_len
                    events["warp"] = [w]*events_len
                    events["code_section"] = [s]*events_len
                    #events["end"] = events["schedule-stmp"] + events["total-exec-time"]
                    synthesis_df = pd.concat([synthesis_df, events], ignore_index=True)
        if path:
            synthesis_df.to_feather(path+".syn")
            yaml.dump(VortexTraceAnalysisClass.extract_info_dict(synthesis_df), open(path+".yml", "w"))
        if plot:
            plot_path = "/".join(path.split("/")[:-2]) + "/"
            VortexTraceAnalysisClass.plot_traces(synthesis_df, plot_path, df_ID)
        
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
                        #child_df.loc[i+1, "schedule-stmp"] = child_df.loc[i+1]["schedule-stmp"] - saved_time
                        child_df = child_df.drop(i)
                    else:
                        child_df.loc[i, "schedule-stmp"] = child_df.loc[i]["schedule-stmp"] - saved_time
                        #time = child_df.loc[i]["schedule-stmp"]
                elen = len(child_df)
                child_df["core"] = [c]*elen
                child_df["warp"] = [w]*elen
                roofline_df = pd.concat([roofline_df, child_df], ignore_index=True)
        if path:
            roofline_df.to_feather(path+".roof")
        if plot:
            VortexTraceAnalysisClass.make_synthesis(roofline_df, df_ID, path+".roof", True)
                
    def trace_postprocessing(self, fpath):
        #Add code section
        def get_code_section(x):
            try:
                return self.code_sections[x["PC"]]
            except:
                return "fini"
        self.iter_df["code_section"]    = self.iter_df.apply(get_code_section, axis=1)
        self.iter_df["e_count"]         = self.iter_df.apply(self.get_exec_count, axis=1)
        self.make_synthesis(self.iter_df, df_ID=self.iter_fname.split("/")[-1]+".AS_IS", path=self.iter_fname, plot=False)
        self.make_roofline(self.iter_df, sections_to_drop=["kernel_loops_bookkeeping","kernel_memory_addressing"], df_ID=self.iter_fname.split("/")[-1]+".ROOF", path=self.iter_fname, plot=True)
        #plot bar charts
        #plot gains in removing kernel_loops_bookkeeping and kernel_memory_addressing
        #plot overhead time vs total time when sweeping the workload size: when is the crossing point?

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