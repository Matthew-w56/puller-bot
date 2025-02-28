#!/bin/bash

# Get to the right working directory, regardless of where it was run from
cd /home/ubuntu || exit
# Make sure we have the right permissions
if [ $(id -u) -ne 0 ]
	then echo "You must run this script using sudo!  Please run: sudo sh ./scripts/setup.sh"
	exit
fi

echo ""
echo "######################"
echo "#     Puller Bot     #"
echo "######################"
echo ""
echo "Welcome to the Puller Bot!  I will now"
echo "set up the environment and script for"
echo "you.  It may take a second, as I need"
echo "to set up a new python environment and"
echo "get it set up.  Starting now.."
echo ""

# Get your python virtual environment started
echo "Setting up new virtual environment (Python).."
python3 -m venv my-venv

# Update your package registry so you know what exists
echo "Updating package registry.."
sudo apt-get update
# Install pip
echo "Installing pip.."
wget https://bootstrap.pypa.io/get-pip.py
sudo ./my-venv/bin/python3 get-pip.py

# Use pip to install playwright (web bot library)
echo "Installing playwright.."
sudo ./my-venv/bin/pip install playwright
echo "Setting up playwright.."
sudo ./my-venv/bin/playwright install-deps
sudo ./my-venv/bin/playwright install

# Get the credential file template setup
echo "Getting credential file template created.."
sudo echo "" > /home/ubuntu/puller-bot/credentials.txt

# Set up other automatically generated files/directories
echo "Making directories and other base files.."
echo "1" > ./resources/status.txt
mkdir ./puller-bot/logs
mkdir ./puller-bot/screenshots

# Set up the puller CLI
echo "Setting up the 'puller' CLI.."
chmod +x ./puller-bot/scripts/puller
sudo cp ./puller-bot/scripts/puller /usr/local/bin/
if ! sudo grep -q "puller" /etc/sudoers; then
    echo "$USER ALL=(ALL) NOPASSWD: puller" | sudo tee -a /etc/sudoers > /dev/null
fi

# It is ready for the user to fill out the credentials file
echo ""
echo "Okay!  Everything is set up for you now."
echo "All you need is accessible through the"
echo "'puller' command-line interface.  Start"
echo "by running"
echo "   puller help"
echo "to see commands that you can run.  Starting"
echo "recommended actions are:"
echo "   puller creds add [username] [password]"
echo "   puller creds list"
echo "   puller start"
echo "   puller status timer"
echo ""
