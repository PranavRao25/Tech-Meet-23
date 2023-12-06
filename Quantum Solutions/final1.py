'''
This code is currently incomplete (oracle, checker is left to be done).
Rem function (remover) is not in this file, it will be added later (probably by priyanshu or pranav).
Proceed with caution.
'''

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import XGate
from qiskit.circuit import AncillaQubit,Qubit
import numpy as np

de = 4
ext = 2
maxde = 10
count = 0
K = int(np.log2(de+1))

def init():
    start = QuantumRegister(K+ext)
    qc = QuantumCircuit(start)
    qc.x(0)
    for i in start:
        qc.h(i)
    return qc

def calc(qc):
    oracle(qc)
    edge = 2
    for i in range(1, de - 1 - edges):
        qc.append(rem(qc,i),list(range(qc.num_qubits)))
    q = QuantumCircuit(qc.num_qubits+K).compose(qc,list(range(qc.num_qubits)))
    count+=1
    for i in range(qc.num_qubits,q.num_qubits):
        q.h(i)
    calc(q)

def oracle(qc):
    if(qc in target_conditions): # target conditions left to figure out
        #X = no of edges of current node left to figure out
        n = node(qc.num_qubits)
        qc.append(rem(qc,K-X),qc.num_qubits)

def checker(i):
    ck = QuantumCircuit(K+1)
    for i in range(K):
        ck.x(i)
    ck.append(XGate().control(list(range(K))),QuantumRegister(ck.num_qubits))
    for i in range(K):
        ck.x(i)
    return ck.to_gate()


def node(n):
    anc = QuantumRegister(1)
    w = QuantumRegister(n)
    nc = QuantumCircuit(w + 1, anc)
    nc.reset(n)
    nc.append(checker(0), list(range(K)) + [n])
    nc.measure(n, anc[0])
    with nc.if_test((anc[0], 1)) as else_:
        for i in range(K):
            nc.reset(n)
            nc.append(checker(i), list(range(K, 2 * K)) + [n])
            nc.measure(n, anc[0])
            with nc.if_test((anc[0], 1)):

    with else_:

qc = init()
# calc(qc)