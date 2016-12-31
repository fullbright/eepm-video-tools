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


#scope = ['https://spreadsheets.google.com/feeds']

# class VideoRenamer():

#     def __init__(self, source_folder):
#         # start editable vars #
#         self.current_script_file = os.path.realpath(__file__)
#         self.current_script_dir = os.path.abspath(os.path.join(self.current_script_file, os.pardir))

#         self.days_old = 28               # how old the files have to be before they are moved
#         self.original_folder = source_folder #"/Users/sergio/Downloads"  # folder to move files from
#         self.logger = logging.getLogger("eepm_video_processor.VideoRenamer")

#         self.validextensions = [".mp4", ".mov", ".mp3"]
#         # end editable vars #

#     def authenticate():
#         credentials = ServiceAccountCredentials.from_json_keyfile_name('client-secrets-oauth2.json', scope)
#         gc = gspread.authorize(credentials)
#         #wks = gc.open("Where is the money Lebowski?").sheet1
#         sht1 = gc.open_by_key(SSHEETID)

#         worksheet = sh.worksheet(SSHEETNAME)


#     # start function definitions #
#     def log(self,level,msg,tofile=True):
#         #print self.msg

#         if tofile == True:
#             if level == 0:
#                 self.logger.info(msg)
#             else:
#                 self.logger.error(msg)

#     def end(self,code):
#         self.log(0,"End.")
#         self.log(0,"-------------------------")
#         #sys.exit(code)

#     # end function definitions #


#     # start process #
#     def process(self):
#         #move_date = date.today() - timedelta(days=self.days_old)
#         #move_date = time.mktime(move_date.timetuple())
#         #logger = logging.getLogger("cuarch")
#         #hdlr = logging.FileHandler(logfile)
#         #hdlr.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
#         #logger.addHandler(hdlr)
#         #logger.setLevel(logging.INFO)

#         self.log(0,"Initialising...")

#         count = 0
#         size = 0.0

#         self.log(0, "Processing the orginal %s" % (self.original_folder))

#         for filename in glob.glob1(self.original_folder, "*.*"):
#             srcfile = os.path.join(self.original_folder, filename)

#             newfilename = ""
#             destfile = os.path.join(self.original_folder, newfilename)
#             #(base, ext) = os.path.splitext(srcfile)
#             #self.log(0, "Checking file %s with extension %s" % (base, ext))

#             if ext in self.validextensions:
#                 if not os.path.isfile(destfile):
#                     size = size + (os.path.getsize(srcfile) / (1024*1024.0))
#                     filedate = time.ctime(os.stat(srcfile).st_mtime)
#                     #shutil.move(srcfile, destfile)

#                     self.log(0,"Archived '" + filename + "', file date : %s" % filedate)
#                     count = count + 1
#                 else:
#                     self.logger.debug("There is already another file named %s" % destfile)

#         self.log(0,"Archived " + str(count) + " files, totalling " + str(round(size,2)) + "MB.")
#         self.end(0)


# def get_credentials():
#     """Gets valid user credentials from storage.

#     If nothing has been stored, or if the stored credentials are invalid,
#     the OAuth2 flow is completed to obtain the new credentials.

#     Returns:
#         Credentials, the obtained credential.
#     """
#     credential_path = utils.get_credential_path()

#     store = oauth2client.file.Storage(credential_path)
#     credentials = store.get()
#     if not credentials or credentials.invalid:
#         flow = client.flow_from_clientsecrets(CLIENT_SECRETS_FILE, SCOPES)
#         flow.user_agent = APPLICATION_NAME
#         if flags:
#             credentials = tools.run_flow(flow, store, flags)
#         else: # Needed only for compatibility with Python 2.6
#             credentials = tools.run(flow, store)
#         print('Storing credentials to ' + credential_path)
#     return credentials

def main2():
    # Read the configuration files
    configvars = utils.load_variables("eepm_videos_processor.cfg")
    sourcepath = configvars['emci.sourcepath'].rstrip()
    destination = configvars['emci.destination'].rstrip()

    validextensions = [".mp4", ".mov"]
    fileToUpload = utils.getNextVideoToProcess(sourcepath, validextensions)
    fileName = utils.path_leaf(fileToUpload)
    
    logger.debug("Starting the process ...")

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
    list_of_lists = worksheet.get_all_values()

    logger.debug("Searching for %s in the spreadsheet ..." % (fileName))
    for currentList in list_of_lists:
        videoFileName = currentList[0]
        videoTitle = currentList[1]
        logger.debug("Processing video %s" % videoFileName)

        if videoFileName == fileName:
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
            


def main():
    
    logger = logging.getLogger("eepm_video_processor.VideoRenamer")
    errormessage = ""
    values = []

    try:
        """Shows basic usage of the Sheets API.

        Creates a Sheets API service object and prints the names and majors of
        students in a sample spreadsheet:
        https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
        """
        logger.debug("Getting spreadsheet authenticated service")
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
        service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

        logger.debug("Got service. Reading spreadsheet")

        spreadsheetId = SSHEETID
        rangeName = SSHEETRANGENAME

        logger.debug("Spreadsheet ID = %s, Range name = %s" % (spreadsheetId, rangeName))
        
        print("Test2")
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
        values = result.get('values', [])

        print("Test")
        print(result)
        print(values)

        logger.debug("Got values")

        if not values:
            print('No data found.')
            logger.debug('No data found.')
        else:
            print('Name, Major:')
            logger.debug('Name, Major:')
            for row in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                print('%s, %s, %s, %s, %s' % (row[0], slugify(row[1]), row[1], row[2], row[3]))
                logger.debug('%s, %s, %s, %s, %s' % (row[0], slugify(row[1]), row[1], row[2], row[3]))
    except:
        errormessage = errormessage + " -> " + sys.exc_info()[0]
        #logger.debug("Something bad happned. The error is ", sys.exc_info()[0], ". Thats all we know")

    finally:

        utils.send_email('EEPB Video Automator <mailgun@mailgun.bright-softwares.com>',
            "video@monegliseaparis.fr",
            "Video renamer : videos processing report",
            "Hello, I have just renamed some videos and I wanted to notify you. Here are the possible errors : " + errormessage + " I am sending this email from the mac computer we use to export videos. I am an Automator application. Enjoy."
            )

        return values

if __name__ == '__main__':
    main2()

    #455804358556-p4mrvndjgmivjdi99j58ga9cq3shj4b1.apps.googleusercontent.com









