from datetime import datetime
import pandas as pd


def PrintGraph(graph):

    for key in graph:
        print(f"---------Node -> {key}---------")
        for v in graph[key]:
            print(f"Edge -> {v}")

def MakeGraph():

    flight_time_map = dict()
    df = pd.read_csv('../database/schedule.csv')

    for i in range(0, len(df)):

        data = df.loc[i]

        if data["FlightNumber"] not in flight_time_map:
            flight_time_map[data["FlightNumber"]] = []

        flight_time_map[data["FlightNumber"]].append(
            (
                data["ScheduleID"],
                data["DepartureTime"],
                data["ArrivalTime"]
             )
        )

    graph = dict()
    df = pd.read_csv('../database/inv.csv')

    for i in range(0, len(df)):

        data = df.loc[i]

        if data["DepartureAirport"] not in graph:
            graph[data["DepartureAirport"]] = []

        departure = -1
        arrival = -1

        for j in flight_time_map[data["FlightNumber"]]:
            if data['ScheduleId'] == j[0]:
                departure = datetime.strptime(j[1].replace(' ', ''), "%H:%M")
                arrival = datetime.strptime(j[2].replace(' ', ''), "%H:%M")
                break

        if departure == -1 or arrival == -1:
            print("No ScheduleID match found for given Inventory data")
            print("Schedule ID ", data["ScheduleID"])

        temp = datetime.strptime(data["DepartureDate"], "%m/%d/%Y")
        departure = departure.replace(day=temp.day, month=temp.month, year=temp.year)
        temp = datetime.strptime(data["ArrivalDate"], "%m/%d/%Y")
        arrival = arrival.replace(day=temp.day, month=temp.month, year=temp.year)

        # Calculating the journey time
        hours = arrival.hour - departure.hour
        minutes = arrival.minute - departure.minute
        seconds = arrival.second - departure.second

        time_of_flight = hours * 3600 + minutes * 60 + seconds

        graph[data["DepartureAirport"]].append(
            {
                "Origin": data["DepartureAirport"],
                "Destination": data["ArrivalAirport"],
                "InventoryID": data["InventoryId"],
                "FlightNumber": data["FlightNumber"],
                "Departure": departure,
                "Arrival": arrival,
                "Time": time_of_flight,
            },
        )

    return graph

MakeGraph()
