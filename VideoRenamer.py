from __future__ import print_function
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date, timedelta
from oauth2client.tools import argparser
from slugify import slugify


import sys
import os
import glob
import shutil
import time
import Utils as utils
import logging
import gspread


import httplib2
import os
from os import listdir
from os.path import isfile, join

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools


SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

CLIENT_SECRETS_FILE = "client_secrets.json"
CREDENTIALS_STORAGE_FILE = "eepm_videos_youtube_uploader-oauth2.json"

SSHEETID = '1ENlHxOp-Ue-h5p1EHpVkzEsFYp21acgPL2oWYcS-IL0' 
SSHEETNAME = 'EXPORT PREDICATIONS 2016/2017'
SSHEETRANGENAME = SSHEETNAME + '!A2:AB'


## Setup logging
logger = logging.getLogger('eepm_video_processor.utils')
logger.setLevel(logging.DEBUG)
current_script_file = os.path.realpath(__file__)
current_script_dir = os.path.abspath(os.path.join(current_script_file, os.pardir))
fh = logging.handlers.RotatingFileHandler(
              "%s/eepm_videos_processor.log" % (current_script_dir),
              maxBytes=20000000, backupCount=5)
#logging.FileHandler("%s/eepm_video_processor.log" % (current_script_dir))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def get_list_of_videos():
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secrets_gspread.json', scope)


    #credentials = store.get()
    logger.debug("Authenticating ...")
    gc = gspread.authorize(credentials)

    logger.debug("Opening the spreadsheet by it's ID %s" % SSHEETID)
    sht1 = gc.open_by_key(SSHEETID)

    logger.debug("Moving to worksheet name %s" % SSHEETNAME)
    worksheet = sht1.worksheet(SSHEETNAME)
    
    logger.debug("Getting all the values ...")
    return worksheet.get_all_values()


def main2():
    # Read the configuration files
    configvars = utils.load_variables("eepm_videos_processor.cfg")
    sourcepath = configvars['emci.sourcepath'].rstrip()
    destination = configvars['emci.destination'].rstrip()
    errormessage = ""

    validextensions = [".mp4", ".mov"]
    #fileToUpload = utils.getNextVideoToProcess(sourcepath, validextensions)
    #fileName = utils.path_leaf(fileToUpload)
    
    
    onlyfiles = [f for f in listdir(sourcepath) if isfile(join(sourcepath, f))]
    #print(onlyfiles)


    logger.debug("Starting the process ...")    
    list_of_lists = get_list_of_videos()

    #logger.debug("Searching for %s in the spreadsheet ..." % (fileName))
    for currentList in list_of_lists:
        videoFileName = currentList[0]
        videoTitle = currentList[1]
        logger.debug("Processing video %s" % videoFileName)

        ## Listing files in the source folder

        for currentFile in onlyfiles:
            #if videoFileName in files:
            #root, dirs, files = os.walk(sourcepath)
            #print(files)

            if videoFileName == currentFile:
                logger.debug("Bingo !!! Found one corresponding to %s" % videoFileName)
                emciFormatedName = utils.getEmciformatedname(videoFileName, videoTitle)
                logger.debug("Formated name : %s" % emciFormatedName)
                
                logger.debug("Renaming the file %s to %s" % (videoFileName, emciFormatedName))
                destfile = os.path.join(sourcepath, emciFormatedName)
                
                try:
                    os.rename(videoFileName, destfile)
                except Exception as e:
                    logger.debug("Oh ! sorry, something bad happened." + str(e))
                else:
                    pass
                finally:
                    logger.debug("File renaming done for %s" % (videoFileName))

    utils.send_email('EEPB Video Automator <mailgun@mailgun.bright-softwares.com>',
        "video@monegliseaparis.fr",
        "Video renamer : videos processing report",
        "Hello, I have just renamed some videos and I wanted to notify you. Here are the possible errors : " + errormessage + " I am sending this email from the mac computer we use to export videos. I am an Automator application. Enjoy."
        )


if __name__ == '__main__':
    main2()

    #455804358556-p4mrvndjgmivjdi99j58ga9cq3shj4b1.apps.googleusercontent.com









