from collections import OrderedDict 
from typing import Union
from math import log
import numpy as np
import functools
import pandas as pd
from itertools import product
import os
import sys
import yaml
import time

import inputs.template as TPL

class ExperimentStringParserClass(object):
    """
    This class parses a string of the form "a:b:c" and returns a list of integers.
    a, b and c gets a different meaning depending on the number of colons in the string and on the presence of specific caracters.
    Supported list types:
    - range: [a]:[b]:[c]
        a: start of the range (default: 0)
        b: end of the range 
        c: step of the range (default: 1)
        Example1: 0:10:2 -> [0,2,4,6,8,10]
        Example2: 10:0:2 -> [10,8,6,4,2,0]
        Example3: 10 -> [0,1,2,3,4,5,6,7,8,9,10]
        NOTE: if b is not specified, a is used as b and start of the range is set to 0
        NOTE: if c is not specified, string is interpreted as a log (see below)
    - log: [a]:[b]:b[c]
        a: start of the range
        b: number of steps
        bc: base of the log (default: 2)
        Example1: 10:5:b2 -> [10,20,40,80,160]
        Example2: 10:5:b3 -> [10,30,90,270,810]
        Example3: 10:5    -> [10,20,40,80,160]
        NOTE: if the character b is not specified, string is interpreted as a range (see above)
    """
    def __init__(self, string):
        self.args_table = ("a","b","c")
        self.parsed_list = []
        self.list_gen_func = None
        self.list_gen_func_args = {}
        self.string = string
        self.parse()
        self.parsed_list = self.list_gen_func(**self.list_gen_func_args)

    @staticmethod
    def make_log_list(a, b, c=2, integers=True):
        start = a
        steps = b
        base = c
        s = int(log(start,base))
        l = np.logspace(s, s+steps-1, num=steps, base=base)
        if integers : l = [int(x) for x in l]
        return list(l)
    
    @staticmethod
    def make_range_list(a, b=0, c=1):
        return list(range(a,b+1,c))

    def parse(self):
        raw_list = self.string.split(":")
        #parse special characters 
        for i, e in enumerate(raw_list):
            if i==2:
                if e[0].isalpha() and e[0]=="b":
                    self.list_gen_func = self.make_log_list
                    self.list_gen_func_args[self.args_table[i]] = int(e[1:])
                    continue
            self.list_gen_func_args[self.args_table[i]] = int(e)
        if self.list_gen_func == None:
            if len(raw_list) == 1: self.list_gen_func = self.make_range_list
            if len(raw_list) == 2: self.list_gen_func = self.make_log_list
            if len(raw_list) == 3: self.list_gen_func = self.make_range_list

class ExperimentClass():
    """
    This class is a wrapper for a single experiment iteration.
    The single experiment is represented with a dictionary where each key has only one value (not a list!).
    This class provides the utilities to generate the command line string and the result file name.
    Methods:
    - fill_arguments: fills the missing arguments with the default values from a template dictionary
    - get_cmd_str: returns the command line string for the experiment
    - make_result_fname: returns the result file name for the experiment
    """
    def __init__(self, struct : dict, res_path : str = ""):
        if struct :
            self.experiments = struct
            self.app = struct["app"]
            self.fill_arguments()
            self.res_path = res_path

    def update_key(self, key, value):
        self.experiments[key] = value
    
    def fill_arguments(self):
        for k in TPL.templateDict[self.app].DICT.keys():
            if k not in self.experiments:
                self.experiments[k] = TPL.templateDict[self.app].DICT[k]

    def get_cmd_str(self):
        name = []
        for k in TPL.templateDict[self.app].CMD[1].keys():
            if k in self.experiments.keys():
                name.append(TPL.templateDict[self.app].CMD[1][k].format(**{k:self.experiments[k]}))
        return " ".join(name)

    def make_result_fname(self):
        name = []
        for k in TPL.templateDict[self.app].STR.keys():
            if k in self.experiments.keys():
                name.append(TPL.templateDict[self.app].STR[k].format(**{k:self.experiments[k]}))
        return self.res_path + "_".join(name)

