#!/usr/bin/python
#

############################
### IMPORT MODULES START ###
############################
import sys, re, subprocess, os, getopt, time, pprint, signal, base64, cookielib, urllib2, urllib
from xml.dom import minidom
from operator import itemgetter
try:
    # Python v2
    from urllib2 import urlopen
except ImportError:
    # Python v3
    from urllib.request import urlopen

# Login URLs
citrix_login_url = 'https://www.citrix.com/login/bridge?url=https%3A%2F%2Fsupport.citrix.com%2Farticle%2FCTX219378'
citrix_err_url = 'https://www.citrix.com/login?url=https%3A%2F%2Fsupport.citrix.com%2Farticle%2FCTX219378&err=y'
citrix_authentication_url = 'https://identity.citrix.com/Utility/STS/Sign-In'
# Login credentials
cuser = ''
cpass = ''

###############################
### INITIAL FUNCTIONS START ###
###############################
### Capture Ctrl+C Presses
def signal_handler(signal, frame):
    print("Quitting.\n")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def login():
    # Store the cookies and create an opener that will hold them
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    # Add our headers
    opener.addheaders = [('User-agent', 'XenPatch')]

    # Install our opener (note that this changes the global opener to the one
    # we just made, but you can also just call opener.open() if you want)
    urllib2.install_opener(opener)

    # Input parameters we are going to send
    payload = {
      'returnURL'  : citrix_login_url,
      'errorURL'   : citrix_err_url,
      'persistent' : '1',
      'username'   : cuser,
      'password'   : cpass
      }

    # Use urllib to encode the payload
    data = urllib.urlencode(payload)

    # Build our Request object (supplying 'data' makes it a POST)
    req = urllib2.Request(citrix_authentication_url, data)
    try:
        u = urllib2.urlopen(req)
	contents = u.read()
    except Exception, err:
        print("...ERR: Failed to Login!")
        print("Error: " + str(err))
        sys.exit(3)

def download_patch(patch_url):
    url = patch_url
    file_name = url.split('/')[-1]
    print("")
    print("Downloading: " + str(file_name))
    try:
        u = urlopen(url)
    except Exception, err:
        print("...ERR: Failed to Download Patch!")
        print("Error: " + str(err))
        sys.exit(3)
        
    try:
        f = open(file_name, 'wb')
    except IOError:
        print("Failed to open/write to " + file_name)
        sys.exit(2)

    meta = u.info()
    try:
        file_size = int(meta.getheaders("Content-Length")[0])
        size_ok = True
    except IndexError, err:
        print("...WARN: Failed to get download size from: %s" % patch_url)
        print("         Will attempt to continue download, with unknown file size")
        time.sleep(4)
	###############
        size_ok = False

    # Check available disk space
    s = os.statvfs('.')
    freebytes = s.f_bsize * s.f_bavail
    if size_ok == False:
        doublesize = 2048
        file_size = 1
    else:
        doublesize = file_size * 2
    if long(doublesize) > long(freebytes):
        print(str("Insufficient storage space for Patch ") + str(file_name))
        print(str("Please free up some space, and run the patcher again."))
        print("")
        print(str("Minimum space required: ") + str(doublesize))
        sys.exit(20)

    print "Download Size: %s Bytes" % (file_size)
        
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
        if size_ok == False:
             status = r"%10d" % (file_size_dl)
        else:
             status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,
    f.close()
    if not os.path.isfile(file_name):
        print("\nERROR: File download for " + str(file_name) + " unsuccessful.")
        sys.exit(15)
    return file_name


patch_url = 'https://support.citrix.com/supportkc/filedownload?uri=/filedownload/CTX219499/XS65ESP1046.zip'
login();
download_patch(patch_url);



