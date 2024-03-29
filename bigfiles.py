#!/usr/bin/python3

import os, sys
import time
import argparse
from pathlib import Path
import glob
from loguru import logger
from datetime import datetime

EXCLUDES = ['.git', '__pycache__', '.idea', '.vscode', '.ipynb_checkpoints']

def format_bytes(size):
	# 2**10 = 1024
	power = 2**10
	n = 0
	power_labels = {0 : '', 1: 'kilo', 2: 'mega', 3: 'giga', 4: 'tera'}
	while size > power:
		size /= power
		n += 1
	return size, power_labels[n]+'bytes'

def humanbytes(B):
	"""Return the given bytes as a human friendly KB, MB, GB, or TB string."""
	B = float(B)
	KB = float(1024)
	MB = float(KB ** 2) # 1,048,576
	GB = float(KB ** 3) # 1,073,741,824
	TB = float(KB ** 4) # 1,099,511,627,776

	if B < KB:
		return f'{B:.0f} B' #return f'{0} {1}'.format(B,'B' if 0 == B > 1 else 'B')
	elif KB <= B < MB:
		return '{0:.0f} KB'.format(B / KB)
	elif MB <= B < GB:
		return '{0:.0f} MB'.format(B / MB)
	elif GB <= B < TB:
		return '{0:.0f} GB'.format(B / GB)
	elif TB <= B:
		return '{0:.0f} TB'.format(B / TB)

def filelist_generator(startpath):
	# foo
	#filelist_ = [Path(k) for k in glob.glob(str(Path(path))+'/**',recursive=True, include_hidden=True) if k not in EXCLUDES]
	startpath = Path(startpath)
	# filelist_ = [Path(k) for k in glob.glob(str(startpath),recursive=True, include_hidden=True)]
	filelist_ = [k for k in startpath.rglob('*')]
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
	myparse = argparse.ArgumentParser(description="Find big files")
	_default = str(Path(myparse.prog).parent)
	# myparse.add_argument('--path', metavar='path', type=str, help="Path to search", nargs='?', const='.', action='store_const')
	myparse.add_argument('path', nargs='?', type=str, default=_default,	 metavar='input_path')
	myparse.add_argument('-m','--maxfiles', metavar='maxfiles', type=int, help="Limit to x results", default=30)
	myparse.add_argument('-e', '--excludes', help="use exclude list", action='store_true', default=False)
	myparse.add_argument('-r','--reverse', help="reverse list", action='store_true', default=False, dest='reverselist')
	args = myparse.parse_args()
	if not args.excludes:
		EXCLUDES = []
	maxfiles = args.maxfiles
	#input_path = args.path
	# filelist = []
	# filelist = [Path(k) for k in glob.glob(str(Path(args.path))+'/**',recursive=True, include_hidden=True)]
	reslist = [k for k in filelist_generator(args.path)]
	reslist.sort(key=lambda x: x[1], reverse=args.reverselist)
	#logger.debug(f'[done]  r:{len(reslist)}')
	print(f'{"size":<15} {"path":<30}')
	for file in reslist[-maxfiles:]:
		fitem = Path(file[0])
		parent = str(fitem.parent)
		if parent == '.':
			parent = ''
		#print(f'{humanbytes(file[1]):<5}  file: {parent}/{fitem.name[:30]:<30} ')
		print(f'{humanbytes(file[1]):<15} {parent}/{fitem.name} ')
	# if filelist:
	# 	for k in filelist:
	# 		try:
	# 			if Path(k).is_file() and not Path(k).is_symlink():
	# 				reslist.append((Path(k), k.stat().st_size))
	# 		except PermissionError as e:
	# 			logger.warning(f'[err] {e} k={k}')

	# 	#reslist = [(k, k.stat().st_size) for k in filelist if k.is_file()]
