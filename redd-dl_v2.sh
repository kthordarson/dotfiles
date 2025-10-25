#!/bin/bash

# Configuration
output="$HOME/temp"
useragent="MyRedditScraper/1.0"
limit=25  # Reddit API typically allows up to 25-100 posts per request

# Check for required tools
if ! command -v jq >/dev/null 2>&1; then
    echo "Error: jq is required but not installed. Please install jq."
    exit 1
fi
if ! command -v wget >/dev/null 2>&1; then
    echo "Error: wget is required but not installed. Please install wget."
    exit 1
fi

# Check for subreddit argument
if [ -z "$1" ]; then
    echo "Usage: $0 <subreddit>"
    exit 1
fi

subreddit="$1"
url="https://www.reddit.com/r/$subreddit/.json?limit=$limit"

# Create output directory
mkdir -p "$output" || { echo "Error: Failed to create directory $output"; exit 1; }

# Main loop for pagination
after=""
while : ; do
    # Construct URL with pagination
    if [ -n "$after" ]; then
        fetch_url="$url&after=$after"
    else
        fetch_url="$url"
    fi

    # Fetch JSON data
    if ! content=$(wget -U "$useragent" -q -O - "$fetch_url" 2>/dev/null) || [ -z "$content" ]; then
        echo "Error: Failed to fetch data from $fetch_url"
        exit 1
    fi

    # Check if JSON is valid
    if ! echo "$content" | jq . >/dev/null 2>&1; then
        echo "Error: Invalid JSON response from Reddit"
        exit 1
    fi

    # Extract posts
    posts=$(echo "$content" | jq -r '.data.children[] | {id: .data.id, title: .data.title, url: .data.url}')
    if [ -z "$posts" ]; then
        echo "No posts found or end of listing."
        break
    fi

    # Process each post
    echo "$posts" | jq -r '[.id, .title, .url] | @tsv' | while IFS=$'\t' read -r id title url; do
        # Check for image URLs
        if [[ "$url" =~ \.(gif|jpg|jpeg|png)$ ]]; then
            # Sanitize title for filename
            newname=$(echo "$title" | tr -s '[:space:]' '_' | tr -d '/\\:*?"<>|' | head -c 50)
            newname="${newname}_${subreddit}_${id}.${url##*.}"

            echo "Downloading: $newname"
            if ! wget -U "$useragent" -nv -nc -O "$output/$newname" "$url"; then
                echo "Warning: Failed to download $url"
            fi
        fi
    done

    # Get next page's 'after' parameter
    after=$(echo "$content" | jq -r '.data.after')
    if [ "$after" == "null" ] || [ -z "$after" ]; then
        break
    fi

    # Respect Reddit's rate limits
    sleep 2
done

echo "Download complete."