#TODO add constraint fails in metadata dump (and maybe accpet it as input in the exp yml file)
class ExperimentManagerClass():
    """
    This class is a manager for a set of experiments.
    The experiments are represented as a dictionary, where each key is a parameter and each value is 
    single or a list of values for that parameter.
    It can be initialized with a dictionary or through a configuration file.
    Constructor arguments:
    - conf_file: the path to the configuration file
    Examples (in YAML sintax): 
    ________________________________
    app       : vecadd
    driver    : simx
    threads   : "4:4"
    ________________________________
    In the example above, the experiments list will be a list of one experiment.
    App and driver are fixed parameters, while threads is a parameter to be sweeped expressed as ExperimentString.
    - struct: the dictionary containing the experiments
    one of the two arguments must be specified
    - path: the path to the result files (Manadatory)
    - oID: the ID of the experiment (Manadatory if experiments are run in hierarchical mode)
    Methods:
    - See sections below
    Members:
    - experiments: the list of experiments
    """
    def __init__(self, conf_file : str = None, struct : Union[dict, OrderedDict] = OrderedDict({}),
                    path : str = None, constraints : list = [], oID: int = None, force_flat = False):
        #Args
        self.experiments = struct
        self.output_path = path if path[-1] == "/" else path + "/"
        assert self.output_path != None, "Path is not specified"
        self.constraints = constraints
        self.force_flat = force_flat #forces the flat hierarchy (e.g. if already in a container)
        self.oID = oID

        #Checkpoint
        self.checkpoint_fname = "checkpoint.feather" if self.oID == None else "checkpoint_{}.feather".format(self.oID)
        self.checkpoint_path = self.output_path  + self.checkpoint_fname
        self.experiment_dump_fname = "experiments.dump.yml"
        self.experiment_dump_path = self.output_path + self.experiment_dump_fname
        self.raw_output_path = self.output_path + "raw/"
        os.makedirs(self.raw_output_path, exist_ok=True)

        if conf_file != None:
            with open(conf_file,"r") as stream:
                blob = yaml.safe_load(stream)
                self.experiments = blob

        #Members
        self.outer_loop_dict = OrderedDict({})
        self.outer_iter = 0
        self.inner_loop_dict = OrderedDict({})
        self.inner_iter = 0
        self.fixed_dict = {}
        self.experiment_df = pd.DataFrame({})
        self.verbose = True

        #-----------------------------INIT--------------------------------
        if (not self.check_checkpoint()):
            self.make_metadata()
        else :
            print("Checkpoint found, loading from checkpoint...")
            self.load_checkpoint(make_metadata=True) #Metadata is needed if we are loading from checkpoint
        
        self.child_checkpoint_path = self.output_path + "checkpoint_{}.feather" if self.hierarchy=="Outer" else None
        self.export_experiment()

    '''-----------------------------UTILS--------------------------------'''
    '''
    get_app_name: returns the application name
    make_command: returns the command line string for the experiment
    __str__: prints the experiment manager
    '''
    def get_app_name(self):
        '''
        Returns the application name.
        '''
        return self.experiments["app"]

    def set_output_dir(self, path):
        '''
        Sets the output directory.
        '''
        self.output_path = path if path[-1] == "/" else path + "/"
        self.set_dirs()
    
    def set_dirs(self):
        self.raw_output_path = self.output_path + "raw/"
        os.makedirs(self.raw_output_path, exist_ok=True)
        self.checkpoint_path = self.output_path + self.checkpoint_fname
        self.experiment_dump_path = self.output_path + self.experiment_dump_fname
        self.child_checkpoint_path = self.output_path + "checkpoint_{}.feather" if self.hierarchy=="Outer" else None
        print("Output path set to {}".format(self.output_path))
        print("Raw output path set to {}".format(self.raw_output_path))
        print("Checkpoint path set to {}".format(self.checkpoint_path))
        print("Experiment dump path set to {}".format(self.experiment_dump_path))
        print("Child checkpoint path set to {}".format(self.child_checkpoint_path))

    def make_command(self, ID, exp=None, meta_dict={}):
        if self.hierarchy == "Outer":
            command = TPL.templateDict[self.experiments["app"]].CMD[0].format(**meta_dict,oID=ID)
        elif self.hierarchy == "Inner" or self.hierarchy == "Flat":
            command = "( {} ) > {} 2>&1".format( exp.get_cmd_str(), exp.make_result_fname())
        else:
            print("Unknown hierarchy!")
            raise Exception
        command = " ".join(command.split())
        return command
    
    def __str__(self):
        print("---------------------------------------------------------------------")
        print("Experiment Manager\n")
        print("Experiment {}".format(self.experiments["app"]))
        print("Result path {}".format(self.output_path))
        #print("Total iterations:{} Checkpoint:{}".format(self.iterations, self.offset))
        print("Fixed parameters:")
        for k in self.fixed_dict.keys():
            print("------{}: {}".format(k, self.fixed_dict[k]))
        print("Outer loop parameters:")
        for k in self.outer_loop_dict.keys():
            print("------{}: {}".format(k, self.outer_loop_dict[k]))
        print("Outer loop iterations: {}".format(self.outer_iter))
        print("Inner loop parameters:")
        for k in self.inner_loop_dict.keys():
            print("------{}: {}".format(k, self.inner_loop_dict[k]))
        print("Inner loop iterations: {}".format(self.inner_iter))
        for f in self.constraints:
            print("Constraint: {}".format(f))
        print("Total iterations: {}".format(len(self.experiment_df)))
        return("---------------------------------------------------------------------\n")

    '''-----------------------------EXPERIMENT DICTIONARY--------------------------------'''
    '''
    update: updates the experiments and rewrites the metadata
    key_update: updates a key in the experiment dictionary
    export_experiment: exports the experiment to a YAML file
    load_experiment: loads the experiment from a YAML file
    '''
    
    def update(self, struct : Union[dict, OrderedDict]):
        '''
        Updates the experiments and rewrites the metadata.
        '''
        self.experiments = struct
        self.make_metadata()
    
    def key_update(self, key, value):
        '''
        Updates a key in the experiment dictionary.
        '''
        self.experiments.update({key:value})
    
    def export_experiment(self):
        '''
        Exports the experiment to a YAML file
            Parameters:
                outfile (str): name of the output file
        '''
        if self.hierarchy == "Outer" or self.hierarchy == "Flat":
            print("Exporting experiment to {}".format(self.experiment_dump_path))
            with open(self.experiment_dump_path, 'w') as fout:
                yaml.dump(self.experiments, fout)
    
    def load_experiment(self):
        '''
        Loads the experiment from a YAML file
            Parameters:
                path (str): path to the YAML file
        '''
        with open(self.experiment_dump_path, 'r') as fin:
            self.experiments = yaml.safe_load(fin)
        self.make_metadata()

    '''-----------------------------DATAFRAME QUERIES--------------------------------'''
    '''
    get_total_iter: returns the total number of experiments
    get_inner_loop_size: returns the number of inner loop experiments
    get_outer_loop_size: returns the number of outer loop experiments
    get_missing_inner_loop: returns the number of missing inner loop experiments for a given outer loop experiment
    get_missing_outer_loop: returns the number of missing outer loop experiments
    get_gloabal_ID: returns the global ID for a given outer and inner loop ID
    get_outer_ID: returns the outer loop ID for a given global ID
    get_missing_IDs: returns the missing outer or absolute IDs
    '''

    def get_total_iter(self):
        return len(self.experiment_df)
    
    def get_inner_loop_size(self):
        return self.inner_iter
    
    def get_outer_loop_size(self):
        return self.outer_iter
    
    def get_missing_inner_loop(self, oID):
        return len(self.experiment_df.loc[(self.experiment_df['Status']==1) & (self.experiment_df['oID']==oID)])

    def get_missing_outer_loop(self):
        return len(self.experiment_df.loc[self.experiment_df['Status']==1]['oID'].unique())

    def get_missing_loops(self):
        return len(self.experiment_df.loc[self.experiment_df['Status']==1])

    def get_gloabal_ID(self, ID):
        return self.experiment_df.loc[(self.experiment_df['oID']==ID[0]) & (self.experiment_df['iID']==ID[1]), 'ID'].values[0]
    
    def get_outer_ID(self, ID):
        return self.experiment_df.loc[self.experiment_df['ID']==ID, 'oID'].values[0]
    
    def get_missing_IDs(self, ID = None):
        '''
        Returns the IDs of the experiments that are not completed.
            Parameters:
                ID (int): the ID of the outer loop experiment. If None, returns all the missing IDs.'
            Returns:
                list: the list of missing IDs.
        '''
        if self.hierarchy == "Outer":   #Return the missing oIDs of the outer loop
            child_df = self.experiment_df.loc[self.experiment_df['Status']==0]
            return list(child_df['oID'].unique())
        elif self.hierarchy == "Inner": #Return the missing IDs of the inner loop
            child_df = self.experiment_df.loc[(self.experiment_df['Status']==0) & (self.experiment_df['oID']==ID)]
            return child_df['ID'].values.tolist()
        elif self.hierarchy == "Flat":  #Return the missing IDs of the flat loop
            child_df = self.experiment_df.loc[self.experiment_df['Status']==0]
            return child_df['ID'].values.tolist()
        else:
            print("Unknown hierarchy: {}!".format(self.hierarchy))
            raise Exception
    
    '''-----------------------------SAMPLE & COMMIT--------------------------------'''
    '''
    sample: samples an experiment from the dataframe
    commit: commits the result of an experiment (or a set of experiments)
    '''
    def sample(self, ID: Union[list, int]):
        if self.hierarchy == "Outer":
            e = None
        elif self.hierarchy == "Inner" or self.hierarchy == "Flat":
            if type(ID) == list: ID = self.get_gloabal_ID(ID) # if ID is a list of oID and iID, convert it to a global ID
            e = self.experiment_df.loc[self.experiment_df['ID']==ID].to_dict('records')[0]
            e = ExperimentClass(struct=e, res_path=self.raw_output_path)
        else:
            print("Unknown hierarchy: {}!".format(self.hierarchy))
            raise Exception
        return e
    
    def commit(self, ID : Union[list, int], ret, lock):
        if self.hierarchy == 'Outer':
            rets = None
            if ret==0: #if job submission was successful
                LOCK =True
                ii = 0
                while (LOCK):
                    status = self.check_status(oID=ID)
                    if self.verbose and ii%10==0: self.print_oID_status(ID, ii, status) 
                    ii+=1
                    if functools.reduce(np.logical_and, list(status)):
                        LOCK = False
                    time.sleep(60)
                # actual commit
                child_df = pd.read_feather(self.child_checkpoint_path.format(ID))   
                rets = child_df.loc[child_df['oID']==ID, 'Return'].values.tolist()
                os.remove(self.child_checkpoint_path.format(ID))
            with lock:
                self.update_dataframe()
                self.experiment_df.loc[self.experiment_df['oID']==ID, 'Status'] = 1
                self.experiment_df.loc[self.experiment_df['oID']==ID, 'Return'] = rets if ret==0 else ret
                self.store_checkpoint()
                ret = rets if ret==0 else ret
        elif self.hierarchy == 'Inner' or self.hierarchy == 'Flat':
            if type(ID)==list: ID = self.get_gloabal_ID(ID) # if ID is a list of oID and iID, convert it to a global ID
            with lock:
                self.update_dataframe()
                self.experiment_df.loc[self.experiment_df['ID']==ID, 'Status'] = 1
                self.experiment_df.loc[self.experiment_df['ID']==ID, 'Return'] = ret
                self.store_checkpoint()
        else:
            print("Unknown hierarchy!")
            raise Exception
        if self.verbose: self.print_status(ID, ret)
    
    def print_oID_status(self, oID, t, stats):
        IDs = self.experiment_df.loc[(self.experiment_df['oID']==oID)]['ID'].values.tolist()
        missing = []
        for i in range(len(IDs)):
            if not stats[i]: missing.append(IDs[i])
        elapsed = t
        done = len(IDs)-len(missing)
        print("[MIN: {}] oID:{} - Waiting for child to finish... Done {}/{}\n------> Missing IDs: {}".format(elapsed, oID, done, self.inner_iter,missing))

    '''-----------------------------STATUS--------------------------------'''
    '''
    check_status: checks the status of an experiment (or a set of experiments)
    print_status: prints the status of an experiment (or a set of experiments)
    '''
    def check_status(self, ID=None, oID=None):
        if ID!=None:    # Used for inner and flat hierarchy to check single core experiment
            if type(ID) == list: ID = self.get_gloabal_ID(ID)
            status = self.experiment_df.loc[self.experiment_df['ID']==ID]['Status'].values[0]
        elif oID!=None: # Used for outer hierarchy to check the status of the child experiments with a specific oID
            if (not os.path.isfile(self.child_checkpoint_path.format(oID))):
                status = [ 0 for _ in range(self.inner_iter) ]
            else:
                child_df = pd.read_feather(self.child_checkpoint_path.format(oID))
                status = child_df.loc[child_df['oID']==oID]['Status'].values.tolist()
        else:           # Used for inner hierarchy to check the status of its own assigend experiments
            status = self.experiment_df.loc[self.experiment_df['oID']==self.oID]['Status'].values.tolist()
        return status
    
    def print_status(self, ID, ret): #clean here
        if self.hierarchy == 'Outer':
            OK = 0
            if type(ret)!=list: ret = [ret for i in range(self.inner_iter)]
            for i in ret:
                if i==0: OK+=1
            print("Outer Loop: {}/{} - Done!".format(self.get_missing_outer_loop(), self.outer_iter))
            print("------> oID:{} - Done! Return: {}/{} were succesfull".format(ID, OK, self.inner_iter)) #could give a percentage here
        elif self.hierarchy == 'Inner':
            oID = self.get_outer_ID(ID)
            print("{}/{}  - Done!".format(self.get_missing_inner_loop(oID=oID), self.inner_iter))
            print("------> ID:{} - Done! Return: {}".format(ID, ret))
        elif self.hierarchy == 'Flat':
            print("{}/{}  - Done!".format(self.get_missing_outer_loop(), self.outer_iter))
            print("------> ID:{} - Done! Return: {}".format(ID, ret))
        else:
            print("Unknown hierarchy!")
            raise Exception
        sys.stdout.flush()

    '''-----------------------------METADATA--------------------------------'''
    '''
    set_hierarchy: sets the hierarchy of the experiment
    _reduce: reduces the structure of the experiment (recursive)
    reduce: reduces the structure of the experiment (wrapper)
    make_loop_dict: makes a dictionary of the inner and outer loops
    make_df: makes a dataframe of the experiment that will be used to store the status
    make_metadata: makes the metadata of the experiment (reduce, loop_dict, df)
    '''
    def set_hierarchy(self):
        '''
        Sets the hierarchy of the experiment.
        '''
        if self.force_flat: self.hierarchy = "Flat"
        if (self.oID is None) and (not self.force_flat): 
            if self.inner_iter > 1:  self.hierarchy = "Outer"
            else:                    self.hierarchy = "Flat"
        else:                        self.hierarchy = "Inner"
        print("Hierarchy: {}".format(self.hierarchy))

    #-----------------------------REDUCE--------------------------------
    @staticmethod
    def _reduce(struct):
        r = {}
        for k in struct.keys():
            if type(struct[k]) == str:
                r[k] = ExperimentStringParserClass(struct[k]).parsed_list if struct[k][0].isdigit() else struct[k]
            elif type(struct[k]) == list:
                l = []
                for e in struct[k]:
                    if type(e) == str and e[0].isdigit():
                        l.extend(ExperimentStringParserClass(e).parsed_list)
                    else:
                        l.append(e)
                r[k] = l
            elif type(struct[k]) == dict:
                r[k] = ExperimentManagerClass._reduce(struct[k])
            else:
                r[k] = struct[k]
        return r

    def reduce(self):
        self.experiments = self._reduce(self.experiments)

    #----------------------------------------------------------------------
    #-----------------------------LOOP_DICT--------------------------------
    def make_loop_dict(self):
        for k in self.experiments.keys():
            if type(self.experiments[k])==list:
                self.outer_loop_dict[k] = self.experiments[k]
            elif type(self.experiments[k])==dict:
                if (k == 'OuterParams'):
                    for kk in self.experiments[k].keys():
                        if type(self.experiments[k][kk])==list:
                            self.outer_loop_dict[kk] = self.experiments[k][kk]
                        else:
                            self.fixed_dict[kk] = self.experiments[k][kk]
                elif (k == 'InnerParams'):
                    for kk in self.experiments[k].keys():
                        if type(self.experiments[k][kk])==list:
                            self.inner_loop_dict[kk] = self.experiments[k][kk]
                        else:
                            self.fixed_dict[kk] = self.experiments[k][kk]
                else:
                    raise Exception("Wrong dictionary structure")
            else:
                self.fixed_dict[k] = self.experiments[k]

    #----------------------------------------------------------------------
    def apply_constriants(self):
        print("Trimming experiment df. Applying constraints...")
        for f in self.constraints:
            if not os.path.isfile(f):
                print("WARNING: Constraint file {} does not exist!".format(f))
                continue
            constraint_list = yaml.load(open(f, 'r'), Loader=yaml.FullLoader)
            for c in constraint_list:
                try :   
                    self.experiment_df = self.experiment_df.query(c)
                    print("Constraint {} applied!".format(c))
                    print("------> New length of experiment_df: {}".format(len(self.experiment_df)))
                except: print("WARNING: Constraint {} could not be applied!".format(c))
        self.experiment_df = self.experiment_df.reset_index(drop=True)
    #----------------------------------------------------------------------
    def make_df(self):
        #Makeing iter fields
        oKeys = list(self.outer_loop_dict.keys()) + list(self.fixed_dict.keys())                #keys for outer loop and fixed fields
        steps = list(product(*self.outer_loop_dict.values(),*self.inner_loop_dict.values()))    #steps for outer and inner loop
        keys = list(self.outer_loop_dict.keys()) + list(self.inner_loop_dict.keys())            #keys for outer and inner loop
        self.experiment_df = pd.DataFrame(steps, columns=keys)
        
        #Extending fixed fields
        for k in self.fixed_dict.keys():
            self.experiment_df[k] = self.fixed_dict[k]
        
        self.apply_constriants()
        
        #Adding oID field
        child_df = self.experiment_df
        child_df = child_df[oKeys].drop_duplicates(subset=oKeys) # drop duplicates from outer loop and fixed fields
        for i in range(len(child_df.index)):
            d = child_df.iloc[[i]].to_dict('records')[0]        # get the i-th row as a dictionary
            for k in d.keys(): d[k] = [d[k]]                    # convert the values to a list of values
            self.experiment_df.loc[ self.experiment_df[oKeys].isin(d).sum(1) == len(d.keys()), 
                                    'oID'] = i # add the oID to the child_df

        # Adding iID field
        for i in list(self.experiment_df['oID'].unique()):
            self.experiment_df.loc[self.experiment_df['oID']==i, 'iID'] = list(range(len(self.experiment_df.loc[self.experiment_df['oID']==i].index)))

        #Making oID and iID int, setting outer_iter and inner_iter
        self.experiment_df[['oID','iID']] = self.experiment_df[['oID','iID']].astype(int)
        self.outer_iter = self.experiment_df['oID'].max()+1
        self.inner_iter = self.experiment_df['iID'].max()+1

        #Adding ID, Status, Return fields
        IDs = [i for i in range(len(self.experiment_df))]
        status = [0 for i in range(len(self.experiment_df))]
        ret = [None for i in range(len(self.experiment_df))]
        self.experiment_df['ID'] = IDs
        self.experiment_df['Status'] = status
        self.experiment_df['Return'] = ret
    
    def make_metadata(self):
        self.reduce()
        self.make_loop_dict()
        self.make_df()
        self.set_hierarchy()

    '''-----------------------------CHECKPOINT--------------------------------'''
    '''
    check_checkpoint: checks if a checkpoint exists
    load_checkpoint: loads the checkpoint (if called in init it will also load the metadata)
    update_dataframe: updates the dataframe with the checkpoint
    store_checkpoint: stores the checkpoint
    '''

    def check_checkpoint(self):
        if os.path.isfile(self.checkpoint_path):
            return True
        else:
            return False

    def load_checkpoint(self, make_metadata=True):
        if make_metadata:
            self.load_experiment()
        self.experiment_df = pd.read_feather(self.checkpoint_path)
        if make_metadata:
            self.report_checkpoint()

    def update_dataframe(self):
        if self.check_checkpoint():
            self.load_checkpoint(make_metadata=False)
    
    def store_checkpoint(self):
        self.experiment_df.to_feather(self.checkpoint_path)
    
    def report_checkpoint(self):
        print("Checkpoint exists: {}".format(self.checkpoint_path))
        print("Checkpoint contains {} experiments".format(len(self.experiment_df.index)))
        print("Done experiments: {}".format(self.get_missing_loops()))
        print("Remaining experiments: {}".format(self.get_total_iter()-self.get_missing_loops()))
        if self.hierarchy=="Inner":
            stats = self.check_status()
            self.print_oID_status(self.oID, "INIT", stats)