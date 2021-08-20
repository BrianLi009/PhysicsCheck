import numpy as np
import itertools
import math

from numpy.core.shape_base import block

def gen_matrix(size):
    """
    given size of the square matrix, it generates matrix with entry from 1 to size**2 in order
    """
    matrix_lst = []
    new_lst=[]
    vertices = list(range(1, size**2+1))
    for i in range(size**2):
        if (i%size == 0 and i!=0):
            matrix_lst.append(new_lst)
            new_lst=[]
        new_lst.append(vertices[i])
    matrix_lst.append(new_lst)
    m = np.array(matrix_lst)
    return m

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

def relabel_2(constraint, n, max_label, relabeled_dict_2):
    """
    relabel from block_iso's dictionary to the regular label
    """
    entry_to_edge_dict = {}
    new_constraint = []
    adjacency_matrix = gen_matrix(n)
    """extract upper triangle"""
    """we can first get rif of the repetitive entries due to symmetry"""
    upper_matrix = upper_triangle(adjacency_matrix)
    lower_matrix = lower_triangle(adjacency_matrix)
    for i in range(1, len(upper_matrix)+1):
        entry_to_edge_dict[upper_matrix[i-1]] = i 
    for var in constraint:
        if abs(var) in lower_matrix: 
            if var > 0:
                new_constraint = new_constraint + [upper_matrix[lower_matrix.index(var)],]
            else:
                new_constraint = new_constraint + [-upper_matrix[lower_matrix.index(abs(var))],]
        elif abs(var) in upper_matrix:
            new_constraint = new_constraint + [int(var),]
        elif abs(var) not in upper_matrix and abs(var) not in lower_matrix: #identify extra variables
            if abs(var) in relabeled_dict_2:
                if var > 0:
                    new_constraint = new_constraint + [relabeled_dict_2[abs(var)],]
                else:
                    new_constraint = new_constraint + [-relabeled_dict_2[abs(var)],]
            else:
                if var > 0:
                    new_constraint = new_constraint + [int(max_label + 1),]
                    relabeled_dict_2[abs(var)] = int(max_label + 1)
                else:
                    new_constraint = new_constraint + [int(-(max_label + 1)),]
                    relabeled_dict_2[abs(var)] = int(max_label + 1)
                max_label += 1
        else:
            print ("entered with" + str(var))
            new_constraint = new_constraint + [int(var),]
    #relabel upper matrix with appropriate edges
    relabeled_constraint = []
    for var in new_constraint:
        if abs(var) in upper_matrix:
            if var > 0:
                relabeled_constraint = relabeled_constraint + [entry_to_edge_dict[abs(var)],]
            else:
                relabeled_constraint = relabeled_constraint + [-entry_to_edge_dict[abs(var)],]
        else:
            relabeled_constraint = relabeled_constraint + [int(var),]
    final_constraint = []
    for var in new_constraint:
        if abs(var) < math.comb(n, 2):
            if var > 0:
                new_var = int(abs(var) + math.comb(n, 2))
            else:
                new_var = int(-(abs(var) + math.comb(n, 2)))
            final_constraint.append(new_var)
        else:
            final_constraint.append(int(var))
    return [final_constraint, max_label, relabeled_dict_2]

def relabel_3(constraint, n, max_label, relabeled_dict_2):
    """
    relabel from block_iso's dictionary to the regular label
    """
    entry_to_edge_dict = {}
    entry_to_edge_dict_2 = {}
    new_constraint = []
    adjacency_matrix = gen_matrix(n)
    adjacency_matrix_2 = adjacency_matrix + n**2
    """extract upper triangle"""
    """we can first get rif of the repetitive entries due to symmetry"""
    upper_matrix_1 = upper_triangle(adjacency_matrix)
    lower_matrix_1 = lower_triangle(adjacency_matrix)
    upper_matrix_2 = upper_triangle(adjacency_matrix_2)
    lower_matrix_2 = lower_triangle(adjacency_matrix_2)
    for i in range(1, len(upper_matrix_1)+1):
        entry_to_edge_dict[upper_matrix_1[i-1]] = i
    for i in range(1, len(upper_matrix_2)+1):
        entry_to_edge_dict_2[upper_matrix_2[i-1]] = i + math.comb(n, 2)
    for var in constraint:
        if abs(var) in lower_matrix_1: 
            if var > 0:
                new_constraint = new_constraint + [upper_matrix_1[lower_matrix_1.index(var)],]
            else:
                new_constraint = new_constraint + [-upper_matrix_1[lower_matrix_1.index(abs(var))],]
        elif abs(var) in upper_matrix_1:
            new_constraint = new_constraint + [int(var),]
        elif abs(var) in lower_matrix_2:
            if var > 0:
                new_constraint = new_constraint + [upper_matrix_2[lower_matrix_2.index(var)],]
            else:
                new_constraint = new_constraint + [-upper_matrix_2[lower_matrix_2.index(abs(var))],]
        elif abs(var) in upper_matrix_2:
            new_constraint = new_constraint + [int(var),]
        elif abs(var) not in upper_matrix_1 and abs(var) not in lower_matrix_1 and abs(var) not in upper_matrix_2 and abs(var) not in lower_matrix_2: #identify extra variables
            if abs(var) in relabeled_dict_2:
                if var > 0:
                    new_constraint = new_constraint + [relabeled_dict_2[abs(var)],]
                else:
                    new_constraint = new_constraint + [-relabeled_dict_2[abs(var)],]
            else:
                if var > 0:
                    new_constraint = new_constraint + [int(max_label + 1),]
                    relabeled_dict_2[abs(var)] = int(max_label + 1)
                else:
                    new_constraint = new_constraint + [int(-(max_label + 1)),]
                    relabeled_dict_2[abs(var)] = int(max_label + 1)
                max_label += 1
        else:
            print ("entered with" + str(var))
            new_constraint = new_constraint + [int(var),]
    #relabel upper matrix with appropriate edges
    relabeled_constraint = []
    for var in new_constraint:
        if abs(var) in upper_matrix_1:
            if var > 0:
                relabeled_constraint = relabeled_constraint + [entry_to_edge_dict[abs(var)],]
            else:
                relabeled_constraint = relabeled_constraint + [-entry_to_edge_dict[abs(var)],]
        elif abs(var) in upper_matrix_2:
            if var > 0:
                relabeled_constraint = relabeled_constraint + [entry_to_edge_dict_2[abs(var)],]
            else:
                relabeled_constraint = relabeled_constraint + [-entry_to_edge_dict_2[abs(var)],]
        else:
            relabeled_constraint = relabeled_constraint + [int(var),]
    return [relabeled_constraint, max_label, relabeled_dict_2]

def upper_triangle(matrix):
    """
    put the entries of the upper trianglular matrix  into a list
    """
    entry_lst = []
    dim = matrix.shape[0]
    for i in range(dim):
        for j in range(dim):
            if i < j:
                entry_lst.append(matrix[i][j])
    return entry_lst

def lower_triangle(matrix):
    """
    put the entries of the lower trianglular matrix  into a list
    """
    entry_lst = []
    dim = matrix.shape[0]
    for j in range(dim):
        for i in range(dim):
            if i > j:
                entry_lst.append(matrix[i][j])
    return entry_lst

#print (block_iso(17))