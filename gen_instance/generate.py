#!/usr/bin/python

from pysat.formula import CNF 
from squarefree import squarefree
from triangle import triangle
from mindegree import mindegree
from noncolorable import noncolorable
from cubic import cubic

import sys, getopt
def generate(n):
    """
    n: size of the graph
    Given n, the function calls each individual constraint-generating function, then write them into a DIMACS file as output
    The variables are listed in the following order:
    edges - n choose 2 variables
    triangles - n choose 3 variables
    extra variables from cubic
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
    for constraint in squarefree(n, edge_dict):
        cnf.append(constraint)
    print ("graph is squarefree")
    for constraint in triangle(n, edge_dict, tri_dict):
        cnf.append(constraint)
    print ("all vertices are part of a triangle")
    for constraint in noncolorable(n,  edge_dict, tri_dict):
        cnf.append(constraint)
    print ("graph is noncolorable")
    for constraint in mindegree(n, edge_dict):
        cnf.append(constraint)
    print ("minimum degree of each vertex is 3")
    for constraint in cubic(n, count):
        cnf.append(constraint)
    print ("isomorphism blocking applied")
    cnf.to_file("constraints_" + str(n))

if __name__ == "__main__":
   generate(int(sys.argv[1]))