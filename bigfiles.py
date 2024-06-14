#!/usr/bin/python3

import os, sys
import time
import argparse
from pathlib import Path
import glob
from loguru import logger
from datetime import datetime
from utils import filelist_generator, EXCLUDES, humanbytes

if __name__ == '__main__':
	myparse = argparse.ArgumentParser(description="Find big files")
	_default = str(Path(myparse.prog).parent)
	myparse.add_argument('path', nargs='?', type=str, default=_default,	 metavar='input_path')
	myparse.add_argument('-wc','--wildcard', required=False, metavar='wildcard', nargs='?', type=str, help="search by wildcard", default='*')
	myparse.add_argument('-m','--maxfiles', metavar='maxfiles', type=int, help="Limit to x results", default=30)
	myparse.add_argument('-e', '--excludes', help="use exclude list", action='store_true', default=False)
	myparse.add_argument('-r','--reverse', help="reverse list", action='store_true', default=False, dest='reverselist')
	args = myparse.parse_args()
	print(f'args:  {args}')
	if args.excludes:
		exclude_list = EXCLUDES
	else:
		exclude_list = []
	maxfiles = args.maxfiles
	reslist = [k for k in filelist_generator(args, exclude_list)]
	reslist.sort(key=lambda x: x.size, reverse=args.reverselist)
	print(f'{"size":<15} {"path":<30}')
	for file in reslist[-maxfiles:]:
		fitem = Path(file.name)
		parent = str(fitem.parent)
		if parent == '.':
			parent = ''
		print(f'{humanbytes(file.size):<15} {parent}/{fitem.name} ')
