#!/usr/bin/env bash
echo "search for string: $2 in folder: $1"
for f in $(find $1 -type f -name '*.dll');
do
    s=$(strings $f | sort |uniq| grep -i $2)
    if [[ $s ]] then
        echo "strinsgs in file $f"
        echo $s
        echo "==================="
    fi
done;
