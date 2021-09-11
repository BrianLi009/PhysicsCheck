import itertools
from pysat.formula import CNF

def colorable(n):
    """
    generate the encoding for graph G with size n is 010-colorable
    the variables are labeled in the following order: [edge labels, color labels for each vertex]
    total number of variables is math.comb(n,2) + n
    the edge variables are labeled column by column by the new convention
    """
    cnf = CNF()
    constraint = []
    edge_dict = {}
    counter = 1
    color_var = {}
    for j in range(1, n+1):
        for i in range(1, n+1):
            if i < j:
                edge_dict[(i,j)] = counter
                counter += 1
    for v in range(1, n+1):
        color_var[v] = counter
        counter += 1
    for edge in edge_dict.keys():
        v1 = edge[0]
        v2 = edge[1]
        edge_var = edge_dict[edge]
        v1_color_var = color_var[v1]
        v2_color_var = color_var[v2]
        constraint_1 = [-edge_var, -v1_color_var, -v2_color_var]
        constraint = constraint + [constraint_1]
    vertices_lst = list(range(1, n+1))
    triangles = itertools.combinations(vertices_lst, 3)
    for triangle in triangles:
        v_1 = triangle[0]
        v_2 = triangle[1]
        v_3 = triangle[2]
        vertices = [v_1, v_2, v_3]
        vertices.sort()
        edge_1 = (vertices[0], vertices[1])
        edge_2 = (vertices[1], vertices[2])
        edge_3 = (vertices[0], vertices[2])
        constraint_2 = [-edge_dict[edge_1], -edge_dict[edge_2], -edge_dict[edge_3], color_var[v_1], color_var[v_2], color_var[v_3]]
        constraint = constraint + [constraint_2]
    for clause in constraint:
        cnf.append(clause)
    cnf.to_file('colorable_' + str(n))

for i in range(20, 23):
    colorable(i)