import itertools

def mindegree(n, edge_dict):
    constraint = []
    vertices_lst = list(range(1, n+1))
    if n <= 3:
        for v in vertices_lst:
            constraint = constraint + [[-v]]
    else:
        for v in vertices_lst:
            #pick a vertex
            vertices_lst_copy = vertices_lst.copy()
            vertices_lst_copy.remove(v)
            for choice in list(itertools.combinations(vertices_lst_copy, n-3)):
                # a conjunction over all subsets of size n-3
                constraint_1 = []
                for v_2 in choice:
                    edge = tuple(sorted((v, v_2)))
                    constraint_1.append(edge_dict[edge])
                constraint = constraint + [constraint_1]
    return constraint