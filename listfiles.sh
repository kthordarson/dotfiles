#!/bin/bash

# Default directory is current directory (.)
DIRECTORY="${1:-.}"

# Check if the directory exists
if [[ ! -d "$DIRECTORY" ]]; then
    echo "Error: Directory '$DIRECTORY' does not exist."
    exit 1
fi

# Use find to list files, then format output with size and date
find "$DIRECTORY" -type f -exec ls -l --human-readable --time-style=long-iso {} + | \
awk '{
    size=$5;  # Human-readable size
    date=$6;  # Date in YYYY-MM-DD
    time=$7;  # Time in HH:MM:SS
    # Remaining fields are the file name (may include spaces)
    file=""; for (i=8; i<=NF; i++) file=file $i (i<NF ? " " : "");
    printf "%-10s %s %s  %s\n", size, date, time, file
}' | sort -h

exit 0