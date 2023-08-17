import os
import yaml

from .script import ScriptsParserClass

class ExtractorParserClass(ScriptsParserClass):
    def __init__(self):
        super(ExtractorParserClass, self).__init__()

    def init_parser(self):
        self.parser.add_argument("-o", "--output_dir", action="store", type=str, help="Output direcory for the results.")
        self.parser.add_argument("-a", "--app", action="store", type=str, help="C application to run the experiment on.")
        self.parser.add_argument("-f", "--yml_file", action="store", type=str, help="YML file with the experiment database.")
    
    def set_defaults(self):
        self.parser.set_defaults(output_dir=None)
        self.parser.set_defaults(app=None)
        self.parser.set_defaults(yml_file='')

    def reduce_args(self):
        if self.args.app is None:
            dump_file = os.path.join(self.args.output_dir, "experiments.dump.yml")
            if not os.path.isfile(dump_file): raise FileNotFoundError(dump_file)
            with open(dump_file, "r") as f:
                dump = yaml.safe_load(f)
            self.args.app = dump["app"]

    def check_args(self):
        if not os.path.isdir(self.args.output_dir): raise FileNotFoundError(self.args.output_dir)