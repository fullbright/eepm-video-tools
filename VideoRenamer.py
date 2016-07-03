from __future__ import print_function
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date, timedelta
from oauth2client.tools import argparser


import sys
import os
import glob
import shutil
import time
import dailymotion_upload as dailymotion
import logging
import gspread


import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'



scope = ['https://spreadsheets.google.com/feeds']

class VideoRenamer():

    def __init__(self, source_folder):
        # start editable vars #
        self.current_script_file = os.path.realpath(__file__)
        self.current_script_dir = os.path.abspath(os.path.join(self.current_script_file, os.pardir))

        self.days_old = 28               # how old the files have to be before they are moved
        self.original_folder = source_folder #"/Users/sergio/Downloads"  # folder to move files from
        self.logger = logging.getLogger("eepm_video_processor.VideoRenamer")

        self.validextensions = [".mp4", ".mov", ".mp3"]
        # end editable vars #

    def authenticate():
        credentials = ServiceAccountCredentials.from_json_keyfile_name('client-secrets-oauth2.json', scope)
        gc = gspread.authorize(credentials)
        wks = gc.open("Where is the money Lebowski?").sheet1

    # start function definitions #
    def log(self,level,msg,tofile=True):
        #print self.msg

        if tofile == True:
            if level == 0:
                self.logger.info(msg)
            else:
                self.logger.error(msg)

    def end(self,code):
        self.log(0,"End.")
        self.log(0,"-------------------------")
        #sys.exit(code)

    # end function definitions #


    # start process #
    def process(self):
        #move_date = date.today() - timedelta(days=self.days_old)
        #move_date = time.mktime(move_date.timetuple())
        #logger = logging.getLogger("cuarch")
        #hdlr = logging.FileHandler(logfile)
        #hdlr.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
        #logger.addHandler(hdlr)
        #logger.setLevel(logging.INFO)

        self.log(0,"Initialising...")

        count = 0
        size = 0.0

        self.log(0, "Processing the orginal %s" % (self.original_folder))

        for filename in glob.glob1(self.original_folder, "*.*"):
            srcfile = os.path.join(self.original_folder, filename)

            newfilename = ""
            destfile = os.path.join(self.original_folder, newfilename)
            #(base, ext) = os.path.splitext(srcfile)
            #self.log(0, "Checking file %s with extension %s" % (base, ext))

            if ext in self.validextensions:
                if not os.path.isfile(destfile):
                    size = size + (os.path.getsize(srcfile) / (1024*1024.0))
                    filedate = time.ctime(os.stat(srcfile).st_mtime)
                    shutil.move(srcfile, destfile)

                    self.log(0,"Archived '" + filename + "', file date : %s" % filedate)
                    count = count + 1
                else:
                    self.logger.debug("There is already another file named %s" % destfile)

        self.log(0,"Archived " + str(count) + " files, totalling " + str(round(size,2)) + "MB.")
        self.end(0)


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    
    errormessage = ""
    values = []

    try:
        """Shows basic usage of the Sheets API.

        Creates a Sheets API service object and prints the names and majors of
        students in a sample spreadsheet:
        https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
        """
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)

        spreadsheetId = '1ENlHxOp-Ue-h5p1EHpVkzEsFYp21acgPL2oWYcS-IL0'
        rangeName = 'SUIVI EXPORT 2016!A2:AB'
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId, range=rangeName).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
        else:
            print('Name, Major:')
            for row in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                print('%s, %s, %s, %s' % (row[0], row[1], row[2], row[3]))
    except:
        errormessage = errormessage + " -> " + sys.exc_info()[0]
        logger.debug("Something bad happned. The error is ", sys.exc_info()[0], ". Thats all we know")

    finally:

        dailymotion.send_email('EEPB Video Automator <mailgun@mailgun.bright-softwares.com>',
            "video@monegliseaparis.fr",
            "Video renamer : videos processing report",
            "Hello, I have just uploaded the video $videofile to Youtube and I wanted to notify you. Here are the possible errors : " + errormessage + " I am sending this email from the mac computer we use to export videos. I am an Automator application. Enjoy."
            )

        return values

if __name__ == '__main__':
    main()

    #455804358556-p4mrvndjgmivjdi99j58ga9cq3shj4b1.apps.googleusercontent.com









