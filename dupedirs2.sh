#!/bin/bash
# Default usage (min depth 3, no size filter)
# ./dupedirs2.sh /path/to/search

# # Set minimum size to 10MB
# ./dupedirs2.sh /path/to/search 10MB

# # Set maximum depth to 5 and minimum size to 100MB
# ./dupedirs2.sh /path/to/search 100MB 5

# # Set maximum depth to 5 (no size filter)
# ./dupedirs2.sh /path/to/search 5


# Check if provided path exists
if [ ! -d "$1" ]; then
    echo "Error: Directory '$1' does not exist"
    exit 1
fi

# Default values
MAX_DEPTH=3
MIN_SIZE=0

# Parse arguments
if [ $# -ge 2 ]; then
    # Check if second argument is numeric (depth) or a size specification
    if [[ $2 =~ ^[0-9]+$ ]]; then
        MAX_DEPTH=$2
        if [ $# -ge 3 ]; then
            MIN_SIZE=$3
        fi
    else
        MIN_SIZE=$2
        # If we have 3 args and the 3rd is numeric, it's the depth
        if [ $# -ge 3 ] && [[ $3 =~ ^[0-9]+$ ]]; then
            MAX_DEPTH=$3
        fi
    fi
fi

# Function to convert human-readable size to bytes
to_bytes() {
    local size=$1
    local value=$(echo $size | sed 's/[^0-9.]//g')
    local unit=$(echo $size | sed 's/[0-9.]//g' | tr '[:lower:]' '[:upper:]')
    
    case $unit in
        KB|K) value=$(echo "$value * 1024" | bc) ;;
        MB|M) value=$(echo "$value * 1024 * 1024" | bc) ;;
        GB|G) value=$(echo "$value * 1024 * 1024 * 1024" | bc) ;;
        TB|T) value=$(echo "$value * 1024 * 1024 * 1024 * 1024" | bc) ;;
        *) value=${value:-0} ;; # Default to bytes or 0 if empty
    esac
    
    echo ${value%.*}  # Remove decimal part
}

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

# Convert MIN_SIZE to bytes for comparison
MIN_SIZE_BYTES=$(to_bytes $MIN_SIZE)

# Find all directories and identify duplicates by name
echo "Searching for duplicate directory names in $1 (max depth: $MAX_DEPTH, min size: $(human_readable_size $MIN_SIZE_BYTES))"
echo "Results:"

# Find directories, extract their names, and identify duplicates
find "$(realpath "$1")" -maxdepth $MAX_DEPTH -type d -not -path "$(realpath "$1")" | while read -r dir; do
    basename "$(realpath "$dir")"
done | sort | uniq -d | while read -r dirname; do
    # Create a temporary file for this group of directories
    tmp_file=$(mktemp)
    has_matches=0
    
    # Find all directories with this name and calculate their metrics
    find "$(realpath "$1")" -maxdepth $MAX_DEPTH -type d -name "$dirname" | while read -r dup_dir; do
        size=$(du -sb "$dup_dir" | cut -f1)
        if [ "$size" -ge "$MIN_SIZE_BYTES" ]; then
            filecount=$(find "$dup_dir" -type f | wc -l)
            subdirs=$(find "$dup_dir" -type d | wc -l)
            
            # Create a signature based on metrics
            signature="${size}_${filecount}_${subdirs}"
            
            echo "$dup_dir;$size;$filecount;$subdirs;$signature" >> "$tmp_file"
            has_matches=1
        fi
    done
    
    # Only process if we have directories meeting the size criteria
    if [ -s "$tmp_file" ]; then
        echo "Duplicate directory name: $dirname"
        
        # Process each directory and mark identical ones
        while IFS=';' read -r dup_dir size filecount subdirs signature; do
            human_size=$(human_readable_size $size)
            
            # Count how many entries have this signature
            identical=$(grep -c ";$signature$" "$tmp_file")
            
            if [ "$identical" -gt 1 ]; then
                echo "  - $dup_dir (Size: $human_size files $filecount subdirs $subdirs) [SAME SIZE/COUNT]"
            else
                echo "  - $dup_dir (Size: $human_size files $filecount subdirs $subdirs)"
            fi
        done < "$tmp_file"
    fi
    
    # Clean up
    rm -f "$tmp_file"
done