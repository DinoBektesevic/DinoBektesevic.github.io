import matplotlib.pyplot as plt
import numpy as np
import json


with open("fieldCalendar.json", "r") as dataFile:
    data = json.load(dataFile)

smallerData = []
for row in data:
    smallerData.append(
        {
            "mjd": row["mjd"],
            "monthName": row["monthName"],
            "dayOfMonth": row["dayOfMonth"],
            "nFields": row["nFields"],
            "moonPhase": row["moonPhase"],
            "moonHours": row["moonHours"],
            "obsHours": row["obsHours"],
            "darkPercent": row["darkPercent"][0],
       }
    )


with open("fixFieldCalendar.json", "w") as dataFile:
    dataFile.write(json.dumps(smallerData))


a = 1

