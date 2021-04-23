#!/usr/bin/python3

from PIL import Image
import os
def scantree(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            if entry.name.lower().endswith('.JPG'):
                yield entry


if __name__ == "__main__":
        jpglist = []
        for entry in scantree("/media/sda1"):
                jpglist.append(entry)
        for jpgimage in jpglist:
            #print (jpgimage.name)
            try:
                im = Image.open(jpgimage.path)
                im.verify()
            except Exception as e:
                print(f'Error with {jpgimage.name} {e}')
                badname = jpgimage.path + '.badimage'
                # print(badname)
                os.rename(jpgimage.path, badname)


#im = Image.open("foo.png")
#im.verify()



