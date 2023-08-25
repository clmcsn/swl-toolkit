import os
from toolkit.data_analysis import data_analysis as da
from toolkit.util.parsers import extractor as parsers

parser = parsers.ExtractorParserClass()
extractor = da.extractorsDict[parser.args.mode](    parser.args.output_dir, 
                                                    parser.args.app, 
                                                    yml_file=parser.args.yml_file)

extractor.extract()