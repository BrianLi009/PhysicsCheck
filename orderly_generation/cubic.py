import itertools
import math
from relabel import *

from numpy.core.shape_base import block

def block_iso(n):
    """Take in a "undetermined" graph representation given by Boolean edge variables? 
       Generate all possible $A_{i,j}$ and $A_{j,i}$, for instance, A_{i,j} are made by accessing the ith row, then take away the ith and jth entry.
       Put entries of $A_{i,j}$ as [x_1,x_2,...x_n], and entries of $A_{j,i}$ as [y_1,y_2,...,x_m]
       Use the lex clause from Lam's problem to generate clauses return all clauses"""
    adj_matrix = gen_matrix(n) #generate matrices with entry 1,2,...,
    adj_matrix_lst = list(itertools.chain(*list(adj_matrix)))
    dict = {}
    size = n
    count = 1
    constraint = []
    extra_var_count = n**2+1
    for entry in adj_matrix_lst:
        dict[entry] = count
        count += 1
    for i in range(size-1):
        for j in range(i+1, size):
            A_i = list(adj_matrix[i])
            A_j = list(adj_matrix[j])
            A_ij = A_i[:i] + A_i[i+1:j] + A_i[j+1:]
            A_ji = A_j[:i] + A_j[ i+1:j] + A_j[j+1:]
            #print (A_ij, A_ji)
            for n in range(len(A_ij)):
                dict[(i,j,n)] = extra_var_count
                extra_var_count += 1
            for n in range(len(A_ij)):
                if n == 0:
                    constraint_1 = [-dict[A_ij[n]], dict[A_ji[n]]]
                    constraint_2 = [-dict[A_ij[n]], dict[(i,j,n)]]
                    constraint_3 = [dict[A_ji[n]], dict[(i,j,n)]]
                    constraint = constraint + [constraint_1, constraint_2, constraint_3]
                else:
                    constraint_1 = [-dict[A_ij[n]], dict[A_ji[n]], -dict[(i,j,n)]]
                    constraint_2 = [-dict[A_ij[n]], dict[(i,j,n)], -dict[(i,j,n-1)]]
                    constraint_3 = [dict[A_ji[n]], dict[(i,j,n)], -dict[(i,j,n-1)]]
                    constraint = constraint + [constraint_1, constraint_2, constraint_3]
            constraint_4 = [-dict[A_ij[-1]], -dict[(i,j,len(A_ij)-1)]]
            constraint_5 = [dict[A_ji[-1]], -dict[(i,j,len(A_ij)-1)]]
            constraint = constraint + [constraint_4] + [constraint_5]
    for i in range(size):
        constraint = constraint + [[-dict[adj_matrix[i][i]]]]
        for j in range(size):
            constraint = constraint + [[-dict[adj_matrix[i][j]], dict[adj_matrix[j][i]]]]#make sure it's symmetric
            constraint = constraint + [[dict[adj_matrix[i][j]], -dict[adj_matrix[j][i]]]]
    #print (constraint)
    return constraint