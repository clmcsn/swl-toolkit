import scripts.toolkit.stream_parsing as stream_parsing
import os
from util.os_utils import cmd

itp = os.path.realpath("./inputs/kernel_assembly/vecadd")
otp = os.path.realpath("./outputs/test_dotdump_vecadd/")

def test_vecadd():
    output_test_path = os.path.realpath(otp + "/vecadd_test/")
    _ = cmd('mkdir -p {}'.format(output_test_path))

    ss_parser = stream_parsing.DotDumpRISCVParsingClass(output_path=output_test_path, dump_file=itp+"/vecadd.dump")
    df = ss_parser.get_df()
    ##print(df)

if __name__ == "__main__":
    _ = cmd("rm -rf {}".format(otp))
    test_vecadd()
    # check output