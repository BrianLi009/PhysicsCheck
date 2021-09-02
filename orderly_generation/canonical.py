import numpy as np
import itertools
from math import comb, perm

from numpy.core.fromnumeric import var
from cubic import *
from relabel import *
import sys

def generate_canonical_clauses(n):
    clauses = []
    A_dict = {}
    B_dict = {}
    perm_dict = {}
    total_variables = 0
    for j in range(1, n+1):
        for i in range(1, n+1): #the upper triangle variables
            if i < j:
                total_variables += 1
                A_dict[(i, j)] = total_variables
    #generate all of B's entries as variables
    for j in range(1, n+1):
        for i in range(1, n+1):
            if i < j:
                total_variables += 1
                B_dict[(i, j)] = total_variables
    #generate all possible permutations as variables
    for i in range(1, n+1):
        for j in range(1, n+1):
            total_variables += 1
            perm_dict[(i, j)] = total_variables
    for i in range(1, n+1):
        constraint_1 = []
        constraint_2 = []
        for j in range(1, n+1):
            constraint_1.append(perm_dict[(i, j)])
            constraint_2.append(perm_dict[(j,i)])
        clauses = clauses + [constraint_1] + [constraint_2]
        for j in range(1, n+1):
            for j_prime in range(1, n+1):
                if j != j_prime:
                    constraint_3 = [-perm_dict[(i, j)], -perm_dict[(i, j_prime)]]
                    constraint_4 = [-perm_dict[(j, i)], -perm_dict[(j_prime, i)]]
                    clauses = clauses + [constraint_3] + [constraint_4]
    perm_lst = []
    for perm in perm_dict.keys():
        perm_lst.append(perm)
    for possible_perm in list(itertools.permutations(perm_lst, 2)):
        i = possible_perm[0][0]
        i_prime = possible_perm[0][1]
        j = possible_perm[1][0]
        j_prime = possible_perm[1][1]
        if (i != j) and (i_prime != j_prime):
            constraint_5 = [-A_dict[tuple(sorted((i,j)))], -perm_dict[(i, i_prime)], -perm_dict[(j, j_prime)], B_dict[tuple(sorted((i_prime,j_prime)))]]
            constraint_6 = [-B_dict[tuple(sorted((i_prime,j_prime)))], -perm_dict[(i, i_prime)], -perm_dict[(j, j_prime)], A_dict[tuple(sorted((i,j)))]]
            clauses = clauses + [constraint_5] + [constraint_6]
    """create the lex clause between matrix A and B"""
    A_edges = list(A_dict.keys())
    B_edges = list(B_dict.keys())
    lex_variables = list(range(total_variables+1, total_variables+len(A_edges)))
    for k in range(1, len(lex_variables)):
        constraint_7 = [-B_dict[B_edges[k]], A_dict[A_edges[k]], -lex_variables[k-1]]
        constraint_8 = [-B_dict[B_edges[k]], lex_variables[k], -lex_variables[k-1]]
        constraint_9 = [A_dict[A_edges[k]], lex_variables[k], -lex_variables[k-1]]
        clauses = clauses + [constraint_7] + [constraint_8] + [constraint_9]
    constraint_10 = [-B_dict[B_edges[0]], A_dict[A_edges[0]]]
    constraint_11 = [-B_dict[B_edges[0]], lex_variables[0]]
    constraint_12 = [A_dict[A_edges[0]], lex_variables[0]]
    constraint_13 = [-lex_variables[-1], -B_dict[B_edges[-1]]]
    constraint_14 = [-lex_variables[-1], A_dict[A_edges[-1]]]    
    clauses = clauses + [constraint_10] + [constraint_11]+[constraint_12] + [constraint_13]+[constraint_14]
    return clauses

#print (generate_canonical_clauses(5))
