import glob
import pandas as pd
import numpy
import seaborn as sns
import matplotlib.pyplot as plt


# filename = "mjd-59662-sdss-simple-expanded.csv"

allfiles = glob.glob("testDir/mjd*-simple-expanded.csv")

for filename in allfiles:

    df = pd.read_csv(filename, index_col=0)
    newfilename = filename.strip(".csv") + "-priority.csv"

    priority = numpy.array([-1]*len(df))
    completion = numpy.array([-1]*len(df))

    df["priority"] = priority
    df["completion"] = completion

    fields = list(set(df[df.objType=="sdss field"]["fieldID"]))
    fieldPriority = numpy.random.choice([0,1,2,3,4,5], size=len(fields))
    fieldCompletion = numpy.random.uniform(high=100, size=len(fields))

    for field, priority, completion in zip(fields, fieldPriority, fieldCompletion):
        # check if its scheduled
        sched = list(df[df.fieldID==field]["scheduled"])
        if True in sched:
            # give all scheduled plates high priority
            priority = 0
        df["priority"].loc[df["fieldID"]==field] = priority
        df["completion"].loc[df["fieldID"]==field] = completion

    df.reset_index()
    df.to_csv(newfilename)
    # sns.scatterplot(x="fieldID", y="completion", data=df[df.objType=="sdss field"])
    # plt.show()

# import pdb; pdb.set_trace()
# print(fields)