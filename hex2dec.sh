#!/bin/bash
echo "Type a hex number"
read -r hexNum
printf "The decimal value of $hexNum=%d\n" $((16#$hexNum))
