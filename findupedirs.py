#!/usr/bin/env python3
import os
import sys
from collections import defaultdict

def get_dir_info(path):
    """Get size and file count for a directory, excluding hidden files."""
    try:
        total_size = 0
        file_count = 0
        for root, _, files in os.walk(path):
            if '/.' in root:  # Skip hidden directories
                continue
            for file in files:
                if file.startswith('.'):  # Skip hidden files
                    continue
                file_count += 1
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, PermissionError):
                    pass  # Skip files that can't be accessed
        return total_size, file_count
    except (OSError, PermissionError):
        return None, None  # Return None if directory can't be accessed

def findupesdirs(path1, path2, max_depth=1):
    """Find directories with matching size and file count in two paths, up to max_depth."""
    if not path1 or not path2:
        print("Error: Please provide exactly two paths")
        sys.exit(1)
    if not os.path.isdir(path1) or not os.path.isdir(path2):
        print("Error: Both arguments must be valid directories")
        sys.exit(1)

    # Normalize paths to remove trailing slashes
    path1 = os.path.normpath(path1)
    path2 = os.path.normpath(path2)

    dir_groups = defaultdict(list)

    for base_path in [path1, path2]:
        # Get immediate subdirectories (depth 1)
        try:
            subdirs = [d for d in os.listdir(base_path) 
                      if os.path.isdir(os.path.join(base_path, d)) and not d.startswith('.')]
        except (OSError, PermissionError):
            print(f"Error: Cannot access {base_path}")
            continue

        for dir_name in subdirs:
            dir_path = os.path.join(base_path, dir_name)
            # Calculate depth relative to base_path
            relative_path = os.path.relpath(dir_path, base_path)
            depth = 0 if relative_path == '.' else relative_path.count(os.sep) + 1
            # print(f"Debug: Processing {dir_path}, Depth: {depth}")
            if depth > max_depth:
                continue  # Skip directories beyond max_depth
            size, file_count = get_dir_info(dir_path)
            if size is not None and file_count is not None:
                dir_groups[(size, file_count)].append(dir_path)

    for (size, file_count), paths in dir_groups.items():
        if len(paths) > 1:
            print(f"Duplicate Directories (Size: {size} Bytes, File Count: {file_count}):")
            for path in paths:
                print(path)
            print()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 findupesdirs.py <path1> <path2>")
        sys.exit(1)
    findupesdirs(sys.argv[1], sys.argv[2], max_depth=1)

