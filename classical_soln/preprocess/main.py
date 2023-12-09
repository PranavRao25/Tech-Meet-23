# { input = database }, { output = identified affected flights & passengers }

from disruptions import *
from ruleEngine import *
import pandas as pd

Delayed_Flights = {}
Cancelled_Inventory = set()
Cancelled_Flights = {}
passenger_flight_map = {}
affected_passengers = []

for disruption in Disruptions:

    if disruption["Type"] == "Cancelled":

        if disruption["Flight Number"] not in Cancelled_Flights:
            Cancelled_Flights[disruption["Flight Number"]] = {}

        df = pd.read_csv('../database/inv.csv')

        for i in range(0, len(df)):

            data = df.loc[i]

            if data["Flight Number"] == disruption["Flight Number"]:

                if data["Departure Date"] == disruption["Date"]:

                    Cancelled_Inventory.add(data["InventoryId"])
                    # This is to use in graph.py to avoid using this as an edge

                    # TODO: Decide how to store the identified flight & then identify the passengers

                else:

                    continue
            else:

                continue

        df = pd.read_csv('../database/passengers.csv')

        for i in range(len(df)):
            data = df.loc[i]
            if (data["Flight Number"] == disruption["Flight Number"]):
                affected_passengers.append(data)
            else:
                continue

        passenger_flight_map[disruption["Flight Number"]] = affected_passengers
        affected_passengers = []
