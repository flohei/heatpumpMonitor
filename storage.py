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
    This module is responsible for storing the data from the heat pump in a
    round robin database (rrd).
    
    Written by Robert Penz <robert@penz.name>
"""

import time
import os
from pyrrd.rrd import RRD, RRA, DS

step = 60

# rrd allows only up to 19 chars
dataSources = ( #1234567890123456789
                "flow_temp", 
                "return_temp", 
                "hot_gas_temp", 
                "dhw_temp", 
                "flow_temp_hc2", 
                "inside_temp", 
                "evaporator_temp", 
                "condenser_temp", 
                "extr_speed_set", 
                "vent_speed_set", 
                "expel_speed_set", 
                "extr_speed_actual", 
                "vent_speed_actual", 
                "expel_speed_actual", 
                "outside_temp", 
                "rel_humidity", 
                "dew_point_temp"
            )


class Storage:
    # our storage object
    _rrd = None

    def __init__(self, filename="heatpumpMonitor.rrd"):
        if not os.path.isfile(filename):
            self._rrd = self._createRRD(filename)
        else:
            self._rrd = RRD(filename)

    def _createRRD(self, filename):
        """ create an rrd file which fits our requirements """

        # Let's setup some data sources for our RRD
        dss = []
        for source in dataSources:
            dss.append(DS(dsName=source, dsType='GAUGE', heartbeat=900))

        # An now let's setup how our RRD will archive the data
        rras = []
        # 1 days-worth of one-minute samples --> 60/1 * 24
        rra1 = RRA(cf='AVERAGE', xff=0, steps=1, rows=1440) 
        # 7 days-worth of five-minute samples --> 60/5 * 24 * 7
        rra2 = RRA(cf='AVERAGE', xff=0, steps=5, rows=2016)
        # 30 days-worth of one hour samples --> 60/60 * 24 * 30
        rra3 = RRA(cf='AVERAGE', xff=0, steps=60, rows=720)
        # 1 year-worth of half day samples --> 60/60 * 24/12 * 365
        rra4 = RRA(cf='AVERAGE', xff=0, steps=720, rows=730)
        rras.extend([rra1, rra2, rra3, rra4])

        # With those setup, we can now created the RRD
        myRRD = RRD(filename, step=step, ds=dss, rra=rras, start=int(time.time()))
        myRRD.create(debug=False)
        return myRRD

    def add(self, aDict):
        """ adds the provided values to the rrd database with the current datetime """
        # we need to put the dict an correct line
        tmp = []
        for source in dataSources:
            tmp.append(aDict.get(source) or "U")
        self._rrd.bufferValue(int(time.time()), *tmp)
        self._rrd.update(debug=False)


# Main program: parse command line and start processing
def main():
    aS = Storage()
    tmp = {'expelled air speed actual': 0, 'return temperature': 24.600000000000001, 'relative humidity': 26.399999999999999,
           'condenser temperature': 24.5, 'flow temperature': 25.800000000000001, 'extractor speed actual': 28,
           'evaporator temperature': 19.5, 'DHW temperature': 46.5, 'inside temperature': 22.600000000000001,
           'ventilator speed set': 35.0, 'extractor speed set': 35.0, 'hot gas temperature': 24.899999999999999,
           'flow temperature HC2': -60.0, 'expelled air speed set': 0.0, 'ventilator speed actual': 28,
           'softwareVersion': 4.3799999999999999, 'dew point temperature': 0.0, 'outside temperature': 5.0999999999999996}
    aS.add(tmp)
    print aS._rrd.info()

    
if __name__ == '__main__':
    main()
