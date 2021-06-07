"""This script generates data for the Calendar visualization.
"""


import glob
import pandas as pd
from astropy.time import Time
import numpy
import time
import matplotlib.pyplot as plt
import seaborn as sns


# one file per mjd
allFiles = glob.glob("testDir/*priority.csv")

mjd = []
moonPhase = []
moonHours = []
obsHours = []
darkPercent = []
brightPercent = []
monthName = []
monthInt = []
year = []
dayOfYear = []
dayOfMonth = []
nFields = []
dateStr = []

tstart = time.time()

allFiles.sort()

for f in allFiles:
    df = pd.read_csv(f, index_col=0)

    # discover the mjd
    _mjd = int(numpy.floor(df["mjdExpStart"].to_numpy()[0]))

    dt = Time(_mjd, format="mjd").datetime
    dateStr.append(dt.isoformat())

    mjd.append(_mjd)
    year.append(dt.year)
    monthInt.append(dt.month)
    dayOfMonth.append(dt.day)
    monthName.append(dt.strftime("%B"))
    dayOfYear.append(dt.timetuple().tm_yday)

    # get only sdss fields
    fieldsDF = df[df.objType == "sdss field"]
    nFields.append(len(set(fieldsDF["fieldID"])))

    # use the mean moon phase as the moon phase for this mjd
    moonPhase.append(numpy.mean(df["moonPhase"]))

    # find the timestep between mjds
    mjdSlots = numpy.array(list(set(df["mjdExpStart"].to_numpy())))
    mjdSlots.sort()
    # this should be something like 8 minutes
    mjdHoursBin = numpy.mean(numpy.diff(mjdSlots))*24  # hours

    # compute the difference in hourse between the first exposure
    # and the last exposure (might be off by 8 minutes but whatever)
    _obsHours = (mjdSlots[-1]-mjdSlots[0])*24
    obsHours.append(_obsHours) # total number of observable hours




    # figure out when the moons up
    moonUp = df[df.moonAlt > 0]
    moonUp = moonUp.groupby("mjdExpStart").mean()
    # number of timeslots the moon is up for multiplied by duration of time slot
    _moonHours = len(moonUp) * mjdHoursBin
    moonHours.append(_moonHours)
    _brightPercent = _moonHours / obsHours
    brightPercent.append(_brightPercent)
    darkPercent.append(1-_brightPercent)

    # print(nFields)
tend = time.time()
print("took", (tend-tstart)/60, "minutes")

calDF = {}
calDF["mjd"] = mjd
calDF["moonPhase"] = moonPhase
calDF["moonHours"] = moonHours
calDF["obsHours"] = obsHours
calDF["darkPercent"] = darkPercent
calDF["brightPercent"] = brightPercent
calDF["monthName"] = monthName
calDF["monthInt"] = monthInt
calDF["year"] = year
calDF["dayOfYear"] = dayOfYear
calDF["dayOfMonth"] = dayOfMonth
calDF["nFields"] = nFields
calDF["dateStr"] = dateStr


import pdb; pdb.set_trace()
calDF.to_json("fieldCalendar.json", orient="records")
calDF.to_csv("fieldCalendar.csv")


# import pdb; pdb.set_trace()