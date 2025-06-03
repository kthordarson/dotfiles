#!/bin/bash

transliterate_chinese_v3() {
    local path="$1"

    # Check if path is provided
    if [[ -z "$path" ]]; then
        echo "Error: No path provided. Usage: transliterate_chinese /path/to/directory"
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
    echo "Debug: Input path is '$path'"

    # Find files and directories, filter for Chinese characters using python3
    find "$path" -depth -maxdepth 3 -type d -print0 | while IFS= read -r -d $'\0' item; do
        # Use python3 to check for Chinese characters (U+4E00 to U+9FFF)
        if python3 -c "import sys; sys.exit(0 if any('\u4e00' <= c <= '\u9fff' for c in '''$item''') else 1)" 2>/dev/null; then
            dir=$(dirname "$item")
            base=$(basename "$item")

            # Debug: Print current item being processed
            echo "Debug: Processing '$item'"

            # Try to transliterate Chinese characters to Pinyin
            new_base=$(echo "$base" | uconv -x '::Any-Latin; ::Latin-ASCII; ::Lower' 2>/dev/null | tr -s ' ' '_' | tr -C 'a-zA-Z0-9._()-+ ' '_')

            # Debug: Print uconv output
            echo "Debug: uconv output for '$base' is '$new_base'"

            # Fallback: Replace Chinese characters with underscores, preserve other printable characters
            if [[ -z "$new_base" || "$new_base" == "$base" ]]; then
                new_base=$(echo "$base" | python3 -c "import sys, re; print(re.sub(r'[\u4e00-\u9fff]', '_', sys.stdin.read().strip()))" | tr -s ' ' '_')
                echo "Debug: Fallback used, new_base is '$new_base'"
            fi

            # Clean up multiple underscores and leading/trailing underscores
            new_base=$(echo "$new_base" | tr -s '_' | sed 's/^_//;s/_$//')
            new_base=$(echo "$new_base" | sed 's/^_//;s/_$//')

            # If new_base is empty, use a sanitized version of the original
            if [[ -z "$new_base" ]]; then
                new_base=$(echo "$base" | tr -C 'a-zA-Z0-9._()-+ ' '_' | tr -s '_' | sed 's/^_//;s/_$//')
                echo "Debug: Empty new_base, using sanitized original: '$new_base'"
            fi

            # Debug: Print the new name
            echo "Debug: New name will be '$new_base'"

            # If transliteration produced a different name
            if [[ "$base" != "$new_base" && -n "$new_base" ]]; then
                new_item="$dir/$new_base"
                # Check if the new name already exists to avoid overwriting
                if [[ -e "$new_item" ]]; then
                    echo "Warning: Cannot rename '$item' to '$new_item' (target already exists)."
                    continue
                fi
                # Check if new_base is valid (using grep instead of =~)
                if echo "$new_base" | grep -E '^[a-zA-Z0-9._()-+ ]+$' >/dev/null; then
                    # Perform the rename
                    # mv -v "$item" "$new_item"
                    echo "Renamed '$item' to '$new_item'"
                else
                    echo "Warning: Invalid filename '$new_base' for '$item'. Skipping."
                fi
            else
                echo "Debug: No change needed for '$item' (no valid new name)"
            fi
        fi
    done
}

new_transliterate_chinese() {
    local path="$1"

    # Check if path is provided
    if [[ -z "$path" ]]; then
        echo "Error: No path provided. Usage: transliterate_chinese /path/to/directory"
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
    echo "Debug: Input path is '$path'"

    # Find files and directories, filter for Chinese characters using python3
    find "$path" -depth -maxdepth 3 -type d -print0 | while IFS= read -r -d $'\0' item; do
        # Use python3 to check for Chinese characters (U+4E00 to U+9FFF)
        if python3 -c "import sys; sys.exit(0 if any('\u4e00' <= c <= '\u9fff' for c in '''$item''') else 1)" 2>/dev/null; then
            # Get the directory and filename
            dir=$(dirname "$item")
            base=$(basename "$item")

            # Debug: Print current item being processed
            echo "Debug: Processing '$item'"

            # Try to transliterate Chinese characters to Pinyin
            new_base=$(echo "$base" | uconv -x '::Any-Latin; ::Latin-ASCII; ::Lower' 2>/dev/null | tr -s ' ' '_' | tr -C 'a-zA-Z0-9._()-+ ' '_')

            # Fallback: Replace Chinese characters with underscores, preserve other printable characters
            if [[ -z "$new_base" || "$new_base" == "$base" ]]; then
                new_base=$(echo "$base" | python3 -c "import sys, re; print(re.sub(r'[\u4e00-\u9fff]', '_', sys.stdin.read().strip()))" | tr -s ' ' '_')
            fi

            # Clean up multiple underscores and leading/trailing underscores
            new_base=$(echo "$new_base" | tr -s '_' | sed 's/^_//;s/_$//')

            # If new_base is empty, use a sanitized version of the original
            if [[ -z "$new_base" ]]; then
                new_base=$(echo "$base" | tr -C 'a-zA-Z0-9._()-+ ' '_' | tr -s '_' | sed 's/^_//;s/_$//')
            fi

            # Debug: Print the new name
            echo "Debug: New name will be '$new_base'"

            # If transliteration produced a different name
            if [[ "$base" != "$new_base" && -n "$new_base" ]]; then
                new_item="$dir/$new_base"
                # Check if the new name already exists to avoid overwriting
                if [[ -e "$new_item" ]]; then
                    echo "Warning: Cannot rename '$item' to '$new_item' (target already exists)."
                    continue
                fi
                # Check if new_base is valid (allow spaces and +)
                # if [[ "$new_base" =~ ^[a-zA-Z0-9._()-+ ]+$ ]]; then
                if [[ "$new_base" =~ ^[a-zA-Z0-9._\(\)\-\ \+]+$ ]]; then
                    # Perform the rename
                    # mv -v "$item" "$new_item"
                    echo "Renamed '$item' to '$new_item'"
                else
                    echo "Warning: Invalid filename '$new_base' for '$item'. Skipping."
                fi
            else
                echo "Debug: No change needed for '$item' (no valid new name)"
            fi
        fi
    done
}

improved_transliterate_chinese() {
    local path="$1"

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

    # Find files and directories with Chinese characters
    find "$path" -depth -type d -print0 | while IFS= read -r -d $'\0' item; do
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
                echo "rename: '$item' → '$new_item'"
            else
                echo "No change needed for: '$item'"
            fi
        fi
    done
}
