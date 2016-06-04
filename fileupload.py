#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
# vi:ts=4:et
# $Id: file_upload.py,v 1.5 2005/02/13 08:53:13 mfx Exp $

import os, sys, json
import pycurl
from StringIO import StringIO
import urllib

COOKIEFILE="emcicookies.txt"

# Class which holds a file reference and the read callback
class FileReader:
    def __init__(self, fp):
        self.fp = fp
    def read_callback(self, size):
        return self.fp.read(size)
"""
# Check commandline arguments
if len(sys.argv) < 3:
    print "Usage: %s <url> <file to upload>" % sys.argv[0]
    raise SystemExit
url = sys.argv[1]
filename = sys.argv[2]
"""

def upload(url, filename):

    if not os.path.exists(filename):
        print "Error: the file '%s' does not exist" % filename
        raise SystemExit

    fullurl = "%s?name=%s" % (url, os.path.basename(filename))

    print fullurl

    # Initialize pycurl
    storage = StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.COOKIEFILE, COOKIEFILE)
    c.setopt(pycurl.COOKIEJAR, COOKIEFILE)
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

def set_name_and_descr(url, newfilename, newfiletitle, newfiledescription):
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
    c.setopt(pycurl.COOKIEFILE, COOKIEFILE)
    c.setopt(pycurl.COOKIEJAR, COOKIEFILE)
    c.setopt(pycurl.VERBOSE, 1)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, settings_data)
    c.perform()

    content = storage.getvalue()

    #curl -i --trace-ascii emcitrace-ascii-renamefiles.txt --data-urlencode "finished_files%5B%5D=$NEWFILENAME" --data-urlencode "file%5B1%5D%5Boriginal%5D=$NEWFILENAME" --data-urlencode "file%5B1%5D%5Bfile%5D=$NEWFILENAME" --data-urlencode "file%5B1%5D%5Bname%5D=$NEWFILENAME" --data-urlencode "file%5B1%5D%5Bdescription%5D=$NEWFILENAME" --data-urlencode submit=ok --cookie ./emcicookies.txt --cookie-jar ./emcicookies3.txt $UPLOAD_PROCESS_URL >> $LOGFILE 2>&1

    return content
