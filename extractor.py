import os
import da.data_analysis as da
import util.parsers.extractor as parsers

APP = os.getenv("APP")
if APP is None: raise Exception("APP environment variable not set. No default parser available.")
else:
    parser = parsers.ExtractorParserClass()
    extractor = da.extractorsDict[APP](parser.args.output_dir, parser.args.app)

extractor.extract()
if parser.args.correct: extractor.add_extraction_metadata_to_checkpoint()