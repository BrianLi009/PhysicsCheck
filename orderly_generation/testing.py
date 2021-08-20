import numpy as np
from canonical import *
import itertools
from collections import Counter

file1 = open('17-exhaustive', 'r')
Lines = file1.readlines()
v=17
matrix_lst = []
winning_matrix = []
for solution in Lines:
    matrix_lst.append(produce_matrix(row_to_col(solution, v), v))
for matrices in list(itertools.combinations(matrix_lst, 2)):
    matrix_1 = matrices[0]
    matrix_2 = matrices[1]
    winning_matrix.append(compare_two_matrix(matrix_1, matrix_2))
