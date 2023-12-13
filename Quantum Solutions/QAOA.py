import pandas as pd
from qiskit.circuit.library import TwoLocal
import numpy as np
import datetime as dt
from qiskit_algorithms import QAOA
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo
from qiskit_algorithms import NumPyMinimumEigensolver
from qiskit_optimization.algorithms import MinimumEigenOptimizer, WarmStartQAOAOptimizer, CplexOptimizer, CobylaOptimizer
from qiskit.primitives import Sampler
from qiskit_algorithms.optimizers import COBYLA
from qiskit_algorithms.utils.algorithm_globals import algorithm_globals
import copy
import sys
"""
    We are creating a QUBO instance of a Quadratic Program and solving it using Warm Start QAOA.
     
    Quantum Solver Class does the following:
    1. takes as an input the affected flight's inventory id
    2. maintains an list of relevant flights
    3. Creates the appropriate Quadratic Program
    4. Converts it into QUBO instance
    5. Solve it using Warm Start QAOA (we use classical optimiser as either Cplex or COBYLA)
    6. Return the list of alternate flights 
    
    Flow of the functions:
    1. __init__
    2. __preProcess
    3. quantumSolve()
    4. __run()
    5. QAOA_algo()
    6. __postProcess()
"""


class QuantumSolver:
    df = None  # INV.csv
    highval = 1000000  # used for G (neglecting some flights)
    inv_id: str  # stores the affected flight inventory id
    flight = None  # affected flight row
    FullList: dict
    Q = A = B = Nb = Na = G = Delay = None  # matrices to be used in Quadratic Program

    def __init__(self, inv_id, FullList, inFile):
        """
            Input : Corresponding inventory id of affected flight from the provided datafile
            Creates a list of relevant flights, initializes matrices, and calls the QuantumSolve() function
        """

        self.df = pd.read_csv(inFile)

        startTime = dt.datetime.now()
        self.inv_id = inv_id
        self.FullList = FullList

        self.lst = self.__preProcess()  # list of relevant flights
        if len(self.lst) == 0:  # no relevant flights present
            raise Exception('No alternate flights')
        print(len(self.lst), "Feasible Flights\n")

        self.length = len(self.lst)
        self.length = min(self.length, 10)
        file = open("Selected Flights", "w")
        for i in self.lst[:self.length]:
            file.write(str(i) + "\n\n")
        file.close()

        # all matrices
        self.Q = np.zeros((self.length, self.length))
        self.A, self.B, self.Nb, self.G, self.Na = np.zeros_like(self.Q), np.zeros_like(self.Q), np.zeros_like(
            self.Q), np.zeros_like(self.Q), np.zeros_like(self.Q)
        self.Delay = np.zeros((self.length,))

        print("\nAffected Flight\n")
        print(self.flight)

        ans = self.quantumSolve()  # invoke the quantum solve function
        TimeTaken = (dt.datetime.now() - startTime)

        for i in range(len(ans)):
            print("Solution", i, end="\n\n")
            print(ans[i])
            print("\n")

        print(TimeTaken)

    def __diff(self, date1, time1, date2, time2):
        """
            returns difference in time of date2-date1
        """
        dt1 = dt.datetime.strptime(date1 + " " + time1, "%m/%d/%Y %H:%M")
        dt2 = dt.datetime.strptime(date2 + " " + time2, '%m/%d/%Y %H:%M')
        difference = dt2 - dt1
        return int(difference.total_seconds() // 60)

    def __preProcess(self) -> list:
        """
            Creates a list of relevant flights which have sensible departure and arrival times
        """
        index = self.df.loc[self.df["InventoryId"] == self.inv_id].index[0]  # get the index from the dataset
        self.flight = self.df.loc[index]  # affected flight
        list_of_feasible_flights = []
        currFlTime = self.__diff(date1=self.flight["DepartureDate"], time1=self.flight["DepartureTime"],
                                 date2=self.flight["ArrivalDate"],
                                 time2=self.flight["ArrivalTime"])

        for i in range(len(self.df)):
            data = self.df.loc[i]
            if index == i:
                continue
            fromlst = self.FullList.get(data["InventoryId"])
            if fromlst:
                if fromlst == "Cancelled":
                    continue
            if data["ArrivalAirport"] == self.flight["DepartureAirport"] or data["DepartureAirport"] == self.flight[
                "ArrivalAirport"]:
                continue
            timebtwArr_Curdep = self.__diff(date1=self.flight["DepartureDate"], time1=self.flight["DepartureTime"],
                                            date2=data["ArrivalDate"],
                                            time2=data["ArrivalTime"])
            timebtwdep_CurrDep = self.__diff(date1=self.flight["DepartureDate"], time1=self.flight["DepartureTime"],
                                             date2=data["DepartureDate"],
                                             time2=data["DepartureTime"])
            flightTime = self.__diff(date1=data["DepartureDate"], time1=data["DepartureTime"],
                                     date2=data["ArrivalDate"],
                                     time2=data["ArrivalTime"])

            if timebtwArr_Curdep < 60 or timebtwdep_CurrDep > 72 * 60:  # rule 1,2,3  # following the Minimum Ground Time and Maximum Connecting Time
                continue
            elif flightTime > currFlTime and data["DepartureAirport"] != self.flight["DepartureAirport"] \
                    and data["ArrivalAirport"] != self.flight["ArrivalAirport"]:  # rule 4
                continue
            else:
                list_of_feasible_flights.append(data)

        airports = [self.flight["DepartureAirport"]]
        feas = []
        while len(airports) != 0:
            airport = airports.pop()
            for i in list_of_feasible_flights:
                if i["DepartureAirport"] == airport:
                    feas += [i]
                    airports += i["ArrivalAirport"]

        return feas

    def __run(self):
        """
            Creates the Matrices required for the Quadratic Program
        """
        self.graph = dict()  # to keep a tally of unique flights

        # Nodes
        for i in range(self.length):
            data = self.lst[i]  # a single flight

            if data["InventoryId"] not in self.graph:
                self.graph[data["InventoryId"]] = (
                    data["DepartureAirport"],
                    data["ArrivalAirport"],
                    data["DepartureDate"],
                    data["DepartureTime"],
                    data["ArrivalTime"],
                    data["ArrivalDate"]
                )

                # Q Matrix measures the total time taken by the flight (Arr - Dep of the flight)
                self.Q[i, i] = self.__diff(data["DepartureDate"], data["DepartureTime"], data["ArrivalDate"],
                                           data["ArrivalTime"]) * 100

                # A Matrix measures if the current flight departs from the same airport as Affected flight
                # Nb Matrix measures the neighbouring flight connectivity(by deparuture)
                # Na Matrix measures the neighbouring flight connectivity(by arrival)
                # G Matrix measures the ground time spent by a flight (next departure - arrival)
                if data["DepartureAirport"] == self.flight["DepartureAirport"]:
                    self.A[i, i] = 1
                    self.Nb[i, i] = 1
                    # self.G[i, i] = self.__diff(self.flight["DepartureDate"], self.flight["DepartureTime"],
                    #                            data["DepartureDate"], data["DepartureTime"]) * 100
                else:
                    self.A[i, i] = 0
                if data["ArrivalAirport"] == self.flight["ArrivalAirport"]:
                    self.Na[i, i] = 1
                    self.B[i, i] = 1
                    self.Delay[i] = int(
                        self.__diff(self.flight["DepartureDate"], self.flight["DepartureTime"], data["ArrivalDate"],
                                    data["ArrivalTime"]) * 100)
                else:
                    self.B[i, i] = 0

                # Edges
                for j in range(self.length):
                    fl2 = self.lst[j]
                    if self.Nb[i, i] == 1 and i != j:
                        self.G[i, j] = 0
                    else:
                        # if data["InventoryId"] == fl2["InventoryId"]:
                        #     ti = self.__diff(self.flight["DepartureDate"], self.flight["DepartureTime"],
                        #                      fl2["DepartureDate"], fl2["DepartureTime"]) * 100
                        #     self.G[i, j] = ti
                        # else:
                        if data["DepartureAirport"] == fl2["ArrivalAirport"]:
                            self.Nb[i, j] = 1
                            ti = int(self.__diff(fl2["ArrivalDate"], fl2["ArrivalTime"], data["DepartureDate"],
                                                 data[
                                                     "DepartureTime"]) * 100)  # minutes(fl2["DepartureTime"]) - minutes(data["ArrivalTime"])
                            if ti < 6000 or ti > 72000:
                                self.G[i, j] = 0
                            else:
                                self.G[i, j] = ti
                        else:
                            self.G[i, j] = 0
                    if data["ArrivalAirport"] == fl2["DepartureAirport"]:
                        self.Na[i, j] = 1
        self.G = self.G.astype(int)


    def QAOA_algo(self) -> list:
        """
        Main Function of the Class
        Quadratic Program : 1. Objective Function - Q
                            2. Linear Constraints - A & B
                            3. Quadratic Constraints - N & G
        Why QUBO - Each flight has two options - Either it can be in the path or not
        :return: list of alternate flights as
        """
        qp = QuadraticProgram("flights")
        F = self.Q + self.G  # quadratic form matrix
        F = F.astype(int)

        # print(F)

        qp.minimize(linear=self.Delay, quadratic=F)  # matrices fed into the quadratic program
        qp.binary_var_list(self.length)
        qp.linear_constraint(np.ones(self.length, ), ">", 1)
        qp.linear_constraint(self.A.diagonal(), "=", 1)
        qp.linear_constraint(self.B.diagonal(), "=", 1)
        for i in range(self.length):
            linear = copy.deepcopy(self.Nb[i, :])
            linear[i] -= 1
            qp.linear_constraint(linear, ">", 0)
            print(linear)
        # qp.quadratic_constraint(-1*np.ones((self.length,)),self.Nb,"=",0)
        print(np.linalg.det(self.Na))
        start1 = dt.datetime.now()
        mod = qp.to_docplex()
        mod.solve()
        mod.print_solution()
        print(dt.datetime.now() - start1)
        # print(qp.prettyprint())
        # sys.exit(0)

        qp = QuadraticProgramToQubo().convert(qp)
        # qp.quadratic_constraint(quadratic=self.Nb,linear=-1*np.ones((self.length,)),sense="=",rhs=0)
        print(qp.prettyprint())

        # qubitOp, offset = qp.to_ising()  # conversion into Ising Problem

        two = TwoLocal(self.length, 'rx', 'cx', 'linear', reps=2, insert_barriers=True)  # an ansatz circuit

        start = dt.datetime.now()
        algorithm_globals.random_seed = 12345

        qaoa_mes = QAOA(sampler=Sampler(), optimizer=COBYLA())  # a qaoa instance of the quadratic program
        qaoa_mes.ansatz = two
        # ws_qaoa = WarmStartQAOAOptimizer(pre_solver=CobylaOptimizer(),relax_for_pre_solver=True,qaoa=qaoa_mes,epsilon=0.0)
        ws_qaoa = WarmStartQAOAOptimizer(pre_solver=CplexOptimizer(), relax_for_pre_solver=False, qaoa=qaoa_mes,
                                         epsilon=0.0)
        # qaoa = MinimumEigenOptimizer(qaoa_mes)
        ws_qaoa_result = ws_qaoa.solve(qp)
        print(ws_qaoa_result.prettyprint())

        ans = list(ws_qaoa_result.variables_dict.values())
        print(dt.datetime.now() - start)

        return ans

    def quantumSolve(self) -> list:
        """
        Linker between all working functions
        :return: list of suitable alternative flights
        """
        total = []
        self.__run()  # we will get the Q A B N G matrices initialised now
        prevAns = []
        # while True:
        for i in range(1):
            ans = self.QAOA_algo()
            # if ans == prevAns:
            #     break
            # prevAns=ans
            total.append([self.__postProcess(ans[:self.length])])
        return total

    def __postProcess(self, bitString: list) -> list:
        """
        Convert the output from QAOA_algo() function into a suitable format
        :param bitString:
        :return: list of flights corresponding to the bitString
        """
        flights = []
        isStarting = False
        isEnding = False  # TO check if path is complete (If not complete do no add this path)
        for i in range(len(bitString)):
            if bitString[i] == 1:
                flights.append(self.lst[i])
        #         if self.lst[i]["DepartureAirport"]==self.flight["DepartureAirport"]:
        #             isStarting=True

        #         if self.lst[i]["ArrivalAirport"]==self.flight["ArrivalAirport"]:
        #             isEnding=True
        # if not isEnding or not isStarting:
        #     return []
        for i in range(len(bitString)):
            if bitString[i] == 0:
                continue
            for j in range(len(bitString)):
                if bitString[j] == 1:
                    self.Q[i, j] = self.highval
        return flights
