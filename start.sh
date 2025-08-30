#!/usr/bin/env bash

# This script automates the setup and startup of the Internship Tracker application.

# --- Check for .env file ---
if [ ! -f ".env" ]; then
    echo "================================================================="
    echo "‼️  SETUP REQUIRED: .env file not found!"
    echo "================================================================="
    echo "You need to provide your Supabase database URL."
    echo ""
    echo "--- Instructions ---"
    echo "1. Create the .env file by copying the example:"
    echo "   cp example.env .env"
    echo ""
    echo "2. Get your Supabase Connection String (URI):"
    echo "   a. Go to your project on Supabase.com"
    echo "   b. Navigate to Project Settings > Database."
    echo "   c. Find the 'Connection string' section and copy the URI."
    echo ""
    echo "3. Open the new .env file and paste your URI as the value for"
    echo "   SQLALCHEMY_DATABASE_URI."
    echo ""
    echo "After you've done this, run this script again: ./start.sh"
    echo "================================================================="
    exit 1
fi

# --- NEW: Check for config.json and prompt for links ---
CONFIG_FILE="config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "================================================================="
    echo "‼️  SETUP REQUIRED: config.json file not found!"
    echo "================================================================="
    echo "Creating a new config.json file for your personal links."
    echo "Please provide the following URLs (leave blank to skip):"
    echo ""
    read -p "Enter your LinkedIn URL: " linkedin_url
    read -p "Enter your GitHub URL: " github_url
    read -p "Enter your Personal Website URL: " website_url

    # Create the JSON file
    echo "{" > $CONFIG_FILE
    echo "    \"linkedin\": \"$linkedin_url\"," >> $CONFIG_FILE
    echo "    \"github\": \"$github_url\"," >> $CONFIG_FILE
    echo "    \"personal_website\": \"$website_url\"" >> $CONFIG_FILE
    echo "}" >> $CONFIG_FILE
    echo "================================================================="
    echo "✅ config.json created successfully!"
    echo "================================================================="
fi

# Define the name of the virtual environment directory
VENV_DIR="venv"

# 1. Check if the virtual environment directory exists.
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv $VENV_DIR
    echo "Virtual environment created."
fi

# 2. Activate the virtual environment.
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# 3. Install/update the required packages.
echo "Installing/updating requirements from requirements.txt..."
pip install -r requirements.txt

# 4. Start the Flask application.
echo "Starting the Internship Tracker..."
python app.py

# Deactivate the virtual environment when the script is exited
deactivate
echo "Application stopped and virtual environment deactivated."
