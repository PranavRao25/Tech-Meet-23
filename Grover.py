"""
    This is an ongoing circuit implementation of Grover's Algorithm
    Leftout work:
    2. Defining Oracle appropriately
    3. Execution
    (Delay by 4:30 hrs)
"""


from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np

n = 10
a = [np.random.randint(0, 5) for i in range(100)]  # required soln


def function(x):  # oracle
    return 1 if (x in a) else 0


def cnx(n):
    # Multi-qubit CX Gate
    qc = QuantumCircuit(n)

    if n == 2:
        qc.cx(n - 2, n - 1)
    elif n == 3:
        qc.ccx(n - 3, n - 2, n - 1)
    else:
        qc.crz(np.pi / 2, n - 2, n - 1)
        qc.cu(np.pi / 2, 0, 0, 0, n - 2, n - 1)
        qc.append(cnx(n - 1), [i for i in range(n - 2)] + [n - 1])
        qc.cu(-np.pi / 2, 0, 0, 0, n - 2, n - 1)
        qc.append(cnx(n - 1), [i for i in range(n - 2)] + [n - 1])
        qc.crz(-np.pi / 2, n - 2, n - 1)

    return qc.to_gate()


def oracle(chk, work, com):
    # w : no of working bits
    # frame the appropriate oracle problem
    # it will choose the solutions which match the condition
    # write a circuit according to your condition using function
    # N computing qubits, W working qubits, 1 checker qubit
    # circuit division :
    # 1. Different condition clauses
    # 2. Result into checker bit
    # 3. uncomputation
    orc = QuantumCircuit(chk,work,com)
    # Step 1
    # Step 2
    # Step 3
    return orc.to_gate()


def diffuser(chk, work, com):
    # to amplify the correct solution
    # N computing qubits, 1 checker qubit
    N = len(chk) + len(work) + len(com)
    dif = QuantumCircuit(chk, work, com)

    for i in range(len(com)):
        dif.x(com[i])

    # amplification
    dif.append(cnx(len(com) + len(chk)), [i for i in range(len(chk))] + [i for i in range(N - len(com), N)])

    for i in range(len(com)):
        dif.x(com[i])
    return dif


def grover_Algo(n):  # n is no of qubits
    w = 3  # to be defined
    c = 1  # to be defined
    N = n + 1 + w + c  # total no of qubits
    gr = int(np.floor(np.sqrt(n) * np.pi / 4))  # grover rotation number

    com = QuantumRegister(n + 1, 'q')
    work = QuantumRegister(w, 'w')
    chk = QuantumRegister(c, 'c')
    cl = ClassicalRegister(n + 1)
    grover = QuantumCircuit(chk, work, com, cl)

    grover.x(com[-1])
    grover.barrier()
    for r in range(gr):
        for i in range(len(com)):
            grover.h(com[i])
        grover.append(oracle(chk, work, com), [i for i in range(N)])
        for i in range(len(com[:-1])):
            grover.h(com[i])
        grover.append(diffuser(chk, work, com[:-1]), [i for i in range(N - 1)])
        for i in range(len(com[:-1])):
            grover.h(com[i])
    grover.barrier()
    grover.measure(com, cl)

    return grover

gr = grover_Algo(4)
