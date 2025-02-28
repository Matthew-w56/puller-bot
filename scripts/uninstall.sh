#!/bin/bash

# Get to the right working directory, regardless of where it was run from
cd /home/ubuntu || exit
# Make sure we have the right permissions
if [ "$(id -u)" -ne 0 ]
	then echo "You must run this script using sudo!  Please run: sudo sh ./scripts/botStop.sh"
	exit
fi

# The job of this script is to:
#   - Stop the service (if applicable)
#   - Delete the service/timer files from /etc/systemd/system/
#   - Delete the puller CLI from /usr/bin/

# Artifact left: the sudoers entry for the puller CLI


# Stop the service
sudo systemctl stop puller-bot.timer
sudo systemctl stop puller-bot
sudo systemctl disable puller-bot.timer
sudo systemctl disable puller-bot

# Delete the service and timer from the system directory
rm -f /etc/systemd/system/puller-bot*

# Delete the puller CLI from /usr/bin/
rm -f /usr/bin/puller
