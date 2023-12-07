'''
This code is currently incomplete (oracle, checker is left to be done).
Rem function (remover) is not in this file, it will be added later (probably by priyanshu or pranav).
Proceed with caution.
'''

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import XGate,MCXGate
from qiskit.circuit import AncillaQubit,Qubit
import numpy as np
import remover

de = 4 # de = (K+B)*maxde (max no of bits)
ext = 2 # used by remover
delta = 6 # delta = max no of edges
maxde = 10 # maximum depth
count = 0
K = int(np.ceil(np.log2(delta+1))) # Getting no of bits required to represent delta+1, K = ceil(log2(delta + 1))
qK = QuantumRegister(K) # branching qubits
rem = QuantumRegister(ext) # required for remover
orc = QuantumRegister(2) # required for oracle
B = QuantumRegister(3) # represents the actual value
removeCircuit = remover.createRemoverCircuits(de,ext,delta,K) # list of remove circuits

def init():
    qc = QuantumCircuit(rem,orc,K,B)
    qc.x(rem.size+orc.size)
    for i in K: # O(K)
        qc.h(i)
    for i in B: # O(B)
        qc.h(i)
    return qc

def calc(qc): # 1 iteration - O(maxde*(de+K+?))
    oracle(qc) # O(?)
    for i in range(1, de - 1 - delta): # O(de - delta)
        qc.append(removeCircuit[i],list(range(qc.num_qubits)))
    q = QuantumCircuit(qc.num_qubits+K.size+B.size).compose(qc,list(range(qc.num_qubits)))
    # Reassign remover circuit
    # count+=1
    for i in range(qc.num_qubits,qc.num_qubits+K.size): # O(K)
        q.h(i)
    '''
    for i in range(delta):
        qc.append(MCXGate(K,(2,3)),target = removeCircuit[i])
    '''
    calc(q)

def oracle(qc): # check the qc if in target state (yes, then remove all), get current node edges
    if(qc in target_conditions): # target conditions left to figure out
        v = rem.size + orc.size + ((qc.num_qubits - rem.size - orc.size)//(qK.size+B.size) -1)*(qK.size+B.size)-1
        n = node(v) # given the qubits of B, return the corresponding vertex
        X = # no of edges of current node left to figure out, get edges from n
        qc.append(removeCircuit[K-X],qc.num_qubits) #

def checker(i):
    ck = QuantumCircuit(K+1)
    for i in range(K):
        ck.x(i)
    ck.append(XGate().control(list(range(K))),QuantumRegister(ck.num_qubits))
    for i in range(K):
        ck.x(i)
    return ck.to_gate()


def node(n): # get the value of the last B register
    anc = ClassicalRegister(1)
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