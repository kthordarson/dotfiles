#!/bin/bash

# Check for required arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <path> <pattern> <rm>"
    echo "Example: $0 /home/user '*.log'"
    exit 1
fi
DO_RM="$3"
SEARCH_PATH="$1"
PATTERN="$2"
MIN_SIZE=$((1024)) # Minimum size in bytes
if [ "$DO_RM" != "1" ] && [ "$DO_RM" != "0" ]; then
    echo "Error: The third argument must be '1' (to remove files) or '0' (to just list files)."
    exit 1
fi
if [ "$DO_RM" = "1" ]; then
    echo "Searching for duplicates in '$SEARCH_PATH' matching pattern '$PATTERN' minsize $MIN_SIZE ... and will remove duplicates."
else
    echo "Searching for duplicates in '$SEARCH_PATH' matching pattern '$PATTERN' minsize $MIN_SIZE ... keeping dupes."
fi


# Create a temporary file to store checksums, sizes, and paths
TMPFILE=$(mktemp)

# Find files, compute checksums, and store them with file sizes
find "$SEARCH_PATH" -type f -name "$PATTERN" -size +$MIN_SIZE -print0 | while IFS= read -r -d '' file; do
    checksum=$(md5sum "$file" | awk '{print $1}')
    size=$(stat -c%s "$file")
    echo "$checksum $size $file"
done > "$TMPFILE"

# Find and process duplicates
echo "Duplicate files (same content):"
awk '{count[$1]++} END {for (c in count) if (count[c]>1) print c}' "$TMPFILE" | while read -r dup; do
    echo "-----"
    group=$(grep "^$dup" "$TMPFILE")
    size=$(echo "$group" | head -n1 | awk '{print $2}')
    echo "Size: $size bytes"
    files=()
    while read -r line; do
        file=$(echo "$line" | cut -d' ' -f3-)
        files+=("$file")
    done <<< "$group"

# Keep the first file, delete the rest
echo "Keeping: ${files[0]}"
for ((i=1; i<${#files[@]}; i++)); do
    if [ "$DO_RM" = "1" ]; then
        echo "Removing file: ${files[i]}"
        # rm -f "${files[i]}"
    else
        echo "Would remove file: ${files[i]}"
    fi
    done
done


# # Find and print duplicates
# echo "Duplicate files (same content):"
# awk '{count[$1]++} END {for (c in count) if (count[c]>1) print c}' "$TMPFILE" | while read -r dup; do
#     echo "-----"
#     group=$(grep "^$dup" "$TMPFILE")
#     size=$(echo "$group" | head -n1 | awk '{print $2}')
#     echo "Size: $size bytes"
#     echo "$group" | while read -r line; do
#         file=$(echo "$line" | cut -d' ' -f3-)
#         echo "File: $file"
#     done
# done

# Clean up
rm "$TMPFILE"
