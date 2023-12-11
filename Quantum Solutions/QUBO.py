# from database import INV.csv
import pandas as pd
from qiskit_optimization.applications import *
from qiskit.circuit.library import TwoLocal
import numpy as np
import datetime as dt
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo
from qiskit_algorithms.minimum_eigensolvers import SamplingVQE,VQE,SamplingMinimumEigensolver
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms.optimizers import SPSA
from qiskit.primitives import Sampler

class QuantumSolver:
    df = pd.read_csv(".\INV.csv") #INV.csv
    

    highval = 1000000 # used for G (neglecting some flights)
    startNode, endNode="", "" # indices of the inventory dataset
    inv_id:str
    flight=None
    Q=A=B=N=G=None

    def __init__(self,inv_id):
        # self.startNode,self.endNode = start,end
        startTime=dt.datetime.now()
        self.inv_id=inv_id
        self.lst=self.__preProcess()
        print(len(self.lst),"Total Flights:\n")
        for i in self.lst:
            print(i)
        self.length = len(self.lst)
        self.Q = np.zeros((self.length,self.length))
        self.A,self.B,self.N,self.G=np.zeros_like(self.Q),np.zeros_like(self.Q),np.zeros_like(self.Q),np.zeros_like(self.Q) # all matrices

        print("\nAffected Flight\n")
        print(self.flight)
        ans=self.quantumSolve()
        print(ans)

        print((dt.datetime.now()-startTime))

    
    def __diff(self,date1, time1, date2, time2):
        """
            returns difference in time of date2-date1
        """
        dt1 = dt.datetime.strptime(date1 + " " + time1, "%m/%d/%Y %H:%M")
        dt2 = dt.datetime.strptime(date2 + " " + time2, '%m/%d/%Y %H:%M')
        difference = dt2 - dt1
        return int(difference.total_seconds() // 60)


    def __preProcess(self):
        # start = self.df.loc[self.startNode]
        # end = self.df.loc[self.endNode]
        # flight=self.df.loc[self.df["InventoryId"]==self.inv_id]
        index=self.df.loc[self.df["InventoryId"]==self.inv_id].index[0]
        flight=self.df.loc[index]
        self.flight=flight
        list_of_feasible_flights=[]

        for i in range(len(self.df)):
            data = self.df.loc[i]
            if index==i:
                print("pass")
                continue
            ti = self.__diff(date1=flight["DepartureDate"],time1=flight["DepartureTime"],date2=data["ArrivalDate"],time2=data["ArrivalTime"])
            ti2 = self.__diff(date1=flight["DepartureDate"],time1=flight["DepartureTime"],date2=data["DepartureDate"],time2=data["DepartureTime"])
            # print(ti,ti2)
            if ti < 60 or ti2 > 72*60:
                continue
            else:
                list_of_feasible_flights.append(data)
            
        return list_of_feasible_flights

    def __run(self):
        self.graph = dict()

        # Nodes
        # for loop working
        for i in range(len(self.lst)):
            data = self.lst[i]

            if data["InventoryId"] not in self.graph:
                self.graph[data["InventoryId"]] = (
                    data["DepartureAirport"],
                    data["ArrivalAirport"],
                    data["DepartureDate"],
                    data["DepartureTime"],
                    data["ArrivalTime"],
                    data["ArrivalDate"]
                )

                self.Q[i,i] = self.__diff(data["DepartureDate"], data["DepartureTime"], data["ArrivalDate"], data["ArrivalTime"])*100
                if data["DepartureAirport"] == self.flight["DepartureAirport"]:
                    self.A[i, i] = 1
                    self.N[i, i] = 1
                    self.G[i,i]= self.__diff(self.flight["DepartureDate"],self.flight["DepartureTime"],data["DepartureDate"],data["DepartureTime"])*100
                else:
                    self.A[i, i] = 0
                self.B[i, i] = 1 if (data["ArrivalAirport"] == self.flight["ArrivalAirport"]) else 0

            # Edges
                for j in range(len(self.lst)):
                    fl2 = self.lst[j]
                    if self.N[i,i] == 1 and i!=j:
                        self.G[i,j]=0
                    else:
                        if data["InventoryId"] == fl2["InventoryId"]:
                            ti= self.__diff(self.flight["DepartureDate"],self.flight["DepartureTime"],fl2["DepartureDate"],fl2["DepartureTime"])*100
                            self.G[i,j]=ti
                        else:
                            if data["DepartureAirport"] == fl2["ArrivalAirport"]:
                                self.N[j,i] = 1
                                ti = int(self.__diff(fl2["ArrivalDate"],fl2["ArrivalTime"],data["DepartureDate"],data["DepartureTime"])*100 )# minutes(fl2["DepartureTime"]) - minutes(data["ArrivalTime"])
                                if ti <6000 or ti >72000 :
                                    self.G[i,j]=self.highval
                                else:
                                    self.G[i,j]=ti
                            else:
                                self.N[j,i]=0
                                self.G[i,j]=0

        print("Q:\n ",self.Q)
        print("G:\n ",self.G)
        print("A:\n ",self.A)
        print("B:\n ",self.B)
        print("N:\n ",self.N)

    def quantumSolve(self) -> list:
        total = []
        self.__run() # we will get the Q A B N G matrices initialised now
        qp = QuadraticProgram("flights")
        F = self.Q + self.highval*(self.A + self.B - self.N) + self.G # quadratic form matrix
        for i in range(self.length):
            F=F+self.highval*np.matmul(np.reshape(self.N[:,i],(-1,1)),np.transpose(np.reshape(self.N[:,i],(-1,1))))
            # print(i,self.N[:,i])
            # print(np.matmul(np.reshape(self.N[:,i],(-1,1)),np.transpose(np.reshape(self.N[:,i],(-1,1)))))
        F=F.astype(int)
        # L = -2*(self.A.diagonal() + self.B.diagonal()) - 2*self.highval*(np.ones((self.A.shape[0],))) # linear matrix
        L = -2*self.highval*(self.A.diagonal() + self.B.diagonal())  # linear matrix
        L=L.astype(int)
        print(L)
        print(F)
        # L = np.reshape(L,(1,self.A.shape[0]))[0]
        qp.minimize(linear=L,quadratic=F) # matrices fed into the quadratic program
        qp.binary_var_list(L.size)

        # qp.

        # qp.minimize(linear=L)  # quadratic=F) # matrices fed into the quadratic program        
        # return qp
        print(qp.objective)

        qubitOp, offset = qp.to_ising()  # conversion into Ising Problem
        two = TwoLocal(self.length, 'rx', 'cx', 'linear', reps=2, insert_barriers=True)  # an ansatz circuit
        start=dt.datetime.now()
        optimizer = SPSA(maxiter=3000) # try other optimizers
        print(dt.datetime.now()-start)
        start=dt.datetime.now()
        vqe = SamplingVQE(sampler=Sampler(), ansatz=two, optimizer=optimizer)
        print(dt.datetime.now()-start)
        start=dt.datetime.now()
        vqe_op1 = MinimumEigenOptimizer(vqe)
        print(dt.datetime.now()-start)
        start=dt.datetime.now()
        result = vqe_op1.solve(qp)
        print(dt.datetime.now()-start)
        start=dt.datetime.now()
        ans = list(result.variables_dict.values())

        # total.append(postProcess(ans))
        print(ans)
        total.append(self.__postProcess(ans))
        return total

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
                flights.append(self.lst[i])
        for i in range(len(flights)):
            for j in range(len(flights)):
                if i!=j :
                    self.Q[i,j]=self.highval
        return flights


QuantumSolver("INV-ZZ-1875559")