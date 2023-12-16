import pandas as pd
import numpy as np
import datetime as dt
from qiskit_algorithms import QAOA
from qiskit_optimization.problems import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo
import copy
from qiskit_algorithms import NumPyMinimumEigensolver
from qiskit_optimization.algorithms import MinimumEigenOptimizer, WarmStartQAOAOptimizer, CplexOptimizer
from qiskit.primitives import Sampler
from qiskit_algorithms.optimizers import COBYLA
from qiskit_algorithms.utils.algorithm_globals import algorithm_globals

"""
    We are creating a QUBO instance of a Quadratic Program and solving it using Warm Start QAOA.
     
    Quantum Solver Class does the following:
    1. takes as an input the affected flight's inventory id
    2. maintains an list of relevant flights
    3. Creates the appropriate Quadratic Program
    4. Converts it into QUBO instance
    5. Solve it using Warm Start QAOA (we use classical optimiser as either Cplex or COBYLA)
    6. Return the list of alternate flights 
    
    What the user needs to do:
    1. Setup an object of the QuantumSolver
    2. Call solve() method
    
    Flow of the functions:
    1. __init__
    2. __preProcess
    
    1. solve()
    2. quantumSolve()
    3. __run()
    4. QAOA_algo()
    5. __postProcess()
"""


