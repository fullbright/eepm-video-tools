# eepm-video-tools
This repository contains scripts for the video department at Paris Bastille.

# Installation

## Install the launchd daemon
The idea is that the mac os x computer call periodically the script and upload the files to the ftp

 1. Edit the fr.monegliseaparis.dev.ftpuploads to suit your needs.
 2. Copy the file to /Library/LaunchDaemons/
 3. Reboot the mac

## Install the libraries for the uploader

	sudo pip install --upgrade google-api-python-client --ignore-installed six 
	pip install PyVimeo
	pip install requests
	pip install requests-toolbelt
	pip install simplejson
	pip install dailymotion
	pip install httplib2
	pip install oauth2client
	pip install gspread

To have it all installed at once, run the following command : 

	pip install -r requirements.txt

If something failed, try the following:
 * brew doctor
 * brew install python
 * brew update

### Configure FTP Uploads

	TO BE DONE.
	//TODO

### Configure Youtube upload feature

	TO BE DONE.
	//TODO

#### Create an application and retrieve the API Keys and API secret

Connect to http://console.google.com and create an application.
Retrieve the client credentials json files.


#### Authorize the tool to upload videos to your channel

To be able to automatically upload the videos to youtube, you need to connect to our channel through a web browser.
The command you are going to run will try to upload a video and you will be asked to approve the action.

You will need to following :
	1. A video to upload. Replace the $videofile with the video to upload
	2. A title and description for the video. Replace the $videotitle


Execute the following command : 
	python youtube-upload.py --file=$videofile --title="$videotitle auto uploaded" --description="Automatically uploaded $videotitle in private mode." --keywords="Eglise Paris Metropole, Eglise Paris Bastille", --category=22 --privacyStatus="private"

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


# Dev tools installations

I recommend to use virtualenv to configure the running environement of development.

    pip install virtualenv
    pip install setuptools
    virtualenv venv
    pip install -r requirements.txt

At the very end of the developement, run these to save your work.

    deactivate
    pip freeze > requirements.txt


[Learn more](http://docs.python-guide.org/en/latest/dev/virtualenvs/)

# Improvements

Code improvements

 - [X] Better logging. Logrotate the logs
 - [ ] Merge all the configuration files in one
 - [ ] Change the configuration file format to json or yaml, python should be able to read it
 - [ ] A mailing class/function to handle all the emailing, logs to attach, text formating
 - [ ] A main script that handles the move to the directpry where the scripts and logs are located
 - [ ] A main script with command line options to trigger tasks directly.
 - [ ] Write a file renamer function to automatically rename emci files before uploading them. Read the name from a remote database
 - [ ] Clean the code
 - [ ] Better logging : separate logs into functional units 
