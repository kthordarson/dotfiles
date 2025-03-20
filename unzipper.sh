#!/bin/bash
function unzip {
	startdir=$1
	find "$startdir" -maxdepth 1 -type f -name "*.zip" -print | while read -r zipfile; do
		zipbase=$(basename "$zipfile" | sed 's/ //g' | sed 's/\.zip//')
		echo "zipfile $zipfile zipbase $zipbase"
		7z x "$zipfile" -o"$startdir/$zipbase"
	done
}

if [[ -z $1 ]]; then

	echo "No search dir passed. searching in $(pwd)"
	startdir=$(pwd)
	#exit 1
else
	startdir=$1
	unzip "$startdir"
fi
exit 0
