#!/usr/bin/python3

import os
import time
import argparse
from pathlib import Path
from glob import glob
from dataclasses import dataclass, field
import operator

EXCLUDES = ['.git', '__pycache__', '.idea', '.vscode', '.ipynb_checkpoints']

@dataclass(order=True, frozen=False)
class FileItem:
	sort_index: int = field(init=False, repr=False)
	name: Path
	size: int =0
	def __init__ (self, name:Path):
		self.name = name
		self.filename = str(name.name)
		self.size = self.name.stat().st_size
	def __str__(self):
		return f'{self.name}'
	def get_size(self):
		return get_size_format(self.size,suffix='B')

@dataclass(order=True, frozen=False)
class DirItem:
	sort_index: int = field(init=False, repr=False)
	name: Path
	totalsize: int = 0
	subfilecount: int = 0
	subdircount: int = 0
	subitemcount: int = 0
	#bigfiles: list = []

	def __init__(self, name:Path, getbigfiles=False, maxfiles=3):
		self.name = name
		self.dirname = str(name.name)
		self.maxfiles = maxfiles
		self.totalsize = get_directory_size(self.name)
		self.subfilecount = get_subfilecount(self.name)
		self.subdircount = get_subdircount(self.name)
		self.subitemcount = self.subfilecount + self.subdircount
		self.bigfiles = []
		self.filelist = []
		if getbigfiles:
			self.get_bigfiles()

	def __post_init(self):
		object.__setattr__(self, 'sort_index', self.totalsize)

	def __str__(self):
		return f'{self.name}'

	def __repr__(self) -> str:
		return f'{self.name}'

	def get_size(self):
		return get_size_format(self.totalsize,suffix='B')

	def get_bigfiles(self):
		subfiles = [FileItem(k) for k in self.name.glob('**/*') if k.is_file()]
		self.bigfiles = sorted(subfiles, key=lambda d: d.size, reverse=True)[0:self.maxfiles]

def get_directory_size(directory):
	total = 0
	try:
		for entry in os.scandir(directory):
			if entry.is_symlink():
				break
			if entry.is_file():
				total += entry.stat().st_size
			elif entry.is_dir():
				try:
					total += get_directory_size(entry.path)
				except FileNotFoundError as e:
					print(f'[err] dir:{directory} {e}')
	except NotADirectoryError:
		return os.path.getsize(directory)
	except (PermissionError, FileNotFoundError) as e:
		print(f'[err] dir:{directory} {e}')
		return 0
	return total

def get_subfilecount(directory):
	try:
		filecount = len([k for k in directory.glob('**/*') if k.is_file()])
	except PermissionError as e:
		print(f'[err] {e} d:{directory}')
		return 0
	return filecount

def get_subdircount(directory):
	dc = 0
	try:
		dc = len([k for k in directory.glob('**/*') if k.is_dir()])
	except (PermissionError,FileNotFoundError) as e:
		print(f'[err] {e} d:{directory}')
	return dc

def get_size_format(b, factor=1024, suffix="B"):
	for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
		if b < factor:
			return f"{b:.2f} {unit}{suffix}"
		b /= factor
	return f"{b:.2f} {suffix}"


if __name__ == '__main__':
	myparse = argparse.ArgumentParser(description="show folder sizes and things..")
	_default = str(Path(myparse.prog).parent)
	# myparse.add_argument('--path', metavar='path', type=str, help="Path to search", default=".")
	myparse.add_argument('path', nargs='?', type=str, default=_default,	 metavar='input_path')
	myparse.add_argument('--number', metavar='filenum', type=int, help="Limit to x results", default=10)
	myparse.add_argument('--sort', metavar='sort', type=str, help="sort by size/files/dirs", default='size')
	myparse.add_argument('--maxfiles', metavar='maxfiles', type=int, help="include X biggest file(s)", default='0')
	myparse.add_argument('--excludes', help="use exclude list", action='store_true', default=False)
	myparse.add_argument('-r','--reverse', help="reverse list", action='store_true', default=False, dest='reverselist')
	args = myparse.parse_args()
	if args.excludes:
		pass # EXCLUDES = ['.git', '__pycache__', '.idea', '.vscode', '.ipynb_checkpoints']
	else:
		pass # EXCLUDES = []
	input_path = Path(args.path)
	limit = args.number
	getbigfiles = False
	if args.maxfiles >= 1:
		getbigfiles = True
		#print(f'[d] getbigfiles:{getbigfiles} args.topfiles:{args.maxfiles}')
	filelist = []
	itemlist = []
	folderlist = [k for k in input_path.glob('*') if not k.is_file() and k.name not in EXCLUDES]
	try:
		#itemlist = [DirItem(name=k, getbigfiles=getbigfiles, maxfiles=args.maxfiles) for k in folderlist]
		for k in folderlist:
			di = DirItem(name=k, getbigfiles=getbigfiles, maxfiles=args.maxfiles)
			itemlist.append(di)
	except KeyboardInterrupt as e:
		print(f'[KeyboardInterrupt] il:{len(itemlist)} fl:{len(folderlist)}')
	total_size = 0
	total_items = 0
	total_files = 0
	total_dirs = 0
	if args.sort == 'size':
		sorteditems = sorted(itemlist, key=operator.attrgetter("totalsize"), reverse=args.reverselist)
	if args.sort == 'files':
		sorteditems = sorted(itemlist, key=operator.attrgetter("subfilecount"), reverse=args.reverselist)
	if args.sort == 'dirs':
		sorteditems =  sorted(itemlist, key=operator.attrgetter("subdircount"), reverse=args.reverselist)
	print(f'[size] {" "*5}[name]{" "*15}[items] [files] [folders]')
	print(f'{"-"*60}')
	for item in sorteditems:
		print(f'{item.get_size():<10}  {item.dirname[0:20]:<20} {item.subitemcount:<7} {item.subfilecount:<7} {item.subdircount:<7}')
		if getbigfiles:
			for bigitem in item.bigfiles:
				print(f'\t[bi] {bigitem.filename[0:20]:<20} {bigitem.get_size():>10}')
		total_size += item.totalsize
		total_items += item.subitemcount
		total_files += item.subfilecount
		total_dirs += item.subdircount
	#print(f'[t] {get_size_format(b=total_size, suffix="B")} {" "*34} {total_files:,} {total_dirs:,}')
	print(f'{"-"*60}')
	print(f'{get_size_format(b=total_size, suffix="B")} {" "*23}{total_items:<7} {total_files:<7} {total_dirs:<7}')
