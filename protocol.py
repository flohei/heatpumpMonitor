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
    This module is responsible for the communication with the LWZ heat pump.
    Currently it is only able to query the heat pump and can therefore not 
    write options. This is by design do not damage the LWZ.
    
    Written by Robert Penz <robert@penz.name>
"""

import serial
import struct
import sys
import time
import protocolVersions

# normally no need to change it
serialTimeout = 5

# protocol constants
STARTCOMMUNICATION = "\x02"
ESCAPE = "\x10"
BEGIN = "\x01\x00"
END = "\x03"
GETVERSION = "\xfd"

def convert2Number(s, fixedDecimals=1):
    """ converts various input values into float or int """
    if not len(s) in (1, 2):
        raise ValueError, "Error: currenty this function supports only 1 and 2 byte inputs"
    elif len(s) == 1:
        f = ">b"
    else:
        f = ">h"
    l = struct.unpack(f,s)[0]
    if fixedDecimals == 0:
        return l
    else:
        return l/10.0**fixedDecimals

def convert2DateTime(s, separator):
    """ converts the input into a string which looks like a time or date """
    if len(s) != 2:
        raise ValueError, "Error: only 2 byte inputs are supported"
    l = "%04d" % struct.unpack("<H", s)[0]
    return l[:2] + separator + l[2:]

def printHex(s):
    print "debug: ", 
    i = 0
    for t in s:
        if i % 4 == 0:
            print "| %d:" % i,  
        print "%02x" % ord(t),
        i += 1
    print "|"
    sys.stdout.flush()

def _calcChecksum(s):
    """ Internal function that calcuates the checksum """
    checksum = 1
    for i in xrange(0, len(s)):
        checksum += ord(s[i])
        checksum &= 0xFF
    return chr(checksum)

def verifyChecksum(s):
   """ verify if the provided string contains a valid checksum returns True if the checksum matches """
   if len(s) < 2:
       raise ValueError, "The provided string needs to be atleast 2 bytes long"
   return s[0] == _calcChecksum(s[1:])

def addChecksum(s):
    """ inserts a the beginning a checksum """
    if len(s) < 1:
        raise ValueError, "The provided string needs to be atleast 1 byte long"    
    return (_calcChecksum(s) + s)


class Protocol:
    # The device we talk to
    _serialDevice = None
    _debug = None
    
    # Protocol Versions object 
    _protocolVersions = None
    _version = None
    
    # The protocol definition the used version of the protocol 
    _config = None
    
    # The object which does the serial talking
    _ser = None

    def __init__(self, serialDevice="/dev/ttyS0", versionsConfigDirectory = "/usr/local/share/heatpump/protocolVersions", newStyleSerialCommunication = True,  debug=False):
        self._serialDevice = serialDevice
        self._debug = debug
        self._newStyleSerialCommunication = newStyleSerialCommunication
        
        # get everything we need for the version specific stuff
        self._protocolVersions = protocolVersions.ProtocolVersions(versionsConfigDirectory)
        self._version = self.versionQuery()
        print "Heatpump reports Version %s" % self._version
        sys.stdout.flush()
        self._config = self._protocolVersions.getConfig(self._version)
        print "Using protocol definition from %s (%s)" % (self._config["author"], self._config["comment"])
        sys.stdout.flush()


    def _establishConnection(self):
        """ opens the serial connection and makes a "ping" to check if the 
            heat pump is responding 
        """
        if self._ser:
            raise IOError, "Error: serial connection already open"
        
        # open the serial connection
        if self._newStyleSerialCommunication:
            # 57600, 8, N, 1
            self._ser = serial.Serial(self._serialDevice, timeout=serialTimeout, baudrate=57600)
        else:
            # old version
            self._ser = serial.Serial(self._serialDevice, timeout=serialTimeout) 

        # check if the heat pump is connected and responds
        self._ser.write(STARTCOMMUNICATION)
        s = self._ser.read(1)
        if s != ESCAPE:
            raise IOError, "Error: heat pump does not respond - is it connected?"


    def _closeConnection(self):
        """ just closes the connection """
        if self._ser:
            self._ser.close()
            self._ser = None
            # we wait 1 sec, as it should be avoided that the connection is opened to fast again
            time.sleep(1)
    
    def _get(self, queryName,  queryRequest,  queryResponseLength):
        """ internal method which does the real quering - provide it with a dict
            of the query protocol and it will handle the rest
        """
        if not self._ser:
            raise IOError, "Error: serial connection not open"
        # we try to start the communication 5 times, as sometimes some heatpump firmware versions
        # have problems replying which are gone after a reconnect
        success = False
        retry = 0
        maxRetries = 5
        while (not success and retry < maxRetries):
            self._ser.write(BEGIN + addChecksum(queryRequest) + ESCAPE + END)
            s = self._ser.read(2)
            if s == ESCAPE + STARTCOMMUNICATION:
                success = True
            else:
                retry += 1
                self._closeConnection()
                self._establishConnection()
        if not success:
            raise IOError, "Error: Tried the request %s five times but the heat pump did not anwser correctly." % queryName
        
        # ready to receive data
        self._ser.write(ESCAPE)
        
        # we read data until we get the END flag, but not if the END flag is not escaped
        s = ""
        escaping = False
        while 1:
            tmp = self._ser.read(1)
            if not tmp:
                raise IOError, "Error: data stream brocken during %s reponse" % queryName
        
            if len(s) < 2: # first 2 chars should be the header
                s += tmp
                if len(s) == 2 and s != BEGIN:
                    raise IOError, "Error: wrong response header for %s request" % queryName
            else:
                if escaping:
                    if tmp == END: # special handling
                        break # we just stop reading
                    elif tmp == ESCAPE: # just add the char as it got escaped
                        s += tmp
                        escaping = False
                    else:
                        raise IOError, "Error: some char (%02x) got escaped which should not in %s request" % (ord(tmp), queryName)                    
                elif tmp == ESCAPE: # this char is used for escaping
                    escaping = True # do add nothing
                else: # normal, just add the char
                    s += tmp

        # don't really know why, but it seems necessary for some versions
        if self._config and self._config["globalReplaceString"]:
            s = s.replace(self._config["globalReplaceString"][0], self._config["globalReplaceString"][1])
            
        # check the checksum and if the response matches the request
        s = s[len(BEGIN):]
        if len(s) - 2 != queryResponseLength: # 2 = the checksum and the response id.
            raise IOError,  "Error: the received %s response has an invalid length (%d instead of %d)" % (queryName, len(s) - 2, queryResponseLength)
        elif not verifyChecksum(s):
            raise IOError,  "Error: the received %s response has an invalid checksum" % queryName
        elif s[1] != queryRequest:
            raise IOError,  "Error: the received %s response has an other id (%02x) as the request " % (queryName, ord(s[1]))
        payload = s[2:]

        # all worked, now we need to reset the connection in a state we can talk again
        self._ser.write(ESCAPE + STARTCOMMUNICATION)
        s = self._ser.read(1)
        # some heat pumps don't answer sometimes, but as everything else works for these heat pumps , its ok and we ignore it
        if s and s != ESCAPE:
            printHex(s)
            raise IOError, "Error: could not be set again into receiving mode (%s)" % queryName
        
        # for debugging
        if self._debug:
            printHex(payload)
        
        return payload
    
    def _getVersion(self):
        """ extracts the version of the heat pump software """
        return str(convert2Number(self._get("getVersion", GETVERSION, 2), 2))
    
    def _getValues(self, queryData):
        """ extracts the values configured for this query """
        s = self._get(queryData["name"],  queryData["request"],  queryData["responseLength"])
        result = {}
        for entry in queryData["values"]:
            # diffent types need to be converted differently
            if entry["type"] == "fixedPoint":
                result[entry["name"]] =  convert2Number(s[entry["position"]:entry["position"] + entry["size"]], entry["fixedDecimals"])
            elif entry["type"] == "DateTime":
                result[entry["name"]] =  convert2DateTime(s[entry["position"]:entry["position"] + entry["size"]], entry["separator"])
        return result
    
    def versionQuery(self):
        """ the version query is seperated from the other as it is fixed and not queried every time """
        try:
            self._establishConnection()
            return self._getVersion()
        finally:
            self._closeConnection()
    
    def query(self):
        """ this method return you a dict with the retrieved values from the heat pump """
        result = {}
        try:
            self._establishConnection()
            for query in self._config["queries"]:
                result.update(self._getValues(query))
        finally:
            self._closeConnection()
        return result
        

# Main program: only for testing
def main():
    aP = Protocol(versionsConfigDirectory="protocolVersions/")
    #print aP._config
    print aP.query()


if __name__ == '__main__':
    main()
