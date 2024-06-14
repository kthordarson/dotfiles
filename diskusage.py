#!/usr/bin/python3

import os
import time
import argparse
from pathlib import Path
from glob import glob
from dataclasses import dataclass, field
import operator
from utils import get_size_format, EXCLUDES, FileItem, DirItem


if __name__ == '__main__':
	myparse = argparse.ArgumentParser(description="show folder sizes and things..")
	_default = str(Path(myparse.prog).parent)
	# myparse.add_argument('--path', metavar='path', type=str, help="Path to search", default=".")
	myparse.add_argument('path', nargs='?', type=str, default=_default,	 metavar='input_path')
	myparse.add_argument('--number', metavar='filenum', type=int, help="Limit to x results", default=10)
	myparse.add_argument('--sort', metavar='sort', type=str, help="sort by size/files/dirs", default='size')
	myparse.add_argument('--maxfiles', metavar='maxfiles', type=int, help="include X biggest file(s)", default='0')
	myparse.add_argument('-e','--excludes', help="use exclude list", action='store_true', default=False)
	myparse.add_argument('-r','--reverse', help="reverse list", action='store_true', default=False, dest='reverselist')
	myparse.add_argument('-wc','--wildcard', required=False, metavar='wildcard', nargs='?', type=str, help="search by wildcard", default='*')
	args = myparse.parse_args()
	if args.excludes:
		exclude_list = EXCLUDES
	else:
		exclude_list = []
	input_path = Path(args.path)
	limit = args.number
	getbigfiles = False
	if args.maxfiles >= 1:
		getbigfiles = True
		#print(f'[d] getbigfiles:{getbigfiles} args.topfiles:{args.maxfiles}')
	filelist = []
	itemlist = []
	folderlist = [k for k in input_path.glob('*') if not k.is_file() and k.name not in exclude_list]
	try:
		#itemlist = [DirItem(name=k, getbigfiles=getbigfiles, maxfiles=args.maxfiles) for k in folderlist]
		for k in folderlist:
			di = DirItem(name=k, getbigfiles=getbigfiles, maxfiles=args.maxfiles, wildcard=args.wildcard)
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
