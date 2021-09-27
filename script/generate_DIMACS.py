import pysat
from pysat.formula import CNF
import numpy as np
from triangle import *
from squarefree import *
from non_colorable import *
from minthree import *
from cubic import *
from relabel import *
from matching import *
from minthree_2 import *
import timeit

def generate_dimacs(n):
    """
    very similar to generate_graph, but only save the constraint into a DIMACS file
    """
    cnf = CNF()
    matches = matching(n)
    num_of_edges = np.math.factorial(n)/(np.math.factorial(2)*np.math.factorial(n-2))
    num_of_triangles = math.comb(n, 3)
    relabeled_dict = {} #list of relabeled vertices
    relabeled_dict_2 = {}
    #print (num_of_edges)
    max_label = int(num_of_triangles + num_of_edges)
    for constraint in encode_squarefree(n): #does not contain C4 subgraph, no extra variables
        #print (constraint)
        constraint = relabel_from_matching(constraint, matches)
        cnf.append(constraint)
    print ("constraint_1 added")
    for constraint in all_triangle(n): #every vertex is a part of the triangle, needs relabeling
        #print ("triangle")
        #print (max_label)
        #print (constraint)
        constraint = relabel_from_matching(constraint, matches)
        cnf.append(constraint) #problem solved here is double-labeled free variables"""
    print ("constraint_2 added")
    for constraint in non_colorable(n):
        #print (constraint)
        constraint = relabel_from_matching(constraint, matches)
        cnf.append(constraint) #problem solved here is double-labeled free variables
    print ("constraint_3 added")
    #add the non-010 constraint here
    #we want to disable this constraint for now to generate non-colorable constraint on the fly
    """for constraint in encode_min_three(n): #each vertex has minimum degree 3, contain extrvariables
        #print (constraint)
        relabelled = relabel(constraint, num_of_edges, max_label, relabeled_dict)
        constraint = relabelled[0]
        #print (constraint)
        max_label = relabelled[1]
        relabeled_dict = relabelled[2]
        constraint = relabel_from_matching(constraint, matches)
        cnf.append(constraint)"""
    for constraint in encode_min_three_2(n):
        constraint = relabel_from_matching(constraint, matches)
        cnf.append(constraint)
    print ("constraint_4 added")
    for constraint in block_iso(n): #block some isomorphic graphs
        #print (constraint)
        relabelled = relabel_2(constraint, n, max_label, relabeled_dict_2)
        constraint = relabelled[0]
        max_label = relabelled[1]
        #print (constraint)
        relabeled_dict_2 = relabelled[2]
        constraint = relabel_from_matching(constraint, matches)
        cnf.append(constraint)
    print ("isomorphism blocked")
    cnf.to_file('constraints_' + str(n))
    #cnf.to_file('no_trig_all_constraints_' + str(n))

def generate_squarefree(n):
    cnf = CNF()
    matches = matching(n)
    num_of_edges = np.math.factorial(n)/(np.math.factorial(2)*np.math.factorial(n-2))
    for constraint in encode_squarefree(n): #does not contain C4 subgraph, no extra variables
        #print (constraint)
        constraint = relabel_from_matching(constraint, matches)
        cnf.append(constraint)
    cnf.to_file('squarefree_' + str(n))

generate_dimacs(17)