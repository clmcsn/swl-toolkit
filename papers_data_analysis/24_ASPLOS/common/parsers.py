"""Parser for plot scripts"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from toolkit.util.parsers.script import ScriptsParserClass  # noqa: E402
from . import defines as CDEFS  # noqa: E402


class ParserClass(ScriptsParserClass):
    """Parser class for plot scripts"""
    def __init__(self, caller_path: str = ""):
        """Constructor for ParserClass"""
        self.caller_path = caller_path
        super().__init__()

    def init_parser(self):
        """Initialize parser"""
        self.parser.add_argument('-r', '--results_dir', action='store', type=str,
                                 help='Results directory')
        self.parser.add_argument('-p', '--plots_dir', action='store', type=str,
                                 help='Plots directory')
        self.parser.add_argument('--figure_name', action='store', type=str,
                                 help='Figure name')
        self.set_defaults()

    def set_defaults(self):
        """Set default values"""
        self.parser.set_defaults(results_dir=os.path.join(self.caller_path, CDEFS.RES_DIR))
        self.parser.set_defaults(plots_dir=os.path.join(self.caller_path, CDEFS.PLOT_DIR))
        self.parser.set_defaults(figure_name=CDEFS.FIG_NAME)

    def check_args(self):
        """Check if the arguments are valid"""
        if not os.path.isdir(self.args.results_dir):
            print('Invalid results directory {}'.format(self.args.results_dir))
            raise ValueError('Invalid results directory')
        if not os.path.isdir(self.args.plots_dir):
            os.makedirs(self.args.plots_dir, exist_ok=True)

    def reduce_args(self):
        """Reduce the arguments"""
        self.args.results_dir = os.path.abspath(self.args.results_dir)
        self.args.plots_dir = os.path.abspath(self.args.plots_dir)
