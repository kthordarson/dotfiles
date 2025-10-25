#!/bin/bash


# Check if provided path exists
if [ ! -d "$1" ]; then
    echo "Error: Directory '$1' does not exist"
    exit 1
fi

if [ $# -eq 2 ]; then
    MAX_DEPTH=$2
else
    MAX_DEPTH=3  # Default maximum depth for search
fi

# Function to convert bytes to human-readable format
human_readable_size() {
    local size=$1
    local units=("B" "KB" "MB" "GB" "TB")
    local unit=0
    local value=$size

    while [ ${value%.*} -ge 1024 ] && [ $unit -lt 4 ]; do
        value=$(echo "scale=2; $value / 1024" | bc)
        ((unit++))
    done
    printf "%.2f %s" $value ${units[$unit]}
}

# Find all directories and identify duplicates by name
echo "Searching for duplicate directory names in $1 (max depth: $MAX_DEPTH)"
echo "Results:"

# Find directories, extract their names, and identify duplicates
find "$(realpath "$1")" -maxdepth $MAX_DEPTH -type d -not -path "$(realpath "$1")" | while read -r dir; do
    basename "$(realpath "$dir")"
done | sort | uniq -d | while read -r dirname; do
    echo "Duplicate directory name: $dirname"
    # Find all directories with this name and calculate their sizes
    find "$(realpath "$1")" -maxdepth $MAX_DEPTH -type d -name "$dirname" | while read -r dup_dir; do
        size=$(du -sb "$dup_dir" | cut -f1)
        filecount=$(find "$dup_dir" -type f | wc -l)
        subdirs=$(find "$dup_dir" -type d | wc -l)
        human_size=$(human_readable_size $size)
        echo "  - $dup_dir (Size: $human_size files $filecount subdirs $subdirs)"
    done
done