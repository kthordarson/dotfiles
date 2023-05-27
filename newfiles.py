#!/usr/bin/python3

import os
import time
import argparse
from pathlib import Path
from loguru import logger
from datetime import datetime
import glob
from dataclasses import dataclass, field
import operator

@dataclass(order=True, frozen=False)
class FileItem:
	sort_index: int = field(init=False, repr=False)
	name: Path
	size: int
	st_atime: int
	st_mtime: int
	st_ctime: int
	def __init__ (self, name:Path):
		self.name = Path(name)
		self.filename = str(name)
		try:
			self.size = self.name.stat().st_size
		except AttributeError as e:
			logger.error(f'[err] {e} file: {self.filename}')
		self.st_atime = self.name.stat().st_atime
		self.st_mtime = self.name.stat().st_mtime
		self.st_ctime = self.name.stat().st_ctime
	def __str__(self):
		return f'{self.name}'
	def get_size(self):
		return get_size_format(self.size,suffix='B')


def get_size_format(b, factor=1024, suffix="B"):
	for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
		if b < factor:
			return f"{b:.2f} {unit}{suffix}"
		b /= factor
	return f"{b:.2f} {suffix}"

def filelist_generator(startpath, EXCLUDES):
	# foo
	#filelist_ = [Path(k) for k in glob.glob(str(Path(path))+'/**',recursive=True, include_hidden=True) if k not in EXCLUDES]
	if startpath.endswith('/'):
		startpath += '**'
	else:
		startpath += '/**'
	# startpath = Path(startpath)
	filelist_ = [FileItem(Path(k)) for k in glob.glob(startpath,recursive=True, include_hidden=True) if not Path(k).is_symlink()]
	logger.debug(f'[flg] :{len(filelist_)}')
	for file in filelist_:
		skipfile = False
		file = str(file)
		for fp in file.split('/'):
			if fp in EXCLUDES:
				skipfile = True
		if not skipfile:
			try:
				if Path(file).is_file():
					yield (FileItem(file))
					#yield((Path(file), Path(file).stat().st_size, Path(file).stat().st_ctime))
			except PermissionError as e:
				logger.warning(f'[err] {e} file: {file}')
			except TypeError as e:
				logger.error(f'[err] {e} file: {file}')

def debugprintlist(filelist):
	#reslist.sort(key=lambda x: x[1], reverse=args.reverse)
	#logger.debug(f'[done] r:{len(reslist)}')
	timefmt = '%d-%m-%Y %H:%M:%S'
	print(f'{"file":<30}{"ctime":<21}{"mtime":<21}{"atime":<21}')
	print(f'{"-"*90}')
	for file in filelist[-maxfiles:]:
		ct = datetime.fromtimestamp(file.st_ctime).strftime(timefmt)
		mt = datetime.fromtimestamp(file.st_mtime).strftime(timefmt)
		at = datetime.fromtimestamp(file.st_atime).strftime(timefmt)
		print(f'{file.filename[:30]:30} | {ct} | {mt} | {at}')

def printlist(filelist, args):
	#reslist.sort(key=lambda x: x[1], reverse=args.reverse)
	#logger.debug(f'[done] r:{len(reslist)}')
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
	#print(f'{"-"*90}')
	s0 = 'file'.ljust(maxlen)+str(args.sort)
	print(s0)
	for file in filelist[-maxfiles:]:
		if args.sort == 'ctime':
			datefield = datetime.fromtimestamp(file.st_ctime).strftime(timefmt)
		elif args.sort == 'mtime':
			datefield = datetime.fromtimestamp(file.st_mtime).strftime(timefmt)
		elif args.sort == 'atime':
			datefield = datetime.fromtimestamp(file.st_atime).strftime(timefmt)
		s0 = str(file.name).ljust(maxlen)+str(datefield)
		print(s0)
		#print(f'{file.name} | {datefield}')

if __name__ == '__main__':
	myparse = argparse.ArgumentParser(description="Find new files")
	_default = str(Path(myparse.prog).parent)
	# myparse.add_argument('--path', metavar='path', type=str, help="Path to search", nargs='?', const='.', action='store_const')
	myparse.add_argument('path',  nargs='?', type=str, default=_default,	 metavar='input_path')
	#myparse.add_argument('--path', metavar='path', type=str, help="Path to search", default=".")
	myparse.add_argument('--maxfiles', '-m', metavar='maxfiles', type=int, help="Limit to x results", default=30)
	myparse.add_argument('--reverse','-r', help="reverse", action='store_true', dest='reverse', default=False)
	myparse.add_argument('--excludes', '-e', help="use exclude list", action='store_true', default=True)
	myparse.add_argument('--sort', '-s', metavar='sort', type=str, help="sort by ctime/mtime/atime", default='ctime')
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
	#reslist = [k for k in filelist_generator(args.path)]
	if args.path.endswith('/'):
		startpath = args.path + '**'
	else:
		startpath = args.path + '/**'
	filelist = [k for k in filelist_generator(args.path, EXCLUDES)]
	#filelist = [FileItem(Path(k)) for k in glob.glob(startpath,recursive=True, include_hidden=True)]
	printlist(filelist, args)

