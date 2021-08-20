import numpy as np
import itertools
from math import comb, perm

from numpy.core.fromnumeric import var
from cubic import *
from relabel import *
import sys

def matching(v):
    num_edges = comb(v, 2)
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

def sol_to_lst(solution):
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

def row_to_col(solution, v):
    """input string of solutions in row matrix, then output string solutions in column matrix in a list"""
    """NEED TO FIX"""
    new_assignment = []
    g = solution.split()
    if 'a' in g:
        g.remove('a')
    if '0' in g:
        g.remove('0')
    matches = matching(v)
    for variable in g:
        if int(variable) > 0:
            match = matches[abs(int(variable))]
        else:
            match = -matches[abs(int(variable))]
        new_assignment.append(match)
    return sorted(new_assignment, key=abs)

def row_to_col_cubic(encoding, v):
    """given a cubic encoding, we also turn it into column form using new_assignment"""
    new_encoding = []
    matches = matching(v)
    for clause in encoding:
        new_clause = []
        for variable in clause:
            if abs(variable) in matches.keys():
                if variable > 0:
                    new_var = matches[abs(variable)]
                else:
                    new_var = -matches[abs(variable)]
                new_clause.append(new_var)
            else:
                new_clause.append(variable)
        new_encoding.append(new_clause)
    return new_encoding

def produce_matrix(solutions, v):
    """given solutions in the form of the output of row_to_col, return a matrix"""
    matrix = np.zeros((v, v)) #first start with a zero matrix with the right size
    lst = list(range(0, v))
    entries = list(itertools.combinations(lst, 2))
    #entries.sort(key=lambda x:x[1]) #sort it column by column
    for i in range(len(entries)):
        position = entries[i]
        value = solutions[i]
        if value > 0:
            matrix[position[0], position[1]] = 1
            matrix[position[1], position[0]] = 1
        else:
            matrix[position[0], position[1]] = 0
            matrix[position[1], position[0]] = 0
    matrix = matrix.astype(int)
    return matrix

def findRank(s): 
    #source: https://www.geeksforgeeks.org/lexicographic-rank-of-a-binary-string/
    N = len(s)
    sb = ""
    for i in range(0,N):
        if (s[i] == '0'):
            sb += str('0')
        else:
            sb += str('1')
    bin = str(sb)
    X = pow(2, N)
    Y = int(bin)
    ans = X + Y - 1
    return ans

def compare_two_matrix(m1, m2):
    """take in two matrix and return the one with the higher lex order, compare m1 against m2, only return m2 if m2 is larger"""
    num_of_col = m1.shape[0]
    for i in range(num_of_col):
        str_1 = ''
        str_2 = ''
        column_1 = list(m1[:, i])
        column_2 = list(m2[:, i])
        lst_1 = [str(int) for int in column_1]
        lst_2 = [str(int) for int in column_2]
        comparable_1 = (str_1.join(lst_1))
        comparable_2 = (str_2.join(lst_2))
        rank_1 = findRank(comparable_1)
        rank_2 = findRank(comparable_2)
        if rank_1 >= rank_2:
            continue
        else:
            return m2 
    return m1

def generate_canonical_clauses(n):
    clauses = []
    A_dict = {}
    B_dict = {}
    perm_dict = {}
    total_variables = 1
    #vertices_lst = list(range(1, n+1))
    #edge_lst = list(itertools.combinations(vertices_lst, 2))
    #edge_lst.sort(key=lambda x:x[1]) #this is all we have to do to switch the order of edge_lst
    #generate all of A's entries as variables
    for i in range(1, n+1):
        for j in range(1, n+1):
            #if i < j:
            A_dict[(i, j)] = total_variables
            total_variables += 1
    #generate all of B's entries as variables
    for i in range(1, n+1):
        for j in range(1, n+1):
            #if i < j:
            B_dict[(i, j)] = total_variables
            total_variables += 1
    #generate all possible permutations as variables
    for i in range(1, n+1):
        for j in range(1, n+1):
            perm_dict[(i, j)] = total_variables
            total_variables += 1
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
    for i in range(1, n+1):
        for j in range(1, n+1):
            for i_prime in range(1, n+1):
                for j_prime in range(1, n+1):
                    #if i_prime < j_prime:
                    constraint_5 = [-A_dict[(i,j)], -perm_dict[(i, i_prime)], -perm_dict[(j, j_prime)], B_dict[(i_prime,j_prime)]]
                    constraint_6 = [-B_dict[(i_prime,j_prime)], -perm_dict[(i, i_prime)], -perm_dict[(j, j_prime)], A_dict[(i,j)]]
                clauses = clauses + [constraint_5] + [constraint_6]
    for i in range(1, n+1):
        for j in range(1, n+1):
            if i == j:
                constraint_11 = [-A_dict[(i,j)]]
                constraint_12 = [-B_dict[(i,j)]]
                clauses = clauses + [constraint_11] + [constraint_12]
            constraint_7 = [-A_dict[(i,j)], A_dict[(j,i)]]
            constraint_8 = [A_dict[(i,j)], -A_dict[(j,i)]]
            constraint_9 = [-B_dict[(i,j)], B_dict[(j,i)]]
            constraint_10 = [B_dict[(i,j)], -B_dict[(j,i)]]
            clauses = clauses + [constraint_7] + [constraint_8] + [constraint_9] + [constraint_10]
    return clauses

def merge_canonical_cubic(n, canonical_clauses, cubic_clauses):
    """we will relabel the extra clauses of canonical to follow after the cubic clauses"""
    #matches = matching(n)
    total_clauses = []
    max_label = math.comb(n, 2)*2
    relabeled_dict = {}
    for constraint in canonical_clauses:
        relabelled = relabel_3(constraint, n, max_label, relabeled_dict)
        #print (constraint)
        constraint = relabelled[0]
        #print (constraint)
        max_label = relabelled[1]
        relabeled_dict = relabelled[2]
        total_clauses = total_clauses + [constraint]
    relabeled_dict = {}
    """for constraint in cubic_clauses:
        relabelled = relabel_2(constraint, n, max_label, relabeled_dict)
        print (constraint)
        constraint = relabelled[0]
        print (constraint)
        max_label = relabelled[1]
        relabeled_dict = relabelled[2]
        total_clauses = total_clauses + [constraint]"""
    return total_clauses

#(generate_canonical_clauses(5))
#(merge_canonical_cubic(5, generate_canonical_clauses(5), block_iso(5)))
#print (row_to_col_cubic(block_iso(5),5))
#print (merge_canonical_cubic(17, generate_canonical_clauses(17), block_iso(17)))
print(matching(5))