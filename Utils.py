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


# load the variables

def load_variables(configfile):

    logger.debug("Loading variables from config file %s" % (configfile))
    dataMap = {}

    logger.debug("Testing yaml config file to initiate conversion")
    if not os.path.exists(YAMLCONFIGFILE):
        convertIniToYaml()

    # If there is a yaml configuration file, use it.
    logger.debug("Checking if a yaml file is available to use it")
    if os.path.exists(YAMLCONFIGFILE):
        logger.debug("Found a yaml file, using it")
        f = open(YAMLCONFIGFILE)
        dataMap = yaml.load(f)
        f.close()

    # TODO : Remove the line below after stabilizing the yaml config conversion

    return dataMap

    #configvars = {}
    ## read the configuration file
    #with open(configfile) as myfile:
    #    for line in myfile:
    #        if not line.startswith('#') and not line.strip() == '' : # ignore line begining with #
    #            name, var = line.partition("=")[::2]
    #            #print "Storing variable %s with value %s" % (name, var)
    #            configvars[name.replace('\\n', '').strip()] = var.replace('\\n', '')
    #return configvars

def convertIniToYaml():

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

def send_email(sender, recipients, subject, htmlmessage):
    """
        Sends an email using mailgun
    """

    socket.gethostname()
    subject = subject + "(" + hostname + ")"
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

