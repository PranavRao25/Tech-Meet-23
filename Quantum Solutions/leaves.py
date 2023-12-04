from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import XGate
import numpy as np
import matplotlib.pyplot as plt
from qiskit import Aer, execute
import networkx as nx

G = nx.Graph() # original graph
G.add_nodes_from(list(range(12)))
G.add_edges_from([
    (0,1),(0,2),(0,3),
    (1,0),(1,4),(1,5),
    (2,0),(2,6),
    (3,0),(3,7),
    (4,1),(4,8),
    (1,5),(5,9),
    (6,2),
    (7,3),(7,10),(7,11),
    (8,4),
    (9,5),
    (10,7),
    (11,7)
])

G1 = nx.Graph() # Edge Graph
G1.add_nodes_from(G.edges())
for i in G1.nodes():
    for j in G1.nodes():
        if(i!=j and (i[0]==j[0] or i[1]==j[0] or i[0]==j[1] or i[1]==j[1])):
            G1.add_edge(i,j)

# Classical
curN = 0
while(list(G.neighbors(curN))!=[]):
    r = np.random.choice(list(G.neighbors(curN)))
    curE = (curN,r)
    print(r)
    if(curE in G1.nodes()):
        print(curE)
    if(r in [6,8,9,10,11]):
        break
    curN = r

# Quantum
curN = 0
while (True):
    ngb = list(G.neighbors(curN))

# What is needed : Probabilities (sounds like Q Learning)

start = [0]
current = [0]
visited = [0]
target = {6,8,9,10,11}

def init():  # Initialise the Walk Circuit
    qc = QuantumCircuit(coins, qubits, clas)
    qc.h(coins)  # Coin vector put in superposition
    return qc


def coinOp():
    qc.h(coin)  # coin

    # add new points according to probability
    for i in list(set(current).difference(set(visited))):
        visited.append(i)
        current += list(G.neighbors(i))

    # check
    return (not set(current).isdisjoint(target))

def add(coin, qubit):  # Increment the position value
    qc = QuantumCircuit(coin, qubit)
    qc.cx(coin[0], qubit[0])
    for i in range(1, len(qubit)):
        for j in range(i):
            qc.x(qubit[j])
        qc.append(XGate().control(i+1), [coin[0]]+[qubit[j] for j in range(i+1)])
        for j in range(i):
            qc.x(qubit[j])
    return qc.to_gate()

def sub(coin, qubit):  # Decrement the position value
    qc = QuantumCircuit(coin, qubit)
    for i in range(1, len(qubit)):
        for j in range(i):
            qc.x(qubit[j])
        qc.append(XGate().control(i+1), [coin[0]]+[qubit[j] for j in range(i+1)])
        for j in range(i):
            qc.x(qubit[j])
        qc.cx(coin[0], qubit[0])
    return qc.to_gate()

def evol(coin, qubit):  # Evolution of the walker vector with coin vector
    qc = QuantumCircuit(coin, qubit)
    qc.h(coin)
    qc.append(add(coin, qubit), list(range(qc.num_qubits))) # add
    qc.x(coin)
    qc.append(sub(coin, qubit), list(range(qc.num_qubits))) # sub
    qc.x(coin)
    return qc.to_gate()

def walk(coin, qubit, N):  # Walk N times
    for i in range(N):
        qc.append(evol(coin, qubit), list(range(qc.num_qubits)))

qubits = QuantumRegister(4, 'nodes')
coins = QuantumRegister(2, 'coins')
clas = ClassicalRegister(4, 'meas')

qc = init()
walk(coins, qubits, len(qubits))
qc.measure(qubits, clas)