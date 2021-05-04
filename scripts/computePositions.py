import pandas as pd
# from coordio import ICRS, Site
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, SkyCoord, get_moon
import astroplan
from astropy import units as u
import time
import numpy
from multiprocessing import Pool

"""
This script takes output from the roboscheduler (one file per night)
and computes the alt/az positions of the fields for each time point
as well as where the moon is and how bright it is...

makes a file per night in tidy format (and one mega file with everything)

documentation sucks, but maybe it can be a useful reference.

Also you don't have the raw files...
"""

tStart = time.time()

### read in csvs and join to get ra/decs for each field
rsFields = pd.read_csv("rsFields.csv")
fieldCenters = rsFields.groupby("fieldid").head().reset_index()
# drop everything but racen and deccen
fieldCenters = fieldCenters[["racen", "deccen", "fieldid", "cadence"]]

# print("cadence set", set(fieldCenters.cadence))

rsSchedule = pd.read_csv("sched.csv")

jointTableAll = rsSchedule.set_index("fieldID").join(fieldCenters.set_index("fieldid"))
# jointTable["fieldID"] = jointTable.index
jointTableAll = jointTableAll.reset_index()
jointTableAll.rename(columns={'index':'fieldID'}, inplace=True)
jointTableAll.sort_values(["mjdExpStart", "scheduled", "fieldID"], ascending=[True, False, True], ignore_index=True, inplace=True)



# jointTable = jointTable[jointTable.mjd <= 59305]

# print(len(rsSchedule), len(jointTable))
# print(jointTable)

############# get positions ###########

### site info
APO = EarthLocation.of_site("Apache Point Observatory")
# print("APO site", APO)

def doOneChunk(mjd):
    print("on mjd", mjd)
    jointTable = jointTableAll[jointTableAll.mjd == mjd].reset_index()
    jointTable.drop("index", axis="columns", inplace=True)
    allMJDs = jointTable.mjdExpStart.to_numpy()
    astropyTimes = Time(allMJDs, format='mjd', scale='tai')
    allRAs = jointTable.racen.to_numpy()
    allDecs = jointTable.deccen.to_numpy()

    astropyCoords = SkyCoord(
        ra = allRAs * u.deg, dec = allDecs * u.deg,
        frame='icrs', obstime=astropyTimes
    )

    # tstart = time.time()
    observedCoords = astropyCoords.transform_to(AltAz(location=APO))
    # print("took", time.time()-tstart, "for", len(observedCoords))

    jointTable["alt"] = observedCoords.alt.deg
    jointTable["az"] = observedCoords.az.deg
    jointTable["airmass"] = observedCoords.secz

    # calculate hour angle Meeus pg 94
    # note I'm not sure i've got hour angle right!!!!
    h = observedCoords.alt.rad  # altitude
    phi = APO.lat.rad # latitude
    # azimuth measured westward of south (azimuth for astropy is east of north 180 off)
    A = observedCoords.az.rad - numpy.pi
    A = A % 2*numpy.pi
    haRad = numpy.arctan2(numpy.sin(A), numpy.cos(A)*numpy.sin(phi) + numpy.tan(h)*numpy.cos(phi))
    haDeg = numpy.degrees(haRad)

    jointTable["haDeg"] = haDeg

    ### finally compute moon stuff
    # print('starting moon')
    moonCoords = get_moon(astropyTimes, location=APO)

    moonRA = moonCoords.ra.deg
    moonDec = moonCoords.dec.deg

    jointTable["moonRA"] = moonRA
    jointTable["moonDec"] = moonDec

    # get moon in AltAz
    moonObservedCoords = moonCoords.transform_to(AltAz(location=APO))
    jointTable["moonAlt"] = moonObservedCoords.alt.deg
    jointTable["moonAz"] = moonObservedCoords.az.deg

    # calculate moon separation
    moonSep = moonCoords.separation(observedCoords)
    jointTable["moonSep"] = moonSep.deg

    moonPhase = astroplan.moon.moon_illumination(astropyTimes)
    jointTable["moonPhase"] = moonPhase
    jointTable.to_csv("mjd-%i-sdss-fields.csv"%(mjd))
    return jointTable
# print("moon took", time.time()-tstart, "for", len(observedCoords))

# import pdb; pdb.set_trace()

# print(altRad)

mjds = list(set(jointTableAll.mjd))

mjds.sort()
p = Pool(11)
dfs = p.map(doOneChunk, mjds)
finalDF = pd.concat(dfs, ignore_index=True)
finalDF.sort_values(["mjdExpStart", "scheduled", "fieldID"], ascending=[True, False, True], ignore_index=True, inplace=True)
finalDF.reset_index()
finalDF.to_csv("all-sdss-fields.csv")
# import pdb; pdb.set_trace()

# jointTable.to_csv("sdss-fields.csv")

tend = time.time()
totalTime = (tend - tStart)/60
print("took %.2f mintues"%(totalTime))


# import pdb; pdb.set_trace()

# print(observedCoords)