#!/usr/bin/python3
import os
import time
import argparse
from pathlib import Path
from glob import glob
from dataclasses import dataclass, field
import operator



if __name__ == '__main__':
	myparse = argparse.ArgumentParser(description="check symlinks")
	_default = str(Path(myparse.prog).parent)
	myparse.add_argument('path', nargs='?', type=str, default=_default,	 metavar='input_path')
	myparse.add_argument('-t','--type', help="Searchtype, d for dirs, f for files, a for both. ", action='store', default='a', dest='searchtype')
	myparse.add_argument('-sa','--showall', help="Show all links", action='store_true', default=True, dest='showall')
	myparse.add_argument('-sb','--showbroken', help="Show broken links", action='store_true', default=False, dest='showbroken')
	myparse.add_argument('-fb', '--findbroken', help="Attempt to find broken links", action='store_true', default=False, dest='findbroken')
	myparse.add_argument('-fix', '--fixbroken', help="Attempt to fix broken links", action='store_true', default=False, dest='fixbroken')
	myparse.add_argument('-rb', '--removebroken', help="Remove broken links", action='store_true', default=False, dest='removebroken')
	args = myparse.parse_args()
	input_path = Path(args.path)
	if args.searchtype == 'd':
		print(f'searching for dirs in {input_path}')
		symlinks = [k for k in os.scandir(input_path) if k.is_symlink() and k.is_dir() and os.path.exists(os.path.realpath(k))]
		broken_symlinks = [k for k in os.scandir(input_path) if k.is_symlink() and k.is_dir() and not os.path.exists(os.path.realpath(k))]
	if args.searchtype == 'f':
		print(f'searching for files in {input_path}')
		symlinks = [k for k in os.scandir(input_path) if k.is_symlink() and k.is_file() and os.path.exists(os.path.realpath(k))]
		broken_symlinks = [k for k in os.scandir(input_path) if k.is_symlink() and k.is_file() and not os.path.exists(os.path.realpath(k))]
	if args.searchtype == 'a':
		print(f'searching {input_path}')
		symlinks = [k for k in os.scandir(input_path) if k.is_symlink()  and os.path.exists(os.path.realpath(k))]
		broken_symlinks = [k for k in os.scandir(input_path) if k.is_symlink()  and not os.path.exists(os.path.realpath(k))]
	# symlinks = [k for k in glob(pathname=args.path+'**', recursive=True) if Path(k).is_symlink()]
	print(f'Found {len(symlinks)} working and {len(broken_symlinks)} broken symlinks in {input_path}')
	if args.findbroken:
		# attempt to find broken links
		for idx, sl_ in enumerate(broken_symlinks):
			sl = Path(sl_)
			broken = sl.name
			candidates = [k for k in glob(str(input_path)+'/**',recursive=True) if broken in k and os.path.exists(k)]
			print(f'[{idx}/{len(broken_symlinks)}] found {len(candidates)} candidates for {sl.name} ')
			for c in candidates:
				print(f'\t{c}')
	elif args.showbroken:
		for idx, sl_ in enumerate(broken_symlinks):
			sl = Path(sl_)
			print(f'[{idx}/{len(broken_symlinks)}] {sl} -> {os.path.realpath(sl)} ')
	elif args.showall:
		for idx, sl_ in enumerate(symlinks):
			sl = Path(sl_)
			print(f'[{idx}/{len(symlinks)}] {sl} -> {os.path.realpath(sl)} ')
