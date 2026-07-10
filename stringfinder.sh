#!/usr/bin/env bash

# Script to search for a string in files within a directory
# Usage: ./script.sh <directory> <search_string> [-c] [-e <extension>]

# Function to display usage information
usage() {
    echo "Usage: $0 <directory> <search_string> [-c] [-e <extension>]"
    echo "  -c: Case-sensitive search"
    echo "  -e: Limit search to files with specified extension (e.g., 'txt')"
    exit 1
}

# Function to print colored output
print_color() {
    local color="$1"
    shift
    # ANSI colors: red=31, green=32, blue=34
    printf "\033[${color}m%s\033[0m\n" "$@"
}

# Check for minimum arguments
if [[ $# -lt 2 ]]; then
    print_color 31 "Error: Directory and search string are required."
    usage
fi

# Assign arguments
directory="$1"
search_string="$2"
shift 2

# Default options
case_sensitive=false
file_extension=""

# Parse optional arguments
while getopts "ce:" opt; do
    case $opt in
        c) case_sensitive=true ;;
        e) file_extension="$OPTARG" ;;
        *) usage ;;
    esac
done

# Validate directory
if [[ ! -d "$directory" ]]; then
    print_color 31 "Error: '$directory' is not a valid directory."
    exit 1
fi

# Build find command based on file extension
find_cmd="find \"$directory\" -type f"
[[ -n "$file_extension" ]] && find_cmd="$find_cmd -name \"*.$file_extension\""

# Set grep options
grep_opts="-i" # Default: case-insensitive
[[ "$case_sensitive" == true ]] && grep_opts=""

# Initialize counters
total_files=0
matched_files=0

# Print header
print_color 34 "Searching for '$search_string' in '$directory'..."

# Process files
while IFS= read -r -d '' file; do
    ((total_files++))
    # Extract strings and search for the pattern
    matches=$(strings "$file" 2>/dev/null | sort | uniq | grep $grep_opts "$search_string" | head)
    if [[ -n "$matches" ]]; then
        ((matched_files++))
        print_color 32 "Found in: $file"
        # Print matches with indentation and line numbers
        echo "$matches" | awk '{print "\t" NR ": " $0}'
        echo ""
    fi
done < <(eval "$find_cmd -print0")

# Print summary
print_color 34 "Summary:"
echo "Total files searched: $total_files"
echo "Files with matches: $matched_files"

exit 0