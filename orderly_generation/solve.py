from generate import generate_encoding
from pysat.solvers import Cadical
from pysat.formula import CNF
from relabel import *
from testing import *

def solve(encoding, assumption):
    cnf = CNF()
    cnf.from_file(file)
    s = Cadical()
    s.append_formula(cnf.clauses)
    solving = s.solve(assumptions = assumption)
    if solving == True:
        n=17
        solution = s.get_model()
        #print (solution)
        print(solution[: int(n*(n-1))])
        #print(produce_matrix(solution[int(n*(n-1)/2) : int(n*(n-1))], 17))
    else:
        print (False)

file1 = open('17.exhaust', 'r')
Lines = file1.readlines()
count = 1
file = 'orderly_cubic17'
for solution in Lines:
    print (count)
    count += 1
    assumption = preprocess_maplesat(solution)
    #print (assumption)
    #print (produce_matrix(assumption, 17))
    solve(file, assumption)