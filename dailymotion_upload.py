#!/usr/bin/python

import dailymotion
import os
import json
import requests

MAILGUN_APIKEY = 'key-44faoj5x2z0nbxz3r08todivhnh17261'

# load the variables

def load_variables(configfile):
    configvars = {}
    # read the configuration file
    with open(configfile) as myfile:
        for line in myfile:
            if not line.startswith('#') and not line.strip() == '' : # ignore line begining with #
                name, var = line.partition("=")[::2]
                print "Storing variable %s with value %s" % (name, var)
                configvars[name.replace('\\n', '').strip()] = var.replace('\\n', '')

    return configvars


# upload the video
def upload(videofile, title, API_KEY, API_SECRET, USERNAME, PASSWORD):
	

    d = dailymotion.Dailymotion()
    d.set_grant_type('password', api_key=API_KEY, api_secret=API_SECRET, 
        scope=['manage_videos'], info={'username': USERNAME, 'password': PASSWORD})

    print "Posting the video %s to dailymotion in private mode" % (videofile)

    url = d.upload(videofile)

    print "Setting video in private mode with the url %s" % url

    return d.post('/me/videos',
		{'url': url, 'title': title, 'published': 'false', 'channel': 'lifestyle'})

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


def removelockfile(lockfilename):
    print "Removing lock file "
    os.remove(lockfilename)

def send_email(sender, recipients, subject, htmlmessage):
    """
        Sends an email using mailgun
    """

    attachments = {}
    filesToAttach = ["/var/log/myjob.eepm_video_processor.log", "/var/log/myjob.youtubeupload.log", "/var/log/myjob.ftpupload.log", "/var/log/myjob.emciupload.log"]
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


def main():

    errormessage = ""

    try:
        print "--------------- Starting the dailymotion process --------------- "
        validextensions = [".mp4", ".mov"]
        configvars = load_variables("dailymotion.uploader.cfg")

        API_KEY = configvars['dailymotionkey'].rstrip()
        API_SECRET = configvars['dailymotionsecretkey'].rstrip()
        USERNAME = configvars['dailymotion_username'].rstrip()
        PASSWORD = configvars['dailymotion_password'].rstrip()
        lockfilename = configvars['lockfilename'].rstrip()
        sourcepath = configvars['sourcepath'].rstrip()

        # prevent double upload with a lock file
        check_lock_file(lockfilename)
        
        # pick the first video and upload it    
        print "Processing the source path" , sourcepath
        nextfiletoprocess = ""
        for name in os.listdir(sourcepath):    
            (base, ext) = os.path.splitext(name)
            if ext in validextensions:
                print " === Got the one to process : ", os.path.join(sourcepath, name)
                nextfiletoprocess_name = name
                nextfiletoprocess_path = os.path.join(sourcepath, name)

                print "Break out of the loop"
                break

        # Got our file, then upload it
        nextfiletoprocess_title = "%s auto uploaded" % nextfiletoprocess_name

        response = upload(nextfiletoprocess_path, nextfiletoprocess_title, API_KEY, API_SECRET, USERNAME, PASSWORD)
        #response = "{u'owner': u'xok987', u'id': u'x3kh5zt', u'channel': u'news', u'title': u'PF_video10.mov auto uploaded'}"

        # check if the upload is ok
        #response = response.replace("'", "\"")
        print response
        #jsonresponse = json.loads(response)

        if 'id' in response.keys() :
            print "Upload was successfull. %s found in %s" % (nextfiletoprocess_title, response)
            # move the file to the archive folder
            destinationpath = configvars['destination'].rstrip()
            dst = os.path.join(destinationpath, name)
            print "Moving video file from %s to %s" % (nextfiletoprocess_path, dst)
            os.rename(nextfiletoprocess_path, dst)

        else:
            print "%s was not found in %s" % (nextfiletoprocess_title, response)
            print "Upload failed. File will not be moved to the archive so we can process it next time."



        # remove the lock file
        removelockfile(lockfilename)
        print "--------------- Dailymotion process ended --------------- "

    except:
        errormessage = errormessage + " -> " + sys.exc_info()[0]
        logger.debug("Something bad happned. The error is ", sys.exc_info()[0], ". Thats all we know")

    finally:

        dailymotion.send_email('EEPB Video Automator <mailgun@mailgun.bright-softwares.com>',
            "video@monegliseaparis.fr",
            "Video file $videofile successfully uploaded to Youtube",
            "Hello, I have just uploaded the video $videofile to Youtube and I wanted to notify you. Here are the possible errors : " + errormessage + " I am sending this email from the mac computer we use to export videos. I am an Automator application. Enjoy."
            )

if __name__ == '__main__':
    main()