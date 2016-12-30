#!/usr/bin/python

import dailymotion
import os
import json
import requests
import glob
import logging
import logging.handlers
import ntpath
import shutil
import yaml
import socket
from slugify import slugify
from ftplib import FTP, FTP_TLS

MAILGUN_APIKEY = 'key-44faoj5x2z0nbxz3r08todivhnh17261'
YAMLCONFIGFILE = "settings.yaml"
INICONFIGFILE = "eepm_videos_processor.cfg"


## Setup logging
logger = logging.getLogger('eepm_video_processor')
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



class FtpUploadTracker:
    sizeWritten = 0
    totalSize = 0
    lastShownPercent = 0
    counter = 0

    def __init__(self, totalSize):
        self.totalSize = totalSize
        self.counter = 0

    def handle(self, block):
        self.counter += 1
        self.sizeWritten += 1024
        #percentComplete = round((self.sizeWritten / self.totalSize) * 100)
        percentComplete = round((self.sizeWritten / float(self.totalSize)) * 100)
        

        if (self.lastShownPercent != percentComplete):
            self.lastShownPercent = percentComplete
            print("%d - %s percent complete (%d/%d)" % (self.counter, str(percentComplete), self.sizeWritten, self.totalSize))
            logger.debug("%d - %s percent complete (%d/%d)" % (self.counter, str(percentComplete), self.sizeWritten, self.totalSize))

def uploadThisToFtp(ftpserver, ftpuser, ftppass, filepath, ftpfolder):

    # Handle ending slash issue in the ftp folder
    if ftpfolder.endswith("/"):
        ftpfolder = ftpfolder[:-1]

    destfileName = path_leaf(filepath)
    (base, ext) = os.path.splitext(destfileName)
    baseSlugified = slugify(base)
    ftpfilename = ftpfolder + '/' + destfileName #baseSlugified + ext


    logger.debug("Uploading %s to %s (folder %s) using credentials %s and %s" % (filepath, ftpserver, ftpfolder, ftpuser, ftppass))
    logger.debug("FTP File name is : %s" % (ftpfilename))
    ftp = FTP(ftpserver)
    ftp.login(ftpuser, ftppass)
    welcomeMsg = ftp.getwelcome()
    #logger.debug("Welcome Message : ", str(welcomeMsg))
    print welcomeMsg
    filesList = ftp.nlst()
    #logger.debug("Files nlst : ", str(filesList))
    print filesList
    ftp.retrlines('LIST')

    # ftps.prot_p()
    #ftp.storlines("STOR %s" %('franck_lefillatre.mp4'), open('Franck Lefillatre.mp4'))

    totalSize = os.path.getsize(filepath)
    print('Total file size : ' + str(round(totalSize / 1024 / 1024 ,1)) + ' Mb')
    uploadTracker = FtpUploadTracker(int(totalSize))
    ftp.storbinary("STOR %s" % (ftpfilename), open(filepath, 'rb'), 1024, uploadTracker.handle)
    ftp.close()
    return True

# def uploadThisToFtp(ftpserver, ftpuser, ftppass, filepath):

#     destfileName = utils.path_leaf(filepath)
#     (base, ext) = os.path.splitext(destfileName)
#     baseSlugified = slugify(base)
#     ftpfilename = baseSlugified + ext


#     logger.debug("Uploading %s to %s using credentials %s and %s" % (filepath, ftpserver, ftpuser, ftppass))
#     logger.debug("FTP File name is : %s" % (ftpfilename))
#     ftp = FTP(ftpserver)
#     ftp.login(ftpuser, ftppass)
#     # ftps.prot_p()
#     #ftp.storlines("STOR %s" %('franck_lefillatre.mp4'), open('Franck Lefillatre.mp4'))

#     totalSize = os.path.getsize(filepath)
#     print('Total file size : ' + str(round(totalSize / 1024 / 1024 ,1)) + ' Mb')
#     uploadTracker = FtpUploadTracker(int(totalSize))
#     ftp.storbinary("STOR %s" %(ftpfilename), open(filepath, 'rb'), 1024, uploadTracker.handle)
#     ftp.close()
#     return True

def get_credential_path():
    #home_dir = os.path.expanduser('~')
    #credential_dir = os.path.join(home_dir, '.credentials')
    #if not os.path.exists(credential_dir):
    #    os.makedirs(credential_dir)
    #credential_path = os.path.join(credential_dir,
    #                               'sheets.googleapis.com-python-quickstart.json')
    credential_path = "eepm_videos_youtube_uploader-oauth2.json"
    logger.debug("Getting credential path %s" % credential_path)
    return credential_path

# load the variables

def load_variables(configfile):

    logger.debug("Loading variables from config file %s" % (configfile))
    dataMap = {}

    logger.debug("Testing yaml config file to initiate conversion")
    if not os.path.exists(YAMLCONFIGFILE):
        convertIniToYaml()

    dataMap = load_variables_fromyaml()

    # TODO : Remove the line below after stabilizing the yaml config conversion
    dataMap = load_variables_fromini()
    return dataMap

def load_variables_fromyaml():

    # If there is a yaml configuration file, use it.
    logger.debug("Checking if a yaml filei %s is available to use it" % (YAMLCONFIGFILE))
    dataMap = {}

    if os.path.exists(YAMLCONFIGFILE):
        logger.debug("Found a yaml file, using it")
        f = open(YAMLCONFIGFILE)
        dataMap = yaml.load(f)
        f.close()

    return dataMap

