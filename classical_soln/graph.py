from datetime import datetime
import pandas as pd


def PrintGraph(graph):
    for key in graph:

        print(f"---------Node -> {key}---------")

        for v in graph[key]:
            print(f"Edge -> {v}")


def MakeGraph():

    graph = dict()

    df = pd.read_csv('schedule.csv')

    for i in range(0, len(df)):

        data = df.loc[i]

        if data["DepartureAirport"] not in graph:
            graph[data["DepartureAirport"]] = []

        # temp = datetime.strptime(data["date of departure"], "%d %B %Y")
        departure = datetime.strptime(data["DepartureTime"].replace(' ', ''), "%H:%M")
        # departure = departure.replace(day=temp.day, month=temp.month, year=temp.year)

        # temp = datetime.strptime(data["date of arrival"], "%d %B %Y")
        arrival = datetime.strptime(data["ArrivalTime"].replace(' ', ''), "%H:%M")
        # arrival = arrival.replace(day=temp.day, month=temp.month, year=temp.year)

        # Calculating the journey time
        hours = arrival.hour - departure.hour
        minutes = arrival.minute - departure.minute
        seconds = arrival.second - departure.second

        time_of_flight = hours * 3600 + minutes * 60 + seconds
        #
        graph[data["DepartureAirport"]].append(
            {
                "ArrivalAirport": data["ArrivalAirport"],
                "FlightNumber": data["FlightNumber"],
                "Departure": departure,
                "Arrival": arrival,
                "Time": time_of_flight,
            },
        )

    return graph
