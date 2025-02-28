#!/bin/bash

# Get to the right working directory, regardless of where it was run from
cd /home/ubuntu || exit
# Make sure we have the right permissions
if [ $(id -u) -ne 0 ]
	then echo "You must run this script using sudo!  Please run: sudo sh ./scripts/botStop.sh"
	exit
fi

echo ""
echo "######################"
echo "#     Puller Bot     #"
echo "######################"
echo ""
echo "Stopping the puller bot.."
echo ""

sudo systemctl stop puller-bot.timer
sudo systemctl stop puller-bot
sudo systemctl disable puller-bot.timer
sudo systemctl disable puller-bot

echo ""
echo "The puller bot has successfully been stopped."
echo "To start it up again, run:"
echo "   sudo sh ./scripts/botStart.sh"
echo ""
