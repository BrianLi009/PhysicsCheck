import itertools

def encode_min_three_2(n):
    """Using a second approach for encoding minimum degree 3, only need the edge variables"""
    vertices_lst = list(range(1, n+1))
    edge_dict = {}
    counter = 1
    constraint = []
    edge_lst = list(itertools.combinations(vertices_lst, 2))
    for edge in edge_lst:
        edge_dict[edge] = counter
        counter += 1    #build the dictionary for variables
    for v in vertices_lst:
        vertices_lst_copy = vertices_lst.copy()
        vertices_lst_copy.remove(v)
        for choice in list(itertools.combinations(vertices_lst_copy, n-3)):
            constraint_1 = []
            for v_2 in choice:
                edge = tuple(sorted((v, v_2)))
                constraint_1.append(edge_dict[edge])
            constraint = constraint + [constraint_1]
    return constraint