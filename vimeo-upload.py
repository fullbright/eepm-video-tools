#!/usr/bin/python

import vimeo
import os
import json
import requests
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

def set_video_title(access_token, video_uri, title, description, privacy):
    payload = {'name': title, 'description': description, 'privacy.view': privacy}
    video_full_url = "https://api.vimeo.com" + video_uri
    print "Set video title. Url is %s and payload is %s" % (video_full_url, payload)

    #print "Setting access_token %s in the Authorization header" % access_token
    auth_headers = {'Authorization': 'Bearer ' + access_token}
    print auth_headers
    
    return requests.patch("https://api.vimeo.com" + video_uri, data=payload, headers=auth_headers)

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
    nextfiletoprocess_description = "%s auto described. A real description must go here." % nextfiletoprocess_name

    v = vimeo.VimeoClient(token=API_TOCKEN, key=API_KEY, secret=API_SECRET)
    about_me = v.get('/me')

    if about_me.status_code == 200 :
        print "I can connect to the account. About me status code is %s and the name is %s" % (about_me.status_code, about_me.json())
    else:
        print "We are not authenticated. Status code is %s", about_me.status_code
    
    print "Uploading video ", nextfiletoprocess_path
    video_uri = v.upload(nextfiletoprocess_path)
    #video_uri = '/videos/152054345'
    print "Done. Video uri is", video_uri

    print "Setting the title of the video %s to %s" % (video_uri, nextfiletoprocess_title)
    #response = v.patch(video_uri, {'name': 'nextfiletoprocess_title', 'description': 'This is the videos description.'})
    response = set_video_title(v.token, video_uri, nextfiletoprocess_title, nextfiletoprocess_description, 'nobody')

    # check if the upload is ok
    #jsonresponse = json.loads(response)

    if response.status_code == 200 :
        print "Upload and metadata set was successfull. Status code value was %s" % (response.status_code)
        # move the file to the archive folder
        destinationpath = configvars['destination'].rstrip()
        dst = os.path.join(destinationpath, name)
        print "Moving video file from %s to %s" % (nextfiletoprocess_path, dst)
        os.rename(nextfiletoprocess_path, dst)

    else:
        print "Upload failed. File will not be moved to the archive so we can process it next time."
        print "Status code was %s" % (response.status_code)



    # remove the lock file
    dailymotion_upload.removelockfile(lockfilename)

    print "-------  Vimeo upload ended --------"

if __name__ == '__main__':
    main()