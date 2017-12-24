
import sys
import os
import glob
import shutil
import time
import Utils as utils
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
        self.logger = logging.getLogger("eepm_video_processor.VideoArchiver")

        self.validextensions = [".mp4", ".mov", ".mp3"]
        # end editable vars #
		# Edit a file from GitHub

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

	filedate = "unknown"
        for filename in glob.glob1(self.original_folder, "*.*"):
            #filedate = os.stat(srcfile).st_mtime
            self.log(0,"Processing : '" + filename + "', file date : %s" % filedate)
            srcfile = os.path.join(self.original_folder, filename)
            destfile = os.path.join(self.new_folder, filename)
            (base, ext) = os.path.splitext(srcfile)
            #self.log(0, "Checking file %s with extension %s" % (base, ext))

            if ext in self.validextensions  and os.stat(srcfile).st_mtime < move_date:
                self.log(0, "The file %s has the valid extension %s and is old enough." % (filename, ext))
                if not os.path.isfile(destfile):
                    size = size + (os.path.getsize(srcfile) / (1024*1024.0))
                    filedate = time.ctime(os.stat(srcfile).st_mtime)
                    shutil.move(srcfile, destfile)

                    self.log(0,"Archived '" + filename + "', file date : %s" % filedate)
                    count = count + 1
                else:
                    self.log(0, "The destination file already exist. Skipping ...")
            else:
                self.log(0, "The file '%s' extension is not in the valid extensions, or not old enough" % filename)

        self.log(0,"Archived " + str(count) + " files, totalling " + str(round(size,2)) + "MB.")
        self.end(0)

        return count, size

if __name__ == '__main__':

    errormessage = ""
    archive_result = ""
    archiver = None
    count = 0
    size = 0

    try:
        # Load the configuration
        configvars = utils.load_variables("eepm_videos_processor.cfg")
        #source_folder = configvars['archiver.sourcepath'].rstrip()
        #destination_folder = configvars['archiver.destination'].rstrip()

        rushs_source_folder = configvars['archiver.rushs.sourcepath'].rstrip()
        rushs_destination_folder = configvars['archiver.rushs.destination'].rstrip()

        youtube_source_folder = configvars['archiver.youtube.sourcepath'].rstrip()
        youtube_destination_folder = configvars['archiver.youtube.destination'].rstrip()

        tbn_source_folder = configvars['archiver.tbn.sourcepath'].rstrip()
        tbn_destination_folder = configvars['archiver.tbn.destination'].rstrip()

        emci_source_folder = configvars['archiver.emci.sourcepath'].rstrip()
        emci_destination_folder = configvars['archiver.emci.destination'].rstrip()

        audio_source_folder = configvars['archiver.audio.sourcepath'].rstrip()
        audio_destination_folder = configvars['archiver.audio.destination'].rstrip()

        # Archive the rushs videos
        archiver = VideoArchiver(rushs_source_folder, rushs_destination_folder)
        count_tmp, size_tmp = archiver.process()
        count += count_tmp
        size += size_tmp

        # Archive the youtube videos
        archiver = VideoArchiver(youtube_source_folder, youtube_destination_folder)
        count_tmp, size_tmp = archiver.process()
        count += count_tmp
        size += size_tmp

        # Archive tbn videos
        archiver = VideoArchiver(tbn_source_folder, tbn_destination_folder)
        count_tmp, size_tmp = archiver.process()
        count += count_tmp
        size += size_tmp

        # Archive emci videos
        archiver = VideoArchiver(emci_source_folder, emci_destination_folder)
        count_tmp, size_tmp = archiver.process()
        count += count_tmp
        size += size_tmp

        # Archive audio files
        archiver = VideoArchiver(audio_source_folder, audio_destination_folder)
        count_tmp, size_tmp = archiver.process()
        count += count_tmp
        size += size_tmp

    except Exception as e:
        errormessage = errormessage + " -> %s" % (str(e))
        #errormessage = "unknown"
        archiver.log(0, "Something bad happned. The error is %s. Thats all we know" % (errormessage))

    finally:

        utils.send_email('EEPB Video Automator <mailgun@mailgun.bright-softwares.com>',
            "video@monegliseaparis.fr",
            "Video archiver : videos processing report",
            "Hello, I have just archived some videos (" + str(count) + ") with size () and I wanted to notify you. Here are the possible errors : " + errormessage + " I am sending this email from the mac computer we use to export videos. I am an Automator application. Enjoy."
        )











