#!/bin/bash

# Script to gather system information from multiple Ubuntu hosts via SSH for comparison

# Define hosts (replace with actual hostnames or IP addresses)
HOSTS=(
    "kth@frog"    # Replace with kth@frog.example.com or IP
    "kth@fiskur"  # Replace with kth@fiskur.example.com or IP
    "kth@zenbook" # Replace with kth@zenbook.example.com or IP
)

# Output file for comparison
OUTPUT_FILE="system_info_comparison.txt"

# Temporary directory for local and remote files
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT # Clean up temp files on exit

# Temporary script file to be executed on remote hosts
REMOTE_SCRIPT="$TEMP_DIR/remote_info.sh"

# Create the remote script
cat << 'EOF' > "$REMOTE_SCRIPT"
#!/bin/bash

# Debugging: Log execution
echo "Running on $HOSTNAME" >&2

# OS and Kernel
os=$(lsb_release -ds 2>/dev/null || echo "Unknown")
kernel=$(uname -r)

# Uptime
uptime=$(uptime -p 2>/dev/null | sed "s/up //")

# CPU
cpu=$(lscpu | grep "Model name" | awk -F: "{print \$2}" | xargs)
cpu_cores=$(lscpu | grep "^CPU(s):" | awk "{print \$2}")

# GPU
gpu=$(lspci | grep -i "VGA\|3D\|Display" | awk -F: "{print \$3}" | xargs || echo "Unknown")

# Memory
memory_total=$(free -m | awk "/Mem:/ {print \$2}")
memory_used=$(free -m | awk "/Mem:/ {print \$3}")
memory_percent=$(awk "BEGIN {printf \"%.1f\", ($memory_used*100)/$memory_total}")

# Packages
dpkg_count=$(dpkg -l 2>/dev/null | grep -c "^ii")
snap_count=$(snap list 2>/dev/null | grep -v "^Name" | wc -l || echo 0)
flatpak_count=$(flatpak list 2>/dev/null | wc -l || echo 0)

# Desktop Environment
de=$(echo "$XDG_CURRENT_DESKTOP" | awk -F: "{print \$1}" 2>/dev/null || echo "None")

# Output formatted info
cat <<OUTPUT
Host: $HOSTNAME
OS: $os
Kernel: $kernel
Uptime: $uptime
CPU: $cpu ($cpu_cores cores)
GPU: $gpu
Memory: ${memory_used}MiB / ${memory_total}MiB (${memory_percent}%)
Packages: $dpkg_count (dpkg), $snap_count (snap), $flatpak_count (flatpak)
Desktop Environment: $de
OUTPUT
EOF

# Make the remote script executable
chmod +x "$REMOTE_SCRIPT"

# Function to gather system info from a single host
gather_info() {
    local host="$1"
    local output_file="$2"
    echo "Gathering info from $host..."

    # Test SSH connectivity
    ssh -o ConnectTimeout=5 -o BatchMode=yes "$host" true 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "Error: Cannot connect to $host. Check SSH configuration or host availability." >> "$TEMP_DIR/error.log"
        echo "Host: $host\nStatus: Unreachable\n" > "$output_file"
        return 1
    fi

    # Copy the script to the remote host
    scp -q "$REMOTE_SCRIPT" "$host:/tmp/remote_info.sh" 2>> "$TEMP_DIR/error.log"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to copy script to $host." >> "$TEMP_DIR/error.log"
        echo "Host: $host\nStatus: Script copy failed\n" > "$output_file"
        return 1
    fi

    # Execute the script remotely and capture output
    ssh -o ConnectTimeout=5 "$host" /bin/bash /tmp/remote_info.sh > "$output_file" 2>> "$TEMP_DIR/error.log"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to execute script on $host." >> "$TEMP_DIR/error.log"
        echo "Host: $host\nStatus: Script execution failed\n" > "$output_file"
    fi

    # Clean up the remote script
    ssh -o ConnectTimeout=5 "$host" rm -f /tmp/remote_info.sh 2>> "$TEMP_DIR/error.log"
}

# Clear output file
> "$OUTPUT_FILE"

# Gather info from each host
for host in "${HOSTS[@]}"; do
    temp_file="$TEMP_DIR/${host//[@.]/_}.txt"
    gather_info "$host" "$temp_file"
    echo "=== $host ===" >> "$OUTPUT_FILE"
    cat "$temp_file" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
done

# Append errors, if any
if [ -s "$TEMP_DIR/error.log" ]; then
    echo "=== Errors ===" >> "$OUTPUT_FILE"
    cat "$TEMP_DIR/error.log" >> "$OUTPUT_FILE"
fi

# Display results
echo "System information gathered. Results saved to $OUTPUT_FILE:"
cat "$OUTPUT_FILE"

# Instructions for comparison
echo -e "\nTo compare manually, open $OUTPUT_FILE in a text editor or use 'column' for side-by-side view (if reformatted)."
echo "For quick checks, search for high memory usage, outdated kernels, or high package counts."