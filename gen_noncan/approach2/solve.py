from networkx.algorithms.isomorphism.isomorph import is_isomorphic
from generate import generate_encoding
from pysat.solvers import *
from pysat.formula import CNF
from relabel import *
from testing import *
import networkx as nx

def solve(file, assumption, count):
    print (assumption)
    cnf = CNF()
    cnf.from_file(file)
    s = Cadical()
    s.append_formula(cnf.clauses)
    solving = s.solve(assumptions = assumption)
    if solving == False:
        print (count)
        print (False)
    else:
        print (count)
        print (True)
        solution = s.get_model()
        n=17
        #print(solution[: int(n*(n-1))])
        """
        matrix_1=produce_matrix(assumption, 17)
        matrix_2=produce_matrix(solution[int(n*(n-1)/2) : int(n*(n-1))], 17)
        G = nx.from_numpy_matrix(matrix_1)
        G2 = nx.from_numpy_matrix(matrix_2)
        print (is_isomorphic(G, G2))"""
        

file1 = open('17.exhaust', 'r')
Lines = file1.readlines()
count = 1
file = 'orderly_cubic_lex_most17'
for solution in Lines:
    if count > 0: #
    	assumption = preprocess_maplesat(solution)
    	#assumption = relabel_from_matching(assumption, matching(17))
    	#assumption = sorted(assumption, key=abs)
    	#print (assumption)
    	#print (produce_matrix(assumption, 17))
    	solve(file, assumption, count)
    count += 1