from database import DATABASE
from graph import PrintGraph
from graph import MakeGraph

graph = MakeGraph(DATABASE)
PrintGraph(graph)

def oracle(x, source, destination):

    while 1:

        if source == destination:
            return True

        edge_number = -1

        for edge in graph[source]:
            if edge_number == -1:
                if x[edge["edge number"]] == '1':
                    source = edge["destination"]
                    edge_number = edge["edge number"]
            elif edge_number == 1:
                return False

        if edge_number == -1:
            return False

print(oracle("1011", "Bangalore", "Delhi"))
