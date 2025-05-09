#!/bin/bash

# File to store the display configuration
CONFIG_FILE="$HOME/display_config.txt"

# Function to save the current display configuration
save_display_config() {
    echo "Saving current display configuration to $CONFIG_FILE..."
    
    # Get the current xrandr configuration
    xrandr --current > "$CONFIG_FILE"
    
    if [ $? -eq 0 ]; then
        echo "Display configuration saved successfully."
    else
        echo "Error: Failed to save display configuration."
        exit 1
    fi
}

# Function to restore the saved display configuration
restore_display_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "Error: Configuration file $CONFIG_FILE not found."
        exit 1
    fi

    echo "Restoring display configuration from $CONFIG_FILE..."

    # Read the saved configuration and parse active outputs
    while IFS= read -r line; do
        # Look for lines indicating connected displays with resolution and position
        if [[ $line =~ ^([A-Za-z0-9-]+)\ connected\ ([0-9]+x[0-9]+)\+([0-9]+)\+([0-9]+) ]]; then
            output="${BASH_REMATCH[1]}"
            resolution="${BASH_REMATCH[2]}"
            x_pos="${BASH_REMATCH[3]}"
            y_pos="${BASH_REMATCH[4]}"
            
            # Check for rotation (normal, left, right, inverted)
            rotation="normal"
            if [[ $line =~ (normal|left|right|inverted) ]]; then
                rotation="${BASH_REMATCH[1]}"
            fi
            
            echo "Restoring $output: ${resolution}+${x_pos}+${y_pos}, rotation: $rotation"
            
            # Apply the settings using xrandr
            xrandr --output "$output" --mode "$resolution" --pos "${x_pos}x${y_pos}" --rotate "$rotation"
            
            if [ $? -ne 0 ]; then
                echo "Error: Failed to restore settings for $output."
                exit 1
            fi
        fi
    done < "$CONFIG_FILE"

    echo "Display configuration restored successfully."
}

# Function to display usage
usage() {
    echo "Usage: $0 {save|restore}"
    echo "  save   : Save the current display configuration"
    echo "  restore: Restore the saved display configuration"
    exit 1
}

# Main script logic
case "$1" in
    save)
        save_display_config
        ;;
    restore)
        restore_display_config
        ;;
    *)
        usage
        ;;
esac
