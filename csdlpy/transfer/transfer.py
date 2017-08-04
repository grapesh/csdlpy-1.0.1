# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 09:59:49 2017

@author: Sergey.Vinogradov
"""
import os
import urllib2
import uuid
import ssl

#==============================================================================
def download (remote, local):
    """
    Downloads remote file (using urllib2) if it does not exist locally.
    """
    if not os.path.exists(local):
        print '[info]: downloading ', remote, ' as ', local
        f = urllib2.urlopen(remote)
        data = f.read()
        with open(local, "w") as code:
            code.write(data)
    else:
        print '[warn]: file ', local, ' exists, skipping.'

#==============================================================================
def refresh (remote, local):
    """
    Downloads remote file (using urllib2), overwrites local copy if exists.
    """
    if not os.path.exists(local):
        print '[info]: downloading ', remote, ' as ', local
    else:
        print '[info]: overwriting ', local, ' file with ', remote
    f = urllib2.urlopen(remote)
    data = f.read()
    with open(local, "w") as code:
        code.write(data)

#==============================================================================
def readlines (remote, tmpDir=None, tmpFile=None):
    """
    1. Downloads remote into temporary file
    2. Reads line by line
    3. Removes temporary file
    """
    
    if tmpFile is None:
        tmpFile  = str(uuid.uuid4()) + '.tmp' # Unique temporary name
    if tmpDir is not None:
        tmpFile = os.path.join(tmpDir, tmpFile)

    print '[info]: downloading ', remote, ' as temporary ', tmpFile

    f        = open( tmpFile, 'w' )
    response = urllib2.urlopen(remote)
    f.write ( response.read() )
    f.close ()
 
    lines  = open(tmpFile).readlines()
    os.remove( tmpFile )
        
    return lines

#==============================================================================
def readlines_ssl (remote, tmpDir=None, tmpFile=None):
    """
    Deals with expired SSL certificate issue.
    1. Downloads remote into temporary file
    2. Reads line by line
    3. Removes temporary file
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE 
 
    if tmpFile is None:
        tmpFile  = str(uuid.uuid4()) + '.tmp'
    if tmpDir is not None:
        tmpFile = os.path.join(tmpDir, tmpFile)

    print '[info]: downloading ', remote, ' as temporary ', tmpFile

    f        = open( tmpFile, 'w' )
    try:
        response = urllib2.urlopen(remote, context = ctx)
    except urllib2.URLError as e:
        print e.reason       
    f.write ( response.read() )
    f.close ()

    lines  = open(tmpFile).readlines()
    os.remove( tmpFile )

    return lines

#==============================================================================
def cleanup (tmpDir='.', tmpExt='.tmp'):
    """
    Removes files with extension tmpExt from the tmpDir.
    """
    files = os.listdir(tmpDir)
    for file in files:
        if file.endswith(tmpExt):
            os.remove(os.path.join(tmpDir,file))

    