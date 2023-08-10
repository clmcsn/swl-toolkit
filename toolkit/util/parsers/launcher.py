import yaml
import os

from util.parsers.script import ScriptsParserClass
from scripts.toolkit.experiments import ExperimentManagerClass, ExperimentStringParserClass
from util.os_utils import cmd, current_utctime_string


class LauncherParserClass(ScriptsParserClass):
    def __init__(self):
        self.exp_book = None
        self.dispatcher = False
        self.meta_dict = {}
        try : self.constraints
        except : self.constraints = []
        super(LauncherParserClass, self).__init__()

    def init_parser(self):
        self.parser.add_argument("-f", "--conf_file", action="store", type=str, help="Configuration file to run a set of experiment.")
        self.parser.add_argument("-C", "--constr_file", action="store", type=str, help="Constraint file to run a set of experiment.")
        self.parser.add_argument("-l", "--launcher_script", action="store", type=str, help="Script that executes the single experiment iteration.")
        self.parser.add_argument("-p", "--launcher_path", action="store", type=str, help="Path to the launcher script.")
        self.parser.add_argument("-a", "--app", action="store", type=str, help="C application to run the experiment on.")
        self.parser.add_argument("-o", "--output_dir", action="store", type=str, help="Output direcory for the results.")
        self.parser.add_argument("--cpus", action="store", type=int, help="Number of CPUs to use for the simulation.")
        self.parser.add_argument("--jobs", action="store", type=int, help="Number of jobs to use for the simulation.")
        self.parser.add_argument("--oID", action="store", type=int, help="ID of the batch of the experiment to run.")
        self.parser.add_argument("--dry_run", action="store_true", help="Prints the experiment book without running it.")
        self.parser.add_argument("--lock_on_first", action="store_true", help="Locks the launcher on the first experiment to finish.")
        self.parser.add_argument("--force_flat_execution", action="store_true", help="Disables the lock on the launcher.")
        self.set_defaults()

    def set_defaults(self):
        self.parser.set_defaults(output_dir=None)
        self.parser.set_defaults(app=None)
        self.parser.set_defaults(cpus=1)
        self.parser.set_defaults(jobs=1)
        self.parser.set_defaults(oID=None)
        self.parser.set_defaults(dry_run=False)
        self.parser.set_defaults(lock_on_first=False)
        self.parser.set_defaults(force_flat_execution=False)

    def reduce_args(self):
        """--conf_file"""
        if self.args.conf_file:
            with open(self.args.conf_file,"r") as stream:
                blob = yaml.safe_load(stream)
                self.exp_book = ExperimentManagerClass( struct = blob, 
                                                        path = self.args.output_dir, 
                                                        oID=self.args.oID, 
                                                        constraints=self.constraints,
                                                        force_flat=self.args.force_flat_execution)
                self.args.app = self.exp_book.get_app_name()

        if self.args.oID:
            self.dispatch = True
        
        for a in vars(self.args):
            if getattr(self.args, a) is not None:
                self.meta_dict[a] = getattr(self.args, a)
                print("{}: {} = {}".format(self.__class__.__name__, a, getattr(self.args, a)))
            
    def check_args(self):
        if self.args.conf_file:
            if not os.path.isfile(self.args.conf_file): raise FileNotFoundError("{} file doesn't exist".format(self.args.conf_file))
        if self.args.output_dir:
            if not os.path.isdir(self.args.output_dir): _ = cmd('mkdir -p {}'.format(self.args.output_dir))
        if (not self.args.app) and (not self.args.conf_file):
            raise TypeError("No application to simulate specified.")

