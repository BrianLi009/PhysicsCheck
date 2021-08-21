import math
import numpy as np

def preprocess_maplesat(solution):
    """given string of solution, return in a list"""
    lst = []
    g = solution.split()
    if 'a' in g:
        g.remove('a')
    if '0' in g:
        g.remove('0')
    for variable in g:
        lst.append(int(variable))
    return lst

def matching(v):
    num_edges = math.comb(v, 2)
    all_entries = list(range(1, num_edges+1))
    matching = {}
    all_cols = []
    col_size = 1
    while all_entries != []:
        col = []
        while len(col) < col_size:
            col.append(all_entries.pop(0))
        col_size += 1
        all_cols.append(col)
    original_order = list(range(1, num_edges+1))
    i = 0
    while i < original_order[-1]:
        for col in all_cols:
            if col != []:
                matching[original_order[i]] = col.pop(0)
                i += 1
    return matching

def relabel_from_matching(constraint, matches):
    """input a constraint, relable it based on matches"""
    new_constraint = []
    for variable in constraint:
        if abs(variable) in matches.keys():
            if variable > 0:
                new_var = matches[abs(variable)]
            else:
                new_var = -matches[abs(variable)]
            new_constraint.append(new_var)
        else:
            new_constraint.append(variable)
    return new_constraint

def relabel_cubic(constraint, num_of_vertices, max_label, relabeled_dict_2):
    """
    relabel from block_iso's dictionary to the regular label
    """
    entry_to_edge_dict = {}
    new_constraint = []
    adjacency_matrix = gen_matrix(num_of_vertices)
    """extract upper triangle"""
    """we can first get rid of the repetitive entries due to symmetry"""
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
    return [relabeled_constraint, max_label, relabeled_dict_2]

def process_cubic_A_B(constraint, n):
    """input a cubic constraint, output the edges in terms of matrix B"""
    new_constraint = []
    for variable in constraint:
        if abs(variable) <= math.comb(n,2):
            if variable > 0:
                new_var = int(abs(variable) + math.comb(n, 2))
            else:
                new_var = int(-(abs(variable) + math.comb(n, 2)))
            new_constraint.append(int(new_var))
        else:
            new_constraint.append(int(variable))
    return new_constraint

"""helper functions"""
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