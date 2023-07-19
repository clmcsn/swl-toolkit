import os
import shlex
import subprocess
import datetime

def non_blocking_cmd(text):
    '''
    Runs a command in a child subprocess and returns the process object.
    The program won't wait for the command to finish.

        Parameters:
            text (str): command to be executed in the NEW shell
        Returns:
            process (subprocess.Popen): process object to check process status
    '''
    cwd = str(os.getcwd())
    print( cwd + ": "+ " ".join(text.split()))
    command = shlex.split(text)
    process = subprocess.Popen( command, 
                                stdout = subprocess.PIPE, 
                                stderr = subprocess.STDOUT,
                                text = True,
                                universal_newlines = True)
    return process

def check_for_errors(retcode, process):
    '''
    Checks if the process returned an error code. If so, it prints the STDOUT
    and raises an exception.
        Parameters:
            retcode (int): return code of the process
            process (subprocess.Popen): process object to check process status
    '''
    if retcode!=0:
        for l in process.stdout:
            print(l)
        process.stdout.close()
        raise ValueError("An error occurred. Check STDOUT. Exiting...")

def cmd(text, check=True, shell=False, verbose=True):
    '''
    Runs a command in a child subprocess and returns the return code.
    The program will wait for the command to finish.
        Parameters:
            text (str): command to be executed in the NEW shell
            check (bool): if True, it checks for errors after the execution of the command
            shell (bool): if True, it executes the command in the current shell
        Returns:
            retcode (int): return code of the process
    '''
    cwd = str(os.getcwd())
    if verbose: print( cwd + ": "+ " ".join(text.split()), flush=True)
    if shell: command = text
    else: command = shlex.split(text)

    process = subprocess.Popen( command, 
                                stdout = subprocess.PIPE, 
                                stderr = subprocess.STDOUT,
                                text = True,
                                universal_newlines = True,
                                shell = shell)
    retcode = process.wait()
    if check: check_for_errors(retcode, process)
    process.stdout.close()
    return retcode

def mkdir(directory):
    '''
    Creates a directory if it does not exist. If it exists, it prints a message.
    Note: If any parent directory does not exist, it will be created.
        Parameters:
            directory (str): directory to be created 
    '''
    if os.path.isdir(directory): print("Directory {} is already present".format(directory))
    else: cmd('mkdir -p {}'.format(directory))

TIME_FORMAT = '%Y_%m_%d_%H_%M'
def current_utctime_string(template=TIME_FORMAT):
    '''
    Returns the current UTC time as a string.
        Parameters:
            template (str): template to format the time
        Returns:
            time (str): current UTC time as a string
    '''
    return datetime.datetime.now(datetime.timezone.utc).strftime(template)

class cd:
    """
    Context manager for changing the current working directory

    Methods
    ------------------------------------------------------------------------------
        __init__(self, newPath):
            Initializes the new working directory
        __enter__(self):
            Changes the current working directory
        __exit__(self, etype, value, traceback):
            Changes the current working directory back to the original one
    """
    def __init__(self, newPath):
        '''
        Initializes the new working directory
            Parameters:
                newPath (str): new working directory
        '''
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)