import os
import yaml

from util.parsers.script import ScriptsParserClass
from util.os_utils import cmd

class DataAnalysisParserClass(ScriptsParserClass):
    def __init__(self, args=None):
        super(DataAnalysisParserClass, self).__init__(args)
    def init_parser(self):
        self.parser.add_argument("-p", "--res_path", action="store", type=str, help="Result path")
        self.parser.add_argument("-c", "--clean", action="store_true", help="Remove plot directory")
    def set_defaults(self):
        self.parser.set_defaults(res_path=None)
    def check_args(self):
        if not os.path.isdir(self.args.res_path): raise FileNotFoundError("{} directory doesn't exixst".format(self.args.res_path))
    def reduce_args(self):
        if self.args.clean: cmd("rm -rf {}".format(self.args.res_path+"plots/"))