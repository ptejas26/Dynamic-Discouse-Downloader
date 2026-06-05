#!/bin/bash

# Get the current timestamp (e.g., 20250518_153012)
timestamp=$(date +"%Y%m%d_%H%M%S")
root_folder="$HOME/Downloads/Learnings/"
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Create a new directory with the timestamp
cd $root_folder
mkdir "$timestamp-$1"
echo "Created directory: $timestamp"

# Change into that directory
cd "$timestamp-$1" || exit

# Clone the repository inside the new folder
if [[ "$1" == "discourse" ]]; then
    git clone git@github.com:ptejas26/Dynamic-Discouse-Downloader.git
    echo "Opening the project 🚀🚀🚀"

elif [[ "$1" == "adk" ]]; then
    git clone git@github.com:ptejas26/AIML-Python-GoogleADK.git
    echo "Opening the project 🚀🚀🚀"

elif [[ "$1" == "geofencing" ]]; then
    git clone git@github.com:ptejas26/Flutter-GeoFencing-App.git
    
else
    echo "Unknown clone target: $1"
fi
echo -e "${GREEN}Cloning of "$1" repository into $timestamp Completed!!!${NC}"
