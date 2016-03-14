#!/usr/bin/python
# -*- coding: utf-8 -*-

####################################
# This script uploads videos to ftp
# Author : S. Afanou
# Date : mar 2016
# email : afanousergio@gmail.com
####################################

## Imports
#import requests, requests.utils, pickle
from poster.encode import multipart_encode
from poster.encode import MultipartParam
from poster.streaminghttp import register_openers
import urllib, urllib2, cookielib
import poster
import os.path
import mimetypes
import json
from StringIO import StringIO

import dailymotion_upload

import os, sys, json
import pycurl

class FileReader:
    def __init__(self, fp):
        self.fp = fp
    def read_callback(self, size):
        return self.fp.read(size)


def initialize_uploads(args):
	## How does it work ?

    # Make sure that we are auhenticated
    cookieJarFile = authenticate()

    # If response is 301 or 302 or 401, then execute authentication procedure
    """
        #print resp.read()
        # If authenticated, upload the video file
        # Register the streaming http handlers with urllib2
        register_openers()

        # Start the multipart/form-data encoding of the file "DSC0001.jpg"
        # "image1" is the name of the parameter, which is normally set
        # via the "name" parameter of the HTML <input> tag.

        # headers contains the necessary Content-Type and Content-Length
        # datagen is a generator object that yields the encoded parameters
        datagen, headers = multipart_encode({"name": open(FILE_UPLOAD_NAME, "rb")})

        # Create the Request object
        request = urllib2.Request(UPLOAD_URL, datagen, headers)
        # Actually do the request, and get the response
        print urllib2.urlopen(request).read()

    """

    """
    print "Uploading with multipart and cookielib"
    opener = poster.streaminghttp.register_openers()
    #opener.add_handler(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
    opener.add_handler(urllib2.HTTPCookieProcessor(cookieJarFile))

    image_param = MultipartParam("file", filename=os.path.basename(FILE_UPLOAD_NAME), filetype=mimetypes.guess_type(filename)[0])
    datagen, headers = multipart_encode([image_param])
    """


    """
    params = {'file': open(FILE_UPLOAD_NAME, "rb"), 'name': FILE_UPLOAD_TITLE}
    print "Uploading video %s" % params

    datagen, headers = poster.encode.multipart_encode(params)

    print datagen
    print headers
    """

    """
    request = urllib2.Request(UPLOAD_URL, datagen, headers)
    print dir(request)

    result = urllib2.urlopen(request)
    print result.read()
    """


    #curl -i --trace-ascii emcitrace-ascii-renamefiles.txt --data-urlencode "finished_files%5B%5D=$NEWFILENAME" --data-urlencode "file%5B1%5D%5Boriginal%5D=$NEWFILENAME" --data-urlencode "file%5B1%5D%5Bfile%5D=$NEWFILENAME" --data-urlencode "file%5B1%5D%5Bname%5D=$NEWFILENAME" --data-urlencode "file%5B1%5D%5Bdescription%5D=$NEWFILENAME" --data-urlencode submit=ok --cookie ./emcicookies.txt --cookie-jar ./emcicookies3.txt $UPLOAD_PROCESS_URL >> $LOGFILE 2>&1

def authenticate():
    """
        Authenticate to the server and stores the cookies into a cookiejar.
        Return the cookiejar object.
    """

    configvars = dailymotion_upload.load_variables("emci.uploader.cfg")
    cookiefile = configvars['COOKIEFILE'].rstrip()
    hiddenpageurl =  configvars['HIDDENPAGE_URL'].rstrip()
    loginpageurl = configvars['LOGIN_URL'].rstrip()
    userlogin = configvars['USER_LOGIN'].rstrip()
    userpassword = configvars['USER_PASS'].rstrip()

    if os.path.exists(cookiefile):
        print "Cookie file exists. Checking the validity of the cookie"
        print "Loading cookies ..."
        parsedCookieJarFile = cookielib.MozillaCookieJar(cookiefile)
        parsedCookieJarFile.load(cookiefile)
        print parsedCookieJarFile

        print "Trying to connect to the hidden page url", hiddenpageurl
        hiidenpageopener = urllib2.build_opener()
        resp = hiidenpageopener.open(hiddenpageurl)

        response_content = resp.read()
        print "response for the page %s is %s" % (hiddenpageurl, resp.getcode())
        print "response content is %s" % (response_content)

        if resp.getcode() == 200 and "Bonjour, " in response_content:
            print "We can fetch the hidden url page", hiddenpageurl
            print "We are authenticated."
            return parsedCookieJarFile

        elif resp.getcode() == 301 or resp.getcode() == 302 or resp.getcode() == 401:
            print "Cannot access the hidden page. Doing a new authentication below ..."
        else:
            print "We have an unhandled response code.", resp.getcode()

    print "Doing a new authentication"
    print "userlogin : %s and userpassword : %s" % (userlogin, userpassword)

    login_data = urllib.urlencode({'login_form_user' : userlogin, 'login_form_pass' : userpassword})
    print "Login data is", login_data

    login_data = "login_form_user=%s&login_form_pass=%s" % (userlogin, userpassword)
    print "Login data unforged is", login_data

    storage = StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, loginpageurl)
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.setopt(pycurl.COOKIEFILE, cookiefile)
    c.setopt(pycurl.COOKIEJAR, cookiefile)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, login_data)
    c.perform()

    content = storage.getvalue()
    print "Login request content : ", content

    return cookielib.LWPCookieJar(cookiefile)


