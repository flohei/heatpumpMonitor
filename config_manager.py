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
    this module handles the config stuff and presents an easy interface for the
    other classes
    
    Written by Robert Penz <robert@penz.name>
"""

from ConfigParser import *
import os
import sys

defaultConfigFile = "/etc/heatpumpMonitor.ini"

class ConfigManager:
    _config = None
    _configFile = None
    def __init__(self, configFile = None):
        # this is needed as the caller can provide None as parameter
        if not configFile:
            configFile = defaultConfigFile

        if not os.path.isfile(configFile):
            sys.stdout = sys.stderr
            print "Error: Cannot find config file %r" % configFile
            sys.exit(2)
 
        self._config = SafeConfigParser()
        self._config.read(configFile)
        self._configFile = configFile

    def getConfigFile(self):
        return self._configFile
        
    # Global
    def getLogFile(self):
        return self._config.get("Global", "logFile")

    def getPidFile(self):
        return self._config.get("Global", "pidFile")
    
    # Storage
    def getDatabaseFile(self):
        return self._config.get("Storage", "databaseFile")
        
    # Mail
    def getSendMails(self):
        return self._config.getboolean("Mail", "sendMails")

    def getSmtpHost(self):
        return self._config.get("Mail", "smtpHost")

    def getSmtpUseTLS(self):
        return self._config.getboolean("Mail", "smtpUseTLS")

    def getSmtpPort(self):
        return self._config.getint("Mail", "smtpPort")

    def getSmtpAuthUser(self):
        return self._config.get("Mail", "smtpAuthUser")

    def getSmtpAuthPass(self):
        return self._config.get("Mail", "smtpAuthPass")

    def getFromAddress(self):
        return self._config.get("Mail", "fromAddress")

    def getToAddresses(self):
        return self._config.get("Mail", "toAddresses").strip().split()

    # Reports
    def getQueryErrorThresholdExceededSubject(self):
        return self._config.get("Reports", "queryErrorThresholdExceededSubject", raw=True)
        
    def getQueryErrorThresholdExceededBody(self):
        return self._config.get("Reports", "queryErrorThresholdExceededBody", raw=True)

    def getCounterDecreasedSubject(self):
        return self._config.get("Reports", "counterDecreasedSubject", raw=True)
        
    def getCounterDecreasedBody(self):
        return self._config.get("Reports", "counterDecreasedBody", raw=True)

    def getCounterIncreasedSubject(self):
        return self._config.get("Reports", "counterIncreasedSubject", raw=True)
        
    def getCounterIncreasedBody(self):
        return self._config.get("Reports", "counterIncreasedBody", raw=True)


    # Protocol
    def getSerialDevice(self):
        return self._config.get("Protocol", "serialDevice")
    
    def getNewStyleSerialCommunication(self):
        return self._config.getboolean("Protocol", "newStyleSerialCommunication")
    
    def getProtocolVersionsDirectory(self):
        return self._config.get("Protocol", "protocolVersionsDirectory")
        
    # Render
    def getRenderOutputPath(self):
        return self._config.get("Render", "renderOutputPath")
    
    def getRenderInterval(self):
        return self._config.getint("Render", "renderInterval")
    
    # Copy
    def getCopyCommand(self):
        return self._config.get("Copy", "copyCommand")
    
    def getCopyInterval(self):
        return self._config.getint("Copy", "copyInterval")    

    # Threshold
    def getThresholdCounters(self):
        return self._config.get("Threshold", "thresholdCounters").strip().split()  
    
    def getQueryErrorThreshold(self):
        return self._config.getint("Threshold", "queryErrorThreshold")  
        
    
# Main program: parse command line and start processing
def main():
    myConfigManager = ConfigManager("heatpumpMonitor.ini")
    print myConfigManager.getCopyCommand()

    
if __name__ == '__main__':
    main()
