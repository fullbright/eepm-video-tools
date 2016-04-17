
import sys
import os
import glob
import shutil
import time
import dailymotion_upload as dailymotion
import logging
from datetime import datetime, date, timedelta
from oauth2client.tools import argparser


class VideoArchiver():

    def __init__(self, source_folder, destination_folder):
        # start editable vars #
        self.current_script_file = os.path.realpath(__file__)
        self.current_script_dir = os.path.abspath(os.path.join(self.current_script_file, os.pardir))

        self.days_old = 28               # how old the files have to be before they are moved
        self.original_folder = source_folder #"/Users/sergio/Downloads"  # folder to move files from
        self.new_folder = destination_folder #"/Users/sergio/Desktop"       # folder to move files to

        self.logfile = "%s/videos_archiving.log" % (self.current_script_dir)      # log file to record what has happened
        self.logger = logging.getLogger("cuarch")
        hdlr = logging.FileHandler(self.logfile)
        hdlr.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

        self.validextensions = [".mp4", ".mov", ".mp3"]
        # end editable vars #

    # start function definitions #
    def log(self,level,msg,tofile=True):
        print msg

        if tofile == True:
            if level == 0:
                self.logger.info(msg)
            else:
                self.logger.error(msg)

    def end(self,code):
        self.log(0,"End.")
        self.log(0,"-------------------------")
        #sys.exit(code)

    # end function definitions #


    # start process #
    def process(self):
        move_date = date.today() - timedelta(days=self.days_old)
        move_date = time.mktime(move_date.timetuple())
        #logger = logging.getLogger("cuarch")
        #hdlr = logging.FileHandler(logfile)
        #hdlr.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
        #logger.addHandler(hdlr)
        #logger.setLevel(logging.INFO)

        self.log(0,"Initialising...")

        count = 0
        size = 0.0

        self.log(0, "Processing the orginal %s to the destination %s" % (self.original_folder, self.new_folder))

        for filename in glob.glob1(self.original_folder, "*.*"):
            srcfile = os.path.join(self.original_folder, filename)
            destfile = os.path.join(self.new_folder, filename)
            (base, ext) = os.path.splitext(srcfile)
            #self.log(0, "Checking file %s with extension %s" % (base, ext))

            if ext in self.validextensions  and os.stat(srcfile).st_mtime < move_date:
                if not os.path.isfile(destfile):
                    size = size + (os.path.getsize(srcfile) / (1024*1024.0))
                    filedate = time.ctime(os.stat(srcfile).st_mtime)
                    shutil.move(srcfile, destfile)

                    self.log(0,"Archived '" + filename + "', file date : %s" % filedate)
                    count = count + 1

        self.log(0,"Archived " + str(count) + " files, totalling " + str(round(size,2)) + "MB.")
        self.end(0)

if __name__ == '__main__':

    # Load the configuration
    #configvars = dailymotion.load_variables("video.archiver.cfg")
    #source_folder = configvars['source_folder'].rstrip()
    #destination_folder = configvars['destination_folder'].rstrip()


    argparser.add_argument("--source", required=True, help="The source folder full path")
    argparser.add_argument("--destination", required=True, help="The destination folder full path")
    args = argparser.parse_args()

    if not os.path.exists(args.source):
        exit("Please specify a valid source folder using the --source= parameter.")

    if not os.path.exists(args.destination):
        exit("Please specify a valid destination folder using the --destination= parameter.")

    source_folder = args.source
    destination_folder = args.destination

    # Start the archiver and archive files
    archiver = VideoArchiver(source_folder, destination_folder)
    archiver.process()
