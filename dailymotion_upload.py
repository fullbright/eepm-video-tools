#!/usr/bin/python

import Utils as utils
import os
import json
import requests
import sys

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



def main():

    logger = logging.getLogger("eepm_video_processor.DailymotionUpload")
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

    except Exception as e:
        logger.debug("Oh daizy. Something bad happened during dailymotion process. Starting error handling")
        errormessage = errormessage + " -> " + str(e) # sys.exc_info()[0]
        logger.debug("Something bad happened. The error is ", sys.exc_info()[0], ". Thats all we know")
        logger.debug("End of error handling.")

    finally:

        utils.send_email('EEPB Video Automator <mailgun@mailgun.bright-softwares.com>',
            "video@monegliseaparis.fr",
            "Dailymotion : videos processing report",
            "Hello, I have just uploaded the video $videofile to Youtube and I wanted to notify you. Here are the possible errors : " + errormessage + " I am sending this email from the mac computer we use to export videos. I am an Automator application. Enjoy."
            )

if __name__ == '__main__':
    main()
