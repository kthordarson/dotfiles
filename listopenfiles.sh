#!/bin/bash
for p in /proc/{0..9}*; do
  i=$(basename "$p")
  echo "scanning pid $p $i"
  for f in "$p"/fd/*; do
    l=$(readlink -e "$f")
    if [ "$l" ]; then
      echo "$i: $l"
    fi
  done
done | sort -u | sort -n

