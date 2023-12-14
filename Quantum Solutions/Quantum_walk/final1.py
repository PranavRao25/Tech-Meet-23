'''
THIS CODE IS CURRENTLY ON HOLD.
This code is currently incomplete (oracle, checker is left to be done).
Proceed with caution.
'''

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import XGate,MCXGate
from qiskit.circuit import AncillaQubit,Qubit
import numpy as np
import remover


delta = 6 # delta = max no of edges
maxde = 10 # maximum depth
count = 0
K = int(np.ceil(np.log2(delta+1))) # Getting no of bits required to represent delta+1, K = ceil(log2(delta + 1))
ext = 2 # used by remover

qK = QuantumRegister(K) # branching qubits
rem = QuantumRegister(ext) # required for remover
orc = QuantumRegister(K+1) # required for oracle
B = QuantumRegister(3) # represents the actual value
measuringReg= ClassicalRegister(3) # represents classical register
de = (2*K+B.size) # de = (K+B)*maxde (max no of bits)

ctrlBits=[i for i in range(de+ext)] #

remCirs = [] #

# 00 state is the end state

def init(): # initialise the circuit
    qc = QuantumCircuit(rem,orc,qK,B,measuringReg)
    qc.x(rem.size+orc.size) # starting in 01 state
    for i in qK: # O(K)
        qc.h(i)
    for i in B: # O(B)
        qc.h(i)

    return qc

def calc(qc:QuantumCircuit,remCircuits):
    # main driver function (it is used for finding the leaves, target nodes, and search through the graph)
    # 1 iteration - O(maxde*(de+K+?))
    # oracle(qc) # O(?)

    # for i in range(1, de - 1 - delta):
        # add remover circuits so that the answer output by oracle will be used and rest will be removed
        # O(de - delta)
      #   qc.append(remCircuits[i],list(range(qc.num_qubits)))
    q = QuantumCircuit(qc.num_qubits+qK.size+B.size).compose(qc,list(range(qc.num_qubits))) # add K+B qubits
    # de is the total encoding qubits (doesn't contain the rem and orc)

    remCircuits = createRemoverCircuits(de,ext,delta,K,B.size) # list of remove circuits (call again as no of qubits have increased)

    # count+=1
    for i in range(qc.num_qubits,qc.num_qubits+qK.size+B.size): # put all of the children into superposition
        q.h(i)

    # call oracle
    oracle(qc)
    for cir in remCircuits: # append remover circuits
        qc.append(cir,ctrlBits)

    return qc
    # calc(q)

def oracle(qc):
    # if check if the current circuit or the qubit state contains target node or leaf node
    end = de + ext + orc - 1 # last qubit
    n = end - qK.size # last B register starting index
    l = n - B.size # to get the last K value
    v = node(qc,l,n) # it will take circuit qubit state and output the corresponding parent vertex

    # cross check if v is target node

    ch = [] # childern of the vertex v
    for i in ch: # check for target nodes
        if(i in target_conds): # i is target node
            ###
            qc.reset(end,last) # set K value, set B value as target, set everything else to 0
    else: # currently no target nodes
        for i in range(len(ch)+1,de+1): # remove the extra states
            oracleSet(len(ch)) # set oracle bits as len(ch) (remove the extra ones)
        b = [encode(i) for i in range(ch) if(not visited(ch))] # set b value of the childern
        superP(qc,de + ext + orc - 1,de + ext + orc - 1 - B.size,b) # superpose the B register with the values in b

    # which child to fill? (maybe through superposition of the B register)

    # check the qc if in target state (yes, then remove all), get current node edges
    # if(qc in target_conditions): # target conditions left to figure out

    #     v = rem.size + orc.size + ((qc.num_qubits - rem.size - orc.size)//(qK.size+B.size) -1)*(qK.size+B.size)-1
    #     n = node(v) # given the qubits of B, return the corresponding vertex
    #     X = # no of edges of current node left to figure out, get edges from n
    #     qc.append(removeCircuit[K-X],qc.num_qubits) #


    qc=Oracle2(qc,de,ext,K,B.size,delta,searchNode="001") #

def checker(i):
    ck = QuantumCircuit(K+1)
    for i in range(K):
        ck.x(i)
    ck.append(XGate().control(list(range(K))),QuantumRegister(ck.num_qubits))
    for i in range(K):
        ck.x(i)
    return ck.to_gate()


def node(n): # get the value of the last B register, convert into bitstring and return the corresponding vertex
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
                pass

    with else_:
        pass

def oracleSet(qc,n): # will set the oracle bits to the given value n
binary = bin(n)[2:].rjust(K,'0') # get bitstring of n
for i in range(len(binary)): # whenever we see a 1, we add a X Gate to the circuit
    if(binary[i]=='1'):
        qc.x(ext+1+i)

qc = init()
removeCircuits = createRemoverCircuits(de,ext,delta,K,B.size) # list of remove circuits
qc=calc(qc,removeCircuits)
qc.draw()
# calc(qc)