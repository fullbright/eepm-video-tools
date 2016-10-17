#!/bin/sh

#################################### 
# This script uploads videos to youtube 
# Author : S. Afanou
# Date : Nov 2015
# email : afanousergio@gmail.com
####################################

echo "Python location"
which python
echo "Starting script youtube uploader"
scriptdirectory="$(dirname "$0")"
echo Moving to script directory $scriptdirectory
cd $(dirname "$0")
echo Current directory is $(pwd)

lockfilename=eepb-video-processor-lockfile.lock

echo Checking if we must update the current code from github

git remote update
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})
BASE=$(git merge-base @ @{u})

if [ $LOCAL = $REMOTE ]; then
    echo "Up-to-date"
elif [ $LOCAL = $BASE ]; then
    echo "Need to pull. Pulling ..."
    git pull --rebase
    echo "Done."
elif [ $REMOTE = $BASE ]; then
    echo "Need to push"
else
    echo "Diverged"
fi

echo "Display ps -af command without awk"
ps -af | grep "eepm_videos_processor"

echo "Display ps -af command with awk"
echo `ps -af | grep "eepm_videos_processor" | awk '{print $2}'`

echo "Display ps -af command and store in a variable"
#currentpid=$(ps -af | grep "eepm_videos_processor" | awk '$8 == "/bin/sh ./eepm_videos_processor.sh" {print $2}')
$currentpid=$$
echo "Current pid $currentpid"
echo $currentpid

#lockfile $lockfilename -l

echo Checking the lock file ...
if [ -a $lockfilename ]; then
	echo Lock file exist.
	echo Checking if the process is still running ...

	lockfilepid=`cat $lockfilename`
	echo "lockfilepid is $lockfilepid"
	
	#ps aux | grep `cat $lockfilename` > /dev/null
	#if [ $? -eq 0 ]; then
	if [ "$currentpid" -eq "$lockfilepid" ]; then
		echo "Current pid $currentpid equals lockfilepid $lockfilepid"
		echo "Process is running ... Exiting ..."
	else
		echo "Current pid $currentpid NOT equals lockfilepid $lockfilepid"
	  	echo "Process is not running. This is a dead lock. Removing the lock file"
	    rm -f $lockfilename
	fi

else
	echo "Lock file doesn't exist. Executing the script ..."

	echo "Writing the pid of the current process to the file $lockfilename"
	#echo $(date) > $lockfilename
	#`ps -af | grep "eepm_videos_processor" | grep -v grep | awk '{print $2}'` > $lockfilename
	echo $currentpid > $lockfilename

	echo Here is the content of the lockfile
	cat $lockfilename
	echo "-------------------------------------------------"
	echo ""
	sleep 90

	## Step 1 -  Launch the youtube uploader
	youtube_result=$(/usr/local/bin/python youtube-upload.py)
	echo "Youtube result = $youtube_result"

	## Step 2 - Launch the dailymotion uploader + vimeo
	vimeo_result=$(/usr/local/bin/python vimeo-upload.py)
	echo "Vimeo result = $vimeo_result" 

	## Step 2 - Launch the dailymotion uploader + vimeo
	dailymotion_result=$(/usr/local/bin/python dailymotion_upload.py)
	echo "Dailymotion result = $dailymotion_result"    

	## Step 3 - Launch the ftp upload for tbn and the others
	ftp_result=$(tbn-videos-upoad.sh)
	echo "FTP result = $ftp_result"

	## Step 4 - Launch the emci upload for enseignemoi and emcitv
	wetransfer_result=$(/usr/local/bin/python Wetransfer.py)
	echo "Wetransfer result = $wetransfer_result"

	## Step 4 - Do some housekeeping
	housekeeping_result=$(/usr/local/bin/python VideoArchiver.py)
	echo "House keeping result = $housekeeping_result"

	echo "Anyways, let's delete the lock file to be able to execute the script again ... on the next call"
	echo Removing the lock file
	rm -f $lockfilename

fi

#exit

# Doing some housekeeping for Youtube
