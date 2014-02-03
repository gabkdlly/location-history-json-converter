#!/usr/bin/env python

# This script is under revision control on github.
# https://github.com/gabkdlly/
# Look under the repository on-the-clock .
# I don't know enough about copyright to know be able to say what licence this
# script should have, since not all the code is my own.
# See the repository on the web for history and legal notices.

from __future__ import division

import sys
import json
import math
from argparse import ArgumentParser
from datetime import datetime
from calendar import timegm
from dateutil.relativedelta import relativedelta


def main(argv):
    arg_parser = ArgumentParser()
    arg_parser.add_argument("input", help="Input File (JSON)")
    args = arg_parser.parse_args()
    try:
        json_data = open(args.input).read()
    except:
        print("Error opening input file")
        return

    try:
        data = json.loads(json_data)
    except:
        print("Error decoding json")
        return

    if "locations" in data and len(data["locations"]) > 0:
        try:
            pass #f_out = open(args.output, "w")
        except:
            print("Error creating output file for writing")
            return

        items = data["locations"]
        years = [2014]
        months = [1]
        for month in [ [y,m] for y in years for m in months ]:
            traverseData(items,month)

    else:
        print("No data found in json")
        return

# Run the actual iteration
def traverseData(items, month):
    # This is where all the fun starts !!
    runningTotal = 0
    tolerance = 0.2
    breaks = 60*60*1000
    startTime = 0
    stopTime = 0
    isCurrentlyAtWork = False
    alreadyTookBreaksToday = False
    worklat = 525258333 / 10000000
    worklon = 135310000 / 10000000
    beginningOfMonth = datetime(month[0],month[1],1)
    beginningOfMonth = timegm(beginningOfMonth.utctimetuple())
    beginningOfMonth *= 1000
    endOfMonth = datetime(month[0],month[1],1)
    endOfMonth = endOfMonth + relativedelta(months=1)
    endOfMonth = timegm(endOfMonth.utctimetuple())
    endOfMonth *= 1000
    lastTimeTookBreaks = 0
    s = ""
    for item in items:
        t = int(item["timestampMs"])
        if not (beginningOfMonth < t < endOfMonth ):
            continue
        lat = int(item["latitudeE7"])
        lat /= 10000000
        lon = int(item["longitudeE7"])
        lon /= 10000000
        close = getDistanceFromLatLonInKm(worklat,worklon,lat,lon) \
                < tolerance
        alreadyTookBreaksToday = alreadyTookBreaksToday and \
                        (t-lastTimeTookBreaks)<(18*60*60*1000)
        if ( not isCurrentlyAtWork ) and close:
            isCurrentlyAtWork = True
            startTime = t
            s += "Ich habe um  " 
            s += datetime.fromtimestamp(int(round(t/1000))).strftime('%Y-%m-%d %H:%M') 
            s += "  aufgehoert zu arbeiten.\n"
        elif isCurrentlyAtWork and close:
            pass
        elif ( not isCurrentlyAtWork ) and ( not close ):
            pass
        elif isCurrentlyAtWork and ( not close ):
            isCurrentlyAtWork = False
            stopTime = t
            s += "Ich fing um  " 
            s += datetime.fromtimestamp(int(round(t/1000))).strftime('%Y-%m-%d %H:%M') 
            s += "  an zu arbeiten.\n"
            runningTotal += (stopTime - startTime)
            if not alreadyTookBreaksToday:
                runningTotal += breaks
                alreadyTookBreaksToday = True
                lastTimeTookBreaks = t
    #f_out.close()
    #print(str(month[0])+'-'+str(month[1]))
    s += "Insgesamt habe ich  " + str( (-runningTotal)/(1000*3600) )
    s += "  Stunden gearbeitet.\n"
    print(s)

# Haversine formula
def getDistanceFromLatLonInKm(lat1,lon1,lat2,lon2):
    R = 6371 # Radius of the earth in km
    dlat = deg2rad(lat2-lat1)
    dlon = deg2rad(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + \
    math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * \
    math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c # Distance in km
    return d


def deg2rad(deg):
    return deg * (math.pi/180)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
