export IFS=$'\n'
#openports=$(sudo lsof -nP -iTCP -sTCP:LISTEN | head -n -1 | sort | uniq -u)
openports=$(sudo lsof -t -nP -sTCP:LISTEN -iTCP | grep -v IPv6 | sort | uniq -u | tail +2)
for k in $openports
    do
        #IFS= read  -d ' '
        pidlist=$(echo $k | awk '{print $1}' | sort -b | uniq -u)
        #echo $pidlist
        for pid in $pidlist
        do
            procline="/proc/$pid/cmdline"
            cmdline=$(cat $procline | tr -d "\r\n\0" | cut -c1-60)
            listenport=$(sudo lsof -nP -p$pid -f -w | grep LISTEN | awk {'print $9'})
            for lp in $listenport
            do
                echo "PID: $pid cmd: $cmdline listen: $lp"
            done
            #echo "PID: $pid cmd: $cmdline"
            #echo "Listen: $listenport"
            #echo $procline
            #echo -e "pid: $pid cmd: $cmdline \n"
        done
    done
