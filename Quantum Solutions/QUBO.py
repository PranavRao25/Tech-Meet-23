from database import INV.csv
import pandas as pd
from qiskit_optimization.applications import *
from qiskit.circuit.library import TwoLocal
import numpy as np
import datetime as dt
from qiskit_optimization import QuadraticProgram
from qiskit_algorithms.minimum_eigensolvers import SamplingVQE,VQE,SamplingMinimumEigensolver
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms.optimizers import SPSA
from qiskit.primitives import Sampler

"""
5 matrices : Q A B N G

Use Inventory and Schedule Dataset
"""

def diff(date1,date2,time1,time2):
    dt1=dt.datetime.strptime(date1+" "+time1,"%d/%m/%Y %H:%M")
    dt2=dt.datetime.strptime(date2+" "+time2,'%d/%m/%Y %H:%M')
    difference=dt2-dt1
    return int(difference.total_seconds()//60)

class QuantumSolver:
    df = pd.read_csv(#INV.csv)
    length = len(df.columns)
    Q,A,B,N,G = np.zeros((length,length)),np.zeros_like(Q),np.zeros_like(Q),np.zeros_like(Q),np.zeros_like(Q)
    highval = 9223372036854775807
    startNode,endNode=0,0

    def __init(self,startNode,endNode):
        self.graph = dict()

        # Nodes
        # for loop working
        for i in range(len(self.df)):
            data = self.df.loc[i]

            if data["FlightNumber"] not in self.graph:
                self.graph[data["FlightNumber"]] = (
                    data["DepartureAirport"],
                    data["ArrivalAirport"],
                    data["DepartureDate"],
                    data["DepartureTime"],
                    data["ArrivalTime"],
                    data["ArrivalDate"]
                )

                self.Q[i,i] = diff(data["DepartureDates"],data["DepartureTime"],data["ArrivalDate"],data["ArrivalTime"])
                self.A[i,i] = 1 if(data["DepartureAirport"]==startNode) else 0
                self.B[i, i] = 1 if (data["ArrivalAirport"] == endNode) else 0


        # Edges
        for i in range(len(self.df)):
            fl1 = self.df.loc[i]
            if fl1["DepartureAirport"]==startNode:
                self.N[i,i]=1
            for j in range(len(self.df)):
                fl2 = self.df.loc[j]
                if fl1==fl2:
                    continue
                else:
                    if fl1["DepartureAirport"]==fl2["ArrivalAirport"]:
                        self.N[i, j] = 1
                        self.G[i,j] = diff(fl2["DepartureDates"],fl2["DepartureTime"],fl1["ArrivalDate"],fl1["ArrivalTime"]) # minutes(fl2["DepartureTime"]) - minutes(fl1["ArrivalTime"])
                        if self.G[i,j]<60 or self.G[i,j]>720:
                            self.G[i,j]=self.highval
                            self.N[i,j]=0
                    else:
                        self.N[i,j]=0
                        self.G[i,j]=self.highval


    def quantumSolve(self) ->list:
        total = []
        self.__init(self.startNode,self.endNode) # we will get the Q A B N G matrices initialised now

        for i in range(5): # 5 alternate solutions
            # Convert into a Quadratic Program
            qp = QuadraticProgram("flights")
            # process the matrices into this program using numpy
            F = self.Q + self.A + self.B + self.N + self.G # quadratic form matrix
            L = -2*(self.A + self.B)  # linear matrix

            qp.minimize(constant=3,linear=L.diagonal(),quadratic=F) # matrices fed into the quadratic program
            # Quantum processing
            """
                To be explored, different optimizers, eigensolvers, (ansatz : best is linear entanglement)
            """

            # qubitOp, offset = qp.to_ising()  # conversion into Ising Problem
            two = TwoLocal(3, 'rx', 'cx', 'linear', reps=2, insert_barriers=True)  # an ansatz circuit
            optimizer = SPSA(maxiter=3000) # try other optimizers
            vqe = SamplingVQE(sampler=Sampler(), ansatz=two, optimizer=optimizer)
            vqe_op1 = MinimumEigenOptimizer(vqe)
            result = vqe_op1.solve(qp)
            ans = list(result.variables_dict.values())

            # total.append(postProcess(ans))
            total.append(self.__postProcess(ans))
        return total


    def __postProcess(self,bitString:list) -> list:
        flights = []
        for i in range(len(bitString)):
            if bitString[i]==1:
                flights.append(self.df.loc[i])
        for i in range(len(flights)):
            for j in range(len(flights)):
                if i!=j :
                    self.Q[i,j]=self.highval
        return flights
