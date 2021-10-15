import itertools

def mindegree(n, edge_dict):
    """Using a second approach for encoding minimum degree 3, only need the edge variables"""
    vertices_lst = list(range(1, n+1))
    constraint = []
    for v in vertices_lst:
        vertices_lst_copy = list(vertices_lst)
        vertices_lst_copy.remove(v)
        for choice in list(itertools.combinations(vertices_lst_copy, n-3)):
            constraint_1 = []
            for v_2 in choice:
                edge = tuple(sorted((v, v_2)))
                constraint_1.append(edge_dict[edge])
            constraint = constraint + [constraint_1]
    return constraint