import numpy as np
from canonical import *
import itertools
from collections import Counter
from relabel import *

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

def produce_matrix(solutions, v):
    """given solutions, return a matrix column-wise"""
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

"""file1 = open('17.exhaust', 'r')
Lines = file1.readlines()
count = 1
lex_dict = {}
for solution in Lines:
    solution = preprocess_maplesat(solution)
    matrix_form = []
    for entry in solution:
        if entry > 0:
            matrix_form.append(1)
        else:
            matrix_form.append(0)
    concat_list = [str(int) for int in matrix_form]
    matrix_in_string = ""
    matrix_in_string = matrix_in_string.join(concat_list)
    lex_order = int(matrix_in_string)
    lex_dict[count] = lex_order
    count += 1
max_lex = max(lex_dict, key=lex_dict.get)
print (max_lex)"""