from pysat.formula import CNF 
from squarefree import squarefree
from triangle import triangle
from mindegree import mindegree
from noncolorable import noncolorable
from cubic import cubic

import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from test_function import *

"""generate partial encoding for only one of the constraint"""

def generate(n, option):
    """
    n: size of the graph
    Given n, the function calls each individual constraint-generating function, then write them into a DIMACS file as output
    The variables are listed in the following order:
    edges - n choose 2 variables
    triangles - n choose 3 variables
    extra variables from cubic
    option: 0=squarefree, 1=triangle, 2=noncolorable, 3=min_degree
    """
    cnf = CNF()
    edge_dict = {}
    tri_dict = {}
    #var_dict = {}
    count = 0
    for j in range(1, n+1):             #generating the edge variables
        for i in range(1, n+1):
            if i < j:
                count += 1
                #var_dict[(i,j)] = count
                edge_dict[(i,j)] = count
    for a in range(1, n-1):             #generating the triangle variables
        for b in range(a+1, n):
            for c in range(b+1, n+1):
                count += 1
                #var_dict[(a,b,c)] = count
                tri_dict[(a,b,c)] = count
    if option == 0:
        for constraint in squarefree(n, edge_dict):
            cnf.append(constraint)
        cnf.to_file("constraints_squarefree_only_" + str(n))
    if option == 1:
        for constraint in triangle(n, edge_dict, tri_dict):
            cnf.append(constraint)
        cnf.to_file("constraints_triangle_only_" + str(n))
    if option == 2:
        for constraint in noncolorable(n,  edge_dict, tri_dict, 1):
            cnf.append(constraint)
        for constraint in triangle_equivalence(n, edge_dict, tri_dict):
            cnf.append(constraint)
        cnf.to_file("constraints_color_only_full_" + str(n))
    if option == 3:
        for constraint in mindegree(n, edge_dict):
            cnf.append(constraint)
        cnf.to_file("constraints_mindegree_only_" + str(n))