"""
    This is an ongoing circuit implementation of Grover's Algorithm
    Leftout work:
    1. Query Gates using the oracle (the current ones are dummy ones)
    2. Defining Oracle appropriately
    3. Execution
    ETC : 21st November 2023 12:00
"""


from qiskit.circuit import QuantumCircuit
import numpy as np

n = 10
a = [np.random.randint(0, 5) for i in range(100)]  # required soln


def function(x):  # oracle
    return 1 if (x in a) else 0


def query(n):
    query_f = QuantumCircuit(n)
    '''To be changed'''
    query_f.cx(0, 1)
    query_f.rx(np.pi / 8, 2)
    return query_f.to_gate()


def grover_algo(n):
    grover = QuantumCircuit(n)
    grot = int(np.floor(np.sqrt(n) * np.pi / 4))

    grover.x(n - 1)
    grover.barrier()
    for i in range(n):
        grover.h(i)

    for r in range(grot):
        grover.append(query(n), [i for i in range(n)])
        for i in range(n - 1):
            grover.h(i)
        grover.append(query(n - 1), [i for i in range(n - 1)])
        for i in range(n - 1):
            grover.h(i)
    grover.measure_all()
    return grover


grover_algo(4)
