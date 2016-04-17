
import sys
import os
import glob
import shutil
import time
import logging
from datetime import datetime, date, timedelta

# start editable vars #
current_script_file = os.path.realpath(__file__)
current_script_dir = os.path.abspath(os.path.join(current_script_file, os.pardir))
days_old = 28               # how old the files have to be before they are moved
original_folder = "/Users/sergio/Downloads"  # folder to move files from
new_folder = "/Users/sergio/Desktop"       # folder to move files to
logfile = "%s/videos_archiving.log" % (current_script_dir)      # log file to record what has happened
# end editable vars #

# start function definitions #
def log(level,msg,tofile=True):
    print msg

    if tofile == True:
        if level == 0:
            logger.info(msg)
        else:
            logger.error(msg)

def end(code):
    log(0,"End.")
    log(0,"-------------------------")

    sys.exit(code)
# end function definitions #


# start process #

move_date = date.today() - timedelta(days=days_old)
move_date = time.mktime(move_date.timetuple())
logger = logging.getLogger("cuarch")
hdlr = logging.FileHandler(logfile)
hdlr.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

log(0,"Initialising...")

count = 0
size = 0.0

for filename in glob.glob1(original_folder, "*.*"):
    srcfile = os.path.join(original_folder, filename)
    destfile = os.path.join(new_folder, filename)
    if os.stat(srcfile).st_mtime < move_date:
        if not os.path.isfile(destfile):
            size = size + (os.path.getsize(srcfile) / (1024*1024.0))
            #shutil.move(srcfile, destfile)

            log(0,"Archived '" + filename + "', file date : %s" % time.ctime(os.stat(srcfile).st_mtime))
            count = count + 1

log(0,"Archived " + str(count) + " files, totalling " + str(round(size,2)) + "MB.")
end(0)


