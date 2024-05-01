#!/usr/bin/python3
import os
import sys
import time
import argparse
from pathlib import Path
from glob import glob
from colorama import Fore, Back, Style
from loguru import logger


def fix_symlink(symlink, target, dryrun=False):
	msgtext = f'  fixing {symlink} -> {target} dryrun={dryrun}'
	logger.debug(msgtext)
	print(msgtext)
	if os.path.exists(target):
		if not dryrun:
			os.unlink(symlink)
			os.symlink(target, symlink)
		logger.debug(f'unlinked {symlink} -> new symlink {target}')
	else:
		logger.error(f'{target} does not exist')

if __name__ == '__main__':
	myparse = argparse.ArgumentParser(description="check symlinks")
	_default = str(Path(myparse.prog).parent)
	myparse.add_argument('path', nargs='?', type=str, default=_default,	 metavar='args.path')
	myparse.add_argument('-t','--type', help="Searchtype, d for dirs, f for files, a for both. ", action='store', default='a', dest='searchtype')
	myparse.add_argument('-sa','--showall', help="Show all links", action='store_true', default=False, dest='showall')
	myparse.add_argument('-sb','--showbroken', help="Show broken links", action='store_true', default=False, dest='showbroken')
	myparse.add_argument('-fb', '--findbroken', help="Attempt to find broken links", action='store_true', default=False, dest='findbroken')
	myparse.add_argument('-fix', '--fixbroken', help="Attempt to fix broken links", action='store_true', default=False, dest='fixbroken')
	myparse.add_argument('-rb', '--removebroken', help="Remove broken links", action='store_true', default=False, dest='removebroken')
	myparse.add_argument('--logfile', help="Logfile", action='store', default='symlinkfixer.log', dest='logfile')
	myparse.add_argument('--dryrun', help="Dry run, do not perform any operations", action='store_true', default=False, dest='dryrun')
	args = myparse.parse_args()
	log_level = "DEBUG"
	log_format = "<green>{time:DD-MM-YYYYY HH:mm:ss.SSS }</green> | <level>{level: <6}</level> | <yellow>Line {line: >3} ({file}):</yellow> <b>{message}</b>"
	logger.add(sys.stderr, level=log_level, format=log_format, colorize=True, backtrace=True, diagnose=True)
	#logger.remove()
	logger.add(args.logfile, level=log_level, format=log_format, colorize=False, backtrace=True, diagnose=True)

	if not args.path.endswith('/'):
		args.path += '/'
	if args.searchtype == 'd': # todo fix
		print(f'{Fore.LIGHTBLUE_EX}Searching for dirs in {Fore.CYAN}{args.path}{Style.RESET_ALL}')
		symlinks = [k for k in os.scandir(args.path) if k.is_symlink() and k.is_dir() and os.path.exists(os.path.realpath(k))]
		broken_symlinks = [k for k in os.scandir(args.path) if k.is_symlink() and k.is_dir() and not os.path.exists(os.path.realpath(k))]
	if args.searchtype == 'f': # todo fix
		print(f'{Fore.LIGHTBLUE_EX}Searching for files in {Fore.CYAN}{args.path}{Style.RESET_ALL}')
		symlinks = [k for k in os.scandir(args.path) if k.is_symlink() and k.is_file() and os.path.exists(os.path.realpath(k))]
		broken_symlinks = [k for k in os.scandir(args.path) if k.is_symlink() and k.is_file() and not os.path.exists(os.path.realpath(k))]
	if args.searchtype == 'a':
		print(f'{Fore.LIGHTBLUE_EX}Searching {Fore.CYAN}{args.path}{Style.RESET_ALL}')
		#symlinks = [k for k in os.scandir(args.path) if k.is_symlink()  and os.path.exists(os.path.realpath(k))]
		symlinks = [k for k in glob(pathname=args.path+'**', recursive=True) if Path(k).is_symlink()]
		broken_symlinks = [k for k in os.scandir(args.path) if k.is_symlink()  and not os.path.exists(os.path.realpath(k))]
	if len(symlinks) == 0:
		print(f'{Fore.LIGHTBLUE_EX}Found {Fore.CYAN}{len(symlinks)} symlinks in {Fore.CYAN}{args.path}{Style.RESET_ALL}')
	elif len(symlinks) > 0:
		print(f'{Fore.LIGHTBLUE_EX}Found {Fore.CYAN}{len(symlinks)} {Fore.LIGHTBLUE_EX}working and {Fore.CYAN}{len(broken_symlinks)} {Fore.LIGHTBLUE_EX}broken symlinks in {Fore.CYAN}{args.path}{Style.RESET_ALL}')
		if args.findbroken:
			# attempt to find broken links
			for idx, sl_ in enumerate(broken_symlinks):
				sl = Path(sl_)
				broken = sl.name
				candidates = [k for k in glob(str(args.path)+'/**',recursive=True) if broken in k and os.path.exists(k)]
				print(f'{Fore.LIGHTBLUE_EX}[{idx}/{len(broken_symlinks)}] found {Fore.CYAN}{len(candidates)} {Fore.LIGHTBLUE_EX}candidates for {Fore.CYAN}{sl.name} {Style.RESET_ALL}')
				for c in candidates:
					print(f'\t{Fore.LIGHTGREEN_EX}{c}{Style.RESET_ALL}')
		elif args.removebroken:
			# attempt to remove broken links, log operations to file
			for idx, sl_ in enumerate(broken_symlinks):
				sl = Path(sl_)
				broken = sl.name
				print(f'{Fore.LIGHTBLUE_EX}[{idx}/{len(broken_symlinks)}] removing {Fore.CYAN}{sl} {Style.RESET_ALL}')
				logger.debug(f'removing {sl}')
				# todo remove broken symlinks...
		elif args.fixbroken:
			# attempt to find and fix broken links, log operations to file
			for idx, sl_ in enumerate(broken_symlinks):
				sl = Path(sl_)
				broken = sl.name
				print(f'{Fore.LIGHTBLUE_EX}[{idx}/{len(broken_symlinks)}] Searching for {Fore.LIGHTGREEN_EX}{sl} {Style.RESET_ALL}')
				candidates = [k for k in glob(str(args.path)+'/**',recursive=True) if broken in k and os.path.exists(k)]
				if len(candidates) == 0:
					print(f'  {Fore.RED}no candidates for {Fore.LIGHTGREEN_EX}{sl} {Style.RESET_ALL}')
				elif len(candidates) == 1:
					# todo fix symlink
					# print(f'  found candidate {Fore.LIGHTGREEN_EX}{candidates[0]} {Fore.LIGHTBLUE_EX}for {Fore.CYAN}{sl} {Style.RESET_ALL}')
					try:
						fix_symlink(symlink=sl, target=candidates[0], dryrun=args.dryrun)
					except Exception as e:
						logger.error(f'unhandled {e} {type(e)} {sl=} target={candidates[0]}')
				elif len(candidates) > 1:
					# todo select best candidate and fix symlink
					print(f'  found {Fore.CYAN}{len(candidates)} {Fore.LIGHTBLUE_EX}for {Fore.CYAN}{sl} {Style.RESET_ALL}')
					for c in candidates:
						print(f'{Fore.LIGHTGREEN_EX}\t{c}{Style.RESET_ALL}')
		elif args.showbroken:
			for idx, sl_ in enumerate(broken_symlinks):
				sl = Path(sl_)
				print(f'{Fore.LIGHTBLUE_EX}[{idx}/{len(broken_symlinks)}] {Fore.BLUE}{sl} -> {Fore.CYAN}{os.path.realpath(sl)} {Style.RESET_ALL}')
		elif args.showall:
			for idx, sl_ in enumerate(symlinks):
				sl = Path(sl_)
				print(f'{Fore.LIGHTBLUE_EX}[{idx}/{len(symlinks)}] {Fore.BLUE}{sl} -> {Fore.CYAN}{os.path.realpath(sl)} {Style.RESET_ALL}')