def upload(url, filename, cookiefile):

    if not os.path.exists(filename):
        print "Error: the file '%s' does not exist" % filename
        raise SystemExit

    fullurl = "%s?name=%s" % (url, os.path.basename(filename))
    print "The full url where the video will be uploaded is", fullurl

    # Initialize pycurl
    storage = StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.COOKIEFILE, cookiefile)
    c.setopt(pycurl.COOKIEJAR, cookiefile)
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.setopt(pycurl.URL, fullurl)

    #c.setopt(pycurl.HTTPPOST, [ ('uploader_0_name', (c.FORM_FILE, filename) ) ])
    #upload_data = urllib.urlencode({"name": filename})
    #c.setopt(pycurl.POSTFIELDS, upload_data)
    #c.setopt(pycurl.HTTPHEADER, ["%s:%s" % ("name", "filename_supervideo.mov")])
    c.setopt(pycurl.VERBOSE, 1)

    c.setopt(pycurl.UPLOAD, 1)
    #c.setopt(pycurl.CUSTOMREQUEST, "PUT")
    #c.setopt(pycurl.POST, 1)

    # Two versions with the same semantics here, but the filereader version
    # is useful when you have to process the data which is read before returning
    if 1:
        c.setopt(pycurl.READFUNCTION, FileReader(open(filename, 'rb')).read_callback)
    else:
        c.setopt(pycurl.READFUNCTION, open(filename, 'rb').read)

    # Set size of file to be uploaded.
    filesize = os.path.getsize(filename)
    #c.setopt(pycurl.INFILESIZE, filesize)


    """
    c.setopt(
        c.HTTPPOST, [
            (
                "uploader_0_name", (c.FORM_FILE, filename, c.FORM_FILENAME, filename, c.FORM_CONTENTTYPE, "video/quicktime")
            )
        ]
    )

    #upload_data = urllib.urlencode({"name": filename})
    upload_data = urllib.urlencode({"name": filename, "file[]": (pycurl.FORM_FILE, filename) })
    #upload_data = [("name", filename), ("file", (pycurl.FORM_FILE, filename)) ]
    c.setopt(pycurl.POSTFIELDS, upload_data)
    #c.setopt(c.HTTPPOST, [(c.FORM_FILE, filename)])
    c.setopt(pycurl.HTTPPOST, [('name', 'filename_of_thebest.mov')])
    c.setopt(pycurl.UPLOAD, 1)
    c.setopt(pycurl.VERBOSE, 1)

    #c.setopt(pycurl.HTTPHEADER, ["%s:%s" % ("name", "filename_supervideo.mov")])
    """

    # Start transfer
    print 'Uploading file %s to url %s' % (filename, url)
    c.perform()
    c.close()

    content = storage.getvalue()
    print content
    return content

