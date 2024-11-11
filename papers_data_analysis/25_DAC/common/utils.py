"""Function utils"""

import os
from typing import List


def get_result_dirs(makefile_dir: str) -> List[str]:
    """Get the list of directories with results"""
    if not os.path.isdir(makefile_dir):
        raise ValueError('Invalid directory')
    if not os.path.exists(os.path.join(makefile_dir, 'Makefile')):
        raise ValueError('Invalid directory')
    # Parse the Makefile
    with open(os.path.join(makefile_dir, 'Makefile'), 'r') as f:
        lines = f.readlines()
    res_dirs = []
    for line in lines:
        if 'RES' in line:
            res_list = line.split('=')[1].strip()
            for res in res_list.split(' '):
                res_dirs.append(res)
    return res_dirs
