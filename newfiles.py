#!/usr/bin/python3

import os
import time
import argparse


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


myparse = argparse.ArgumentParser(description="Find new files")
myparse.add_argument('--path', metavar='path', type=str, help="Path to search", default=".")
myparse.add_argument('--maxfiles', metavar='maxfiles', type=int, help="Limit to x results", default=10)
args = myparse.parse_args()
input_path = args.path
maxfiles = args.maxfiles

filelist = []
result = get_tree(input_path, filelist)
filelist.sort(key=lambda x: x[1], reverse=False)
for file in filelist[-maxfiles:]:
    print(time.ctime(file[1]), file[0].path)
