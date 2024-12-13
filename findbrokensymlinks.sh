#!/bin/bash

# find broken symlinks in a directory
broken=0
symlinkcount=0
if [[ -z $1 ]]; then

	echo "No search dir passed. searching in $(pwd)"
	startdir=$(pwd)
	#exit 1
else
	startdir=$1
	# foundsymlinks=$(find "$startdir" -type l)
	foundsymlinks=$(find $startdir -type l -xtype l -printf '%P\n' | grep -v -E 'docker|flatpak')
	symlinkcount=$(echo "$foundsymlinks" | wc -l)
	echo "Found $symlinkcount symlinks in $startdir"
	for symlink in $foundsymlinks; do
		# echo "cheking symlink: $symlink"
		#fullsympath=$(readlink -f "$startdir/$symlink"
		fullsympath="$startdir/$symlink"
		if [[ ! -e $fullsympath ]]; then
			broken=$((broken + 1))
			destlink=$(readlink -m "$fullsympath")
			echo "[$broken] removing broken symlink: $fullsympath -> $destlink $symlink"
			# rm -f "$fullsympath"
		fi
	done
fi
echo "Found $broken/$symlinkcount broken symlinks in $startdir"
exit 0
