import itertools


def encode_min_three(n):
    """
    input number of vertices n, generate the SAT encoding for minimum degree being 3
    return a list of tuple, where each tuple is a clause, and each integer is a variable (see Sage SAT documentation)
    """
    constraint = []
    edge_dict = {}
    counter = 1
    vertices_lst = list(range(1, n+1))
    edge_lst = list(itertools.combinations(vertices_lst, 2))
    extra_var_count = len(edge_lst)+1
    extra_var_dict = {}
    """
    created a list of all edges, all vertices, and a dictionary for extra variables
    """
    for edge in edge_lst:
        edge_dict[edge] = counter
        counter += 1
    """
    assign each edge to a number in dictionary form, so that we know which edge each integer is referring to
    """
    for vertex in vertices_lst:
        all_edges = [(vertex, i) for i in range(1, n+1) if vertex < i] + [(i, vertex) for i in range(1, n+1) if vertex > i]
        #Now we want at least three of these edges be true
        S_lst = [] #S represents the extra variables
        for i in range(len(all_edges)+1): #generate all possible s_k,n
            S_lst = S_lst + [(i, a) for a in range(0, 4)]
        for var in S_lst:
            extra_var_dict[(var, vertex)] = extra_var_count
            extra_var_count += 1 #similar to before, we label each integer with corresponding s_i,j
        for var in S_lst:
            i = var[0]  #implement base case
            j = var[1]
            if i == 0 or j == 0:
                continue
            constraint_1 = [-extra_var_dict[((i-1,j),vertex)], extra_var_dict[((i,j),vertex)]]
            constraint_2 = [-edge_dict[all_edges[i-1]], -extra_var_dict[((i-1,j-1),vertex)], extra_var_dict[((i,j),vertex)]]
            constraint_3 = [-extra_var_dict[((i,j),vertex)], extra_var_dict[((i-1,j),vertex)], edge_dict[all_edges[i-1]]]
            constraint_4 = [-extra_var_dict[((i,j),vertex)], extra_var_dict[((i-1,j),vertex)], extra_var_dict[((i-1,j-1),vertex)]]
            constraint = constraint + [constraint_1, constraint_2, constraint_3, constraint_4] 
    for c in extra_var_dict:
        if c[0] == (0,0):
            constraint = constraint + [[extra_var_dict[c]]]
        elif c[0][0] < c[0][1]:
            constraint = constraint + [[-extra_var_dict[c]]]
        elif c[0] == (n-1, 3):
            constraint = constraint + [[extra_var_dict[c]]]
        elif c[0][0] == 0:
            constraint = constraint + [[-extra_var_dict[c]]]
        elif c[0][1] == 0:#assign all at least 0 of the j variable to be true
            constraint = constraint + [[extra_var_dict[c]]]
    """
    some variables need to be assigned true by default, see problem 7 of https://arxiv.org/pdf/1906.06251.pdf
    """
    return constraint
