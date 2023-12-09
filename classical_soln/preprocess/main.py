# { input = database }, { output = identified affected flights & passengers }

import pandas as pd
from disruptions import *
from ruleEngine import *

Cancelled_Inventory = set()
Affected_Cities = []
Affected_Passengers = {}

for disruption in Disruptions:

    df = pd.read_csv('../database/inv.csv')
    print(df.keys())

    for i in range(0, len(df)):

        flight = df.loc[i]

        if flight["FlightNumber"] == disruption["Flight Number"] and flight["DepartureDate"] == disruption["Date"]:

            # This is to use in graph.py to avoid using this as an edge
            Cancelled_Inventory.add(flight["InventoryId"])

            t = (flight["DepartureAirport"], flight["ArrivalAirport"])

            # This will be given as input to walk module
            Affected_Cities.append(t)

            # This will be given as input to post process module
            Affected_Passengers[t] = []
            df1 = pd.read_csv('../database/pnr.csv')
            for j in range(len(df1)):
                pnr = df1.loc[j]
                if pnr["FLT_NUM"] == flight["FlightNumber"] and pnr["DEP_DT"] == flight["DepartureDate"]:
                    obj = PNR()
                    obj.Recloc = pnr["RECLOC"]
                    obj.TYPE = "PNR.INDIVIDUAL"
                    obj.Number_of_PAX = pnr["PAX_CNT"]
                    if pnr["PAX_CNT"] > 1:
                        obj.Booked_As = "Group"
                    Affected_Passengers[t].append(obj)
                else:
                    continue
