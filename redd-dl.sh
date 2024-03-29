#!/bin/bash

#cfg
output="~/temp/"
useragent="firefox"

subreddit=$1
url="http://pay.reddit.com/r/$subreddit/.json"
content=`wget -U "$useragent" --no-check-certificate -q -O - $url`
mkdir -p $output
while : ; do
    urls=$(echo -e "$content"|grep -Po '"url":.*?[^\\]",'|cut -f 4 -d '"')
    names=$(echo -e "$content"|grep -Po '"title":.*?[^\\]",'|cut -f 4 -d '"')
    ids=$(echo -e "$content"|grep -Po '"id":.*?[^\\]",'|cut -f 4 -d '"')
    a=1
    for url in $(echo -e "$urls"); do
        if [ -n  "`echo "$url"|egrep \".gif|.jpg\"`" ]; then
            #echo -n "$url: "
            name=`echo -e "$names"|sed -n "$a"p`
            id=`echo -e "$ids"|sed -n "$a"p`
            echo $name
            newname="$name"_"$subreddit"_$id.${url##*.}
            wget -U "$useragent" --no-check-certificate -nv -nc -P down -O "$output/$newname" $url
        fi
        a=$(($a+1))
    done
    after=$(echo -e "$content"|grep -Po '"after":.*?[^\\]",'|cut -f 4 -d '"'|tail -n 1)
    if [ -z $after ]; then
        break
    fi
    url="http://www.reddit.com/r/$subreddit/.json?count=200&after=$after"
    content=`wget -U "$useragent" --no-check-certificate -q -O - $url`
    #echo -e "$urls"
done