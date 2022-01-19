import itertools

def triangle(n, edge_dict, tri_dict):
    """
    generate encoding for "all vertices are part of a triangle"
    we will use the same dictionary for all constraint for consistency and labeling purposes
    """
    constraint = []
    vertices_lst = list(range(1, n+1))
    for triangle in list(itertools.combinations(vertices_lst, 3)):
        # the following encoding are applied in every possible triangle in the graph
        # given a triangle, if encode the equivalence relation
        v_1 = triangle[0]
        v_2 = triangle[1]
        v_3 = triangle[2]
        vertices = [v_1, v_2, v_3]
        vertices.sort()
        edge_1 = (vertices[0], vertices[1])
        edge_2 = (vertices[1], vertices[2])
        edge_3 = (vertices[0], vertices[2])
        constraint_1 = [edge_dict[edge_1], -tri_dict[triangle]]
        constraint_2 = [edge_dict[edge_2], -tri_dict[triangle]]
        constraint_3 = [edge_dict[edge_3], -tri_dict[triangle]]
        constraint_4 = [-edge_dict[edge_1], -edge_dict[edge_2], -edge_dict[edge_3], tri_dict[triangle]]
        constraint = constraint + [constraint_1, constraint_2, constraint_3, constraint_4]
    for vertex in vertices_lst:
        all_in = []
        for triangle in list(itertools.combinations(vertices_lst, 3)):
            if vertex in triangle:
                all_in.append(tri_dict[triangle])   #at least one triangle variable that includes this particular vertex is True
        constraint = constraint + [all_in]
    return constraint