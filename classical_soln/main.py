# Using DFS to find all possible alternate solutions from one airport to other
# As of now time of arrival & departure of flights are not considered, but we can modify the
# following code to have more parameters

import data_base
from dfs import AllPaths
from dfs import PrintPaths
from graph import MakeGraph
from graph import PrintGraph

Database = data_base.DATABASE
Graph = MakeGraph(Database)
PrintGraph(Graph)
print("\n\n")
PrintPaths(AllPaths(Graph, "Bangalore", "Delhi"))
