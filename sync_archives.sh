#!/bin/bash

echo Sycing ARCHIVE2 and My Passport disks 

rsync -ravC --exclude="*\$RECYCLE.*" --exclude="*.TemporaryItems" --exclude="*System*" --exclude="*.Trash*" --exclude="*DS_Store*" --exclude="*.fseventsd*"  /Volumes/My\ Passport/  /Volumes/ARCHIVE2/ > sync-archives.txt 

echo Done.
