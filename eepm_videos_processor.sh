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
	echo "-------------------------------------------------"
	echo ""

	## Step 1 -  Launch the youtube uploader
	youtube_result=$(/usr/local/bin/python youtube-upload.py)

	## Step 2 - Launch the dailymotion uploader + vimeo


	## Step 3 - Launch the ftp upload for tbn and the others


	## Step 4 - Do some housekeeping


	echo "Anyways, let's delete the lock file to be able to execute the script again ... on the next call"
	echo Removing the lock file
	rm -f $lockfilename

fi

#exit

# Doing some housekeeping for Youtube
