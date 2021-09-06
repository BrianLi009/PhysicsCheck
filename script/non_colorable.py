import itertools
import math

def non_colorable(n):
    constraint = []
    edge_dict = {}
    counter = 1
    vertices_lst = list(range(1, n+1))
    edge_lst = list(itertools.combinations(vertices_lst, 2))
    extra_var_count = len(edge_lst)+1
    extra_var_dict = {}
    for triangle in list(itertools.combinations(vertices_lst, 3)):
        extra_var_dict[triangle] = extra_var_count
        extra_var_count += 1
    for edge in edge_lst:
        edge_dict[edge] = counter
        counter += 1
    """this script version does not contain the programmable interface"""
    maximum = math.ceil(n/3)+1
    for i in range(1, maximum+2):
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
                    constraint_1.append(extra_var_dict[triangle])
            constraint = constraint + [constraint_1]
    """tri_constraint = []
    for triangle in extra_var_dict.keys():
        v_1 = triangle[0]
        v_2 = triangle[1]
        v_3 = triangle[2]
        vertices = [v_1, v_2, v_3]
        vertices.sort()
        edge_1 = (vertices[0], vertices[1])
        edge_2 = (vertices[1], vertices[2])
        edge_3 = (vertices[0], vertices[2])
        tri_constraint.append([edge_dict[edge_1],-extra_var_dict[triangle]])
        tri_constraint.append([edge_dict[edge_2],-extra_var_dict[triangle]])
        tri_constraint.append([edge_dict[edge_3],-extra_var_dict[triangle]])
    constraint = constraint + tri_constraint""" #the tri_constraint is redundant if triangle.py is being used
    return constraint