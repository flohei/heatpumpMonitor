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
    This module renders the graphic for the data stored in the rrd database.
    
    Written by Robert Penz <robert@penz.name>
"""

import time
import os

from pyrrd.rrd import RRD, RRA, DS
from pyrrd.graph import DEF, CDEF, VDEF
from pyrrd.graph import LINE, AREA, GPRINT
from pyrrd.graph import ColorAttributes, Graph

# some constants - don't change them
hour = 60 * 60
day = 24 * hour
week = 7 * day
month = day * 30
quarter = month * 3
half = 365 * day / 2
year = 365 * day

times = {
         "3hours": {
                "time": 3*hour, 
                "step": 60 #seconds
                }, 
         "halfday": {
                "time": 12*hour, 
                "step": 60 #seconds
                }, 
         "day": {
                "time": day, 
                "step": 60 #seconds
                }, 
         "week": {
                "time": 7*day, 
                "step": 300 # 5 minutes
                }, 
         "month": {
                "time": 30*day, 
                "step": hour # 1 hour
                },
         "year": {
                "time": 365*day, 
                "step": 12*hour # 1 hour
                }
        }

# define how our graphs should look like

graphsDefinition = {"enduser_temperatures": {
                        "title": "Enduser temperatures", 
                        "verticalLabel": '"degree celsius"', 
                        "sources": {
                                    "flow_temp":{
                                            "title": "flow temperature", 
                                            "color": "#FFA902",
                                            "type": "line"}, 
                                    "return_temp":{
                                            "title": "return temperature", 
                                            "color": "#A31E00",
                                            "type": "line"},                                      
                                    "dhw_temp":{
                                            "title": "DHW temperature", 
                                            "color": "#FF2802",
                                            "type": "line"},                                      
                                    "inside_temp":{
                                            "title": "inside temperature", 
                                            "color": "#75DB15",
                                            "type": "area"},                                      
                                    "outside_temp":{
                                            "title": "outside temperature", 
                                            "color": "#025AFF",
                                            "type": "area"},                                      
                                    }
                        }, 
                    "humidity": {
                        "title": "Humidity", 
                        "verticalLabel": '"rel. humidity"', 
                        "sources": {
                                    "rel_humidity":{
                                            "title": "relative humidity", 
                                            "color": "#025AFF",
                                            "type": "area"}
                                    }
                        }, 
                    "fans": {
                        "title": "Fans", 
                        "verticalLabel": "percent", 
                        "sources": {
                                    "extr_speed_set":{
                                            "title": "extractor speed set", 
                                            "color": "#84FE19",
                                            "type": "line"}, 
                                    "vent_speed_set":{
                                            "title": "ventilator speed set", 
                                            "color": "#FF2802",
                                            "type": "line"}, 
                                    "extr_speed_actual":{
                                            "title": "extractor speed actual", 
                                            "color": "#D9FF02",
                                            "type": "line"}, 
                                    "vent_speed_actual":{
                                            "title": "ventilator speed actual", 
                                            "color": "#FFA902",
                                            "type": "line"}, 
                                    }
                        }, 
                    "internaltemps": {
                        "title": 'heat pump internal temperatures', 
                        "verticalLabel": '"degree celsius"', 
                        "sources": {
                                    "hot_gas_temp":{
                                            "title": "hot gas temperature", 
                                            "color": "#84FE19",
                                            "type": "line"}, 
                                    "evaporator_temp":{
                                            "title": "evaporator temperature", 
                                            "color": "#FF2802",
                                            "type": "line"}, 
                                    "condenser_temp":{
                                            "title": "condenser temperature", 
                                            "color": "#D9FF02",
                                            "type": "line"}, 
                                    "dew_point_temp":{
                                            "title": "dew point temperature", 
                                            "color": "#025AFF",
                                            "type": "line"}, 
                                    }
                        }
                    }

# I don't have following features of the heat pump so the values are always the same.
#        ("flow temperature HC2",        "flow_temp_hc2"), 
#        ("expelled air speed set",      "expel_speed_set"), 
#        ("expelled air speed actual",   "expel_speed_actual"), 

########################### no changes beyond here required ##############################

class Render:
    # our graph object
    _graphs = None
    _filename = None
    _outputPath = None

    def __init__(self, filename="heatpumpMonitor.rrd", outputPath = "."):
        if not os.path.isfile(filename):
            raise IOError, "Error: RRD file missing"
        self._filename = filename    
        self._outputPath = outputPath
        self._graphs = self._initialize()
    
    def _initialize(self):
        """ set up erything we need """

        # Let's configure some custom colors for the graph
        ca = ColorAttributes()
        ca.back = '#333333'
        ca.canvas = '#333333'
        ca.shadea = '#000000'
        ca.shadeb = '#111111'
        ca.mgrid = '#CCCCCC'
        ca.axis = '#FFFFFF'
        ca.frame = '#AAAAAA'
        ca.font = '#FFFFFF'
        ca.arrow = '#FFFFFF'

        # Let's set up the objects that will be added to the graphs
        result = []
        for graphName, graphData in graphsDefinition.items():
            tmp = []
            for sourceName, sourceData in graphData["sources"].items():
                tmp.append(DEF(rrdfile=self._filename, vname=sourceName, dsName=sourceName))
                if sourceData["type"] == "line":
                    tmp.append(LINE(value=sourceName, color=sourceData["color"], legend=sourceData["title"]))
                elif sourceData["type"] == "area":
                    tmp.append(AREA(value=sourceName, color=sourceData["color"], legend=sourceData["title"]))
                
            # Now that we've got everything set up, let's make a graph
            g = Graph('dummy.png', vertical_label=graphData["verticalLabel"], color=ca)
            g.data.extend(tmp)
            g.title = '"%s"' % graphData["title"]
            # create a new variable
            g.filenameBase = graphName
            result.append(g)
        return result

    def render(self):
        """ does the actual painting """
        # Iterate through the different resoltions for which we want to 
        # generate graphs.
        currentTime = int(time.time())
        for timeName, timeData in times.items():
            for g in self._graphs:
                # common stuff first
                g.start =  currentTime - timeData["time"]
                g.end = currentTime
                g.step  = timeData["step"]
                
                # First, the small graph
                g.filename = os.path.join(self._outputPath,"%s_%s_small.png" % (g.filenameBase, timeName))
                g.width = 400
                g.height = 100
                g.write(debug=False)
                
                # Then the big one
                g.filename = os.path.join(self._outputPath,"%s_%s_big.png" % (g.filenameBase, timeName))
                g.width = 800
                g.height = 400
                g.write()



# Main program: parse command line and start processing
def main():
    aR = Render()
    aR.render()

    
if __name__ == '__main__':
    main()
