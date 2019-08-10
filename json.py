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
    This module is responsible for writting the json file which is used on the homepage.
    
    Written by Robert Penz <robert@penz.name>
"""

import time

class Json:
    _filename = None

    def __init__(self, filename="actual_values.json"):
        self._filename = filename
        
    def write(self, values):
        # generate actual_values.html with values
        html = '".id":".value"'
        degC = '&degC'
        f = open(self._filename,"w")
        f.write('{')
        tmpHtml = html.replace(".value", time.strftime("%H:%M %d.%m.%y", time.localtime()));
        f.write(tmpHtml.replace(".id","time") + ',')
        tmpHtml = html.replace(".id","dhw_temp")
        f.write(tmpHtml.replace(".value",str(values.get('dhw_temp')) + degC) + ',')
        tmpHtml = html.replace(".id","inside_temp")
        f.write(tmpHtml.replace(".value",str(values.get('inside_temp')) + degC) + ',')
        tmpHtml = html.replace(".id","outside_temp")
        f.write(tmpHtml.replace(".value",str(values.get('outside_temp')) + degC) + ',')
        tmpHtml = html.replace(".id","flow_temp")
        f.write(tmpHtml.replace(".value",str(values.get('flow_temp')) + degC) + ',')
        tmpHtml = html.replace(".id","return_temp")
        f.write(tmpHtml.replace(".value",str(values.get('return_temp')) + degC) + ',')
        tmpHtml = html.replace(".id","compressor_heating")
        f.write(tmpHtml.replace(".value",str(values.get('compressor_heating')) + "") + ',')
        tmpHtml = html.replace(".id","compressor_dhw")
        f.write(tmpHtml.replace(".value",str(values.get('compressor_dhw')) + ""))
        f.write('}')
        f.close()


# Main program: parse command line and start processing
def main():
    aJ = Json()
    tmp = {'expelled air speed actual': 0, 'return temperature': 24.600000000000001, 'relative humidity': 26.399999999999999,
           'condenser temperature': 24.5, 'flow temperature': 25.800000000000001, 'extractor speed actual': 28,
           'evaporator temperature': 19.5, 'DHW temperature': 46.5, 'inside temperature': 22.600000000000001,
           'ventilator speed set': 35.0, 'extractor speed set': 35.0, 'hot gas temperature': 24.899999999999999,
           'flow temperature HC2': -60.0, 'expelled air speed set': 0.0, 'ventilator speed actual': 28,
           'softwareVersion': 4.3799999999999999, 'dew point temperature': 0.0, 'outside temperature': 5.0999999999999996}
    aJ.write(tmp)

    
if __name__ == '__main__':
    main()
