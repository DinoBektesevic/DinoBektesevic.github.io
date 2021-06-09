"""
The script takes the output files from the querySchedule.py script, organizes
them into csvs.
"""

import numpy
import pandas as pd
import glob
from astropy.time import Time

HoursPerDay = 24
MinutesPerHour = 60

_mjd = []
_fieldID = []
_scheduled = []
_mjdExptime = []
_mjdExpStart = []
_mjdNightStart = []
_mjdNightEnd = []


def parseLine(line):
    # print("line", line)
    line = line.strip()
    mjdStart, mjdEnd, mjdStr, exptime, fieldList = line.split(",", 4)
    fieldList = fieldList.strip()
    mjdFloat = float(mjdStr)
    mjdStartFloat = float(mjdStart)
    mjdEndFloat = float(mjdEnd)
    expFloat = float(exptime)
    fields = fieldList.strip("[").strip("]").split(",")
    fields = [int(x) for x in fields]
    return mjdStartFloat, mjdEndFloat, mjdFloat, expFloat, fields


def parseFiles(shortf, longf):
    # with open(shortf, "r") as f:
    #     slines = f.readlines()
    # with open(longf, "r") as f:
    #     llines = f.readlines()
    # print("on", shortf)

    for isSched, fname in zip([True, False], [shortf, longf]):
        with open(fname, "r") as f:
            lines = f.readlines()
        for line in lines:
            mjdStart, mjdEnd, mjd, exp, fields = parseLine(line)
            for field in fields:
                _mjd.append(int(numpy.floor(mjd)))
                _mjdNightStart.append(mjdStart)
                _mjdNightEnd.append(mjdEnd)
                _mjdExpStart.append(mjd)
                _fieldID.append(field) # sfields
                _scheduled.append(isSched)
                _mjdExptime.append(exp)


    # for sline, lline in zip(slines, llines):
    #     mjd, exp, sfield = parseLine(sline)
    #     assert len(sfield) == 1
    #     _mjd.append(int(numpy.floor(mjd)))
    #     _mjdExpStart.append(mjd)
    #     _fieldID.append(sfield[0]) # sfields
    #     _scheduled.append(True)
    #     _mjdExptime.append(exp)
    #     mjd2, exp2, fields = parseLine(lline)
    #     # assert(mjd==mjd2)
    #     # assert(exp2==exp)
    #     if sfield[0] in fields:
    #         print("removing field")
    #         fields.remove(sfield[0])  # don't double count the scheduled field
    #     for field in fields:
    #         _mjd.append(int(numpy.floor(mjd2)))
    #         _mjdExpStart.append(mjd2)
    #         _fieldID.append(field)
    #         _scheduled.append(False)
    #         _mjdExptime.append(exp2)

if __name__ == "__main__":
    longFiles = glob.glob("rawdata/*long.dat")
    shortFiles = glob.glob("rawdata/*short.dat")

    longFiles.sort()
    shortFiles.sort()

    for shortFile, longFile in zip(shortFiles, longFiles):
        parseFiles(shortFile, longFile)

    d = {}
    d["mjd"] = _mjd
    d["mjdNightStart"] = _mjdNightStart
    d["mjdNightEnd"] = _mjdNightEnd
    d["mjdExpStart"] = _mjdExpStart
    d["mjdExptime"] = _mjdExptime
    d["fieldID"] = _fieldID
    d["scheduled"] = _scheduled

    df = pd.DataFrame(d)

    print("df len", len(df))
    # look for repeated fieldids for the same mjdExpStart
    allStartTimes = set(df.mjdExpStart)
    for startTime in allStartTimes:
        schedID = df[(df.mjdExpStart == startTime) & (df.scheduled == True)]["fieldID"]
        if len(schedID) != 1:
            continue
        nonSchedID = df[(df.mjdExpStart == startTime) & (df.scheduled == False)]["fieldID"]
        dup = nonSchedID[nonSchedID == int(schedID)]
        if len(dup) == 0:
            continue
        df.drop(dup.index, inplace=True)
        # import pdb; pdb.set_trace()
        # df.drop(nonSchedID)

        # print("nonSchedID", len(nonSchedID))
    # print(allStartTimes)
    # print("df after", len(df))
    # for startTime in allStartTimes:
    #     schedID = df[(df.mjdExpStart == startTime) & (df.scheduled == True)]["fieldID"]
    #     if len(schedID) != 1:
    #         continue
    #     nonSchedID = df[(df.mjdExpStart == startTime) & (df.scheduled == False)]["fieldID"]
    #     dup = nonSchedID[nonSchedID == int(schedID)]
    #     assert len(dup) == 0

    df.to_csv("sched.csv", index=False)


