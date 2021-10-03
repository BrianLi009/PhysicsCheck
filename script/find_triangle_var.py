import itertools
import math

def get_variable(tri, n): 
    """
    input a tuple representing a triangle, n representing numbers of vertices
    """
    vertices_lst = vertices_lst = list(range(1, n+1))
    extra_var_count = math.comb(n,2) + 1 #n choose 2 + 1
    extra_var_dict = {}
    #all_possible_triangle = []
    for triangle in list(itertools.combinations(vertices_lst, 3)):
        extra_var_dict[triangle] = extra_var_count
        extra_var_count += 1
    print (extra_var_dict)
    return extra_var_dict[tri]

get_variable([1,2,3],5)