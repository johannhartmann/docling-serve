#!/bin/bash
# Script to install flash-attention from source

set -e

echo "Installing flash-attention from source..."

# Set CUDA_HOME if not already set
export CUDA_HOME=${CUDA_HOME:-/usr/local/cuda}

# Clone flash-attention repository
git clone https://github.com/Dao-AILab/flash-attention.git /tmp/flash-attention

# Navigate to the repository
cd /tmp/flash-attention

# Install flash-attention without build isolation
pip install flash-attn . --no-build-isolation

# Clean up
rm -rf /tmp/flash-attention

echo "Flash-attention installation complete!"