<h4>Quadratic Unconstrained Binary Optimisation</h4>
Input - $x \in \{0,1\}^{n}$
Matrix $Q$ is Upper triangular. ($Q \in \mathbf{R}^{n\times n}$)

Optimisation problem:
$\min_{x} y=x^{T}Qx$ 
for $\max y' = -y$

Constrained to Unconstrained :
Introduce Quadratic penalties into the objective function
The penalties are formulated such that they are 0 for feasible solutions
and equal to some positive penalty for infeasible solutions
If penatlies are driven to zero, we get same problem

But why quadratic?

![[Pasted image 20231118104550.png]]

Here $x,y$ are binary values and P is some constant.

Given general 0/1 optimisation problem:
$\min y = x^{T}Cx$
$Ax = b,x \in \{0,1\}$

1. We assume $A,b$ both have only integer components
2. For inequality constraints, we add slack variables
3. Convert $Ax = b$ into quadratic penalties
	1. ($P(Ax = b)^{T}(Ax = b)$)
	2. $x_{1}+x_{2} \leq 1 \equiv P(x_{1}x_{2})$
4. Choose $P$ suitably.
5. Add them to the objective function

A program is needed to implement this.
Same can be done for linear programs

QUBO as a Query Model of Computation:
Input : $Q \in \mathbf{R}^{n\times n}, \text{Q is upper triangular}$
Output : $x^{*} \in \{0,1\}^{n} \text{ such that } (x^{*})^{T}Q x^{*} \text{ is min}$ 

Advantage:
Lot of Quantum Algorithms are expressed in Query model of computation

<b>Identifying Cliques, independent sets, etc in the flight graph</b>

<h4> Ising Problems </h4>
NP-Hard
Given Graph $G = (V,E)$
Each node assigned $0/1$
A Configuration $\sigma(G)$ is assignment of 0/1 to each node
$\sigma_{i}$ is the binary value of $i$ node
Each edge $e \in E$ has a weight $w(e)$ 
Each vertex $v \in V$ has a weight $h(v)$

Objective Function:
$\min\limits_{\sigma} H(\sigma) = \sum\limits_{i,j} w(e_{ij})\sigma_{i}\sigma_{j} + \mu\sum\limits_{j}h_{j}\sigma_{j}$ 

Same as QUBO (A Quantum technique to solve it, at least physically)

<h4>Adiabatic Quantum Optimisation</h4>
NP-Hard
To find the minimum soln for a Hamiltonian $H_p$
If we know a Hamiltonian $H_0$ whose minimal solution is easy to find, then we can use it to find the same for $H_p$
Adiabatic quantum computing has been shown to be polynomially equivalent to conventional quantum computing in the circuit model.
Stuck at local minima
Adiabatic is a slow process

$H(t) = (1-\frac{t}{T})H_{0} + \frac{t}{T}H_{p}$

Energy of Hamiltonian ?= Total score of our objective function

Measure H(t) at time T to get minimum of $H_p$
T is large

Relation to Binary Integer Linear Programming

Quantum Annealer

