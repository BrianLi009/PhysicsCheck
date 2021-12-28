from typing import Tuple
import networkx as nx
from pysat.formula import CNF
from pysat.solvers import *

def graph6_to_maple(g6_string, n):
    """input graph6 string of n vertices, output variable format"""
    variable_lst = []
    G = nx.from_graph6_bytes(bytes(g6_string, encoding='ascii'))
    total_variables = 0
    A_dict = {}
    edges =  G.edges()
    for j in range(1, n+1):
        for i in range(1, n+1): #the upper triangle variables
            if i < j:
                total_variables += 1
                A_dict[(i, j)] = total_variables
    edges = [(a+1, b+1) for (a, b) in edges]
    for edge in A_dict.keys():
        if edge in edges:
            variable_lst.append(A_dict[edge])
        else:
            variable_lst.append(-A_dict[edge])
    return variable_lst

def solve(file, assumption, count):
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

def find_canonical(g6_string, n, file):
    """find the canonical form of graph corresponding to the graph6 string"""
    assumption = graph6_to_maple(g6_string, n)
    solving = True
    cnf = CNF()
    cnf.from_file(file)
    s = Cadical()
    s.append_formula(cnf.clauses)
    while solving == True:
        solving = s.solve(assumptions = assumption)
        if solving == False:
            print (assumption)
        else:
            print (assumption)
            matrix_B = s.get_model()[int(n*(n-1)/2) : int(n*(n-1))]
            assumption = []
            for entry in matrix_B:
                if entry > 0:
                    assumption.append(abs(entry)-int(n*(n-1)/2))
                else:
                    assumption.append(-(abs(entry)-int(n*(n-1)/2)))

"""file1 = open('all_non_embed_subgraph(10, 11, 12)_minimal.txt', 'r')
Lines = file1.readlines()
for graph in Lines:
    graph = graph[:-1]
    print (graph)
    G = nx.from_graph6_bytes(bytes(graph, encoding='ascii'))
    n = len(G.nodes())
    find_canonical(graph, n, "orderly_cubic_lex_most" + str(n))"""