import subprocess as sp
import os
import shlex
import traceback

import pandas as pd

from . import experiments as exs

#TODO tests:
# normal working ls
# faulty command (?) (ls -l /dev/null)
# implement timers
# implement trace analysis child class

class StreamParsingClass(object):
    """
    Base class for parsing the stream of data coming from a command.
    This class should be inherited by a child class, which implements specific parsing logic depending on the command.
    Constructor arguments:
        output_path : str   - path to the output directory
        timeout : int       - timeout for the command
    Methods:
        run                                 - runs the command and parses the output
        run_command                         - runs the command
        parse                               - parses the output line by line 
        parse_line                          - parses a single line of the output
        reduce_func                         - process the line of the output   (must be implemented in the child class and assigned in the constructor)
        sterr_process_func                  - process the stderr stream        (must be implemented in the child class and assigned in the constructor)
        make_stderr_process_func_arg_dict   - returns a dictionary of arguments for the stderr_process_func method                  (to be overridden)
        make_command                        - creates the command to be run from self.cmd_arg_dict, which must be construceted in the child constructor
        print_command                       - prints the command to be run
        cmd_exception_handler               - handles the exception raised by the command                                           (to be overridden)
        program_exception_handler           - handles the exception raised by this program (e.g. when there is a bug in the code)
        set_timer                           - sets the timer for the command
        
        is_exeption(line)                   - returns True if the line is an exception, False otherwise                             (to be overridden)
    """
    def __init__(self, output_path : str, timeout : int = 0):
        # mandatory constructor arguments
        self.output_path = output_path if output_path[-1] == "/" else output_path + "/"
        assert self.output_path != None, "Path is not specified"

        # optional constructor arguments
        self.timeout = timeout  # in seconds

        # other attributes
        self.stderr_log_file = self.output_path + "process.stderr.log"
        self.log_file = self.output_path + "process.log"
        self.save_to_file = True
        self.CMD_TEMPLATE = ""
        self.command = ""

        self.cmd_arg_dict = {}
        self.exceptions_list = []
        self.reduce_func = self.dummy_reduce_func
        self.sterr_process_func = self.base_stderr_process_func

    @staticmethod
    def dummy_reduce_func(line):
        print(line)

    @staticmethod
    def base_stderr_process_func(out_file_path, stderr_stream, stdout_stream=None):
        with open(out_file_path, "w") as f:
            if stdout_stream:
                for line in stdout_stream:
                    f.write(line)
            for line in stderr_stream:
                print(line.strip())
                f.write(line)
    
    # ad-hoc methods for child classes, to be overridden if needed
    def make_stderr_process_func_arg_dict(self):
        d = {"out_file_path" : self.stderr_log_file,
             "stderr_stream" : self.process.stderr}
        return d

    def print_command(self):
        cwd = str(os.getcwd())
        print( cwd + ": "+ " ".join(self.command.split()))
    
    def make_command(self):
        self.command = self.CMD_TEMPLATE.format(**self.cmd_arg_dict)

    def run_command(self):
        if self.save_to_file:
            self.dump_file = open(self.log_file, "w")
        self.make_command()
        self.print_command()
        """ Quick and dirty hack to handle environment variables in the command."""
        self.command = shlex.split(self.command)
        self.env = os.environ.copy()
        for i in range(len(self.command)):
            if 'CONFIGS=' in self.command[i]:
                env_var = self.command[i].split('=',1)
                self.env[env_var[0]] = env_var[1]
                self.command.remove(self.command[i])
            else:
                break
        """---------------------------------------------------------------------"""
        self.process = sp.Popen(    self.command,
                                    stdout=sp.PIPE,
                                    stderr=sp.PIPE,
                                    env=self.env,
                                    text=True,
                                    universal_newlines=True)
        
    def set_timer(self):
        if self.timeout is None: return

    def reset_timer(self):
        if self.timeout is None: return

    def is_exeption(self, line):
        for exeption in self.exceptions_list:
            if exeption(line):  return True
        return False

    def parse_line(self, line):
        if self.is_exeption(line): return
        self.reduce_func(line)
    
    def parse(self):
        self.set_timer()
        for line in self.process.stdout:
            if self.save_to_file: self.dump_file.write(line)
            self.reset_timer()
            self.parse_line(line)
    
    @staticmethod
    def program_exception_handler(e):
        print("Exception occured while handling the command.")
        traceback.print_tb(e.__traceback__)
        print(Exception, e, "\n")
        return 1

    def cmd_exception_handler(self, r):
        print("An error occurred with retcode: {}. Check STDERR. Exiting...".format(r))
    
    def run(self):
        try :
            self.run_command()
            self.parse()
        except Exception as e:
            self.program_exception_handler(e)
        ret = self.process.wait()
        self.sterr_process_func(**self.make_stderr_process_func_arg_dict())
        if ret != 0:
            self.cmd_exception_handler(ret)
        return ret

    def __str__(self) -> str:
        raise NotImplementedError


