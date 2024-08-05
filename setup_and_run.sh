#!/bin/bash

# Define the virtual environment directory, requirements file, and script location
VENV_DIR="ndmienv"
REQUIREMENTS_FILE="requirements.txt"
SCRIPT_DIR="src"
SCRIPT_NAME="main.py"

# Create a virtual environment
echo "Creating virtual environment..."
python -m venv $VENV_DIR

# Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install necessary packages
echo "Installing required packages..."
pip install --upgrade pip

# Install packages from requirements.txt
pip install -r $REQUIREMENTS_FILE

# Run the script
echo "Running the script..."
python $SCRIPT_DIR/$SCRIPT_NAME

# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Done!"

