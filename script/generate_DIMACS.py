import pysat
from pysat.formula import CNF
import numpy as np
from triangle import *
from squarefree import *
from non_colorable import *
from minthree import *
from cubic import *
from relabel import *

def generate_dimacs(n):
    """
    very similar to generate_graph, but only save the constraint into a DIMACS file
    """
    candidate_count = 0
    cnf = CNF()
    num_of_edges = np.math.factorial(n)/(np.math.factorial(2)*np.math.factorial(n-2))
    relabeled_dict = {} #list of relabeled vertices
    relabeled_dict_2 = {}
    #print (num_of_edges)
    max_label = int((n**2)*4 + num_of_edges)
    #print (max_label)
    for constraint in encode_min_three(n): #each vertex has minimum degree 3, contain extrvariables
        #print (constraint)
        cnf.append(constraint)
    print ("constraint_1 added")
    for constraint in encode_squarefree(n): #does not contain C4 subgraph, no extra variables
        #print (constraint)
        cnf.append(constraint)
    print ("constraint_2 added")
    for constraint in all_triangle(n): #every vertex is a part of the triangle, needs relabeling
        #print ("triangle")
        #print (max_label)
        #print (constraint)
        relabelled = relabel(constraint, num_of_edges, max_label, relabeled_dict)
        constraint = relabelled[0]
        #print (constraint)
        max_label = relabelled[1]
        relabeled_dict = relabelled[2]
        cnf.append(constraint) #problem solved here is double-labeled free variables"""
    print ("constraint_3 added")
    #add the non-010 constraint here
    for constraint in non_colorable(n):
        #print (constraint)
        relabelled = relabel(constraint, num_of_edges, max_label, relabeled_dict)
        constraint = relabelled[0]
        #print (constraint)
        max_label = relabelled[1]
        #print (max_label)
        relabeled_dict = relabelled[2]
        cnf.append(constraint) #problem solved here is double-labeled free variables
    print ("constraint_4 added")
    for constraint in block_iso(n): #block some isomorphic graphs
        #print (constraint)
        relabelled = relabel_2(constraint, n, max_label, relabeled_dict_2)
        constraint = relabelled[0]
        max_label = relabelled[1]
        #print (constraint)
        relabeled_dict_2 = relabelled[2]
        cnf.append(constraint)
    print ("isomorphism blocked")
    cnf.to_file('all_constraints_optimized_' + str(n))
    #cnf.to_file('all_constraints_' + str(n))
    #cnf.to_file('no_trig_all_constraints_' + str(n))
    #cnf.to_file('no_noncolor_all_constraints_' + str(n))

generate_dimacs(17)