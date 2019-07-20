import os
import time
import argparse


def get_tree(path, filelist):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            get_tree(entry.path, filelist)
            filelist.append((entry, entry.stat().st_ctime))
        else:
            entry.stat(follow_symlinks=False).st_size
            filelist.append((entry, entry.stat().st_ctime))


myparse = argparse.ArgumentParser(description="Find new files")
myparse.add_argument('Path', metavar='path', type=str, help="Path to search", default=".")
myparse.add_argument('Number', metavar='filenum', type=int, help="Limit to x results", default=10)
args = myparse.parse_args()
input_path = args.Path
limit = args.Number

filelist = []
result = get_tree("c:/temp/", filelist)
filelist.sort(key=lambda x: x[1], reverse=False)
for file in filelist[-limit:]:
    print(time.ctime(file[1]), file[0].path)
