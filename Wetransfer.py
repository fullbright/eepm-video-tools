#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Upload files or folders to WeTransfer
#
# VERSION       :1.0
# DATE          :2014-12-27
# AUTHOR        :Kevin Raynel <https://github.com/kraynel>
# URL           :https://github.com/kraynel/upload-wetransfer
# DEPENDS       :pip install requests requests-toolbelt

from urlparse import urlparse, parse_qs
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

import os, requests, sys, json, re, argparse, sys, mimetypes, collections
import Utils as utils
import shutil
import time
import datetime

WE_TRANSFER_API_URL = "https://www.wetransfer.com/api/v1/transfers"
CHUNK_SIZE = 5242880

def getTransferId(sender, receivers, message):
    dataTransferId =  { "channel":"",
    "expire_in":   "",
    "from":    sender,
    "message": message,
    "pw" : "",
    "to[]" :   receivers,
    "ttype" :  "1",
    "utype" :  "js"
    }

    r = requests.post(WE_TRANSFER_API_URL, data=dataTransferId)
    response_data = json.loads(r.content)

    return response_data["transfer_id"]

def getFileObjectId(transferId, filename, filesize):
    dataFileObjectId =  { "chunked": "true",
    "direct":   "false",
    "filename":    filename,
    "filesize": filesize
    }

    r = requests.post((WE_TRANSFER_API_URL + "/{0}/file_objects").format(transferId), data=dataFileObjectId)
    response_data = json.loads(r.content)

    return response_data


def getChunkInfoForUpload(transferId, fileObjectId, chunkNumber, chunkSize=CHUNK_SIZE):
    dataChunk = { "chunkNumber" : chunkNumber,
    "chunkSize" :  chunkSize,
    "retries" : "0" }

    r = requests.put((WE_TRANSFER_API_URL + "/{0}/file_objects/{1}").format(transferId, fileObjectId), data=dataChunk)

    return json.loads(r.content)

def drawProgressBar(percent, barLen = 40):
    sys.stdout.write("\r")
    progress = ""
    for i in range(barLen):
        if i < int(barLen * percent):
            progress += "="
        else:
            progress += " "
    sys.stdout.write("[ %s ] %.2f%%" % (progress, percent * 100))
    sys.stdout.flush()

def create_callback(previousChunks, fileSize):

    def callback(monitor):
        drawProgressBar(float(previousChunks + monitor.bytes_read)/float(fileSize))

    return callback

def uploadChunk(chunkInfo, filename, dataBin, fileType, chunkNumber, fileSize):
    url = chunkInfo["url"]

    dataChunkUpload = collections.OrderedDict()
    for k, v in chunkInfo["fields"].items():
        dataChunkUpload[k] = v

    dataChunkUpload["file"] = (filename, dataBin, fileType)

    e = MultipartEncoder(fields=dataChunkUpload)
    m = MultipartEncoderMonitor(e, create_callback(chunkNumber*CHUNK_SIZE, fileSize))

    r = requests.post(url, data=m, headers={'Content-Type': e.content_type})
    print("")

def finalizeChunks(transferId, fileObjectId, partCount):
    dataFinalizeChunk = {
    "finalize_chunked"  : "true",
    "part_count"  : partCount
    }

    r = requests.put((WE_TRANSFER_API_URL + "/{0}/file_objects/{1}").format(transferId, fileObjectId), data=dataFinalizeChunk)
    #print(r.text)

def finalizeTransfer(transferId):
    print("Finalize transfer")

    r = requests.put((WE_TRANSFER_API_URL + "/{0}/finalize").format(transferId))

def cancelTransfer(transferId):
    print("Cancelling transfer")

    r = requests.put((WE_TRANSFER_API_URL + "/{0}/cancel").format(transferId))


def read_in_chunks(file_object, chunk_size=CHUNK_SIZE):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 5Mo."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def uploadFile(transferId, fileToUpload):
    with open(fileToUpload, 'rb') as f:
        fileMimeType = "application/octet-stream"
        #mimetypes.read_mime_types(f.name)
        fileSize = os.path.getsize(fileToUpload)
        fileName = os.path.basename(fileToUpload)

        dataFileObjectId = getFileObjectId(transferId, fileName, fileSize)
        if dataFileObjectId.has_key("url"):
            uploadChunk(dataFileObjectId, fileName, f.read(fileSize), fileMimeType, 0, fileSize)
            finalizeChunks(transferId, dataFileObjectId["file_object_id"], 1)
        else:
            chunkNumber = 1

            for piece in read_in_chunks(f):
                chunkInfo = getChunkInfoForUpload(transferId, dataFileObjectId["file_object_id"], chunkNumber, sys.getsizeof(piece))
                uploadChunk(chunkInfo, fileName, piece, fileMimeType, chunkNumber-1, fileSize)
                chunkNumber = chunkNumber + 1

            finalizeChunks(transferId, dataFileObjectId["file_object_id"], chunkNumber - 1)

