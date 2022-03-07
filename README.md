**ipynb notebook:** collections of jupter notebook cells containing some of the analysis, not a part of the pipeline

**gen_instance:** include scripts that generate SAT instance of certain order with satisfying certain contraints, can be ran using 1-instance-generation.sh

**gen_noncan:** include scripts that generate blocking clauses to block non-canonical representation of a graph, can be ran using 2-add-blocking-clauses.sh

**gen_cubes:** generate the cubes used in cube and conquer, merge cubes into the instance then solve using MapleSAT, can be ran using 3-cube-merge-solve.sh

**embedability:** check whether kochen specker candidates are embedable, if a candidate is indeed embedable, it is a Kochen Specker graph as desired, can be ran using 4-check-embedability.sh

**compute_canada:** the cubing and solving of high order graph might require computing resources, in our case, Compute Canada were used

**Pipeline:** 

dependencies: maplesat-ks, cadical, networkx, z3-solver, and march_cu from cube and conquer. Run dependency-setup.sh for dependency setup

![Showing pipeline and which directory to enter for each step](pipeline.png?raw=true "Pipeline")
