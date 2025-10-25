#!/usr/bin/env bash
echo "search for string: $2 in folder: $1"
find "$1" -type f -iname '*.dll' -print0 | while IFS= read -r -d '' f;
do
    s=$(strings "$f" | sort | uniq | grep -i "$2")
    if [[ $s ]]; then
        echo "strings in file $f"
        echo "$s"
        echo "==================="
    fi
done;
