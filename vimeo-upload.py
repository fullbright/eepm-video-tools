#!/usr/bin/python

import vimeo
import os
import json
import dailymotion_upload

def store_token(token, filename):
    print "Writing vimeo access tocken to", filename
    tokenfile = open(filename, "w")
    tokenfile.write("%s" % token)
    tokenfile.close()

def retrieve_token(filename):
    """ Read the token from the file """
    with open(filename, 'r') as f:
        token = f.readline()

        return token


def main():
    print "-------  Starting Vimeo upload --------"
    validextensions = [".mp4", ".mov"]
    configvars = dailymotion_upload.load_variables("vimeo.uploader.cfg")

    API_KEY = configvars['vimeokey'].rstrip()
    API_SECRET = configvars['vimeosecretkey'].rstrip()
    API_TOCKEN = configvars['vimeoaccesstoken'].rstrip()
    lockfilename = configvars['lockfilename'].rstrip()
    tokenfilename = configvars['tokenfilename'].rstrip()
    sourcepath = configvars['sourcepath'].rstrip()

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

    v = vimeo.VimeoClient(token=API_TOCKEN, key=API_KEY, secret=API_SECRET)
    about_me = v.get('/me')
    print "About me status code %s and body is %s" % (about_me.status_code, about_me.json())

    #token = v.load_client_credentials()
    #store_token(token, tokenfilename)

    #v2 = vimeo.VimeoClient(token=token, key=API_KEY, secret=API_SECRET)

    print "Uploading video ", nextfiletoprocess_path
    video_uri = v.upload(nextfiletoprocess_path)

    #response = upload(nextfiletoprocess_path, nextfiletoprocess_title, API_KEY, API_SECRET, USERNAME, PASSWORD)
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
    dailymotion_upload.removelockfile(lockfilename)

    print "-------  Vimeo upload ended --------"

if __name__ == '__main__':
    main()