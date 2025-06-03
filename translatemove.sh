#!/bin/bash

improved_transliterate_chinese() {
    local path="$1"
    local maxdepth="$2"

    if [[ -z "$maxdepth" ]]; then
        maxdepth=3  # Default to 3 if not provided
    fi
    # Check if path is provided
    if [[ -z "$path" ]]; then
        echo "Error: No path provided. Usage: improved_transliterate_chinese /path/to/directory"
        return 1
    fi

    # Check if path exists
    if [[ ! -e "$path" ]]; then
        echo "Error: Path '$path' does not exist."
        return 1
    fi

    # Check if uconv is installed
    if ! command -v uconv &> /dev/null; then
        echo "Warning: 'uconv' is not installed. Please install icu-devtools (e.g., sudo apt install icu-devtools)."
        return 1
    fi

    # Check if python3 is installed for filtering
    if ! command -v python3 &> /dev/null; then
        echo "Warning: 'python3' is not installed. Please install python3 to filter Chinese characters."
        return 1
    fi

    # Debug: Print the input path
    if [[ $path == '.' ]]; then
        echo "skipping current directory '.'"
        return 0
    fi
    echo "Debug: Input path is '$path' with maxdepth $maxdepth"
    # Find files and directories with Chinese characters
    find "$path" -depth -maxdepth $maxdepth -print0 | while IFS= read -r -d $'\0' item; do
        # echo "Debug: Processing item '$item'"
        # Use python3 to check for Chinese characters (U+4E00 to U+9FFF)
        if python3 -c "import sys; sys.exit(0 if any('\u4e00' <= c <= '\u9fff' for c in '''$item''') else 1)" 2>/dev/null; then
            dir=$(dirname "$item")
            base=$(basename "$item")
            
            # echo "Processing: '$base'"
            
            # First pass: Transliterate Chinese characters to Pinyin
            new_base=$(echo "$base" | uconv -x '::Any-Latin; ::Latin-ASCII;' 2>/dev/null)
            
            # Remove any remaining non-ASCII characters and replace with underscores
            new_base=$(echo "$new_base" | python3 -c "import sys, re; print(re.sub(r'[^\x00-\x7F]', '_', sys.stdin.read()))")
            
            # Replace special characters and spaces with underscores
            new_base=$(echo "$new_base" | tr -s '[:space:]' '_')
            
            # Keep only alphanumeric, underscores, dots, and safe characters
            new_base=$(echo "$new_base" | tr -c 'a-zA-Z0-9._' '_')
            
            # Clean up multiple and trailing underscores
            new_base=$(echo "$new_base" | tr -s '_' | sed 's/^_//;s/_$//')
            
            # Ensure we have a valid filename
            if [[ -z "$new_base" ]]; then
                # Generate a simple transliterated name based on timestamp if all else fails
                new_base="transliterated_$(date +%s)"
            fi
            
            # echo "New name: '$new_base'"
            
            # If transliteration produced a different name
            if [[ "$base" != "$new_base" && -n "$new_base" ]]; then
                new_item="$dir/$new_base"
                
                # Check if the new name already exists
                if [[ -e "$new_item" ]]; then
                    echo "Warning: Cannot rename '$item' to '$new_item' (target exists)"
                    # Add a timestamp to make the name unique
                    new_base="${new_base}_$(date +%s)"
                    new_item="$dir/$new_base"
                    echo "Using alternative name: '$new_base'"
                fi
                
                # Perform the rename (uncomment to actually rename)
                mv -v "$item" "$new_item"
                # echo "rename: '$item' → '$new_item'"
            else
                echo "No change needed for: '$item'"
            fi
        fi
    done
}
