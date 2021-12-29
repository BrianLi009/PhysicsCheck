```bash
├── ipynb notebook: collections of jupter notebook cells containing some of the analysis, not a part of the pipeline
├── gen_int: include scripts that generate SAT instance of certain order with additional parameters
├── gen_noncan: include scripts that generate blocking clauses to block non canonical representation of a graph
├── gen_cubes: generate the cubes used in cube and conquer (require march_cu)
└── compute_canada: given an instance and cubes, cube-in-instance files are generated on Compute Canada (require Cadical for instance simplification)
```

ipynb notebook: collections of jupter notebook cells containing some of the analysis, not a part of the pipeline

gen_int: include scripts that generate SAT instance of certain order with additional parameters

gen_noncan: include scripts that generate blocking clauses to block non canonical representation of a graph

gen_cubes: generate the cubes used in cube and conquer (require march_cu)

compute_canada: given an instance and cubes, cube-in-instance files are generated on Compute Canada (require Cadical for instance simplification)