class LsStreamParsingClass(StreamParsingClass):
    """
    Child class of StreamParsingClass for parsing the output of the ls command.
    Just an example of how to use the StreamParsingClass.
    """
    def __init__(self,  output_path : str, timeout : int = 0, 
                        path : str = ".", args : dict = {}):
        super().__init__(output_path=output_path, timeout=timeout)
        if args: self.cmd_arg_dict.update(args)
        self.CMD_TEMPLATE = "ls {path} -la"
        self.exceptions_list = [self.is_total]
        self.reduce_func = self.ls_reduce_func
        self.sterr_process_func = self.stderr_process_func

        # ad-hoc attributes
        self.path = path
        self.cmd_arg_dict["path"] = self.path

        self.iter_dict = {}
        self.df = pd.DataFrame({})

    @staticmethod
    def stderr_process_func(out_file_path,stderr_stream):
        with open(out_file_path, "w") as f:
            for line in stderr_stream:
                f.write(line)

    @staticmethod
    def is_total(line):
        if line.startswith("total"): return True
        else: return False

    # extract list of user access rights from file only
    def ls_reduce_func(self, line):
        lline = line.split()
        if not self.add_if_file(lline): return
        self.add_file_properties(lline)
        self.add_user_access_rights(lline)
        self.df = pd.concat([self.df, pd.DataFrame(self.iter_dict, index=[0])], ignore_index=True)

    def add_if_file(self, lline):
        obj = lline[-1]
        full_obj_path = self.path + "/" + obj
        # check could have been done as: if lline[0][0] == "-"
        if os.path.isfile(full_obj_path):
            self.iter_dict["path"]  = full_obj_path
            self.iter_dict["fname"] = obj
            return True
        else: return False

    def add_file_properties(self, lline):
        self.iter_dict["size"] = lline[4]
        self.iter_dict["user"] = lline[2]
        self.iter_dict["group"] = lline[3]

    def add_user_access_rights(self, lline):
        self.iter_dict.update(self.add_permissions(lline[0][1:4], "user"))

    @staticmethod
    def add_permissions(permissions : str, who: str):
        d = {"r" : False, "w" : False, "x" : False} 
        if len(permissions) != 3: raise ValueError("_permissions_ string must be 3 characters long")
        if who not in ["user", "group", "others"]: raise ValueError("_who_ must be one of the following: user, group, others")
        for k in d.keys():
            if k in permissions: d[k] = True
        e = {who + "_" + k : v for k, v in d.items()}
        return e

    def __str__(self) -> str:
        return str(self.df)
 
