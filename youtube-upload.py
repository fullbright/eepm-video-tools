#!/usr/bin/python

import httplib
import httplib2
import os
import random
import sys
import time
import logging
import logging.handlers
import glob
import shutil
import traceback

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import Utils as dailymotion


## Setup logging
logger = logging.getLogger('eepm_video_processor.YoutubeUpload')
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


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"
CREDENTIALS_STORAGE_FILE = "eepm_videos_youtube_uploader-oauth2.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service(args):

  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)


  '''
  CLIENT_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  CLIENT_SECRET = "xxxxxxxxxxxxxxxxxxxxxxx"
  flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, YOUTUBE_UPLOAD_SCOPE)
  '''

  #storage = Storage("%s-oauth2.json" % sys.argv[0])
  storage = Storage(CREDENTIALS_STORAGE_FILE)
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    #credentials = run_flow(flow, storage, args)
    #return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    #   http=credentials.authorize(httplib2.Http()))

    # Step 1: get user code and verification URL
    # https://developers.google.com/accounts/docs/OAuth2ForDevices#obtainingacode
    flow_info = flow.step1_get_device_and_user_codes()
    print("Enter the following code at {0}: {1}".format(flow_info.verification_url,flow_info.user_code))
    print("Then press enter.")
    userinput = raw_input()
    print("The user said : {0}".format(userinput))

    # Step 2: get credentials
    # https://developers.google.com/accounts/docs/OAuth2ForDevices#obtainingatoken
    print "Exchanging the tokens ..."
    credentials = flow.step2_exchange(device_flow_info=flow_info)
    print("Access token:  {0}".format(credentials.access_token))
    print("Refresh token: {0}".format(credentials.refresh_token))

    logger.info("Succesfully got access and refresh token. Storing ....")
    print("Storing credentials")
    storage.put(credentials)

    # Get YouTube service
    # https://developers.google.com/accounts/docs/OAuth2ForDevices#callinganapi
    #youtube = build("youtube", "v3", http=credentials.authorize(httplib2.Http()))
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))
  return youtube

def initialize_upload(youtube, options):
  tags = None
  if options['keywords']:
    tags = options['keywords'].split(",")

  body=dict(
    snippet=dict(
      title=options['title'],
      description=options['description'],
      tags=tags,
      categoryId=options['category']
    ),
    status=dict(
      privacyStatus=options['privacyStatus']
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    #media_body=MediaFileUpload(options['file'], chunksize=-1, resumable=True)
    media_body=MediaFileUpload(options['file'], chunksize=50*256*1024, resumable=True)
  )

  return resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print "Uploading file..."
      logger.info("Uploading file...")
      status, response = insert_request.next_chunk()
      print response

      if status is not None:
        print "Uploaded %d%%." % int(status.progress() * 100)
        logger.debug("Uploaded %d%%." % int(status.progress() * 100))

      '''
      if response is not None and 'id' in response:
        print "Video id '%s' was successfully uploaded." % response['id']
        logger.debug("Video id '%s' was successfully uploaded." % response['id'])
      else:
        logger.error("The upload failed with an unexpected response: %s" % response)
        logger.debug("The upload failed with an unexpected response: %s" % response)
        return False
      '''

    except HttpError, e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
        logger.debug("A retriable error occured.")
      else:
        raise
    except RETRIABLE_EXCEPTIONS, e:
      error = "A retriable error occurred: %s" % e
      logger.debug("A retriable error occurred: %s" % e)

    if error is not None:
      print error
      logger.debug(error)
      retry += 1
      logger.debug("Increasing the retry count to %d" % (retry))

      if retry > MAX_RETRIES:
        logger.error("Oh daizy ! Max retry count %s is reached. No longer attempting to retry." % (MAX_RETRIES))
        return False

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      m, s = divmod(sleep_seconds, 60)
      h, m = divmod(m, 60)
      print "Sleeping %f seconds (%d:%02d:%02d) and then retrying..." % (sleep_seconds, h, m, s)
      logger.debug("Sleeping %f seconds (%d:%02d:%02d) and then retrying..." % (sleep_seconds, h, m, s))
      time.sleep(sleep_seconds)
    else:
      logger.debug("There was no error this time. Resetting retry to zero.")
      retry = 0

  if response is not None and 'id' in response:
    print "Video id '%s' was successfully uploaded." % response['id']
    logger.debug("Video id '%s' was successfully uploaded." % response['id'])
    logger.debug("Upload was successful")
    return True
  else:
    logger.error("The upload failed with an unexpected response: %s" % response)
    logger.debug("The upload failed with an unexpected response: %s" % response)
    return False


def main():

  logger.debug("Starting the youtube upload process")
  errormessage = ""

  try:
    logger.debug("Loading variables ...")
    validextensions = [".mp4", ".mov", ".mp3"]
    configvars = dailymotion.load_variables("eepm_videos_processor.cfg")
    sourcepath = configvars['youtube.sourcepath'].rstrip()
    destination = configvars['youtube.destination'].rstrip()

    logger.debug("Uploading videos from %s to youtube, then move it to %s" % (sourcepath, destination))
    for filename in glob.glob1(sourcepath, "*.*"):
      (base, ext) = os.path.splitext(filename)
      logger.debug("Checking file %s with extension %s" % (base, ext))

      if ext in validextensions:
        srcfile = os.path.join(sourcepath, filename)
        logger.debug("File %s extension %s is in valid extensions" % (filename, ext))

        logger.debug("Computing the upload informations")
        videotitle = base
        videodescription = "Automatically uploaded %s in private mode." % videotitle
        videokeywords = "Eglise Paris Metropole, Eglise Paris Bastille"
        videocategory = 22
        videoprivacyStatus = "private"

        logger.debug("Building args object")
        args={
          "file":srcfile,
          "title":videotitle,
          "description":videodescription,
          "category":videocategory,
          "privacyStatus":videoprivacyStatus,
          "keywords":videokeywords
        }

        logger.debug("args object built.")
        #logger.debug(dir(args))
        #setattr(args, 'keywords', videokeywords)
        #logger.debug(dir(args))

        logger.debug("Getting authenticated service...")
        youtube = get_authenticated_service(args)
        logger.debug("Done.")

        try:
          logger.debug("Initializing upload ...")
          uploaded = initialize_upload(youtube, args)

          if uploaded :
            print "Upload was successfull."
            # move the file to the archive folder
            dst = os.path.join(destination, filename)
            print "Moving video file from %s to %s" % (srcfile, dst)
            os.rename(srcfile, dst)

          else:
            print "%s was not found in %s" % (srcfile, response)
            print "Upload failed. File will not be moved to the archive so we can process it next time."


        except HttpError, e:
          errormessage = errormessage + " -> " + e.content
          print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
          logger.debug("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

      else:
        logger.debug("The file %s 's extension is not part of the valid extensions." % filename)

  except Exception, e:
    str(e)
    logger.debug("Oh daizy !!! Something bad happened during Youtube processing. Start exception handling.")
    errormessage = repr(e) #.args[1] # message
    #errormessage = ""
    traceback.print_exc()
    logger.debug("Something bad happned. The error is %s. Thats all we know" % (errormessage))
    logger.debug("End of exception handling.")

  finally:

    dailymotion.send_email('EEPB Video Automator <mailgun@mailgun.bright-softwares.com>',
        "video@monegliseaparis.fr",
        "Youtube : videos processing report",
        "Hello, I have just uploaded the video $videofile to Youtube and I wanted to notify you. Here are the possible errors : " + errormessage + " I am sending this email from the mac computer we use to export videos. I am an Automator application. Enjoy."
        )

if __name__ == '__main__':
  main()
