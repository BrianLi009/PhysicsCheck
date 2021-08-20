from canonical import *
from cubic import *
from pysat.solvers import Cadical
from pysat.formula import CNF

def gen_matrix_from_sol(sol, v):
    """given the solution as strings, we want to generate the full adjacency matrix"""
    return produce_matrix(sol_to_lst(sol), v)

file1 = open('17-exhaustive', 'r')
Lines = file1.readlines()
clauses = merge_canonical_cubic(17, generate_canonical_clauses(17), block_iso(17))
#print (clauses)
count = 0
non_canonical = 0
for solution in Lines:
    """converted_solution = gen_matrix_from_sol(solution, 17)
    print (converted_solution)
    assumption = []
    variable = 1
    for i in range(1, 17+1):
        for j in range(1, 17+1):
            if converted_solution.item(i-1, j-1) == 1:
                assumption.append(variable)
            else:
                assumption.append(-variable)
            variable += 1"""
    assumption = sol_to_lst(solution) #this is fine
    #print (assumption)
    print (produce_matrix(assumption, 17))
    s=Cadical()
    s.append_formula(clauses)
    if s.solve(assumptions=assumption) == False:
        print (s.get_core())
        count += 1
        print ("found " + str(count))
    else:
        n=17
        print (produce_matrix(list(s.get_model())[int((n*(n-1)/2)+1) : int(n*(n-1)+1)], 17))
        #print (s.get_model())
        non_canonical += 1
        print (non_canonical)
