#!/usr/bin/python3

import os
import time
import argparse
from pathlib import Path
from loguru import logger
from datetime import datetime
import glob

def xfilelist_generator(path):
    # foo
    # filelist_ = [Path(k) for k in glob.glob(str(Path(path))+'/**',recursive=True, include_hidden=True)]
    filelist_= []

    for k in glob.glob(str(Path(path))+'/**',recursive=True, include_hidden=True):
        try:
            filelist_.append(Path(k))
        except KeyboardInterrupt as e:
            logger.error(e)
    logger.debug(f'[flg] {len(filelist_)}')
    for k in filelist_:
        try:
            if Path(k).is_file() and not Path(k).is_symlink():
                yield((Path(k), k.stat().st_ctime))
        except PermissionError as e:
            logger.warning(f'[err] {e} k={k}')

def filelist_generator(startpath):
	# foo
	#filelist_ = [Path(k) for k in glob.glob(str(Path(path))+'/**',recursive=True, include_hidden=True) if k not in EXCLUDES]
	if startpath.endswith('/'):
		startpath += '**'
	else:
		startpath += '/**'
	startpath = Path(startpath)
	filelist_ = [Path(k) for k in glob.glob(str(startpath),recursive=True, include_hidden=True)]
	logger.debug(f'[flg] :{len(filelist_)}')
	for file in filelist_:
		try:
			if Path(file).is_file() and not Path(file).is_symlink():
				for p in file.parts:
					if p in EXCLUDES:
						break
				else:
					yield((Path(file), file.stat().st_size))
		except PermissionError as e:
			logger.warning(f'[err] {e} k={file}')



if __name__ == '__main__':
    myparse = argparse.ArgumentParser(description="Find new files")
    _default = str(Path(myparse.prog).parent)
	# myparse.add_argument('--path', metavar='path', type=str, help="Path to search", nargs='?', const='.', action='store_const')
    myparse.add_argument('path', nargs='?', type=str, default=_default,	 metavar='input_path')
    #myparse.add_argument('--path', metavar='path', type=str, help="Path to search", default=".")
    myparse.add_argument('--maxfiles', metavar='maxfiles', type=int, help="Limit to x results", default=30)
    myparse.add_argument('--reverse','-r', help="reverse", action='store_true', dest='reverse', default=False)
    myparse.add_argument('--excludes', help="use exclude list", action='store_true', default=False)
    args = myparse.parse_args()
    if args.excludes:
        EXCLUDES = ['.git', '__pycache__', '.idea', '.vscode', '.ipynb_checkpoints']
    else:
        EXCLUDES = []
    maxfiles = args.maxfiles
    if args.reverse:
        reverse = True
    else:
        reverse = False
    filelist = []
    reslist = [k for k in filelist_generator(args.path)]
    reslist.sort(key=lambda x: x[1], reverse=args.reverse)
    #logger.debug(f'[done] r:{len(reslist)}')
    print(f'{"filetime":<27}{"age":<8}{"file":<20}')
    for file in reslist[-maxfiles:]:
        filetime = datetime.fromtimestamp(file[0].stat().st_ctime)
        age = datetime.now() - filetime
        print(f'{filetime} {age.seconds:<8} {file[0]}')
