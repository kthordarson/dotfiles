#!/bin/bash

pushd() {
    command pushd "$@" >/dev/null || exit
}

popd() {
    command popd "$@" >/dev/null || exit
}

function scandirs() {
    startdir=$1
    echo "searching in $startdir"
    for gitfolder in $(find "$startdir" -maxdepth 2 -type d -name .git -print); do
        pushd "$(pwd)" || exit
        cd "$gitfolder" || exit
        cd ../
        echo "checking $(pwd)"
        remoteurl=$(git remote get-url --all origin)
        if [[ -z $remoteurl ]]; then
            echo -e "\tno remoteurl in $(pwd)"
            continue
        fi
        if [[ $remoteurl == *"git@github.com"* ]]; then
            echo -e "\tSkipping (ssh) remote url $remoteurl in $(pwd)"
            continue
        fi
        gstatus=$(git status 2>&1)
        gcnt=$(echo "${#gstatus}" | wc -c)
        #gcnt=$(echo $gstatus | wc -c)
        if [[ $gstatus == *"nothing to commit, working tree clean"* ]]; then
            # decide what to do with local changes...
            echo -e "\tUptodate nothing to do in $(pwd) $remoteurl $gcnt "
            continue
        fi
        if [[ $gstatus == *"fatal: bad object HEAD"* ]]; then
            # decide what to do with local changes...
            echo -e "\tError $gstatus in $(pwd) $remoteurl $gcnt ... trying pull" #
            pullresult=$(git pull --rebase --autostash --recurse-submodules -q 2>&1)
            if [[ $pullresult == *"fatal: bad object"* ]]; then
                echo -e "\tError in $(pwd) $remoteurl $gcnt" # $pullresult
                fi
            continue
        fi
        if [[ $gcnt -gt 1 ]]; then
            # decide what to do with local changes...
            # echo "gstatus:  in $(pwd) $gcnt " # $gstatus
            modified=$(git status | grep modified | wc -l)
            newfiles=$(git status | grep 'new file' | wc -l)
            echo -e "\tModified: $modified newfiles: $newfiles $(pwd) "
            continue
        else
            if [[ $remoteurl == *"github.com"* ]]; then
                # url looks ok, check http status
                httpstatus=$(curl --write-out %{http_code} --silent --output /dev/null $remoteurl)
                if [[ $httpstatus == 200 ]]; then
                    # http status ok, continue
                    echo -e "\thttpstatus: $httpstatus update $(pwd) from $remoteurl"
                    continue
                fi
                if [[ $httpstatus == 301 ]]; then
                    # http status ok, continue
                    echo -e "\tredirectorhttpstatus: $httpstatus update $(pwd) from $remoteurl"
                    continue
                fi
                if [[ $httpstatus != 200 ]]; then
                    echo -e "\tError httpstatus: $httpstatus update $(pwd) from ${remoteurl}"
                    continue
                fi
        fi
    fi
    popd || exit
    done
    # echo "c: $charcount l: $linecount"
    #done
}


if [[ -z $1 ]];
then

    echo "No search dir passed. searching in $(pwd)"
    startdir=$(pwd)
    #exit 1
else
startdir=$1
scandirs "$startdir"
fi
exit 0
