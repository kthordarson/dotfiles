#!/usr/bin/python3

import os
import time
import argparse
from pathlib import Path
from loguru import logger
from datetime import datetime
def get_tree(path, filelist):
    path = Path(path)
    if path.is_symlink():
        logger.warning(f'[symlink] skipping {path}')
    else:
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False) and not entry.is_symlink():
                try:
                    get_tree(entry.path, filelist)
                    filelist.append((entry, entry.stat().st_ctime))
                except Exception as e:
                    logger.error(f'[err] {e} entry:{entry} entry.is_symlink():{entry.is_symlink()}')
            else:
                if entry.is_file and not entry.is_symlink():
                    filelist.append((entry, entry.stat().st_ctime))
                # try:
                #     entry.stat(follow_symlinks=False).st_size
                # except FileNotFoundError as e:
                #     logger.warning(f'[err] {e}')
                # except Exception as e:
                #     logger.error(f'[err] {e}')

if __name__ == '__main__':
    myparse = argparse.ArgumentParser(description="Find new files")
    myparse.add_argument('--path', metavar='path', type=str, help="Path to search", default=".")
    myparse.add_argument('--maxfiles', metavar='maxfiles', type=int, help="Limit to x results", default=30)
    args = myparse.parse_args()
    input_path = args.path
    maxfiles = args.maxfiles

    filelist = []
    get_tree(input_path, filelist)
    reslist = [k for k in filelist if k[0].is_file()]
    reslist.sort(key=lambda x: x[1], reverse=False)
    logger.debug(f'[done] f:{len(filelist)} r:{len(reslist)}')
    
    for file in reslist[-maxfiles:]:
        filetime = datetime.fromtimestamp(file[0].stat().st_ctime)
        age = datetime.now() - filetime
        print(f'd:{filetime} a:{age.seconds} f:{file[0].path}')
