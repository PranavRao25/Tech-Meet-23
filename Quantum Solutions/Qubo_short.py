# from database import INV.csv
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

class QuantumSolver:
    df = pd.read_csv("/home/pranav/QC/Tech Meet/INV_sample.csv") #INV.csv
    length = len(df)
    Q = np.zeros((length,length))
    A,B,N,G = np.zeros_like(Q),np.zeros_like(Q),np.zeros_like(Q),np.zeros_like(Q) # all matrices

    highval = 9223372036854775807 # used for G (neglecting some flights)
    startNode, endNode="", "" # indices of the inventory dataset
    inv_id:str
    
    def __init__(self, inv_id):
        # self.startNode,self.endNode = start,end
        startTime=dt.datetime.now()
        self.inv_id=inv_id
        lst=self.__preProcess()
        for i in lst:
            print(i,end="\n\n")

        print(len(lst))
        print((dt.datetime.now()-startTime))

    def __diff(self,date1, date2, time1, time2):
        """
            returns difference in time of date2-date1
        """
        print(date1,date2)
        dt1 = dt.datetime.strptime(date1 + " " + time1, "%m/%d/%Y %H:%M")
        dt2 = dt.datetime.strptime(date2 + " " + time2, '%m/%d/%Y %H:%M')
        difference = dt2 - dt1
        return int(difference.total_seconds() // 60)


    def __preProcess(self):
         # start = self.df.loc[self.startNode]
        # end = self.df.loc[self.endNode]
        # flight=self.df.loc[self.df["InventoryId"]==self.inv_id]
        index=self.df.loc[self.df["InventoryId"]==self.inv_id].index[0]
        self.flight=self.df.loc[index]
        list_of_feasible_flights=[]

        for i in range(len(self.df)):
            data = self.df.loc[i]
            ti = self.__diff(date1=self.flight["DepartureDate"],time1=self.flight["DepartureTime"],date2=data["ArrivalDate"],time2=data["ArrivalTime"])
            ti2 = self.__diff(date1=self.flight["DepartureDate"],time1=self.flight["DepartureTime"],date2=data["DepartureDate"],time2=data["DepartureTime"])
            if ti < 60 or ti2 > 72*60:
                continue
            else:
                list_of_feasible_flights.append(data)
            
        return list_of_feasible_flights
    
    def __run(self,startNode,endNode):
        self.graph = dict()

        # Nodes
        # for loop working
        for i in range(len(self.df)):
            data = self.df.loc[i]

            if data["InventoryId"] not in self.graph:
                self.graph[data["InventoryId"]] = (
                    data["DepartureAirport"],
                    data["ArrivalAirport"],
                    data["DepartureDate"],
                    data["DepartureTime"],
                    data["ArrivalTime"],
                    data["ArrivalDate"]
                )

                self.Q[i,i] = self.__diff(data["DepartureDate"], data["ArrivalDate"], data["DepartureTime"], data["ArrivalTime"])
                if data["DepartureAirport"] == self.flight["DepartureAirport"][0]:
                    self.A[i, i] = 1
                    self.N[i, i] = 1
                else:
                    self.A[i, i] = 0
                self.B[i, i] = 1 if (data["ArrivalAirport"] == self.flight["ArrivalAirport"][0]) else 0

            # Edges
                for j in range(len(self.df)):
                    fl2 = self.df.loc[j]
                    if data["InventoryId"] == fl2["InventoryId"]:
                        continue
                    else:
                        if data["DepartureAirport"] == fl2["ArrivalAirport"]:
                            self.N[i, j] = 1
                            self.G[i,j] = self.__diff(fl2["DepartureDate"],data["ArrivalDate"],fl2["DepartureTime"],data["ArrivalTime"]) # minutes(fl2["DepartureTime"]) - minutes(data["ArrivalTime"])
                            if self.G[i,j]<60 or self.G[i,j]>720:
                                self.G[i,j]=self.highval
                                self.N[i,j]=0
                        else:
                            self.N[i,j]=0
                            self.G[i,j]=self.highval

    def quantumSolve(self) ->list:
        total = []
        self.__run(self.flight["DepartureAirport"],self.flight["ArrivalAirport"]) # we will get the Q A B N G matrices initialised now
        
        qp = QuadraticProgram("flights")
        F = np.zeros_like(self.Q)
        F = self.Q + self.A + self.B + self.N + self.G # quadratic form matrix
        L = -2*(np.diagonal(self.A) + np.diagonal(self.B))  # linear matrix
        qp.minimize(linear=L,quadratic=F) # matrices fed into the quadratic program
        return qp

#             qp.minimize(constant=3,linear=L.diagonal(),quadratic=F) # matrices fed into the quadratic program
#         for i in range(3): # 5 alternate solutions
#             # Convert into a Quadratic Program
#             qp = QuadraticProgram("flights")
#             F = self.Q + self.A + self.B + self.N + self.G # quadratic form matrix
#             L = -2*(self.A + self.B)  # linear matrix

#             qp.minimize(constant=3,linear=L.diagonal(),quadratic=F) # matrices fed into the quadratic program
#             # Quantum processing

#             """
#                 To be explored, different optimizers, eigensolvers, (ansatz : best is linear entanglement)
#             """

#             # qubitOp, offset = qp.to_ising()  # conversion into Ising Problem
#             two = TwoLocal(27, 'rx', 'cx', 'linear', reps=2, insert_barriers=True)  # an ansatz circuit
#             optimizer = SPSA(maxiter=3000) # try other optimizers
#             vqe = SamplingVQE(sampler=Sampler(), ansatz=two, optimizer=optimizer)
#             vqe_op1 = MinimumEigenOptimizer(vqe)
#             result = vqe_op1.solve(qp)
#             ans = list(result.variables_dict.values())

#             # total.append(postProcess(ans))
#             total.append(self.__postProcess(ans))
#         return total


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
