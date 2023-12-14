from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister
from qiskit.circuit.library import XGate
from qiskit import Aer, execute
import numpy as np
import matplotlib.pyplot as plt


def init():  # Initialise the Walk Circuit
    circ = QuantumCircuit(coins, qubits, clas)
    circ.x(qubits[0])  # Position 1
    circ.h(coins[0])  # Coin vector put in superposition
    return circ


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
    qc.append(sub(coin, qubit), list(range(qc.num_qubits))) # add # sub
    qc.x(coin)
    return qc.to_gate()


def walk(coin, qubit, N):  # Walk N times
    for i in range(N):
        qc.append(evol(coin, qubit), list(range(qc.num_qubits)))


# Initialise
qubits = QuantumRegister(7, 'nodes')
coins = QuantumRegister(1, 'coins')
clas = ClassicalRegister(7, 'meas')

# Create and Run
qc = init()
walk(coins, qubits, len(qubits))
qc.measure(qubits, clas)

# Simulate and get the result
backend = Aer.get_backend('qasm_simulator')
result = execute(qc, backend, shots=1000).result()
counts = result.get_counts(qc)

# Plot the results
z = []
for k in counts.keys():
    z += [int(k, 2)]*counts[k]
plt.hist(z)