class VortexLauncherParserClass(LauncherParserClass):
    def __init__(self):
        self.constraints = ["inputs/constraints/vortex_exp_constr.yml"]
        super(VortexLauncherParserClass, self).__init__()
    
    @staticmethod
    def int_str(s):
        try:
            return int(s)
        except ValueError:
            return s

    def init_parser(self):
        LauncherParserClass.init_parser(self)
        self.parser.add_argument("-d", "--driver", action="store", type=str, nargs="+", help="Driver of the simulation to evaluate the experiment. Can be a list of drivers.")
        self.parser.add_argument("-t", "--threads", action="store", type=self.int_str, help="Number of hardware threads, can be a list of parameters for make_log_list generation.")
        self.parser.add_argument("-w", "--warps", action="store", type=self.int_str, help="Number of hardware context for warps, can be a list of parameters for range() list generation.")
        self.parser.add_argument("--clusters", action="store", type=self.int_str, help="Number of hardware clusters, can be a list of parameters for range() list generation.")
        self.parser.add_argument("-c", "--cores", action="store", type=self.int_str, help="Number of hardware cores, can be a list of parameters for range() list generation.")
        self.parser.add_argument("-b", "--local_worksize", action="store", type=self.int_str, help="Number of software trheads per block (local worksize), can be a list of parameters for range() list generation.")
        self.parser.add_argument("-l2", "--l2cache", action="store_true", help="Instanciate L2.")
        self.parser.add_argument("--sweep_l2cache", action="store_true", help="Sweep L2 option.")
        self.parser.add_argument("-l3", "--l3cache", action="store_true", help="Instanciate L3.")
        self.parser.add_argument("--sweep_l3cache", action="store_true", help="Sweep L3 option.")
        self.parser.add_argument("-n", "--workload_size", action="store", type=self.int_str, help="Number of element to be processed by the kernel, can be a list of parameters for range() or make_log_list list generation.")
        self.parser.add_argument("--input_list", action="store", type=str, nargs="+", help="List of names for the input files.")

    def set_defaults(self):
        LauncherParserClass.set_defaults(self)    
        self.parser.set_defaults(launcher_script="./ci/blackbox.sh")
        self.parser.set_defaults(launcher_path="../")
        self.parser.set_defaults(output_dir=os.getcwd() + "/outputs/launcher_" + current_utctime_string() + "/")
        self.parser.set_defaults(lock_on_first=False)
        self.parser.set_defaults(constr_file=self.constraints)
    
    def reduce_args(self):
        """--constraints"""
        if self.args.constr_file != self.constraints:
            self.constraints.append(self.args.constr_file)    
        LauncherParserClass.reduce_args(self)
        
        """--threads"""
        if self.args.threads:
            threads = [self.args.threads] if type(self.args.threads)==int else ExperimentStringParserClass(self.args.threads).parsed_list
            self.exp_book.key_update(key="threads", value=threads) 
        """--warps"""
        if self.args.warps:
            warps = [self.args.warps] if type(self.args.warps)==int else ExperimentStringParserClass(self.args.warps).parsed_list
            self.exp_book.key_update(key="warps", value=warps) 
        """--cores"""
        if self.args.cores:
            cores = [self.args.cores] if type(self.args.cores)==int else ExperimentStringParserClass(self.args.cores).parsed_list
            self.exp_book.key_update(key="cores", value=cores)
        """--local_worksize"""
        if self.args.local_worksize:
            lws = ExperimentStringParserClass(self.args.local_worksize)
            self.exp_book.key_update(key="local_worksize", value=lws)
        """--sweep_l2cache"""
        if self.args.sweep_l2cache:
            self.exp_book.key_update(key="l2cache", value=[False,True])
        """--sweep_l3cache"""
        if self.args.sweep_l3cache:
            self.exp_book.key_update(key="l3cache", value=[False,True])
        """--workload_size"""
        if self.args.workload_size:
            wls = ExperimentStringParserClass(self.args.workload_size)
            self.exp_book.key_update(key="workload_size", value=wls)
        
        self.exp_book.reduce()
    
parsersDict = {
    "vortex-run": VortexLauncherParserClass,
    "vortex-tan": VortexLauncherParserClass
}