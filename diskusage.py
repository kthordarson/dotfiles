#!/usr/bin/python3

import os
import time
import argparse
from pathlib import Path
from glob import glob
from dataclasses import dataclass, field
import operator

@dataclass(order=True, frozen=False)
class DirItem:
	sort_index: int = field(init=False, repr=False)
	name: Path
	totalsize: int = 0
	subfiles: int = 0
	subdirs: int = 0

	def __init__(self, name:Path):
		self.name = name
		self.totalsize = get_directory_size(self.name)
		self.subfiles = get_subfilecount(self.name)
		self.subdirs = get_subdircount(self.name)
	
	def __post_init(self):
		object.__setattr__(self, 'sort_index', self.totalsize)
		#self.sort_index = self.totalsize

	def __str__(self):
		return f'{self.name}, {self.totalsize}'

	def get_size(self):		
		return get_size_format(self.totalsize,suffix='B')
	
	def get_filecount(self):
		return self.subfiles

	def get_dircount(self):
		return self.subdirs

def getdirsize(root_directory):
	return sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())	

def get_directory_size(directory):
    """Returns the `directory` size in bytes."""
    total = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file():
                # if it's a file, use stat() function
                total += entry.stat().st_size
            elif entry.is_dir():
                # if it's a directory, recursively call this function
                try:
                    total += get_directory_size(entry.path)
                except FileNotFoundError:
                    pass
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    return total

def get_subfilecount(directory):
	filecount = 0
	filecount = len([k for k in directory.glob('**/*') if k.is_file()])
	return filecount

def get_subdircount(directory):
	dc = 0
	dc = len([k for k in directory.glob('**/*') if k.is_dir()])
	return dc

def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"	
def get_tree(path, filelist):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            try:
                get_tree(entry.path, filelist)
                filelist.append((entry, entry.stat().st_ctime))
            except:
                pass
        else:
            try:
                entry.stat(follow_symlinks=False).st_size
                filelist.append((entry, entry.stat().st_ctime))
            except:
                pass


myparse = argparse.ArgumentParser(description="show folder sizes and things..")
myparse.add_argument('--path', metavar='path', type=str, help="Path to search", default=".")
myparse.add_argument('--number', metavar='filenum', type=int, help="Limit to x results", default=10)
args = myparse.parse_args()
input_path = Path(args.path)
limit = args.number

filelist = []
itemlist = []
folderlist = [k for k in input_path.glob('*') if not k.is_file()]
itemlist = [DirItem(name=k) for k in folderlist]
# itemlist_sorted = sorted(itemlist, key=operator.attrgetter("totalsize"))

for item in sorted(itemlist, key=operator.attrgetter("totalsize")):
	print(f'{item.name} {item.get_size()} {item.subfiles} {item.subdirs}')