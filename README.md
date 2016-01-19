# eepm-video-tools
This repository contains scripts for the video department at Paris Bastille.

# Installation

## Install the launchd daemon
The idea is that the mac os x computer call periodically the script and upload the files to the ftp

 1. Edit the fr.monegliseaparis.dev.ftpuploads to suit your needs.
 2. Copy the file to /Library/LaunchDaemons/
 3. Reboot the mac

## Install the libraries for the youtube uploader

	sudo pip install --upgrade google-api-python-client --ignore-installed six 
	pip install PyVimeo
	pip install requests
	pip install requests-toolbelt
	pip install simplejson
	pip install dailymotion
	pip install httplib2
	pip install oauth2client

If something failed, try the following:
 * brew doctor
 * brew install python
 * brew update

### Vimeo video upload
To be able to upload a video to vimeo using the application, you need to create an application.

#### Create an application

	1. Go to https://developer.vimeo.com/apps
	2. Click on the "Create application button"
	3. Fill the form with the necessary information
	4. Agree to the terms and conditions
	5. Click the "Create app" button

Then, after creating the application, go to the application's page by clicking on it's name. You will be presented with the app's details page.


#### Important : request an upload access

Go through the process of requesting an upload access. It can take up to 5 working days to get the approval.

#### Authenticate

Next to the details link, click on "Authentication"

Note the client id and client secret. You will need them to authenticate and upload videos.

#### Generate an access token

	1. Scroll down to the bottom of the page
	2. You want to select the following scopes : public private purchased create edit delete interact upload
	3. Click the buttom "Generate token" to generate an access token.

#### Fill the configuration file
Fill the vimeo.uploader.cfg with the collected information from the application you created.

# Usage

If you want to upload automatically another set of files, edit directly the script.
