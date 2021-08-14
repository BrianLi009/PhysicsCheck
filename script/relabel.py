import numpy as np
import itertools

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

def relabel(constraint, num_of_edges, max_label, relabeled_dict): #relabeled = a dict with vertices that we've relabeled
    """
    relabel from all_triangle's variable dictionary to the regular label,
    this is needed as we might have overlapping extra variables in two constraints' dictionary,
    and we want to separate them.
    """
    new_constraint = []
    for label in constraint:
        if abs(label) in relabeled_dict:
            if label > 0:
                new_constraint = new_constraint + [relabeled_dict[abs(label)],] #append the old label
            else:
                new_constraint = new_constraint + [-relabeled_dict[abs(label)],] #append the old label
        elif abs(label) > num_of_edges:
            #relabel
            if label > 0:
                new_constraint = new_constraint + [int(max_label + 1), ]
                relabeled_dict[abs(label)] = int(max_label + 1)
            else:
                new_constraint = new_constraint + [int(-(max_label + 1)),]
                relabeled_dict[abs(label)] = int(max_label + 1)
            max_label += 1
        else: #it is an edge label
            new_constraint = new_constraint + [int(label),]
    return [new_constraint, max_label, relabeled_dict]

def relabel_2(constraint, num_of_vertices, max_label, relabeled_dict_2):
    """
    relabel from block_iso's dictionary to the regular label
    """
    entry_to_edge_dict = {}
    new_constraint = []
    adjacency_matrix = gen_matrix(num_of_vertices)
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
