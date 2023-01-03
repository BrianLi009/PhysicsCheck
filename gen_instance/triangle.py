import itertools

def triangle(n, edge_dict, tri_dict, cnf):
    """
    generate encoding for "all vertices are part of a triangle"
    we will use the same dictionary for all constraint for consistency and labeling purposes
    """
    cnf_file = open(cnf, 'a+')
    clause_count = 0
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
        cnf_file.write('{} {} 0\n'.format(str(edge_dict[edge_1]), str(-tri_dict[triangle])))
        cnf_file.write('{} {} 0\n'.format(str(edge_dict[edge_2]), str(-tri_dict[triangle])))
        cnf_file.write('{} {} 0\n'.format(str(edge_dict[edge_3]), str(-tri_dict[triangle])))
        cnf_file.write('{} {} {} {} 0\n'.format(str(-edge_dict[edge_1]), str(-edge_dict[edge_2]), str(-edge_dict[edge_3]), str(tri_dict[triangle])))
        clause_count += 4
    for vertex in vertices_lst:
        string_lst = []
        for triangle in list(itertools.combinations(vertices_lst, 3)):
            if vertex in triangle:
                string_lst.append(str(tri_dict[triangle]))
        string = ' '.join(string_lst)
        cnf_file.write(string + " 0\n")
        clause_count += 1
    return clause_count
