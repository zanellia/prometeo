# Examples

Run an example in Python with `pmt <example>.py`, or transpile it to C, compile it and run it with
`pmt <example>.py --cgen=True` (from the example's directory).

- [`minimal`](minimal): the syntax, on an LQR controller (matrix expressions, vectors, functions)
- [`python_workflow`](python_workflow): developing in Python: checks, comparisons with SciPy and IPOPT, plots and
  debugging, removed when transpiling
- [`sqp_mpc`](sqp_mpc): SQP for MPC with input bounds and an interior-point QP solver (cart-pole, also written
  with explicit linear algebra calls; hanging chain of masses)
- [`riccati_example`](riccati_example): Riccati recursions, used for the benchmark of the main README
- [`helloworld`](helloworld), [`fibonacci`](fibonacci), [`simple_example`](simple_example), [`test`](test):
  basic programs
