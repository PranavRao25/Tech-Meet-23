import math
from qiskit import QuantumCircuit
from qiskit.circuit.library import MCXGate

def createRemoverCircuits(de,ext,delta,K)-> list:
    removeCircuits = []
    ctrl_bits=[de+ext-1-i for i in range(K-1, -1, -1)]+[0]
    # print(ctrl_bits)
    for i in range(delta,-1,-1):
        circuit= QuantumCircuit(de+ext) ## Creating new quantum circuit (remover{i})

        ## adding control on value of above K elements from value delta to 0 and then appending the remover circuits
        for j in range(0,i):
            binaryOfj=bin(delta-j)[2:].rjust(K,'0')
            circuit.append(MCXGate(num_ctrl_qubits=K,ctrl_state=binaryOfj),ctrl_bits)
            circuit=removeAll(circuit,de,ext)

        removeCircuits.append(circuit)

## remover circuit
def removeAll(qc:QuantumCircuit,de,ext)-> QuantumCircuit:
    for i in range(de):
        qc.cswap(0,i+ext,1)
        qc.reset(1)

    qc.reset(0)
    return qc