def uploadDir(top, transferId, recursive):
    '''descend the directory tree rooted at top,
       calling the upload function for each regular file'''

    for root, dirs, files in os.walk(top):
        if not recursive:
            while len(dirs) > 0:
                dirs.pop()

        for name in files:
            print("Upload file : " + os.path.abspath(os.path.join(root, name)))
            uploadFile(transferId, os.path.abspath(os.path.join(root, name)))

def startAutomaticUpload():
    # Read the configuration files
    configvars = utils.load_variables("eepm_videos_processor.cfg")
    sourcepath = configvars['wetransfer.sourcepath'].rstrip()
    destination = configvars['wetransfer.destination'].rstrip()

    # Get the next video from the source path
    validextensions = [".mp4", ".mov", ".mp3"]
    fileToUpload = utils.getNextVideoToProcess(sourcepath, validextensions)

    print "File to upload %s", fileToUpload

    # Upload that video
    if fileToUpload != None :

        size = os.path.getsize(fileToUpload) / (1024*1024.0)
        filedate = time.ctime(os.stat(fileToUpload).st_mtime)
        destfileName = utils.path_leaf(fileToUpload)
        destfile = os.path.join(destination, destfileName)
        if(os.path.isfile(destfile)):
            destfilename = datetime.datetime.now() + "_" + destfilename
            destfile = os.path.join(destination, destfilename)

        print "We are going to process the file %s (%s) MB, date (%s). If upload successfull, will be moved to %s" % (fileToUpload, size, filedate, destfile)

        uploadResult = uploadThisVideo(fileToUpload, "video@monegliseaparis.fr", "afanousergio@yahoo.fr", "EEPM Video %s" % fileToUpload)

        if uploadResult == True:
            print "Move the processed file to the destination"
            print "Moving %s to %s" % (fileToUpload, destfile)

            if not os.path.isfile(destfile):
                size = os.path.getsize(fileToUpload) / (1024*1024.0)
                shutil.move(fileToUpload, destfile)
            else:
                print "Cannot move. Destination file exists."
        else:
            print "Upload failed :( Sorry"

        # Send a mail to tell the gospel ;)
        utils.send_email('EEPB Video Automator <mailgun@mailgun.bright-softwares.com>',
                            "video@monegliseaparis.fr",
                            "WeTransfer : videos processing report",
                            "Hello, I have just uploaded the video to Wetransfer and I wanted to notify you. I am sending this email from the mac computer we use to export videos. I am an Automator application. Enjoy."
                        )


    else :
        print "Nothing to upload. There is no next video."

def uploadThisVideo(videopath, sender, receiver, message):

    # Check that it is not too big for the upload
    fileSize = os.path.getsize(videopath) / (1024*1024.0)
    print "The file %s size %s" % (videopath, fileSize)
    if fileSize > 1900 :
        print "The file is over the 2Go allowed by Wetransfer. Cannot upload"
        return False

    transferId = getTransferId(sender, receiver, message)

    # Upload it
    try:
        if os.path.isfile(videopath):
            print("Upload file : " + videopath)
            uploadFile(transferId, videopath)
            finalizeTransfer(transferId)
            return True
        else:
            print("The object you are trying to upload is not a file")

    except KeyboardInterrupt, e:
        print "Oh daizy, an error occured. ", str(e)
        if transferId:
            cancelTransfer(transferId)
        return False

def main(argv):
    errormessage = ""

    try:
        parser = argparse.ArgumentParser(description='Uploads files or folders to WeTransfer.')
        parser.add_argument('-r', '--receiver', help='emails of the receivers', nargs='*')
        parser.add_argument('-s', '--sender', help='email of the sender', default="myEmail@myDomain.com")
        parser.add_argument('-m', '--message', help='message to send')
        parser.add_argument('-R', '--recursive', help='recursive send', action='store_true')
        parser.add_argument('files', help='files or directory to send', nargs='+')

        args = parser.parse_args();
        mimetypes.init()

        try:
            transferId = getTransferId(args.sender, args.receiver, args.message)

            for it in args.files:
                if os.path.isfile(it):
                    print("Upload file : " + it)
                    uploadFile(transferId, it)
                elif os.path.isdir(it):
                    uploadDir(it, transferId, args.recursive)
                else:
                    print("Not a file/directory : " + it)


            finalizeTransfer(transferId)
        except KeyboardInterrupt:
            print ""
            if transferId:
                cancelTransfer(transferId)
    except:
        errormessage = errormessage + " -> " + sys.exc_info()[0]
        logger.debug("Something bad happned. The error is ", sys.exc_info()[0], ". Thats all we know")

    finally:

        utils.send_email('EEPB Video Automator <mailgun@mailgun.bright-softwares.com>',
            "video@monegliseaparis.fr",
            "WeTransfer : videos processing report",
            "Hello, I have just uploaded the video $videofile to Youtube and I wanted to notify you. Here are the possible errors : " + errormessage + " I am sending this email from the mac computer we use to export videos. I am an Automator application. Enjoy."
            )

if __name__ == "__main__":

    if len(sys.argv) > 1 :
        # We have command line arguments. Let's process them
        main(sys.argv[1:])
    else:
        startAutomaticUpload()