def load_variables_fromini():

    configfile = INICONFIGFILE
    logger.debug("Loading variables from ini file %s" % (configfile))

    configvars = {}

    if os.path.exists(configfile):
        logger.debug("Reading the configuration file")
        with open(configfile) as myfile:
            for line in myfile:
                if not line.startswith('#') and not line.strip() == '' : # ignore line begining with #
                    name, var = line.partition("=")[::2]
                    #print "Storing variable %s with value %s" % (name, var)
                    configvars[name.replace('\\n', '').strip()] = var.replace('\\n', '')
    return configvars

def convertIniToYaml():

    if not os.path.exists(INICONFIGFILE):
        logger.debug("Ini config file %s does not exist. Exiting !!!" % (INICONFIGFILE))
        return {}

    if not os.path.exists(YAMLCONFIGFILE):
        logger.debug("Configuration file %s doesn't exist. Converting the ini file to yaml" % (YAMLCONFIGFILE))

        #variables = load_variables(INICONFIGFILE)
        variables = {}
        # read the configuration file
        with open(INICONFIGFILE) as myfile:
            for line in myfile:
                if not line.startswith('#') and not line.strip() == '' : # ignore line begining with #
                    name, var = line.partition("=")[::2]
                    #print "Storing variable %s with value %s" % (name, var)
                    variables[name.replace('\\n', '').strip()] = var.replace('\\n', '').strip()

        print "Writing data to the yaml file", YAMLCONFIGFILE
        with open(YAMLCONFIGFILE, 'w') as outfile:
            yaml.dump(variables, outfile, default_flow_style=True)
    else:
        logger.debug("Configuration file %s exist. No conversion needed." % (YAMLCONFIGFILE))


def move_to_destination(sourcepath, destinationpath, filename):
    src = os.path.join(sourcepath, filename)
    dst = os.path.join(destinationpath, filename)
    size = os.path.getsize(src) / (1024*1024.0)
    logger.debug("Moving video file from %s to %s (%s)" % (src, dst, size))

    try:
        if not os.path.isfile(dst):        
            os.rename(src, dst)
            #shutil.move(fileToUpload, destfile)
            logger.debug("File %s was successfully moved." % (filename))
        else:
            logger.debug("Cannot move. Destination file exists.")
    except Exception as e:
        logger.error("Error while move file %s, %s" % (filename, str(e)))
    else:
        pass
    finally:
        logger.debug("File moving process finished.")
    



def check_lock_file(lockfilename):
    """ Checks if the lockfile exist,
    If yes, it makes sure that the PID inside is still running.
    If so, print a message and exit """
    if os.path.exists(lockfilename):
        print "Lockfile %s exists. Checking if the process pid is still alive ..." % lockfilename

        if check_pid_in_file(lockfilename):
            print "Process with PID %s is still running. Exiting ..." % currentpid
            exit(0)
        else:
            write_lock_file(lockfilename)
    else:
        write_lock_file(lockfilename)



def check_pid_in_file(filename):
    """ Read the pid from the file
    and check if the Process is still running """
    with open(filename, 'r') as f:
        pid = f.readline()

        # check the PID
        return check_pid(pid)

def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    except TypeError:
        return False
    else:
        return True

def write_lock_file(lockfilename):
    # Write the lock file
    print "No lockfile found. Writing our current process pid to the file."
    currentpid = os.getpid()
    print "Currrent pid is ", currentpid

    lockfile = open(lockfilename, "w")
    lockfile.write("%d" % currentpid)
    lockfile.close()

def getNextVideoToProcess(sourcefolder, validextensions):

    print "Getting next video for folder ", sourcefolder

    for root, dirs, files in os.walk(sourcefolder):

        #for filename in glob.glob1(sourcefolder, "*.*"):
        for filename in files:
          (base, ext) = os.path.splitext(filename)
          logger.debug("Checking file %s with extension %s" % (base, ext))
          print("Checking file %s with extension %s" % (base, ext))

          if ext in validextensions:
            return os.path.join(sourcefolder, filename)

          else:
            logger.debug("The file %s 's extension is not part of the valid extensions." % filename)

        return None

def removelockfile(lockfilename):
    print "Removing lock file "
    os.remove(lockfilename)

def removeLockfileIfprocessnotrunning(lockfilename):

    print "Removing lock file name : %s" % lockfilename
    removelockfile(lockfilename)

def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def print_progress(progress, percent):
    logger.info("[ %s ] %.2f%%" % (progress, percent * 100))

def send_email(sender, recipients, subject, htmlmessage):
    """
        Sends an email using mailgun
    """

    hostname = socket.gethostname()
    subject = subject + " (" + hostname + ")"
    attachments = {}
    filesToAttach = ["/Applications/eepm-video-tools.app/eepm_videos_processor.log"]
    index = 0
    for fileToAttach in filesToAttach:
        if(os.path.exists(fileToAttach)):
            filename = os.path.basename(fileToAttach)
            attachmentindex = "attachment[%d]" % (index)
            attachments[attachmentindex] = (filename + ".txt", open(fileToAttach, 'rb'))
            #attachments[attachmentindex] = ("myjob.youtubeupload.log" + ".txt", open("/var/log/myjob.youtubeupload.log", 'rb'))
            index = index + 1

    request_url = 'https://api.mailgun.net/v3/mailgun.bright-softwares.com/messages'
    request = requests.post(request_url,
                            auth=('api', MAILGUN_APIKEY),
                            files=attachments,
                            data={
                                'from': sender,
                                'to': recipients,
                                'subject': subject,
                                'html': htmlmessage
                            })

    print 'Status: {0}'.format(request.status_code)
    print 'Body:   {0}'.format(request.text)

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)