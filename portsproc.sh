#!/bin/bash
export IFS=$'\n'
openports="$(sudo lsof -ni -t -sTCP:LISTEN | sort | uniq -u | tail +2)"
for pidin in $openports
    do
        pid=$(echo "$pidin" | tr -d "\0")
        cmdline=$(cat /proc/"$pid"/cmdline  | tr -d "\0")
        listenport=$(sudo lsof -nP -p$pid -f -w | grep LISTEN | awk {'print $9'})
        echo "$listenport PID: $pid cmd: $cmdline "
    done
