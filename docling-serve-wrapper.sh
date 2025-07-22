#!/bin/bash
# Wrapper script for docling-serve that installs flash-attention from source if needed

# Check if flash-attention is installed
if ! python -c "import flash_attn" 2>/dev/null; then
    echo "Flash-attention not found. Installing from source..."
    echo "This will take some time on first run..."
    
    # Check if we have CUDA available
    if [ ! -d "/usr/local/cuda" ]; then
        echo "ERROR: CUDA not found at /usr/local/cuda"
        echo "Please ensure you're running this container with GPU support"
        exit 1
    fi
    
    # Install flash-attention from source
    /opt/app-root/bin/install-flash-attention.sh
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install flash-attention"
        exit 1
    fi
fi

# Run the actual docling-serve command
exec docling-serve "$@"