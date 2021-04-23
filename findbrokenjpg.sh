#!/bin/bash
find . -iname '*.jpg' | while read -r f
  do
      identify "$f"
#    if pdftotext "$f" - &> /dev/null; then
#        echo "$f" was ok;
#    else
#        mv "$f" "$f.broken";
#        echo "$f" is broken;
#    fi;
done

