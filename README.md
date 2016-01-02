# eepm-video-tools
This repository contains scripts for the video department at Paris Bastille.

# Installation

## Install the launchd daemon
The idea is that the mac os x computer call periodically the script and upload the files to the ftp

 1. Edit the fr.monegliseaparis.dev.ftpuploads to suit your needs.
 2. Copy the file to /Library/LaunchDaemons/
 3. Reboot the mac

## Install the libraries for the youtube uploader
> sudo pip install --upgrade google-api-python-client --ignore-installed six
> pip install PyVimeo
> pip install requests
> pip install requests-toolbelt
> pip install simplejson
> pip install dailymotion
> pip install httplib2
> pip install oauth2client

If something failed, try the following:
 * brew doctor
 * brew install python
 * brew update

# Usage

If you want to upload automatically another set of files, edit directly the script.
