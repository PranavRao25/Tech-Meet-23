# Author : Sai Hemanth Reddy
# Date : 19 November 2023
# Time : 11:00 AM

# Using DFS to find all possible alternate solutions from one airport to other
# As of now time of arrival & departure of flights are not considered, but we can modify the
# following code to have more parameters

from datetime import datetime

# All Times are assumed to be in IST & 24hrs format
# As of now we are assuming all times mentioned belong to same day
Database = [("Bangalore", "Hyderabad", "F1", "08:00:00", "09 : 00 : 00"),
            ("Bangalore", "Hyderabad", "F4", "08:00:00", "09 : 00 : 00"),
            ("Hyderabad", "Mumbai", "F2", "09 : 30 : 00", "10 : 40 : 00"),
            ("Mumbai", "Delhi", "F3", "11 : 00 : 00", "13 : 00 : 00")
            ]

def MakeGraph(database):

    graph = dict()

    for data in database:

        source = data[0]

        if source not in graph:
            graph[source] = []

        destination = data[1]
        flight_name = data[2]

        departure_time_from_source = datetime.strptime(data[3].replace(' ', ''), "%H:%M:%S")
        arrival_time_at_destination = datetime.strptime(data[4].replace(' ', ''), "%H:%M:%S")

        # Calculating the journey time
        hours = arrival_time_at_destination.hour - departure_time_from_source.hour
        minutes = arrival_time_at_destination.minute - departure_time_from_source.minute
        seconds = arrival_time_at_destination.second - departure_time_from_source.second

        time_of_flight = hours*3600 + minutes*60 + seconds

        graph[source].append(
            (destination,
             flight_name,
             departure_time_from_source,
             arrival_time_at_destination,
             time_of_flight)
        )

    return graph

def dfs(graph, start, end, path, paths):

    path.append(start)

    if start[0] == end:
        paths.append(path.copy())
    else:
        for neighbour in graph[start[0]]:
            if neighbour not in path:
                dfs(graph, neighbour, end, path, paths)
    path.pop()

def AllPossiblePaths(graph, source, destination):
    paths = list()
    for v in graph[source]:
        dfs(graph, v, destination, [], paths)
    return paths

def print_path(paths):
    i = 1
    for path in paths:
        print(f"---- solution {i} -----")
        for node in path:
            print(f"Air port : {node[0]}, Flight : {node[1]}")
        i = i + 1
    pass

Graph = MakeGraph(Database)
print(print_path(AllPossiblePaths(Graph, "Bangalore", "Delhi")))