def set_name_and_descr(url, newfilename, newfiletitle, newfiledescription, cookiefile):
    """
    Set the name and description
    """
    print "Url", url
    print "New file name", newfilename
    print "New file title", newfiletitle
    print "New file description", newfiledescription

    #data = json.dumps({"finished_files[]": newfilename, "file[1][original]": newfilename, "file[1][file]": newfiletitle, "file[1][description]": newfiledescription, "submit": "ok"})
    settings_data = urllib.urlencode({"finished_files[]": newfiletitle, "file[1][original]": newfiletitle, "file[1][file]": newfilename, "file[1][name]": newfiletitle, "file[1][description]": newfiledescription, "upload_failed" : "", "submit": "Continuer"})

    storage = StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.setopt(pycurl.COOKIEFILE, cookiefile)
    c.setopt(pycurl.COOKIEJAR, cookiefile)
    c.setopt(pycurl.VERBOSE, 1)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, settings_data)
    c.perform()

    content = storage.getvalue()

    #curl -i --trace-ascii emcitrace-ascii-renamefiles.txt --data-urlencode "finished_files%5B%5D=$NEWFILENAME" --data-urlencode "file%5B1%5D%5Boriginal%5D=$NEWFILENAME" --data-urlencode "file%5B1%5D%5Bfile%5D=$NEWFILENAME" --data-urlencode "file%5B1%5D%5Bname%5D=$NEWFILENAME" --data-urlencode "file%5B1%5D%5Bdescription%5D=$NEWFILENAME" --data-urlencode submit=ok --cookie ./emcicookies.txt --cookie-jar ./emcicookies3.txt $UPLOAD_PROCESS_URL >> $LOGFILE 2>&1

    return content



def main():
    """
    argparser.add_argument("--file", required=True, help="Video file to upload")
    argparser.add_argument("--title", help="Video title", default="Video Title")
    argparser.add_argument("--description", help="Video description", default="Test Description")
    argparser.add_argument("--name", default="Video file name", help="The name of the video to upload.")
    args = argparser.parse_args()

    if not os.path.exists(args.file):
        exit("Please specify a valid file using the --file= parameter.")

    #youtube = get_authenticated_service(args)
    try:
        print "Sleeping for 60 seconds to prevent launchd from disabling this task"
        print "Start : %s" % time.ctime()
        #time.sleep(60)
        print "End : %s" % time.ctime()
        initialize_upload(args)
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)

    """

    #args = []
    #initialize_uploads(args)


    print "-------  Starting EMCI upload --------"
    validextensions = [".mp4", ".mov"]
    configvars = dailymotion_upload.load_variables("emci.uploader.cfg")

    lockfilename = configvars['lockfilename'].rstrip()
    sourcepath = configvars['sourcepath'].rstrip()
    uploadurl = configvars['UPLOAD_URL'].rstrip()
    uploadprocessurl = configvars['UPLOAD_PROCESS_URL'].rstrip()
    cookiefile = configvars['COOKIEFILE'].rstrip()

    # prevent double upload with a lock file
    dailymotion_upload.check_lock_file(lockfilename)
    
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
    nextfiletoprocess_description = "%s auto described. A real description must go here." % nextfiletoprocess_name

    # Make sure we are authenticated.
    authenticate()
    
    print "Uploading video ", nextfiletoprocess_path


    result = upload(uploadurl, nextfiletoprocess_path, cookiefile)

    print "Here is the result of the upload : ", result

    resultjson = json.loads(result)

    if resultjson.get('NewFileName'):
        NEW_FILE_UPLOAD_NAME = resultjson.get('NewFileName')
        print "New upload file name ", NEW_FILE_UPLOAD_NAME
        print "Done. Video uri is", NEW_FILE_UPLOAD_NAME

        # Set the video name and description in the page
        print "Set the video name and description ..."
        print "Setting the title of the video %s to %s" % (NEW_FILE_UPLOAD_NAME, nextfiletoprocess_title)
        setfileresult = set_name_and_descr(uploadprocessurl, NEW_FILE_UPLOAD_NAME, nextfiletoprocess_title, nextfiletoprocess_description, cookiefile)
        print "Setting file result is ", setfileresult

        if "Votre compte ne vous permet pas de voir cette page" not in setfileresult :
            print "Upload and metadata set was successfull. Status code value was %s" % (setfileresult)
            # move the file to the archive folder
            destinationpath = configvars['destination'].rstrip()
            dst = os.path.join(destinationpath, nextfiletoprocess_name)
            print "Moving video file from %s to %s" % (nextfiletoprocess_path, dst)
            os.rename(nextfiletoprocess_path, dst)

        else:
            print "Upload failed. File will not be moved to the archive so we can process it next time."
            print "Status code was %s" % (response.status_code)

    else:
        print "There is no NewFileName key in the json file", result
        print "Aborting ..."
        exit(-1)

    # remove the lock file
    dailymotion_upload.removelockfile(lockfilename)

    print "-------  EMCI upload ended --------"

if __name__ == '__main__':
    main()