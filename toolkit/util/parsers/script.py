import argparse


class ScriptsParserClass():
    def __init__(self, args=None):
        self.parser = argparse.ArgumentParser(description='Gets options from command line.')
        self.init_parser()
        self.args = self.parser.parse_args(args) if args else self.parser.parse_args()
        self.check_args()
        self.init_attr()
        self.reduce_args()

    def init_parser(self):
        raise NotImplementedError

    def set_defaults(self):
        raise NotImplementedError

    def check_args(self):
        raise NotImplementedError

    def init_attr(self):
        pass

    def reduce_args(self):
        raise NotImplementedError
