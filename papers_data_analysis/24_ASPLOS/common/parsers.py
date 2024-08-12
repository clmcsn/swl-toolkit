"""Parser for plot scripts"""

import os

from toolkit.util.parsers.script import ScriptsParserClass  # noqa: E402
from . import defines as CDEFS  # noqa: E402


class ParserClass(ScriptsParserClass):
    """Parser class for plot scripts"""
    def __init__(self):
        """Constructor for ParserClass"""
        super().__init__()

    def init_parser(self):
        """Initialize parser"""
        self.parser.add_argument('-r', '--results_dir', action='store', type=str,
                                 help='Results directory')
        self.parser.add_argument('-p', '--plots_dir', action='store', type=str,
                                 help='Plots directory')

    def set_defaults(self):
        """Set default values"""
        self.parser.set_defaults(results_dir=CDEFS.RES_DIR)
        self.parser.set_defaults(plots_dir=CDEFS.PLOT_DIR)

    def check_args(self):
        """Check if the arguments are valid"""
        if not os.path.isdir(self.args.results_dir):
            raise ValueError('Invalid results directory')
        if not os.path.isdir(self.args.plots_dir):
            os.makedirs(self.args.plots_dir, exist_ok=True)
