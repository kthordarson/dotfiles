#!/bin/bash
# finna vids og allt info um öll vids

mediafolder[0]=$1

# Setup find correctly.
export IFS=$'\n'

#leita af þessum tegundum...
types=( avi mpg mpeg mkv mp4 )

# counter=0

# setup regex for types
types_re="\\("${types[0]}

for t in "${types[@]:1:${#types[*]}}"; do
    types_re="${types_re}\\|${t}"
done
types_re="${types_re}\\)"

for x in "${mediafolder[@]}"
  do
    echo "$x"
#    for i in $(find "$x" -type f -regex ".*\.${types_re}")
      #do
    find "$x" -type f -regex ".*\.${types_re}" -print0 | while IFS= read -r -d '' i; do
        # echo "$x $counter $i"
        # echo -n "."
        size=$(stat -c "%s" "$i")
        codec=$(ffprobe -print_format csv -v quiet -show_streams -select_streams v "$i" | awk -F',' '{print$3}' )
        echo "$size $codec - $i"
      done
  done

# print the info
# echo $output | tr ';' '\n' | sort -nr

