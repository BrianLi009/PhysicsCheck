#!/usr/bin/python

from pysat.formula import CNF 
from squarefree import squarefree
from triangle import triangle
from mindegree import mindegree
from noncolorable import noncolorable
from cubic import cubic
import subprocess
import os

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
    cnf_file = "squarefree_constraints_" + str(n)
    edge_dict = {}
    tri_dict = {}
    #var_dict = {}
    count = 0
    clause_count = 0
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
    clause_count += squarefree(n, edge_dict, cnf_file)
    print ("graph is squarefree")
    clause_count += mindegree(n, 2, edge_dict, cnf_file)
    print ("each vertex has minimium degree 2")
    var_count, c_count = cubic(n, count, cnf_file) #total number of variables
    clause_count += c_count
    print ("isomorphism blocking applied")
    firstline = 'p cnf ' + str(var_count) + ' ' + str(clause_count)
    subprocess.call(["./gen_instance/append.sh", cnf_file, cnf_file+"_new", firstline])

if __name__ == "__main__":
   generate(int(sys.argv[1]))