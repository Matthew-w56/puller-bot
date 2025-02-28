#!/bin/bash

# Get to the right working directory, regardless of where it was run from
cd /home/ubuntu || exit
# Make sure we have the right permissions
if [ $(id -u) -ne 0 ]
	then echo "You must run this script using sudo!  Please run: sudo sh ./scripts/botStart.sh"
	exit
fi

echo ""
echo "######################"
echo "#     Puller Bot     #"
echo "######################"
echo ""
echo "Time to start running the bot!  I will start by"
echo "creating a new service on this machine whose"
echo "job is to run the bot, and have it repeat every"
echo "4 hours and 10 seconds."
echo ""

# Get the service in place and start it
echo "Copying service files into system folders.."
sudo cp /home/ubuntu/puller-bot/resources/puller-bot.service /etc/systemd/system/puller-bot.service
sudo cp /home/ubuntu/puller-bot/resources/puller-bot.timer /etc/systemd/system/puller-bot.timer
echo "Notifying system of new files.."
sudo systemctl daemon-reload
echo "Telling system to run them if it gets rebooted.."
sudo systemctl enable puller-bot.timer
echo "Telling system to start them now.."
sudo systemctl start puller-bot.timer

echo ""
echo "All done!  Enjoy!"
echo ""
echo "See the ~/puller-bot/screenshots and ~/puller-bot/logs"
echo "folders for more information about each run and for"
echo "debugging purposes if it doesn't work."
echo ""
echo "If you want to stop the bot, run:"
echo "   sudo sh ./scripts/botStop.sh"
echo ""
