#!/usr/bin/env python
# -*- coding: utf-8 -*-

#***************************************************************************
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 3 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#***************************************************************************

"""
    This module executes any custom script in a seperate thread. This way
    it does not block the polling of the heat pump. 
    
    Written by Robert Penz <robert@penz.name>
"""

import sys
import threading
import subprocess

class ThreadedExec(threading.Thread):
    _cmd = None
    
    def __init__(self, cmd):
        threading.Thread.__init__(self)
        self._cmd = cmd
    
    def run(self):
        process = subprocess.Popen(self._cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        for line in process.stdout.read().splitlines():
            # currently only loging 
            print "external:", line.rstrip("\n")
        sys.stdout.flush()

        process.stdin.close()
        errorCode = process.wait()
        if errorCode != 0:
            print "Error: Return code was %d!" % errorCode
   

# Main program: parse command line and start processing
def main():
    t = ThreadedExec("ls -la")
    t.start()
    print "started"
    t.join()
    print "ended"
    
if __name__ == '__main__':
    main()
