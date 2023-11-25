from datetime import datetime


def PrintGraph(graph):
    for key in graph:

        print(f"---------Node -> {key}---------")

        for v in graph[key]:
            print(f"Edge -> {v}")


def MakeGraph(database):

    graph = dict()
    edge_number = 0

    for data in database:

        if data["source"] not in graph:
            graph[data["source"]] = []

        temp = datetime.strptime(data["date of departure"], "%d %B %Y")
        departure = datetime.strptime(data["departure time"].replace(' ', ''), "%H:%M:%S")
        departure = departure.replace(day=temp.day, month=temp.month, year=temp.year)

        temp = datetime.strptime(data["date of arrival"], "%d %B %Y")
        arrival = datetime.strptime(data["arrival time"].replace(' ', ''), "%H:%M:%S")
        arrival = arrival.replace(day=temp.day, month=temp.month, year=temp.year)

        # Calculating the journey time
        hours = arrival.hour - departure.hour
        minutes = arrival.minute - departure.minute
        seconds = arrival.second - departure.second

        time_of_flight = hours * 3600 + minutes * 60 + seconds

        graph[data["source"]].append(
            {
                "destination": data["destination"],
                "flight name": data["flight name"],
                "departure": departure,
                "arrival": arrival,
                "time": time_of_flight,
                "edge number": edge_number
            },
        )

        edge_number = edge_number + 1

    return graph