class VortexTraceAnalysisClass(StreamParsingClass):
    def __init__(self, output_file: str, timeout: int = 0,
                        args: dict = {}, exp : exs.ExperimentClass = exs.ExperimentClass({})):
        self.output_file = output_file + ".feather"
        super().__init__(os.path.dirname(self.output_file), timeout)
        if args:
            args['debug'] = 3 # add debug flag!
            self.cmd_arg_dict.update(args)
            self.experiment = exs.ExperimentClass(struct= self.cmd_arg_dict, res_path=self.output_path)
        # reduce args here
        elif exp is not None:
            self.experiment = exp
            self.experiment.update_key("debug", 3)
        else:
            raise ValueError("Either args or exp must be provided.")
        self.exceptions_list = [self.is_not_trace]
        self.reduce_func = self.vx_trace_reduce_func

        self.iter_dict = {}
        self.df = pd.DataFrame({})

    @staticmethod
    def is_not_trace(line):
        if      line.startswith("TRACE"): return False
        elif    line.startswith("DEBUG"): return False
        elif    line.startswith("PERF"):  return False
        else: return True

    def make_command(self):
        self.command = self.experiment.get_cmd_str()

    def make_stderr_process_func_arg_dict(self):
        d = super().make_stderr_process_func_arg_dict()
        d["stdout_stream"] = self.process.stdout
        return d

    @staticmethod
    def get_instr_dict(lline):
        d = {}
        for l in lline:
            if l.startswith("coreid="):
                d["core"]   = int(l.split("=")[1][:-1]) # remove the trailing comma
            elif l.startswith("wid="):
                d["warp"]   = int(l.split("=")[1][:-1])
            elif l.startswith("PC="):
                try: # if the PC doesn't have a trailing comma
                    d["PC"]     = int(l.split("=")[1], base=16)
                    d["PC-id"]  = l.split("=")[1]
                except:
                    d["PC"]     = int(l.split("=")[1][2:-1], base=16)
                    d["PC-id"]  = l.split("=")[1][2:-1]
            elif l.startswith("(#"):
                d["eID"]    = int(l[2:-1])
            elif l.startswith("tmask="):
                d["tmask"]  = l.split("=")[1][:-1]
            else:
                pass
        return d

    @staticmethod
    def get_trace_line_dict(line):
        lline = line.split()
        d = {}
        d["time-stmp"]  = int(lline[1][:-1]) # remove the trailing semicolon
        d.update(VortexTraceAnalysisClass.get_instr_dict(lline[2:]))
        return d

    def register_schedule(self, d):
        self.df.loc[self.df["eID"] == d["eID"], "schedule-stmp"] = d["time-stmp"]

    def register_commit(self, d):
        schedule_stmp = self.df.loc[self.df["eID"] == d["eID"], "schedule-stmp"].values[0]
        commit_stmp = d["time-stmp"]
        self.df.loc[self.df["eID"] == d["eID"], "total-exec-time"] = commit_stmp - schedule_stmp

    def reduce_trace(self, line):
        if "pipeline-schedule:" in line:
            self.register_schedule(self.get_trace_line_dict(line))
        elif "pipeline-commit:" in line:
            self.register_commit(self.get_trace_line_dict(line))
        else:
            pass

    def register_new_instruction(self):
        self.df = pd.concat([self.df, pd.DataFrame(self.iter_dict, index=[0])], ignore_index=True)

    def reduce_debug(self, line):
        if "Fetch:" in line:
            self.iter_dict = self.get_instr_dict(line.split()[2:])
        elif " Instr " in line:
            self.iter_dict["instr"] = line.split()[3][:-1].lower() # remove the trailing colon
            self.register_new_instruction()
        else:
            pass

    def vx_trace_reduce_func(self, line):
        if line.startswith("TRACE"):
            self.reduce_trace(line)
        elif line.startswith("DEBUG"):
            self.reduce_debug(line)

    def run(self):
        ret = super().run()
        if ret == 0 or ret == 2:
            if not self.df.empty:
                self.df.to_feather(self.output_file)
        return ret

class DotDumpRISCVParsingClass(StreamParsingClass):
    def __init__(self, output_path: str, timeout: int = 0,
                    args: dict = {}, dump_file : str = ""):
        super().__init__(output_path, timeout)
        self.output_file = self.output_path + os.path.basename(dump_file) + ".feather"
        if args: self.cmd_arg_dict.update(args)
        self.CMD_TEMPLATE = "cat {dump_file}"
        self.exceptions_list = [self.is_out_of_code_section, self.is_function_name]
        self.reduce_func = self.get_instruction_stats

        # ad-hoc attributes
        if dump_file == "": raise ValueError("Dump file not specified.")
        self.dump_file = dump_file
        self.cmd_arg_dict["dump_file"] = self.dump_file

        self.format = "ELF32-riscv"
        self.in_code_section = False
        self.func_name = "---"
        self.iter_dict = {}
        self.df = pd.DataFrame({})

    def is_file_format(self, line):
        if not self.in_code_section:
            lline = line.strip().split()
            if len(lline) == 4:
                if lline[0].endswith("elf:"):
                    if lline[-1] != "ELF32-riscv":
                        print("Warning: file format is not ELF32-riscv")
                        print("File format is: {}".format(lline[-1]))
                        self.format = lline[-1]
                    return True
        return False

    def is_out_of_code_section(self, line):
        if line.strip() == "": return True
        if self.is_file_format(line): return True
        if line.startswith("Disassembly of section"):
            if (".text:" in line) or (".init:" in line):
                self.in_code_section = True
                return True
            else:
                self.in_code_section = False
                return True
        return not self.in_code_section
        
    def is_function_name(self, line):
        if self.in_code_section:
            lline = line.strip().split()
            if len(lline) == 2:
                if self.format == "ELF32-riscv":            self.func_name = lline[1][:-1]
                elif self.format == "elf32-littleriscv":    self.func_name = lline[1][1:-2] # remove < and >: e.g. <main>: -> main
                return True
        return False
    
    @staticmethod
    def remap_assembly(instr):
        if instr=="vx_pred":
            return "tmc"
        elif instr.startswith("vx_"):
            return instr[3:]
        else:
            return instr
        
    def get_instruction_stats(self, line):
        lline = line.strip().split()
        self.iter_dict["PC-id"] = "0x" + lline[0][:-1]
        if self.format == "ELF32-riscv":            self.iter_dict["instr"] = self.remap_assembly(lline[5])
        elif self.format == "elf32-littleriscv":    self.iter_dict["instr"] = self.remap_assembly(lline[2])
        self.iter_dict["func"] = self.func_name
        self.df = pd.concat([self.df, pd.DataFrame(self.iter_dict, index=[0])], ignore_index=True)

    def run(self):
        ret = super().run()
        if ret == 0:
            self.df.to_feather(self.output_file)
        return ret
    
    def get_df(self):
        r = self.run()
        if r == 0:
            return self.df
        else:
            raise ValueError("Error while parsing the dump file.")

