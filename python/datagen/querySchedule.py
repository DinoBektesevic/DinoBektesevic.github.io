"""This script runs on the sdss5 server at APO.

It grabs scheduled and optional fields for a year beginning April 2021.
"""


import sys
import argparse
import os

from sdssdb.peewee.sdss5db import opsdb, targetdb
if not targetdb.database.connected:
    print("!! CONFIG !!", opsdb.database._config)

import roboscheduler.scheduler


def runScheduler(mjd, returnAll):
    scheduler = roboscheduler.scheduler.Scheduler(observatory="apo", airmass_limit=1.5)
    scheduler.initdb(designbase="test-newfield-hack", fromFits=False)
    scheduler.fields.fromdb

    mjd_evening_twilight = scheduler.evening_twilight(mjd)
    mjd_morning_twilight = scheduler.morning_twilight(mjd)

    exp_nom = 18 / 60 / 24

    now = mjd_evening_twilight

    inQueue = list()

    # starttimes = list()

    errors = list()
    mode = "short"
    if returnAll:
        mode = "long"
    fName = "%i-%s.dat"%(mjd, mode)
    fout = open(fName, "w")
    while now < mjd_morning_twilight:
        exp_max = (mjd_morning_twilight - now) // exp_nom
        # field id and exposure nums of designs
        field_id, designs = scheduler.nextfield(mjd=now,
                                                maxExp=exp_max,
                                                live=True,
                                                ignore=inQueue,
                                                returnAll=returnAll)
        if field_id is None:
            print(f"[WARN] No field for {now:.3f}")
            now += exp_nom
            continue
        inQueue.append(field_id)
        # starttimes.append(now)
        if not returnAll:
            field_id = [field_id]
        exptime = exp_nom # force all exposures to nominal  * len(designs)
        fout.write("%.6f, %.6f, %.6f, %.6f, %s\n"%(mjd_evening_twilight, mjd_morning_twilight, now, exptime, str(field_id)))
        print(f"{now:.3f}, {len(designs) * exp_nom:.3f}", field_id)

        if returnAll:
            designs = designs[0]
        else:
            designs = len(designs)

        now += exp_nom # * designs (force all exposures to nominal)
    fout.close()

if __name__ == "__main__":
    mjdStart = 59305  # first day in april
    mjdEnd = mjdStart + 365 # last day in april
    mjdStep = 10
    returnAll = False

    for mjd in range(mjdStart, mjdEnd):
        runScheduler(mjd, returnAll=False)
        runScheduler(mjd, returnAll=True)
