"""
    This is an ongoing circuit implementation of Grover's Algorithm
    Left out work:
    1. Defining Oracle appropriately
    2. Execution
"""


from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np

a = [np.random.randint(0, 5) for i in range(100)]  # required soln


def function(x):  # oracle
    return 1 if (x in a) else 0


# QFT Circuit
def qft(com):
    """Creates an n-qubit QFT circuit"""
    qft_circ = QuantumCircuit(com)

    def swap_registers(circ, c):
        n = len(c)
        for qubit in range(n // 2):
            circ.swap(qubit, n - qubit - 1)
        return circ

    def qft_rotations(circ, c):
        """Performs qft on the first n qubits in circuit (without swaps)"""
        if len(c) == 0:
            return circ

        c = c[:-1]
        circ.h(len(com))
        for qubit in range(len(com)):
            circ.cp(np.pi / 2 ** (len(c) - qubit), qubit, len(c))
        qft_rotations(circ, c)

    qft_rotations(qft_circ, com)
    swap_registers(qft_circ, com)
    return qft_circ.to_instruction()


# Inverse Quantum Fourier Transform
def qft_dagger(com):
    """n-qubit QFTdagger the first n qubits in circ"""
    qft_d = QuantumCircuit(com)

    # Don't forget the Swaps!
    for qubit in range(len(com) // 2):
        qft_d.swap(qubit, n - qubit - 1)
    for j in range(len(com)):
        for m in range(j):
            qft_d.cp(-np.pi / float(2 ** (j - m)), m, j)
        qft_d.h(j)
    return qft_d.to_gate()


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


def bitflipOracle():
    # Bit Flip Oracle |yx> => |y>|x+f(y>

    bfO = QuantumCircuit(2)
    bfO.cx(0, 1)
    return bfO.to_gate()


def phaseFlipOracle():
    # Phase Flip Oracle |x> => (-1)^f(x)|x>

    pfO = QuantumCircuit(2)
    pfO.x(1)
    pfO.h(0)
    pfO.append(bitflipOracle(), [0, 1])
    pfO.h(0)
    pfO.x(1)

    return pfO.to_gate()


def oracle(chk, work, com):
    # w : no of working bits
    # frame the appropriate oracle problem
    # it will choose the solutions which match the condition
    # write a circuit according to your condition using function
    # N computing qubits, W working qubits, 1 checker qubit
    # circuit division :
    # 1. Different condition clauses
    # 2. Result into checker bit
    # 3. uncomputation (can be optional)
    orc = QuantumCircuit(chk, work, com)
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
    return dif.to_gate()


def groverOp(chk, work, com):
    # Grover Operator : Runs the Grover Rotations

    G = QuantumCircuit(chk, work, com)
    G.append(oracle(chk, work, com), [i for i in range(G.num_qubits)])
    for i in range(len(com[:-1])):
        G.h(com[i])
    G.append(diffuser(chk, work, com[:-1]), [i for i in range(G.num_qubits-1)])
    for i in range(len(com[:-1])):
        G.h(com[i])
    G = G.decompose()
    return G.to_gate()


def cGrovOp(work):
    # Control Grover Operator : Used in Quantum Counting

    # work split to chk, wrk, com
    g = groverOp(chk, wrk, com)
    return g.control()


def counting(p, n):
    # To count no of solns

    pre = QuantumRegister(p, 'q')
    work = QuantumRegister(n, 'w')
    cl = ClassicalRegister(p)
    count = QuantumCircuit(pre, work, cl)

    for i in pre:
        count.h(i)
    for i in work:
        count.h(i)
    for i in range(len(pre) - 1):
        for j in range(2 ** i):
            count.append(cGrovOp(work), [i] + [i for i in range(n)])
    count.barrier()

    count.append(qft_dagger(pre), pre)

    count.measure(pre, cl)
    return count


def grover_Algo(n):
    # Grover Algorithm

    # n is no of qubits
    w = 3  # to be defined
    c = 1  # to be defined
    gr = int(np.floor(np.sqrt(n) * np.pi / 4))  # grover rotation number

    com = QuantumRegister(n + 1, 'q')
    work = QuantumRegister(w, 'w')
    chk = QuantumRegister(c, 'c')
    cl = ClassicalRegister(n + 1)
    grover = QuantumCircuit(chk, work, com, cl)

    grover.x(com[-1])
    grover.barrier()
    for i in range(len(com)):
        grover.h(com[i])
    for r in range(gr):
        grover.append(groverOp(chk, work, com), [i for i in range(grover.num_qubits)])
    grover.barrier()
    grover.measure(com, cl)

    return grover


grove = grover_Algo(4)
