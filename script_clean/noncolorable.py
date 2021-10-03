import itertools

def noncolorable(n, edge_dict, tri_dict):
    constraint = []
    vertices_lst = list(range(1, n+1))
    """this script version does not contain the programmable interface"""
    for i in range(1, n):
        #get all possible combinations of i vertices, divide by 3, plus 1, round up
        possible_comb = list(itertools.combinations(vertices_lst, i))
        for choice in possible_comb: #we pick i vertices to be labeled
            constraint_1 = []
            trig_vertices = []
            for v in vertices_lst:
                if v not in choice:
                    trig_vertices.append(v)
            all_edges = list(itertools.combinations(choice, 2))
            for e in all_edges:
                constraint_1.append(edge_dict[e])
            if len(trig_vertices) > 2:
                all_triangle  = list(itertools.combinations(trig_vertices, 3))
                for triangle in all_triangle: 
                    constraint_1.append(tri_dict[triangle])
            constraint = constraint + [constraint_1]
    return constraint