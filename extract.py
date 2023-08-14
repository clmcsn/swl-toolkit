import os
from toolkit.data_analysis import data_analysis as da
from toolkit.util.parsers import extractor as parsers

APP = os.getenv("APP")
if APP is None: raise Exception("APP environment variable not set. No default parser available.")
else:
    parser = parsers.ExtractorParserClass()
    extractor = da.extractorsDict[APP](parser.args.output_dir, parser.args.app)

extractor.extract()