#!/bin/bash

# Deactivate any active virtual environment
deactivate 2>/dev/null || true

# Check if venv exists and remove if it does
if [ -d "venv" ]; then
    rm -rf venv
fi

# Create and activate new venv
python3 -m venv venv
source venv/bin/activate

# Uninstall any existing global installation
pip uninstall -y disscli 2>/dev/null || true

# Install package in editable mode
pip install -e .

# Verify we're using the right version
which diss

echo "Development environment ready!"
echo "The 'diss' command is now using your local development version"
echo "Run 'source venv/bin/activate' in new terminals to use the development version" 