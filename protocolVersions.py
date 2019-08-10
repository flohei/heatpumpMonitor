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
    This module handles the version specific settings of the protocol to the heat
    pump. It loads them from the ini files and provides an interface for the
    protocol.py module.
    
    Written by Robert Penz <robert@penz.name>
"""

from ConfigParser import *
import os

class ProtocolVersions:
    _config = None
    _versionsConfigDirectory = None
    def __init__(self, versionsConfigDirectory):
        self._versionsConfigDirectory = versionsConfigDirectory
        self._config = self.parseAllConfigs()
        
    
    def getConfig(self, version):
        """ returns the config specific for the request heat pumpt software version """
        try:
            return self._config[version]
        except:
            raise ValueError, "No configuration available for this software version of the heat pump."
    
    def parseAllConfigs(self):
        """ searches through the directory and adds eachs version config to the big config """
        result = {}
        for filename in os.listdir(self._versionsConfigDirectory):
            if os.path.splitext(filename)[1].lower() == ".ini":
                versions, config = self.parseConfig(os.path.join(self._versionsConfigDirectory, filename))
                for version in versions:
                    result[version] = config
        return result

    def parseConfig(self, filename):
        """ parses the config into our internal format, not much error handling is done
            at this point as these files should be only created by "experts" ;-)
        """
        config = {}
        
        p = ConfigParser()
        p.read(filename)
        
        # global section stuff
        versions = p.get("Global", "versions").strip().split()
        config["author"] = p.get("Global", "author")
        config["comment"] = p.get("Global", "comment")
        
        # later this can be extended for multible replaces
        tmp = p.get("Global", "globalReplaceString").strip().decode("string-escape").split()
        if not tmp:
            config["globalReplaceString"] = None
        else:
            config["globalReplaceString"] = tmp
        
        # now jump to the query specific settings
        queries = []
        for queryName in p.get("Global", "queries").strip().split():
            query = {"name": queryName}
            query["comment"] = p.get(queryName, "comment")
            query["request"] = p.get(queryName, "request").decode("string-escape")
            query["responseLength"] = p.getint(queryName, "responseLength")
            
            # now the value part in the correct order
            tmp = p.items(queryName)
            tmp.sort()
            vs = []
            for name, value in tmp:
                if not name.startswith("value"):
                    continue
                v = value.strip().split()
                if v[2].lower() == "fixedpoint":
                    vs.append({"name": v[0], "position": int(v[1]), "type": "fixedPoint", "size": int(v[3]), "fixedDecimals": int(v[4])})
                elif v[2].lower() == "datetime":
                    vs.append({"name": v[0], "position": int(v[1]), "type": "DateTime", "size": int(v[3]), "separator": v[4]})
            query["values"] = vs
            queries.append(query)
        config["queries"] = queries
        return versions, config
        

# Main program: only for testing
def main():
    aP = ProtocolVersions("protocolVersions/")
    print aP._config


if __name__ == '__main__':
    main()