class QuantumSolver:
    """
    Create Object of this class with required arguments .
    Call Solve method to solve the problem.
    """
    df = None  # INV.csv
    highval = 1000000  # used for incresing the weight of matrix
    inv_id: str  # stores the affected flight inventory id
    flight = None  # affected flight row
    FullList: dict  # Stores InventoryId of all the disrupted flights
    # =========
    # matrices to be used in Quadratic Program
    MatFlightTime: np.ndarray  # Stores flight time of xi th flight. This will be also used to remove already got solutions.
    MatArrArp: np.ndarray  # 1 if ith flight is departure airport = impacted flight departure airport
    MatDepArp: np.ndarray  # 1 if ith flight is Arrival airport = impacted flight Arrival airport
    MatNeigh: np.ndarray  # 1 if ith flight have a flight whose arrivalAirport == departureAirport else 0
    MatGndDelay: np.ndarray  # stores the ground delay between ith and jth flight.
    MatTltDelay: np.ndarray  # stores total delay if this node is the last node(This remains zero for all flights whose arrival  airport is not = arrival airport of impacted flight)

    # ========

    def __init__(self, inv_id, ImpactedFlights: dict, inFile):
        """
            Input :
                inv_id:Corresponding inventory id of affected flight from the provided datafile
                ImpactedFlights: Dictionary of all the impacted flights
                inFile: Input File To take the flights from

            Creates a list of relevant flights, initializes matrices, and calls the QuantumSolve() function
        """

        self.df = pd.read_csv(inFile)

        self.inv_id = inv_id
        self.FullList = ImpactedFlights

        self.lst = self.__preProcess()  # list of relevant flights
        if len(self.lst) == 0:  # no relevant flights present
            raise Exception('No alternate flights')
        print(len(self.lst), "Feasible Flights\n")

        self.length = len(self.lst)
        self.length = min(self.length, 10)

        # #===============
        # #Temporary ::saves all the selected flights to be used by the solver . Turn This on to see all the selected flights.

        # file=open("Selected Flights","w")
        # for i in self.lst[:self.length]:
        #     file.write(str(i)+"\n\n")
        # file.close()
        # #===============

        # Initializing above-mentioned flights
        self.MatFlightTime = np.zeros((self.length, self.length))
        self.MatNeigh, self.MatGndDelay = np.zeros_like(self.MatFlightTime), np.zeros_like(self.MatFlightTime)
        self.MatArrArp, self.MatDepArp, self.MatTltDelay = np.zeros((self.length,)), np.zeros((self.length,)), np.zeros(
            (self.length,))

        print("\nAffected Flight\n")
        print(self.flight)

    def solve(self):
        """
        Returns the list of all the alternate solutions in order of best to worse.
        """
        startTime = dt.datetime.now()
        ans = self.quantumSolve()  # invoke the quantum solve function
        TimeTaken = (dt.datetime.now() - startTime)
        print("TimeTaken:", TimeTaken)

        return ans

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

        # refer to above rule set to check which rule is being implemented

        index = self.df.loc[self.df["InventoryId"] == self.inv_id].index[0]  # get the index from the dataset
        self.flight = self.df.loc[index]  # affected flight
        list_of_feasible_flights = []
        impactedFlightStatus = self.FullList.get(self.flight["InventoryId"])
        currFlTime = self.__diff(date1=self.flight["DepartureDate"], time1=self.flight["DepartureTime"],
                                 date2=self.flight["ArrivalDate"],
                                 time2=self.flight["ArrivalTime"])  # store flight time of impacted flight.
        arrivalsAt = dict()
        departsAt = dict()

        for i in range(len(self.df)):
            data = self.df.loc[i]
            if index == i:
                continue
            fromlst = self.FullList.get(data["InventoryId"])
            if fromlst:
                if fromlst == "Cancelled":  # If Flight is cancelled then do not add it. rule 8
                    continue
            if data["ArrivalAirport"] == self.flight["DepartureAirport"] or data["DepartureAirport"] == self.flight["ArrivalAirport"]:  # rule 5,6
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

            if impactedFlightStatus != "Cancelled" and self.__diff(date1=self.flight["ArrivalDate"],
                                                                   time1=self.flight["ArrivalTime"],
                                                                   date2=data["ArrivalDate"],
                                                                   time2=data[
                                                                       "ArrivalTime"]) > 0:  # rule 9 If this flight is not cancelled then do not consider any flight taking more time than this.
                continue
            if timebtwArr_Curdep < 60 or timebtwdep_CurrDep > 72 * 60:  # rule 1,2,3  # following the Minimum Ground Time and Maximum Connecting Time
                continue
            elif flightTime > currFlTime and data["DepartureAirport"] != self.flight["DepartureAirport"] \
                    and data["ArrivalAirport"] != self.flight["ArrivalAirport"]:  # rule 4
                continue
            else:
                list_of_feasible_flights.append(data)
                if data["ArrivalAirport"] in arrivalsAt.keys():
                    arrivalsAt[data["ArrivalAirport"]] += 1
                else:
                    arrivalsAt[data["ArrivalAirport"]] = 1
                if data["DepartureAirport"] in departsAt.keys():
                    departsAt[data["DepartureAirport"]] += 1
                else:
                    departsAt[data["DepartureAirport"]] = 1

        for fl in list_of_feasible_flights:  # Removes all those flights for which no other flights preceeds them or no other flight succeed them
            if (fl["DepartureAirport"] not in departsAt.keys() or fl["ArrivalAirport"] not in arrivalsAt.keys()) and fl[
                "DepartureAirport"] != self.flight["DepartureAirport"] and \
                    fl["ArrivalAirport"] != self.flight["ArrivalAirport"]:
                list_of_feasible_flights.remove(fl)

        return list_of_feasible_flights

    def __run(self):
        """
            Creates the Matrices required for the Quadratic Program
        """
        ConsideredFlights = dict()  # to keep a tally of unique flights

        # Nodes
        for i in range(self.length):
            data = self.lst[i]  # a single flight

            if data["InventoryId"] not in ConsideredFlights:
                ConsideredFlights[data["InventoryId"]] = (
                    data["DepartureAirport"],
                    data["ArrivalAirport"],
                    data["DepartureDate"],
                    data["DepartureTime"],
                    data["ArrivalTime"],
                    data["ArrivalDate"]
                )

                # Q Matrix measures the total time taken by the flight (Arr - Dep of the flight)
                self.MatFlightTime[i, i] = self.__diff(data["DepartureDate"], data["DepartureTime"],
                                                       data["ArrivalDate"],
                                                       data["ArrivalTime"]) * 100

                # putting values to the matrices as defined above
                if data["DepartureAirport"] == self.flight["DepartureAirport"]:
                    self.MatArrArp[i] = 1
                    self.MatNeigh[i, i] = 1
                else:
                    self.MatArrArp[i] = 0
                if data["ArrivalAirport"] == self.flight["ArrivalAirport"]:
                    self.MatDepArp[i] = 1
                    self.MatTltDelay[i] = int(
                        self.__diff(self.flight["DepartureDate"], self.flight["DepartureTime"], data["ArrivalDate"],
                                    data["ArrivalTime"]) * 100)
                else:
                    self.MatDepArp[i] = 0

                # Edges
                for j in range(self.length):
                    fl2 = self.lst[j]
                    if self.MatNeigh[i, i] == 1 and i != j:
                        self.MatGndDelay[i, j] = 0
                    else:
                        if data["DepartureAirport"] == fl2["ArrivalAirport"]:
                            self.MatNeigh[i, j] = 1
                            ti = int(self.__diff(fl2["ArrivalDate"], fl2["ArrivalTime"], data["DepartureDate"],
                                                 data[
                                                     "DepartureTime"]) * 100)  # minutes(fl2["DepartureTime"]) - minutes(data["ArrivalTime"])
                            if ti < 6000 or ti > 72000:
                                self.MatGndDelay[i, j] = self.highval
                                self.MatNeigh[i, j] = 0
                            else:
                                self.MatGndDelay[i, j] = ti
                        else:
                            self.MatGndDelay[i, j] = 0

        self.MatGndDelay = self.MatGndDelay.astype(int)

    def QAOA_algo(self) -> list:
        """
        Main Function of the Class
        Quadratic Program : 1. Objective Function - MatFlightTime+MatGndDelay + MatTltDelay(linear)
                            2. Linear Constraints - MatArrArp & MatDepArp
                            3. Quadratic Constraints - MatNeigh
        Why QUBO - Each flight has two options - Either it can be in the path or not
        :return: list of alternate flights as
        """
        qp = QuadraticProgram("flights")
        F = self.MatFlightTime + self.MatGndDelay  # quadratic form matrix
        F = F.astype(int)

        qp.minimize(linear=self.MatTltDelay, quadratic=F)  # matrices fed into the quadratic program
        qp.binary_var_list(self.length)
        qp.linear_constraint(np.ones(self.length, ), ">", 1)  # at least 1 flights must be selected
        # qp.linear_constraint(np.ones(self.length, ), "<", 5)  # Maximum 5 flights must be selected
        qp.linear_constraint(self.MatArrArp, "=",
                             1)  # There must be only and necessarily 1 flight with departureAirport = DepartureAirport of impacted flight
        qp.linear_constraint(self.MatDepArp, "=",
                             1)  # There must be only and necessarily 1 flight with ArrivalAirport = ArrivalAirport of impacted flight
        for i in range(self.length):  # Applies the constraint that if a flight is on(1) then there must at least 1 neighbouring flight that is on(1)
            linear = copy.deepcopy(self.MatNeigh[i, :])
            linear[i] -= 1
            qp.linear_constraint(linear, ">", 0)

        # qp = QuadraticProgramToQubo().convert(qp)
        print("Variables : ", qp.get_num_binary_vars)

        # Classical Solver
        # start1 = dt.datetime.now()
        # ws_qaoa_result=(CplexOptimizer().solve(qp))
        # print(dt.datetime.now() - start1)
        # print(qp.prettyprint())

        # Quadratic  Solver

        # qubitOp, offset = qp.to_ising()  # conversion into Ising Problem

        # start = dt.datetime.now()

        algorithm_globals.random_seed = 12345
        qaoa_mes = QAOA(sampler=Sampler(), optimizer=COBYLA(maxiter=2))  # a qaoa instance of the quadratic program

        # ws_qaoa = WarmStartQAOAOptimizer(pre_solver=CobylaOptimizer(),relax_for_pre_solver=True,qaoa=qaoa_mes,epsilon=0.0)
        ws_qaoa = WarmStartQAOAOptimizer(pre_solver=CplexOptimizer(), relax_for_pre_solver=False, qaoa=qaoa_mes, epsilon=0.0)
        ws_qaoa_result = ws_qaoa.solve(qp)

        # print(ws_qaoa_result.variables_dict.values())
        ans = list(ws_qaoa_result.variables_dict.values())
        # print(dt.datetime.now() - start)

        return ans

    def quantumSolve(self) -> list:
        """
        Linker between all working functions
        :return: list of suitable alternative flights
        """
        total = []
        self.__run()  # we will get the Q A B N G matrices initialised now
        prevAns = []

        # Runs the algorithm to get maximum number of solutions
        while True:
            ans = self.QAOA_algo()
            if ans == prevAns or ans in total:
                break
            prevAns = ans
            if len(prevAns) == 0:
                break
            total.append([self.__postProcess(ans[:self.length])])

        return total

    def __postProcess(self, bitString: list) -> list:
        """
        Convert the output from QAOA_algo() function into a suitable format
        :param bitString:
        :return: list of flights corresponding to the bitString
        """
        path = []
        isStarting = False
        isEnding = False  # TO check if path is complete (If not complete do not add this path)
        for i in range(len(bitString)):
            if bitString[i] == 1:
                added = False
                # Loop to add the flights to the path in order that is like A->B,B->C ... not like B->C,A->B,...
                for idx in range(len(path)):
                    if path[idx]["ArrivalAirport"] == self.lst[i]["DepartureAirport"]:
                        path = path[:idx + 1] + [self.lst[i]] + path[idx + 1:]  # Add this flight before idx th flight
                        added = True
                        break
                    if self.lst[i]["ArrivalAirport"] == path[idx]["DepartureAirport"]:
                        path = path[:idx] + [self.lst[i]] + path[idx:]  # Add this flight after idx th flight
                        added = True
                        break

                if self.lst[i]["DepartureAirport"] == self.flight["DepartureAirport"]:
                    isStarting = True
                    if not added:
                        path = [self.lst[i]] + path  # Adds this flight to very start of the path.
                    added = True

                if self.lst[i]["ArrivalAirport"] == self.flight["ArrivalAirport"]:
                    isEnding = True
                if not added:
                    path.append(self.lst[i])  # Adds this flight to last of the path
        if not isEnding or not isStarting:
            return []

        # to increase the value of objective function for this path so that next time solver do not consider this flight again.
        for i in range(len(bitString)):
            if bitString[i] == 0:
                continue
            for j in range(len(bitString)):
                if bitString[j] == 1 and i != j:
                    self.MatFlightTime[i, j] = self.highval
                    self.MatFlightTime[j, i] = self.highval

        return path
