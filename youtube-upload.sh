#!/bin/bash

#################################### 
# This script uploads videos to youtube 
# Author : S. Afanou
# Date : Nov 2015
# email : afanousergio@gmail.com
####################################


echo "Starting script youtube uploader"
scriptdirectory="$(dirname "$0")"
echo Moving to script directory $scriptdirectory
cd $(dirname "$0")
echo Current directory is $(pwd)

configfilename=youtube.uploader.cfg

echo Reading configuration file $configfilename...
if [ -a $configfilename ]; then
	echo Configuration file found. Importing ...
	source $configfilename

	echo Checking the lock file ...
	if [ -a $lockfilename ]; then
		echo Lock file exist.
		echo Script is running. Exiting ...

	else
		echo "Lock file doesn't exist. Executing the script ..."

		echo "Wrting the current date to the file $lockfilename"
		echo $(date) > $lockfilename

		echo Here is the content of the lockfile
		cat $lockfilename

		for videofile in $sourcepath/*.{mov,mxf,mp4}; do 
			echo "Processing $videofile file.."; 

			videotitle=$(basename $videofile)

			# else execute the script
			echo "Processing video file $videofile"
			echo 'python youtube-upload.py --file=$videofile --title="$videotitle auto uploaded" --description="Automatically uploaded $videotitle in private mode." --keywords="Eglise Paris Metropole, Eglise Paris Bastille", --category=22 --privacyStatus="private" --noauth_local_webserver'
			responsecode=$(python youtube-upload.py --file=$videofile --title="$videotitle auto uploaded" --description="Automatically uploaded $videotitle in private mode." --keywords="Eglise Paris Metropole, Eglise Paris Bastille", --category=22 --privacyStatus="private" --noauth_local_webserver)
			#sleep 30
			
			echo Upload finished.
			echo Http code is $responsecode

			if [[ $responsecode == *successfully* ]]; then
				echo "The response code contains 'successfully'. Full code is $responsecode"

				echo "Moving the file to the $destination"
				mv $videofile $destination
				echo Done.

				curl -s --user 'api:key-44faoj5x2z0nbxz3r08todivhnh17261' \
						https://api.mailgun.net/v3/mailgun.bright-softwares.com/messages \
						-F from='EEPB Video Automator <mailgun@mailgun.bright-softwares.com>' \
						-F to=video@monegliseaparis.fr \
						-F subject="Video file $videofile successfully uploaded to ftp" \
						-F text="Hello, I have just uploaded the video $videofile to ftp and I wanted to notify you. I am sending this email from the mac computer we use to export videos. I am an Automator application. Enjoy."

			else
				echo "The response doesn't start with 2. The full code is $responsecode"
			fi
		done	

		echo "Anyways, let's delete the lock file to be able to execute the script again ... on the next call"
		echo Removing the lock file
		rm -f $lockfilename

	fi

	#exit

	#


else
	echo "Sorry, can't find the configuration file. Exiting ..."
	exit -1
fi
