import os.path
from ftplib import FTP, FTP_TLS

# Init
filename = 'Franck Lefillatre.mp4'
#filename = 'ubuntu-14.04.5-desktop-amd64.iso'
sizeWritten = 0

# Define a handle to print the percentage uploaded
def handle(block):
    sizeWritten += 1024 # this line fail because sizeWritten is not initialized.
    percentComplete = sizeWritten / totalSize
    print(str(percentComplete) + " percent complete")

class FtpUploadTracker:
    sizeWritten = 0
    totalSize = 0
    lastShownPercent = 0
    counter = 0

    def __init__(self, totalSize):
        self.totalSize = totalSize
        self.counter = 0

    def handle(self, block):
    	self.counter += 1
        self.sizeWritten += 1024
        #percentComplete = round((self.sizeWritten / self.totalSize) * 100)
        percentComplete = round((self.sizeWritten / float(self.totalSize)) * 100)
        

        if (self.lastShownPercent != percentComplete):
            self.lastShownPercent = percentComplete
            print("%d - %s percent complete (%d/%d)" % (self.counter, str(percentComplete), self.sizeWritten, self.totalSize))



ftp = FTP('dev.bright-softwares.com')
ftp.login("bob", "bob")
# ftps.prot_p()
#ftp.storlines("STOR %s" %('franck_lefillatre.mp4'), open('Franck Lefillatre.mp4'))

totalSize = os.path.getsize(filename)
print('Total file size : ' + str(round(totalSize / 1024 / 1024 ,1)) + ' Mb')
uploadTracker = FtpUploadTracker(int(totalSize))
ftp.storbinary("STOR %s" %(filename), open(filename, 'rb'), 1024, uploadTracker.handle)
ftp.close()