The scheduling process splits the aircraft, crew and passengers into separate entities so that their scheduling and handling can happen independently.

The first step into the scheduling plan is route planning, which happens long before operating. This step optimally schedules all the airline’s flight routes throughout a specified period.

Traditionally, disruptions are solved sequentially: first, the airline’s operational control center OCC deals with rescheduling the aircraft, then the crew is reallocated to the new flight plan, and finally, the passengers’ itineraries are dealt with. The problem of recovering the aircraft schedule is known as the Aircraft Recovery Problem (ARP).

The ARP consists of delaying, canceling or swapping flights to recover the flight plan keeping the changes, delays and costs as low as possible.

Quadratic Unconstrained Binary Optimization

Input - $|x\rangle = |010001000\rangle$ 
Matrix $Q$ is Upper triangular.

Optimization problem:
$\max/\min y=x^{T}Qx$ 

Constrainted to Unconstrainted :
But why quadratic?

Present Classical Solutions:
1. Simulated Annealling
2. Hill Climbing
3. Particle Swarm Optimization (PSO)
	1. kind of multi-particle Hill Climbing
	2. seems to be better than HC
	3. no gradient
4. Ant Colony Optimization (ACO)
	1. Different particles/ants schotaiscally search for the solution (shortest path in a weighted edge graph)
	2. Different paths are compared
	3. Each path importance is updated (longer are decreased, shorter are increased)
Fastest - SA,PSO,HC,ACO
Cost - HC, PSO, SA, ACO

Rotations?

Difference between aircraft and flight - PNR?

Quantum-inspired Artificial Bee Colony:

Artifical Bee Colony Algorithm:
1. N scouts scattered across the space randomly
2. They evaluate the fitness level of N solutions
3. Out of N solutions, $N_1$ best solutions are taken
4. The neighborhood of the solution is searched for better solutions, and the neighborhood is shrunk
5. Local Maxima - stop for a neighborhood
6. Repeat

Hard Change
1. unavoidable delays/canceling
2. affects mulitple flights

Soft Change
1. Swapping aircrafts

<h4>Two Stage Hueristic Algorithm</h4>
LOFs are a sequence of feasible flights that can be flown by an aircraft on a given day. 

![[Pasted image 20231118134512.png]]

Initialization: Classical 
All feasible LOFs are generated
Generated graphs 

Use networkx module in python

Graph Structure:

![[Pasted image 20231118172002.png]]

1. Node - A flight an aircraft can perform
2. Edge - Connection between two flights an aircraft can perform sequentially
	1. Contains delay in performing the two sequential flights (actual arrival time - scheduled arrival time + minimum rotation time) calculated through:
		 ![[Pasted image 20231118142802.png]]
	2. Each edge has a unique key marking the cumulative path

3. Mulitple edges between nodes possible, as different delays based on different paths of an aircraft

AAT - Actual Arrival Time for flight f
SAT - Scheduled Arrival Time for flight f
TD - Total delay from previous flights 
PD - Propagation Delay
MTT - Minimum Turn Time
SDT - Scheduled Departure Time
DD - Disruption Time

Generation Process:
1. Root Node - Flight after which the disruption occured 
2. See that a disruption occured at an airport
3. Find other possible flights which can be taken from that airport 
4. Build a graph recursively
![[Pasted image 20231118135419.png]]

Stage 1 : Classical 
Iterate through each aircraft feasible flights graph and remove the paths that are most costly (if edge delay > a constant)
They are scored, and sorted (only the ones with evaluation below a threshold are kept, rest removed)

![[Pasted image 20231118152514.png]]

Stage 2: Quantum
So we model the QUBO
Binary variables - $q_{f,a}$ represents flight $f$ assigned to aircraft $a$
We iterate through the graphs and add one binary variable at a time

$C = P_{a} + P_{b} + P_{di} + P_{s} + P_{dq} +C_{OF}$
1. $P_{a}$ - Assignment Penalty
	1. Only one aircraft per flight
	2. Minus 1 as one of them will be assigned which cannot be a penalty
2. $P_{b}$ - Impossible Pairing Penalty
	1. Simulataneous assignments of flights with no valid path
3. $P_{di}$ - Initial Delay
	1. total delay due to disruptions
4. $P_{s}$ - Swap Delay
5. $P_{dq}$ - Quadratic Delay
	1. For a particular aircraft, we go through the two consecutive flights and add the delay for it to perform both the flights (TD = PD + DD)
	2. Used only in the case of 1 edge
6. $C_{OF}$ - Cost of Objective Function

These Penalties and objective function is used to generate a Quadratic Matrix

[Qiskit Optimization](https://qiskit.org/ecosystem/optimization/apidocs/qiskit_optimization.html) Quadratic Program

Final:
Solve the QUBO and evaluate the solution

<b>First construct LOFs</b>

Constraints -
the arrival destination from a flight must be identical to the departure of the next flight, and the time between both flights must be within a defined interval $T_{min}, T_{max}$, where $T_{min}$ might be a negative value to allow delays on the departure.

After LOFs are generated, an Aircraft Recovery Network
is constructed by assigning each LOF to every available aircraft. The only constraint in this phase is that if there is a maintenance plan in a LOF, it must be assigned only to the aircraft assigned to
the maintenance.

With the network, it generates an Aircraft Recovery Model with the objective function to minimize costs and the required constraints.

<h2>Problem in Generation of LOFs - Exponential </h2>
