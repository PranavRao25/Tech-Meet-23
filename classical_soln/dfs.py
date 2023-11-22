def TimeDelay(first_flight, second_flight):
    arrival_of_first_flight = first_flight["arrival"]
    departure_of_second_flight = second_flight["departure"]

    # Check if the first flight arrives before the second flight departs
    if arrival_of_first_flight < departure_of_second_flight:
        return True  # First flight arrives before second flight departs
    else:
        return False  # First flight arrives after or at the same time as second flight departs


def dfs(g, start_edge, end, path, paths):
    path.append(start_edge)

    if start_edge["destination"] == end:

        paths.append(path.copy())

    else:

        for next_edge in g[start_edge["destination"]]:
            if next_edge not in path:
                if TimeDelay(start_edge, next_edge):
                    dfs(g, next_edge, end, path, paths)

    path.pop()


def AllPaths(g, source, destination):
    paths = list()

    for v in g[source]:
        dfs(g, v, destination, [], paths)

    return paths


def PrintPaths(paths):
    i = 1

    for path in paths:

        print(f"---- solution {i} -----")

        for node in path:
            print()
            print(
                f'\tDestination : {node["destination"]}\n\tFlight Name : {node["flight name"]}\n\tDeparture time from source : {node["departure"]}\n\tArrival time at destination : {node["arrival"]}')
            print()

        print()
        i = i + 1
