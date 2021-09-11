import itertools

def all_triangle(n): #can confirm the encoding is correct
    """
    generate encoding for "all vertices are part of a triangle"
    we will use the same dictionary for all constraint for consistency and labeling purposes
    """
    constraint = []
    edge_dict = {}
    counter = 1
    vertices_lst = list(range(1, n+1))
    edge_lst = list(itertools.combinations(vertices_lst, 2))
    extra_var_count = len(edge_lst)+1
    extra_var_dict = {}
    #all_possible_triangle = []
    for edge in edge_lst:
        edge_dict[edge] = counter
        counter += 1
    for triangle in list(itertools.combinations(vertices_lst, 3)):
        extra_var_dict[triangle] = extra_var_count
        extra_var_count += 1
        #all_possible_triangle.append(extra_var_dict[triangle])
        v_1 = triangle[0]
        v_2 = triangle[1]
        v_3 = triangle[2]
        vertices = [v_1, v_2, v_3]
        vertices.sort()
        edge_1 = (vertices[0], vertices[1])
        edge_2 = (vertices[1], vertices[2])
        edge_3 = (vertices[0], vertices[2])
        constraint_1 = [edge_dict[edge_1], -extra_var_dict[triangle]]
        constraint_2 = [edge_dict[edge_2], -extra_var_dict[triangle]]
        constraint_3 = [edge_dict[edge_3], -extra_var_dict[triangle]]
        constraint = constraint + [constraint_1, constraint_2, constraint_3]
    for vertex in vertices_lst:
        all_in = []
        for triangle in list(itertools.combinations(vertices_lst, 3)):
            if vertex in triangle:
                all_in.append(extra_var_dict[triangle])
        constraint = constraint + [all_in]
    #constraint = constraint + [all_possible_triangle] 
    return constraint
