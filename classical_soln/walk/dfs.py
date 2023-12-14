from datetime import timedelta

def TimeDelay(first_flight, second_flight, affected_flight_arrival):

    arrival_of_first_flight = first_flight["Arrival"]
    departure_of_second_flight = second_flight["Departure"]

    # Check if the first flight arrives before the second flight departs
    if arrival_of_first_flight < departure_of_second_flight:

        time_difference = departure_of_second_flight - arrival_of_first_flight

        # Assuming you want to allow delays between 1 and 12 hours
        if timedelta(hours=1) <= time_difference <= timedelta(hours=12):
            return True
        else:
            return False

    else:
        return False  # First flight arrives after or at the same time as the second flight departs


def dfs(g, start_edge, end, path, paths, affected_flight_arrival):

    path.append(start_edge)

    ETD = start_edge["Arrival"] - affected_flight_arrival
    if len(path) > 5 or len(paths) > 10 or ETD > timedelta(hours=72):
        path.pop()
        return

    if start_edge["Destination"] == end:
        if path not in paths:
            paths.append(path.copy())
    else:
        if start_edge["Destination"] in g:
            for next_edge in g[start_edge["Destination"]]:
                if next_edge not in path:
                    if TimeDelay(start_edge, next_edge, affected_flight_arrival):
                        dfs(g, next_edge, end, path, paths, affected_flight_arrival)
    path.pop()

def AllPaths(g, source, destination, affected_flight_departure, affected_flight_arrival):

    paths = list()
    for v in g[source]:
        if v["Departure"] < affected_flight_departure:
            continue
        dfs(g, v, destination, [], paths, affected_flight_arrival)
    return paths

def PrintPaths(paths):

    i = 1

    for path in paths:

        print(f"---- solution {i} -----")

        for node in path:
            print()
            # print(
            #     f'\tOrigin: {node["Origin"]}\n\tDestination: {node["Destination"]}\n\tFlightNumber: {node["FlightNumber"]}\n')
            # print()
            print(node)
            print()

        print()
        i = i + 1
