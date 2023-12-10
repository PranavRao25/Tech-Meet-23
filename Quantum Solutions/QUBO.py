import numpy as np
from database import INV.csv
import pandas as pd
from qiskit_optimization.applications import Maxcut
from qiskit.visualization import array_to_latex
from qiskit.circuit.library import TwoLocal
from qiskit_algorithms.minimum_eigensolvers import SamplingVQE,VQE,SamplingMinimumEigensolver
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms.optimizers import SPSA
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, random_statevector
from qiskit.quantum_info.operators import Operator, Pauli
from qiskit.primitives import Sampler,Estimator

"""
5 matrices : Q A B N G

Use Inventory and Schedule Dataset
"""

df = pd.read_csv(#INV.csv)
Q,A,B,N,G = np.zeros(len(df.columns))),np.zeros(len(df.columns))),np.zeros(len(df.columns))),np.zeros(len(df.columns))),np.zeros(len(df.columns)))
highval = 9223372036854775807
def MakeGraph(startNode,endNode):
    graph = dict()

    # Nodes
    for i in range(len(df)):
        data = df.loc[i]

        if data["FlightNumber"] not in graph:
            graph[data["FlightNumber"]] = (
                data["DepartureAirport"],
                data["ArrivalAirport"],
                data["DepartureDate"],
                data["DepartureTime"],
                data["ArrivalTime"],
                data["ArrivalDate"]
            )

            Q[i,i] = diff(data["DepartureDates"],data["DepartureTime"],data["ArrivalDate"],data["ArrivalTime"])
            A[i,i] = 1 if(data["DepartureAirport"]==startNode) else 0
            B[i, i] = 1 if (data["ArrivalAirport"] == endNode) else 0


    # Edges
    for i in range(len(df)):
        fl1 = df.loc[i]
        if(fl1["DepartureAirport"]==startNode):
            N[i,i]=1
        for j in range(len(df)):
            fl2 = df.loc[j]
            if(fl1==fl2):
                continue
            else:
                if(fl1["DepartureAirport"]==fl2["ArrivalAirport"]):
                    N[i, j] = 1
                    G[i,j] = diff(fl2["DepartureDates"],fl2["DepartureTime"],fl1["ArrivalDate"],fl1["ArrivalTime"]) # minutes(fl2["DepartureTime"]) - minutes(fl1["ArrivalTime"])
                    if(G[i,j]<60 or G[i,j]>720):
                        G[i,j]=highval
                        N[i,j]=0
                else:
                    N[i,j]=0
                    G[i,j]=highval

    return graph

def QAOA():
    total = []
    for i in range(5):
        # Quantum processing
        # total.append(postProcess(ans))

def postProcess(bitString):
    flights = []
    for i in range(len(bitString)):
        if(bitString[i]=="1"):
            flights.append(df.loc[i])
    for i in range(len(flights)):
        for j in range(len(flights)):
            if(i!=j):
                Q[i,j]=highval
    return flights