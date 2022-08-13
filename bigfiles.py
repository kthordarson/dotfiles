#!/usr/bin/python3

import os
import time
import argparse
from pathlib import Path
from loguru import logger
from datetime import datetime

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
		return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
	elif KB <= B < MB:
		return '{0:.2f} KB'.format(B / KB)
	elif MB <= B < GB:
		return '{0:.2f} MB'.format(B / MB)
	elif GB <= B < TB:
		return '{0:.2f} GB'.format(B / GB)
	elif TB <= B:
		return '{0:.2f} TB'.format(B / TB)


def get_tree(path, filelist):
	path = Path(path)
	if path.is_symlink():
		logger.warning(f'[symlink] skipping {path}')
	else:
		for entry in os.scandir(path):
			if entry.is_dir(follow_symlinks=False) and not entry.is_symlink():
				try:
					get_tree(entry.path, filelist)
					filelist.append(entry)
				except Exception as e:
					logger.error(f'[err] {e} entry:{entry} entry.is_symlink():{entry.is_symlink()}')
			else:
				if entry.is_file and not entry.is_symlink():
					filelist.append(entry)
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
	reslist = [(k, k.stat().st_size) for k in filelist if k.is_file()]
	reslist.sort(key=lambda x: x[1], reverse=False)
	logger.debug(f'[done] f:{len(filelist)} r:{len(reslist)}')    
	for file in reslist[-maxfiles:]:
		fitem = Path(file[0])
		print(f' {humanbytes(file[1])} {fitem.name}')
