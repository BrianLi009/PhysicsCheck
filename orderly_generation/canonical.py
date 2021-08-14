import numpy as np
import itertools
from math import comb
from cubic import *

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

def row_to_col(solution, v):
    """input string of solutions in row matrix, then output string solutions in column matrix in a list"""
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
    entries.sort(key=lambda x:x[1]) #sort it column by column
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


"""cubic_encoding_19 = block_iso(5) #original row format
cubic_encoding_19_col = row_to_col_cubic(cubic_encoding_19, 5) #now it's in column format"""
#print(matching(5))

"""m1 = produce_matrix([-1, -2, -3, 4, -5, -6, -7, -8, -9, -10], 5)
m2 = produce_matrix([-1, -2, -3, 4, 5, 6, -7, -8, -9, -10], 5)
print (m1)
print (m2)
print (compare_two_matrix(m1, m2))"""

print (findRank("0011"))