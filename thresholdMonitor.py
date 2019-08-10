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
    This module monitors certain thresholds and initiates an alerting if a
    threshold is violated.
    
    Written by Robert Penz <robert@penz.name>
"""

class ThresholdMonitor:
    _config = None
    _report = None
    _referenceValues = None
    _queryErrorCounter = None
    _thresholdCounters = None
    _firstcheck = None

    def __init__(self, config, report):
        self._config = config
        self._report = report
        self._referenceValues = {}
        self._queryErrorCounter = 0
        self._thresholdCounters = config.getThresholdCounters()
        self._firstcheck = True

    def check(self, values):
        """ gets the values the heatpump sent and checks them 
            if a threshold is violated it sends a mail
        """
        # reset error counter
        self._queryErrorCounter = 0
        
        # if its the first check don't report anything, we need a baseline
        if self._firstcheck:
            self._updateBaseline(values)
            self._firstcheck = False
            return
        
        # the actual checks
        for value in self._thresholdCounters:
            if values[value] < self._referenceValues[value]:
                # somehow the value got reseted to an lower value
                # maybe heatpump resetet or an error
                # report that and update the reference value
                self._report.counterDecreased(name = value, reference = self._referenceValues[value], actual = values[value])
                self._referenceValues[value] = values[value]
            elif values[value] > self._referenceValues[value]:
                # ok, counter got incremented, we report that
                self._report.counterIncreased(name = value, reference = self._referenceValues[value], actual = values[value])
                self._referenceValues[value] = values[value]
    
    def gotQueryError(self):
        """ increments the error counter and checks if
            a mail should be send
        """
        self._queryErrorCounter += 1
        if self._queryErrorCounter == self._config.getQueryErrorThreshold():
            # report an error - no other report will be send, until one
            # query worked and resetted the counter
            self._report.queryErrorThresholdExceeded()
    
    def _updateBaseline(self, values):
        """ this methode sets the internal base lines, so we know the
            the status at startup or at sending the last alert
        """
        for value in self._thresholdCounters:
            self._referenceValues[value] = values[value]
    

# Main program: parse command line and start processing
def main():
    import config_manager, report
    config = config_manager.ConfigManager("heatpumpMonitor.ini")
    aT = ThresholdMonitor(config, report.Report(config))
    aT.gotQueryError()
    aT.gotQueryError()
    aT.gotQueryError()
    aT.check({"booster_dhw": 100, "booster_heating": 200})
    aT.check({"booster_dhw": 101, "booster_heating": 200})
    aT.check({"booster_dhw": 100, "booster_heating": 200})
    
if __name__ == '__main__':
    main()
