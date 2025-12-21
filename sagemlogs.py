#!/usr/bin/python3
import os
import argparse
import heapq
from pathlib import Path
import multiprocessing
import re
LOG_PATH = Path("/var/log/remote/192.168.1.3/")

def get_file_size(file_path):
	try:
		return os.path.getsize(file_path)
	except OSError:
		return 0

def get_file_info(file_path):
	return (file_path, get_file_size(file_path))

def get_sizes(args):
	file_paths = [str(p) for p in LOG_PATH.rglob("*") if p.is_file() and p.suffix == args.extension and p.stat().st_size >= args.min_size]
	with multiprocessing.Pool() as pool:
		file_sizes = list(pool.imap_unordered(get_file_info, file_paths, chunksize=100))
	largest_files = heapq.nlargest(args.num_files, file_sizes, key=lambda x: x[1])
	return largest_files

def get_macs_from_sagem_deviceinfo(args):
	logpath = LOG_PATH / "deviceinfo/sagem_deviceinfo.log"
	macs = set()
	mac_pattern = re.compile(r'for device ([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})')
	try:
		with open(logpath, 'r') as f:
			for line in f:
				if "for device" in line:
					match = mac_pattern.search(line)
					if match:
						macs.add(match.group(1).lower())
	except FileNotFoundError:
		print(f"file not found: {logpath}")
	if args.remove_after:
		try:
			os.remove(logpath)
			print(f"Removed file: {logpath}")
		except OSError as e:
			print(f"Error removing file {logpath}: {e}")
	return macs

def get_macs_from_halwifi(args):
	logpath = LOG_PATH / "wifi/sagem_halwifi.log"
	macs = set()
	mac_pattern = re.compile(r'for \[([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})\]')
	try:
		with open(logpath, 'r') as f:
			for line in f:
				if "sta_info" in line:
					match = mac_pattern.search(line)
					if match:
						macs.add(match.group(1).lower())
	except FileNotFoundError:
		print(f"file not found: {logpath}")
	if args.remove_after:
		try:
			os.remove(logpath)
			print(f"Removed file: {logpath}")
		except OSError as e:
			print(f"Error removing file {logpath}: {e}")
	return macs

def get_macs_from_logfile(logpath, args):
	macs = set()
	mac_pattern = re.compile(r'([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})')
	try:
		with open(logpath, 'r') as f:
			for line in f:
				match = mac_pattern.search(line)
				if match:
					macs.add(match.group(1).lower())
	except FileNotFoundError:
		print(f"file not found: {logpath}")
	if args.remove_after:
		try:
			os.remove(logpath)
			print(f"Removed file: {logpath}")
		except OSError as e:
			print(f"Error removing file {logpath}: {e}")
	return macs

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Find the largest log files.")
	parser.add_argument("--num-files", type=int, default=10, help="Number of largest files to display (default: 10)",)
	parser.add_argument("--min-size", type=int, default=1024, help="Minimum file size (default 1024)",)
	parser.add_argument("--extension", "-e", type=str, default='.log', help="File extension (.log)",)
	parser.add_argument("--include-empty", type=bool, default=False, help="Show empty files (default False)",)
	parser.add_argument("--extract-macs", type=bool, default=False, help="Extract mac addressess from log files",)
	parser.add_argument("--mac-file", type=str, default='/home/kth/temp/sagem-macs.txt', help="Save extracted macs to this file",)
	parser.add_argument("--remove-after", type=bool, default=False, help="Remove log files after extraction",)
	args = parser.parse_args()
	if args.include_empty:
		args.min_size = 0
	if args.extract_macs:
		macs = set()
		if Path(args.mac_file).exists():
			try:
				with open(args.mac_file, 'r') as f:
					existing_macs = set(line.strip() for line in f)
				macs.update(existing_macs)
				print(f"\nLoaded {len(existing_macs)} existing MAC addresses from {args.mac_file}")
			except Exception as e:
				print(f"Error reading existing MAC addresses from file: {e} {type(e)}")
		file_paths = [str(p) for p in LOG_PATH.rglob("*") if p.is_file() and p.suffix == args.extension and p.stat().st_size >= args.min_size]
		print(f"\nScanning {len(file_paths)} log files for MAC addresses...")
		for logfile in file_paths:
			macs_in_file = get_macs_from_logfile(logfile, args)
			if macs_in_file:
				print(f"Found {len(macs_in_file)} MAC addresses in {logfile}")
				macs.update(macs_in_file)
		print(f"\nTotal unique MAC addresses extracted: {len(macs)}")
		for mac in macs:
			print(mac)
		try:
			with open(args.mac_file, 'w') as f:
				for mac in macs:
					f.write(mac + '\n')
			print(f"\nSaved MAC addresses to {args.mac_file}")
		except Exception as e:
			print(f"Error saving MAC addresses to file: {e} {type(e)}")
