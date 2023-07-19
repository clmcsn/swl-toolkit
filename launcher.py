import os
import time
import traceback
import multiprocessing.pool as mpp
from multiprocessing import Manager

import util.parsers.launcher as parsers
from util.os_utils import cd, cmd, current_utctime_string
import runner.stream_parsing as stream_parsing

import resource
resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

# TODO add data extraction below (if last oID, then extract data)

APP = os.getenv("APP")
if APP is None: parser = parsers.LauncherParserClass()
else:           parser = parsers.parsersDict[APP]()

def experiment_task(ID, parser, lock):
    try:
        book = parser.exp_book
        launcher_path = parser.args.launcher_path

        e = book.sample(ID)
        command = book.make_command(ID, e, parser.meta_dict)
        with cd(launcher_path):
            if APP=="vortex-run"    : ret = cmd(command, shell=True, check=False)
            elif APP=="vortex-tan"  : ret = stream_parsing.VortexTraceAnalysisClass(exp=e, output_file=e.make_result_fname()).run()
        book.commit(ID, ret, lock)
        return 0
    except Exception as e:
        #book.commit(ID, -1)
        traceback.print_tb(e.__traceback__)
        print(Exception, e)
        return 1

print("Making parent directory for experiment results...")
RESULT_PARENT_DIR = parser.args.output_dir if parser.args.output_dir else os.getcwd() + "/outputs/launcher_" + current_utctime_string()
_ = cmd('mkdir -p {}'.format(RESULT_PARENT_DIR))

parser.exp_book.set_output_dir(RESULT_PARENT_DIR)
print(parser.exp_book)
if parser.args.dry_run: exit(0)

#Setting the number of workers
if parser.exp_book.hierarchy == "Outer":    workers = parser.args.jobs if parser.exp_book.get_outer_loop_size() > parser.args.jobs else parser.exp_book.get_outer_loop_size()
elif parser.exp_book.hierarchy == "Inner":  workers = parser.args.cpus if parser.exp_book.get_inner_loop_size() > parser.args.cpus else parser.exp_book.get_inner_loop_size()
else:                                       workers = parser.args.cpus if parser.exp_book.get_outer_loop_size() > parser.args.cpus else parser.exp_book.get_outer_loop_size()

print("Actual number of workers: {}".format(workers))
print("Starting the experiments...")
FIRST_ITER = True
with Manager() as manager:
    lock = manager.Lock()
    with mpp.ThreadPool(workers) as pool:
        for i in parser.exp_book.get_missing_IDs(parser.args.oID):
            _ = pool.apply_async(experiment_task, args=(i, parser, lock))
            while( FIRST_ITER and (not parser.exp_book.check_status(ID=i)) and parser.args.lock_on_first): time.sleep(2) # Lock on the first experiment to finish to get the code compiled
            #if r.get(): exit(1)
            FIRST_ITER = False
        pool.close()
        pool.join()
print("All experiments finished!")