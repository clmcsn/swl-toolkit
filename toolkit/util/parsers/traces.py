from .script import ScriptsParserClass

import os

from util.os_utils import mkdir, current_utctime_string

class TracesParserClass(ScriptsParserClass):
    def __init__(self, args=None):
        super(TracesParserClass, self).__init__(args)
    
    def init_parser(self):
        self.parser.add_argument("-o", "--output_dir", action="store", type=str, help="Output direcory for the results.")
        self.parser.add_argument("--cores", action="store", type=int, help="Core to trim the traces for.")
        self.parser.add_argument("--warps", action="store", type=int, help="Core to trim the traces for.")
        self.parser.add_argument("-f", "--trace_file", action="store", type=str, help="Original trace file.")
        self.set_defaults()
    
    def set_defaults(self):
        self.parser.set_defaults(output_dir="./outputs/traces_"+current_utctime_string()+"/")
        self.parser.set_defaults(cores=1)
        self.parser.set_defaults(warps=1)
        self.parser.set_defaults(trace_file="../run.log")

    def reduce_args(self):
        pass

    def check_args(self):
        if not os.path.isdir(self.args.output_dir): mkdir(self.args.output_dir)
        if not os.path.isfile(self.args.trace_file): raise FileNotFoundError(self.args.trace_file)