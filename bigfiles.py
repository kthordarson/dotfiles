#!/usr/bin/python3
import os
import argparse
import heapq
from pathlib import Path
import multiprocessing
from functools import partial
from utils import filelist_generator, EXCLUDES, humanbytes

def process_directory(directory, args, exclude_list):
	return list(filelist_generator(args, exclude_list, specific_dir=directory))

if __name__ == '__main__':
	myparse = argparse.ArgumentParser(description="Find big files")
	_default = str(Path(myparse.prog).parent)
	myparse.add_argument('path', nargs='?', type=str, default=_default, metavar='input_path')
	myparse.add_argument('-wc','--wildcard', required=False, metavar='wildcard', nargs='?', type=str, help="search by wildcard", default='*')
	myparse.add_argument('-m','--maxfiles', metavar='maxfiles', type=int, help="Limit to x results", default=30)
	myparse.add_argument('-e', '--excludes', help="use exclude list", action='store_true', default=False)
	myparse.add_argument('-r','--reverse', help="reverse list", action='store_true', default=False, dest='reverselist')
	myparse.add_argument('-d','--debug', help="enable debug mode", action='store_true', default=False, dest='debug')
	args = myparse.parse_args()
	if args.debug:
		print(f'args:  {args}')
	if args.excludes:
		exclude_list = EXCLUDES
	else:
		exclude_list = []

	input_path = Path(args.path)
	top_dirs = [d for d in input_path.iterdir() if d.is_dir() and d.name not in exclude_list]
	if args.debug:
		print(f'top_dirs: {len(top_dirs)} exclude_list: {exclude_list}')

	# Process directories in parallel
	with multiprocessing.Pool(processes=os.cpu_count()) as pool:
		results = pool.map(partial(process_directory, args=args, exclude_list=exclude_list), top_dirs)

	# Add files in the root directory
	largest_files = []

	def add_file(file):
		if len(largest_files) < args.maxfiles:
			heapq.heappush(largest_files, (file.size, file))
		else:
			if file.size > largest_files[0][0]:
				heapq.heappushpop(largest_files, (file.size, file))

	for res in results:
		for file in res:
			add_file(file)

	for file in filelist_generator(args, exclude_list, root_only=True):
		add_file(file)

	# Sort the final list for display
	result_files = [item[1] for item in sorted(largest_files, key=lambda x: x[0], reverse=args.reverselist)]
	if args.debug:
		print(f'largest_files: {len(largest_files)} result_files: {len(result_files)}')

	print(f'{"size":<15} {"path":<30}')
	for file in result_files:
		fitem = Path(file.name)
		parent = str(fitem.parent)
		if parent == '.':
			parent = ''
		print(f'{humanbytes(file.size):<15} {parent}/{fitem.name} ')
