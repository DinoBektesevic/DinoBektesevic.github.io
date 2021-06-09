import pandas as pd
# from coordio import ICRS, Site
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, SkyCoord, get_moon
import astroplan
from astropy import units as u
import time
import numpy
from multiprocessing import Pool

APO = EarthLocation.of_site("Apache Point Observatory")

mjds = 59418

brightStarsDF = pd.read_csv('bright_stars.csv')
brightStarsDF = brightStarsDF[brightStarsDF.Vmag < 4.5]
brightStarsCoords = SkyCoord(l=brightStarsDF['GLON']*u.deg, b=brightStarsDF['GLAT']*u.deg, frame='galactic')

print(len(brightStarsCoords))


def computePositions(ra, dec, objName, objType, magnitude, astropyTimes, timeSteps):
    astropyCoords = SkyCoord(
        ra = ra * u.deg, dec = dec * u.deg,
        frame='icrs', obstime=astropyTimes
    )

    # tstart = time.time()
    observedCoords = astropyCoords.transform_to(AltAz(location=APO))
    # print("took", time.time()-tstart, "for", len(observedCoords))

    _alt = list(observedCoords.alt.deg)
    _az = list(observedCoords.az.deg)
    _airmass = list(observedCoords.secz)

    moonCoords = get_moon(astropyTimes, location=APO)

    _moonRA = list(moonCoords.ra.deg)
    _moonDec = list(moonCoords.dec.deg)

    moonObservedCoords = moonCoords.transform_to(AltAz(location=APO))

    _moonSep = moonCoords.separation(observedCoords)
    _moonSep = list(_moonSep.deg)

    _moonPhase = astroplan.moon.moon_illumination(astropyTimes)
    _moonPhase = list(_moonPhase)

    _moonAlt = list(moonObservedCoords.alt.deg)
    _moonAz = list(moonObservedCoords.az.deg)
    # print("moonalt", _moonAlt)

    nItems = len(_alt)

    d = {}

    d["alt"] = _alt
    d["az"] = _az
    d["airmass"] = _airmass
    d["moonRA"] = _moonRA
    d["moonDec"] = _moonDec
    d["moonAlt"] = _moonAlt
    d["moonAz"] = _moonAz
    d["moonSep"] = _moonSep
    d["moonPhase"] = _moonPhase
    d["fieldID"] = [objName] * nItems
    d["objType"] = [objType] * nItems
    d["magnitude"] = [magnitude] * nItems
    d["mjdExpStart"] = list(timeSteps)
    d["risen"] = list(observedCoords.alt.deg > 0)
    d["scheduled"] = [False]*nItems
    d["observable"] = list(observedCoords.secz < 1.5)
    return pd.DataFrame(d)


def expandSimple(df, mjd):

    timeSteps = numpy.sort(numpy.array(list(set(df.mjdExpStart))))
    astropyTimes = Time(timeSteps, format='mjd', scale='tai')

    # at each timestep calculate the alt/az of stars
    goodIndices = []
    for t in astropyTimes:
        observedCoords = brightStarsCoords.transform_to(AltAz(location=APO, obstime=t))
        _keep = observedCoords.alt.deg > 0
        goodIndices.append(_keep)
        # print(goodInds)

    goodIndices = numpy.any(goodIndices, axis=0)
    _brightStarsDF = brightStarsDF[goodIndices]
    _brightStarsCoords = brightStarsCoords[goodIndices]
    raDecStars = brightStarsCoords.transform_to("icrs")

    # get unique fields
    fields = df.groupby("fieldID").first().reset_index()
    # fields.drop("Unnamed: 0", axis="columns", inplace=True)

    ########### next dataframe to build
    # fieldID = []
    # mjdExpStart = []
    # racen = []
    # ceccen = []
    # alt = []
    # az = []
    # airmass = []
    # moonRA = []
    # moonDec = []
    # moonAlt = []
    # moonAz = []
    # moonSep = []
    # moonPhase = []
    # objType = []
    # magnitude = []

    dfs = []
    for ind, field in fields.iterrows():
        dfs.append(computePositions(field.racen, field.deccen, str(field.fieldID), "sdss field", -999, astropyTimes, timeSteps))


    for (ind, bs), coord in zip(brightStarsDF.iterrows(), raDecStars):
        dfs.append(computePositions(coord.ra.deg, coord.dec.deg, bs.DM, "bright star", bs.Vmag, astropyTimes, timeSteps))

    jointDF = pd.concat(dfs)
    # import pdb; pdb.set_trace()
    print("scheduled before", numpy.sum(jointDF.scheduled))

    scheduled = df[df.scheduled==True]
    for ind, row in scheduled.iterrows():
        ii = (jointDF.fieldID == str(row.fieldID)) & (jointDF.mjdExpStart == row.mjdExpStart)
        jointDF["scheduled"][ii] = True
    # lastly find which were originally scheduled

    jointDF.to_csv("testDir/mjd-%i-sdss-simple-expanded.csv"%mjd)
# print("scheduled after", numpy.sum(jointDF.scheduled))

if __name__ == "__main__":
    mjds = 59418
    df = pd.read_csv("mjd-%i-sdss-simple.csv"%mjds)
    expandSimple(df)
# print(df)
