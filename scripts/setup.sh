#!/bin/bash

# Get to the right working directory, regardless of where it was run from
cd /home/ubuntu || exit
# Make sure we have the right permissions
if [ $(id -u) -ne 0 ]
	then echo "You must run this script using sudo!  Please run: sudo sh ./scripts/setup.sh"
	exit
fi

# Expects: createIfNotExists filepath defaultContent nameForUser
createIfNotExists () {
	if ! [ -f "$1" ]; then
		echo "Getting $3 created.."
		echo $2 | sudo tee $1 > /dev/null
		chmod 666 $1
	else
		echo "No need to create $3 (already found it).."
	fi
}

echo ""
echo "########################"
echo "#      Puller Bot      #"
echo "########################"
echo ""
echo "Welcome to the Puller Bot!"
echo ""
echo "Beginning Setup script for:"
echo " - Bot activation service (timer and service)"
echo " - Bot interaction CLI (puller command)"
echo ""
echo "########################"
echo "#         Logs         #"
echo "########################"
echo ""


# Get your python virtual environment started
if ! [ -d "/home/ubuntu/my-venv" ]; then
	echo "Setting up new virtual environment (Python).."
	echo ""
	echo ""
	python3 -m venv my-venv
	echo ""
	echo ""
else
	echo "No need for a python environment (already found it).."
fi

# Install pip if it isn't already installed
if ! [ -f "/home/ubuntu/get-pip.py" ]; then
	# Update your package registry so you know what exists
	echo ""
	echo ""
	echo "Updating package registry.."
	sudo apt-get update
	echo ""
	echo ""

	# Install pip
	echo "Installing pip.."
	wget https://bootstrap.pypa.io/get-pip.py
	sudo ./my-venv/bin/python3 get-pip.py
	echo ""
	echo ""
else
	echo "No need for installing pip (already found it).."
fi

# Use pip to install playwright (web bot library)
if ! [ -f "/home/ubuntu/my-venv/bin/playwright" ]; then
	echo "Installing playwright.."
	echo ""
	echo ""
	sudo ./my-venv/bin/pip install playwright
	echo "Setting up playwright.."
	sudo ./my-venv/bin/playwright install-deps
	echo ""
	echo ""
else
	echo "No need to install playwright (already found it).."
fi

# Do the playwright install (for downloading the browser needed)
echo "Installing the needed browser support for playwright.."
PLAYWRIGHT_DOWNLOAD_HOST=0
PLAYWRIGHT_BROWSERS_PATH=/home/ubuntu/.cache/playwright
sudo /home/ubuntu/my-venv/bin/python3 -m playwright install chromium
echo ""

# Get the generated file templates set up
echo "Setting up generated files and directories.."
mkdir -p "/home/ubuntu/puller-bot/resources"
mkdir -p "/home/ubuntu/puller-bot/logs"
mkdir -p "/home/ubuntu/puller-bot/screenshots"
createIfNotExists "/home/ubuntu/puller-bot/credentials.txt" "" "credentials file"
createIfNotExists "/home/ubuntu/puller-bot/resources/status.txt" "1" "status file"

# Set up the puller CLI
echo "Setting up the puller CLI.."
chmod +x ./puller-bot/scripts/puller
sudo cp ./puller-bot/scripts/puller /usr/local/bin/
if ! sudo grep -q "puller" /etc/sudoers; then
    echo "$USER ALL=(ALL) NOPASSWD: puller" | sudo tee -a /etc/sudoers > /dev/null
fi

# It is ready for the user to fill out the credentials file
echo ""
echo ""
echo "########################"
echo "#         Done         #"
echo "########################"
echo ""
echo "Puller bot is now fully set up."
echo ""
echo "Next commands to run:"
echo "   puller creds add [username] [password]"
echo "   puller start"
echo "   puller status timer"
echo ""
