import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_rows', None)
import sys
import glob
from expandSimple import expandSimple
from multiprocessing import Pool

# 59418

def doOne(filename):
    print("doing file ------------------")
    print(filename)
    print("-------------------\n\n")
    df = pd.read_csv(filename)
    mjd = int(filename.split("-")[-3])
    print("n fields", len(set(df.fieldID)))
    df = df.groupby(["fieldID", "mjdExpStart"]).mean().reset_index()
    df = df.sort_values(["fieldID", "mjdExpStart"]).reset_index()
    # df = df[["fieldID", "mjdExpStart", "alt", "az"]]

    dropCols = ["Unnamed: 0", "haDeg", "index"]

    df.drop(dropCols, axis="columns", inplace=True)

    expandSimple(df, mjd)

    print("done with file file ------------------")
    print(filename)
    print("-------------------\n\n")


if __name__ == "__main__":
    # mjd = sys.argv[1]
    # print(mjd)

    allFiles = glob.glob("../proc_data/mjd-*-sdss-fields.csv")

    # doOne("../proc_data/mjd-59418-sdss-fields.csv")

    with Pool(11) as p:
        p.map(doOne, allFiles)


    # df.to_csv("mjd-%s-sdss-simple.csv"%mjd)

# print(df)
