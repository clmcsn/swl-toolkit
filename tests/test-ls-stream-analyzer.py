import scripts.toolkit.stream_parsing as stream_parsing
import os
from util.os_utils import cmd

otp = os.path.realpath("./outputs/test_ls/")

def test_ls_home():
    output_test_path = os.path.realpath(otp + "/home_test/")
    _ = cmd('mkdir -p {}'.format(output_test_path))

    USER_HOME = os.path.expanduser("~")
    ss_parser = stream_parsing.LsStreamParsingClass(output_path=output_test_path, path=USER_HOME)
    ss_parser.run()
    print(ss_parser)

def test_ls_exit():
    output_test_path = os.path.realpath(otp + "/devnull_test/")
    _ = cmd('mkdir -p {}'.format(output_test_path))

    ss_parser = stream_parsing.LsStreamParsingClass(output_path=output_test_path, path="/something/that/does/not/exist")
    ss_parser.run()

if __name__ == "__main__":
    _ = cmd("rm -rf {}".format(otp))
    test_ls_home()
    # check test_ls_home output
    test_ls_exit()
    # check test_ls_exit output