class AreaRptParsingClass(StreamParsingClass):
    def __init__(self, output_path: str, timeout: int = 0,
                    args: dict = {}, rpt_file : str = "", depth : int = 0):
        super().__init__(output_path, timeout)
        self.output_file = self.output_path + os.path.basename(rpt_file) + ".feather"
        if args: self.cmd_arg_dict.update(args)
        self.CMD_TEMPLATE = "cat {rpt_file}"
        self.exceptions_list = [self.is_out_of_area_section, self.is_too_low_hierarchy]
        self.reduce_func = self.get_area_stats
        
        # ad-hoc attributes
        if rpt_file == "": raise ValueError("RPT file not specified.")
        self.rpt_file = rpt_file
        self.depth = depth
        self.cmd_arg_dict["rpt_file"] = self.rpt_file
        self.cmd_arg_dict["depth"] = self.depth
        self.in_area_section = False
        self.iter_depth = -1
        self.iter_parent_name = []
        self.df = pd.DataFrame({})
        self.leaf_df = pd.DataFrame({})
        self.iter_dict = {}
        self.iter_dict_prev = {"depth" : -1}


    def is_out_of_area_section(self, line):
        if self.in_area_section:
            return False
        else:
            if line.startswith("-------"):
                self.in_area_section = True
                return True
            else:
                return True
    def is_too_low_hierarchy(self, line):
        if self.in_area_section:
            if self.depth == -1: return False
            left_spaces = len(line) - len(line.lstrip(' '))
            depth = left_spaces // 2
            if depth > self.depth:
                return True
        return False

    def get_area_stats(self, line):
        depth = (len(line) - len(line.lstrip(' '))) // 2
        lline = line.strip().split()
        if len(lline) == 6:
            self.iter_dict["instance"]      = lline[0]
            self.iter_dict["module"]        = lline[1]
            self.iter_dict["parent"]        = self.iter_parent_name[depth-1]
            self.iter_dict["cell_count"]    = int(lline[2])
            self.iter_dict["cell_area"]     = float(lline[3])
            self.iter_dict["net_area"]      = float(lline[4])
            self.iter_dict["total_area"]    = float(lline[5])
            self.iter_dict["depth"]         = depth
        elif len(lline) == 5:
            self.iter_dict["instance"]      = lline[0]
            self.iter_dict["module"]        = lline[0]
            self.iter_dict["parent"]        = lline[0]
            self.iter_dict["cell_count"]    = int(lline[1])
            self.iter_dict["cell_area"]     = float(lline[2])
            self.iter_dict["net_area"]      = float(lline[3])
            self.iter_dict["total_area"]    = float(lline[4])
            self.iter_dict["depth"]         = depth
        self.df = pd.concat([self.df, pd.DataFrame(self.iter_dict, index=[0])], ignore_index=True)
        self.make_leaf_df()
        if depth > self.iter_depth:
            self.iter_parent_name.append(self.iter_dict["instance"])
            self.iter_depth += 1
        elif depth < self.iter_depth:
            for i in range(self.iter_depth - depth):
                self.iter_parent_name.pop()
            self.iter_parent_name[-1] = self.iter_dict["instance"]
            self.iter_depth = depth
        else:
            self.iter_parent_name[-1] = self.iter_dict["instance"]
    
    def make_leaf_df(self):
        if self.iter_dict["depth"] <= self.iter_dict_prev["depth"]:
            for i in range(len(self.iter_parent_name)):
                self.iter_dict_prev["depth_{}".format(i)] = self.iter_parent_name[i]
            self.leaf_df = pd.concat([self.leaf_df, pd.DataFrame(self.iter_dict_prev, index=[0])], ignore_index=True)
        self.iter_dict_prev = self.iter_dict.copy()


    def run(self):
        ret = super().run()
        if ret == 0:
            self.df.to_feather(self.output_file)
            self.leaf_df.to_feather(self.output_file.replace(".feather", "_leaf.feather"))
            self.leaf_df.to_csv(self.output_file.replace(".feather", "_leaf.csv"))
        return ret
