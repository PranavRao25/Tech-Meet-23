from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import XGate
import numpy as np
import matplotlib.pyplot as plt

def init(qc, qubits, coins): 
    qc.x(qubits[0])  # Start at the first node
    qc.h(coins[0])   # Coin vector put in superposition

def add(qc, coin, qubits):
    qc.cx(coins[0], qubits[0])
    for i in range(1, len(qubits)):
        for j in range(i):
            qc.x(qubits[j])
        qc.append(XGate().control(i+1), [coins[0]] + [qubits[j] for j in range(i+1)])
        for j in range(i):
            qc.x(qubits[j])

def sub(qc, coin, qubits):
    for i in range(1, len(qubits)):
        for j in range(i):
            qc.x(qubits[j])
        qc.append(XGate().control(i+1), [coins[0]] + [qubits[j] for j in range(i+1)])
        for j in range(i):
            qc.x(qubits[j])
        qc.cx(coins[0], qubits[0])

def evol(qc, coin, qubits):
    qc.h(coin)
    add(qc, coin, qubits)  # add
    qc.x(coin)
    sub(qc, coin, qubits)  # sub
    qc.x(coin)

def walk_to_target(qc, target_node, qubits, coins): 
    # Walk until the target node is reached
    while qc.qubits[qubits[0]].index != target_node:
        evol(qc, coins[0], qubits)

qubits = QuantumRegister(7, 'nodes')
coins = QuantumRegister(1, 'coins')
clas = ClassicalRegister(7, 'meas')
qc = QuantumCircuit(coins, qubits, clas)

# Set the target node (last node) for the path
target_node = 6

init(qc, qubits, coins)
walk_to_target(qc, target_node, qubits, coins)
qc.measure(qubits, clas)

# Simulate and get the result
from qiskit import Aer, execute

backend = Aer.get_backend('qasm_simulator')
result = execute(qc, backend, shots=1000).result()
counts = result.get_counts(qc)

# Print the result
print("Measurement outcomes:", counts)