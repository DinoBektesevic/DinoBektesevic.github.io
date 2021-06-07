The collection of scripts in this directory grabs and initially formats the
data for our visualization.

querySchedule.py: runs on SDSS servers, queries the field database for fields
for a given night

computePositions.py: computes the position of astronomical fields (and star+moon data)
at each timestep for each night

simplifyMJD.py, sched2csv.py, expandSimple.py, addPriority.py are all
intermediate scripts that were created to add features to the data as our
project progressed.

cal.py: generates the data needed by the calendar visualization.

All these scripts should be organized into a more "sane" pipeline in the future.