#!/usr/bin/python3
import os
from functools import partial

import multiprocessing
import argparse
from pathlib import Path
from datetime import datetime
import operator
from utils import filelist_generator, get_size_format, FileItem, EXCLUDES

def process_directory(directory, args, exclude_list):
	return list(filelist_generator(args, exclude_list, specific_dir=directory))

def debugprintlist(filelist):
	# reslist.sort(key=lambda x: x[1], reverse=args.reverse)
	# logger.debug(f'[done] r:{len(reslist)}')
	timefmt = '%d-%m-%Y %H:%M:%S'
	print(f'{"file":<30}{"ctime":<21}{"mtime":<21}{"atime":<21}')
	print(f'{"-"*90}')
	for file in filelist[-maxfiles:]:
		ct = datetime.fromtimestamp(file.st_ctime).strftime(timefmt)
		mt = datetime.fromtimestamp(file.st_mtime).strftime(timefmt)
		at = datetime.fromtimestamp(file.st_atime).strftime(timefmt)
		print(f'{file.filename[:30]:30} | {ct} | {mt} | {at}')

def printlist(filelist, args):
	# reslist.sort(key=lambda x: x[1], reverse=args.reverse)
	# logger.debug(f'[done] r:{len(reslist)}')
	if args.sort == 'ctime':
		filelist = sorted(filelist, key=operator.attrgetter('st_ctime'), reverse=args.reverse)
	if args.sort == 'atime':
		filelist = sorted(filelist, key=operator.attrgetter('st_mtime'), reverse=args.reverse)
	if args.sort == 'mtime':
		filelist = sorted(filelist, key=operator.attrgetter('st_mtime'), reverse=args.reverse)
	timefmt = '%d-%m-%Y %H:%M:%S'
	maxlen = 0
	for file in filelist[-maxfiles:]:
		if len(str(file.name)) > maxlen:
			maxlen = len(str(file.name))
	# print(f'{"file":<maxlen}{args.sort:<21}')
	# print(f'{"-"*90}')
	s0 = 'file'.ljust(maxlen)+str(args.sort)
	print(s0)
	for file in filelist[-maxfiles:]:
		if args.sort == 'ctime':
			datefield = datetime.fromtimestamp(file.st_ctime).strftime(timefmt)
		elif args.sort == 'mtime':
			datefield = datetime.fromtimestamp(file.st_mtime).strftime(timefmt)
		elif args.sort == 'atime':
			datefield = datetime.fromtimestamp(file.st_atime).strftime(timefmt)
		s0 = str(str(file.name).ljust(maxlen)+str(datefield))
		try:
			print(f'{s0}')
		except UnicodeEncodeError as e:
			print(f'error: {e} {file}')
		# print(f'{file.name} | {datefield}')

if __name__ == '__main__':
	myparse = argparse.ArgumentParser(description="Find new files")
	_default = str(Path(myparse.prog).parent)
	# myparse.add_argument('--path', metavar='path', type=str, help="Path to search", nargs='?', const='.', action='store_const')
	# myparse.add_argument('path', type=str, default=_default,	 metavar='input_path')
	myparse.add_argument('path', nargs='?', type=str, default=_default, metavar='input_path')
	# myparse.add_argument('--path', metavar='path', type=str, help="Path to search", default=".")
	myparse.add_argument('-wc','--wildcard', required=False, metavar='wildcard', type=str, nargs=1, help="search by wildcard", default='*')
	myparse.add_argument('--maxfiles', '-m', metavar='maxfiles', type=int, help="Limit to x results", default=30)
	myparse.add_argument('--reverse','-r', help="reverse", action='store_true', dest='reverse', default=False)
	myparse.add_argument('--excludes', '-e', help="use exclude list", action='store_true', default=True)
	myparse.add_argument('--sort', '-s', metavar='sort', type=str, help="sort by ctime/mtime/atime", default='ctime')
	args = myparse.parse_args()
	if args.excludes:
		exclude_list = EXCLUDES
	else:
		exclude_list = []
	maxfiles = args.maxfiles
	if args.reverse:
		reverse = True
	else:
		reverse = False
	filelist = []
	# reslist = [k for k in filelist_generator(args.path)]
	# filelist = [k for k in filelist_generator(args, exclude_list)]
	input_path = Path(args.path)
	top_dirs = [d for d in input_path.iterdir() if d.is_dir() and d.name not in exclude_list]

	with multiprocessing.Pool(processes=os.cpu_count()) as pool:
		results = pool.map(partial(process_directory, args=args, exclude_list=exclude_list), top_dirs)

	filelist = [item for sublist in results for item in sublist]

	# Add files in the root directory
	root_files = list(filelist_generator(args, exclude_list, specific_dir=input_path, root_only=True))
	filelist.extend(root_files)

	# filelist = [FileItem(Path(k)) for k in glob.glob(startpath,recursive=True, include_hidden=True)]
	printlist(filelist, args)

