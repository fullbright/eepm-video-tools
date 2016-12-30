import os.path
import time
from ftplib import FTP, FTP_TLS
import ftplib

import logging
import logging.handlers
import httplib
import httplib2
import Utils as utils

## Setup logging
logger = logging.getLogger('eepm_video_processor.FtpUpload')
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

# Maximum number of times to retry before giving up.
MAX_RETRIES = 11

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine, ftplib.error_reply,
  ftplib.error_temp, ftplib.error_proto)


# Init
#filename = 'Franck Lefillatre.mp4'
#filename = 'ubuntu-14.04.5-desktop-amd64.iso'
sizeWritten = 0

# Define a handle to print the percentage uploaded
# def handle(block):
#     sizeWritten += 1024 # this line fail because sizeWritten is not initialized.
#     percentComplete = sizeWritten / totalSize
#     print(str(percentComplete) + " percent complete")

# class FtpUploadTracker:
#     sizeWritten = 0
#     totalSize = 0
#     lastShownPercent = 0
#     counter = 0

#     def __init__(self, totalSize):
#         self.totalSize = totalSize
#         self.counter = 0

#     def handle(self, block):
#     	self.counter += 1
#         self.sizeWritten += 1024
#         #percentComplete = round((self.sizeWritten / self.totalSize) * 100)
#         percentComplete = round((self.sizeWritten / float(self.totalSize)) * 100)
        

#         if (self.lastShownPercent != percentComplete):
#             self.lastShownPercent = percentComplete
#             print("%d - %s percent complete (%d/%d)" % (self.counter, str(percentComplete), self.sizeWritten, self.totalSize))
#             logger.debug("%d - %s percent complete (%d/%d)" % (self.counter, str(percentComplete), self.sizeWritten, self.totalSize))


def main():

    # Read the configuration files
    configvars = utils.load_variables("eepm_videos_processor.cfg")
    sourcepath = configvars['ftp.sourcepath'].rstrip()
    destination = configvars['ftp.destination'].rstrip()
    ftpserver = configvars['ftp.ftpserver'].rstrip()
    ftpuser = configvars['ftp.ftpuser'].rstrip()
    ftppass = configvars['ftp.ftppass'].rstrip()
    ftpfolder = "/"

    # Clean the ftp server name
    # Sometime written in the configuration file as 
    if ftpserver.startswith('ftp://'):
        ftpserver = ftpserver.replace('ftp://', '')

    slashPosition = ftpserver.find("/")
    if slashPosition != -1:
        ftpfolder = ftpserver[slashPosition:]
        ftpserver = ftpserver[0:slashPosition]

    # Get the next video from the source path
    validextensions = [".mp3"]
    fileToUpload = utils.getNextVideoToProcess(sourcepath, validextensions)

    logger.debug("File to upload %s" % (fileToUpload))

    # Upload that video
    if fileToUpload != None :

        size = os.path.getsize(fileToUpload) / (1024*1024.0)
        filedate = time.ctime(os.stat(fileToUpload).st_mtime)
        destfileName = utils.path_leaf(fileToUpload)
        destfile = os.path.join(destination, destfileName)
        if(os.path.isfile(destfile)):
            destfilename = datetime.datetime.now() + "_" + destfilename
            destfile = os.path.join(destination, destfilename)

        print "We are going to process the file %s (%s) MB, date (%s). If upload successfull, will be moved to %s" % (fileToUpload, size, filedate, destfile)

        uploadResult = utils.uploadThisToFtp(ftpserver, ftpuser, ftppass, fileToUpload, ftpfolder)

        if uploadResult == True:
            logger.debug("Move the processed file to the destination")
            logger.debug("Moving %s to %s" % (fileToUpload, destfile))

            utils.move_to_destination(sourcepath, destination, destfileName)
            
        else:
            print "Upload failed :( Sorry"

        # Send a mail to tell the gospel ;)
        utils.send_email('EEPB Video Automator <mailgun@mailgun.bright-softwares.com>',
                            "video@monegliseaparis.fr",
                            "FTP : resources processing report",
                            "Hello, I have just uploaded the video to FTP and I wanted to notify you. I am sending this email from the mac computer we use to export videos. I am an Automator application. Enjoy."
                        )


    else :
        print "Nothing to upload. There is no next video."

if __name__ == '__main__':
    main()
