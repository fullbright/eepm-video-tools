#!/usr/bin/python

import dailymotion
import os
import json

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

def main():

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

if __name__ == '__main__':
    main()