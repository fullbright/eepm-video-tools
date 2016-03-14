#!/bin/sh -e

#################################### 
# This script facilitates the installation
# of the video upload application on a MAc OS X System
# Author : S. Afanou
# Date : Nov 2015
# email : afanousergio@gmail.com
#
# Inspired from: http://superuser.com/questions/943983/os-x-launchdaemon-not-running-service-could-not-initialize
####################################

echo "Starting the installation ..."

scriptdirectory="$(dirname "$0")"
echo "Moving to script directory $scriptdirectory"
cd $(dirname "$0")
echo "Current directory is $(pwd)"


echo "To Be Done : Ask questions to collect ftp and youtube credentials"
echo "To Be Done : Copy and paste the client_secrets.json file to the place where the youtube-upload.py is located"

echo "Installing requirements with pip"
pip install -r requirements.txt

echo "Processing the .sh files to make them executable"
for shellscript in *.sh; do 
	echo "Processing the shell script $shellscript ... "
	sudo chmod +x $shellscript
	echo "Done."
done

echo "Processing the plist files to let launchd use them"
for plistfile in *.plist; do 

	echo Processing plist file $plistfile
	#plistfile="com.wintr.eodemail.plist"
	plist_filename=$(basename "$plistfile")
	install_path="/Library/LaunchDaemons/$plist_filename"

	echo "Installing launchctl plist: $plistfile --> $install_path"
	sudo cp -f "$plistfile" "$install_path"
	sudo chown root "$install_path"
	sudo chmod 644 "$install_path"

	sudo launchctl unload "$install_path"
	sudo launchctl load "$install_path"

	echo "to check if it's running, run this command: sudo launchctl list | grep monegliseaparis"
	echo "to uninstall, run this command: sudo launchctl unload \"$install_path\""

done
