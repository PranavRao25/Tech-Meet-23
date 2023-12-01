from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister
from qiskit.circuit.library import XGate
import numpy as np
import matplotlib.pyplot as plt

def init(qc): # Initialise the Walk Circuit
    qc.x(qubits[0]) # Position 1
    qc.h(coins[0]) # Coin vector put in superposition

def add(coin,qubit): # Increment the position value
    qc.cx(coins[0],qubits[0])
    for i in range(1,len(qubits)):
        for j in range(i):
            qc.x(qubits[j])
        qc.append(XGate().control(i+1),[coins[0]]+[qubits[j] for j in range(i+1)])
        for j in range(i):
            qc.x(qubits[j])

def sub(coin,qubit): # Decrement the position value
    for i in range(1,len(qubits)):
        for j in range(i):
            qc.x(qubits[j])
        qc.append(XGate().control(i+1),[coins[0]]+[qubits[j] for j in range(i+1)])
        for j in range(i):
            qc.x(qubits[j])
        qc.cx(coins[0],qubits[0])

def evol(coin,qubit): # Evolution of the walker vector with coin vector
    qc = QuantumCircuit(coin,qubit)
    qc.h(coin)
    add(coin,qubit) # add
    qc.x(coin)
    sub(coin,qubit) # sub
    qc.x(coin)


def walk(qc,N): # Walk N times
    lr = np.random.bit_generator
    for i in range(N):
        evol(qc,np.random.randint(2))

qubits = QuantumRegister(7,'nodes')
coins = QuantumRegister(1,'coins')
clas = ClassicalRegister(7,'meas')
qc = QuantumCircuit(coins,qubits,clas)
init(qc)
walk(qc,len(qubits))
qc.measure(qubits,clas)
