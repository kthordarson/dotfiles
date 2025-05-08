#!/bin/bash
export IFS=$'\n'
pakcs="$(dpkg-query -Wf '${Installed-Size}\t${Package}\n'| sort -n | tail -n 20)"
for pack in $pakcs
    do
		pkgsize=$(echo "$pack" | awk '{print $1}' | numfmt --to iec --format "%.1f")
		pkgname=$(echo "$pack" | awk '{print $2}')
        echo "$pkgsize $pkgname"
    done
