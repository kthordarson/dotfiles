#!/bin/bash
# finna vids og allt info um öll vids

mediafolder[0]=$1

# Setup find correctly.
export IFS=$'\n'

#leita af þessum tegundum...
types=( avi mpg mpeg mkv mp4 )

counter=0

# setup regex for types
types_re="\\("${types[0]}

for t in "${types[@]:1:${#types[*]}}"; do
    types_re="${types_re}\\|${t}"
done
types_re="${types_re}\\)"

for x in "${mediafolder[@]}"
  do
    echo $x
    for i in $(find $x -type f -regex ".*\.${types_re}")
      do
        # echo "$x $counter $i"
        # echo -n "."
        size=$(stat -c "%s" $i)
        codec=$(ffprobe -print_format csv -v quiet -show_streams -select_streams v $i | awk -F',' '{print$3}' )
        output=$(echo "$size $codec - $i")
        echo $output

        # extract header from first bytes of the file
        # vid_header=`xxd -s 112 -l 4 $i`
        # convert to lovercase
        # vid_header=`echo $vid_header | tr [:upper:] [:lower:]`
        # if [[ $vid_header == *div3* ]]; then
        #        echo "$vid_header in $i"
        #        filestoconvert[$counter]=$i
        #        let counter=counter+1
        # fi
      done
  done

# print the info
# echo $output | tr ';' '\n' | sort -nr

