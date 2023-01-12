#!/usr/bin/python3

import os
import time
import argparse
from pathlib import Path
from loguru import logger
from datetime import datetime
import glob

def get_tree(path, filelist, excludes):
    path = Path(path)
    if path.is_symlink():
        logger.warning(f'[symlink] skipping {path}')
    else:
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False) and not entry.is_symlink() and entry.name not in EXCLUDES:
                try:
                    get_tree(entry.path, filelist, excludes)
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
    _default = str(Path(myparse.prog).parent)
	# myparse.add_argument('--path', metavar='path', type=str, help="Path to search", nargs='?', const='.', action='store_const')
    myparse.add_argument('path', nargs='?', type=str, default=_default,	 metavar='input_path')
    #myparse.add_argument('--path', metavar='path', type=str, help="Path to search", default=".")
    myparse.add_argument('--maxfiles', metavar='maxfiles', type=int, help="Limit to x results", default=30)
    myparse.add_argument('--old', help="Show oldest", action='store_true')
    myparse.add_argument('--excludes', help="use exclude list", action='store_true', default=False)
    args = myparse.parse_args()
    if args.excludes:
        EXCLUDES = ['.git', '__pycache__', '.idea', '.vscode', '.ipynb_checkpoints']
    else:
        EXCLUDES = []
    maxfiles = args.maxfiles
    if args.old:
        showold = True
    else:
        showold = False
    filelist = []
    # get_tree(input_path, filelist, EXCLUDES)
    # filelist.append((entry, entry.stat().st_ctime))
    filelist_ = [Path(k) for k in glob.glob(str(Path(args.path))+'/**',recursive=True, include_hidden=True)]
    reslist = []
    for k in filelist_:
        try:
            if Path(k).is_file() and not Path(k).is_symlink():
                reslist.append((Path(k), k.stat().st_ctime))
        except PermissionError as e:
            logger.warning(f'[err] {e} k={k}')
    #reslist = [(Path(k), k.stat().st_ctime) for k in filelist_ if Path(k).is_file()]
    #reslist = [k for k in filelist if k[0].is_file()]
    reslist.sort(key=lambda x: x[1], reverse=showold)
    logger.debug(f'[done] f:{len(filelist_)} r:{len(reslist)}')

    for file in reslist[-maxfiles:]:
        filetime = datetime.fromtimestamp(file[0].stat().st_ctime)
        age = datetime.now() - filetime
        print(f'd:{filetime} a:{age.seconds} f:{str(file[0])}')
