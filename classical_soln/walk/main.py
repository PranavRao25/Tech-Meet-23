# Using DFS to find all possible alternate solutions from one airport to other
# As of now time of arrival & departure of flights are not considered, but we can modify the
# following code to have more parameters
import time
from dfs import AllPaths
from dfs import PrintPaths
from graph import MakeGraph
from graph import PrintGraph
from datetime import datetime

Graph = MakeGraph()
PrintGraph(Graph)
print("\n\n")

# Airports = Graph.keys()
# TotalTime = 0
# for source in Airports:
#
#     for destination in Airports:
#
#         if source != destination:
#
#             start_time = time.time()  # Record the start time
#             paths = AllPaths(Graph, source, destination)
#             end_time = time.time()  # Record the end time
#
#             print(f"Paths from {source} to {destination}:")
#             # PrintPaths(paths)
#             print(f"Time taken: {end_time - start_time} seconds")
#             TotalTime += end_time-start_time
# print(TotalTime)

Affeced_Flight_Departure = datetime.strptime("05/25/2024 4:37", "%m/%d/%Y %H:%M")
Affected_Flight_Arrival = datetime.strptime("05/25/2024 12:50", "%m/%d/%Y %H:%M")

paths = AllPaths(Graph, 'CNN', 'MAA', Affeced_Flight_Departure, Affected_Flight_Arrival)
PrintPaths(paths)
