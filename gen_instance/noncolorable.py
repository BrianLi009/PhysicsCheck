import itertools
import math

def noncolorable(n, edge_dict, tri_dict, cnf, blocked=0.5):
    cnf_file = open(cnf, 'a+')
    clause_count = 0
    vertices_lst = list(range(1, n+1))
    for i in range(1, math.ceil(n*blocked+1)):
        #block all labelings with i label-1s
        possible_comb = list(itertools.combinations(vertices_lst, i))
        #possible_comb contains all possible ways to label the graph with i label-1's
        for choice in possible_comb: 
            constraint_1_lst = []
            trig_vertices = []
            for v in vertices_lst:
                if v not in choice:
                    #if v is not chosen to be colored as 1, it's colored 0 and is put in the list of potential vertices in a '000' triangle
                    trig_vertices.append(v)
            all_edges = list(itertools.combinations(choice, 2))
            for e in all_edges:
                constraint_1_lst.append(str(edge_dict[e])) # At least a pair of label-1 vertices are connected.
            if len(trig_vertices) > 2:
                all_triangle  = list(itertools.combinations(trig_vertices, 3))
                for triangle in all_triangle: 
                    constraint_1_lst.append(str(tri_dict[triangle])) # At least a set of three label-0 vertices form a C_3 subgraph.
            constraint_1 = ' '.join(constraint_1_lst)
            cnf_file.write(constraint_1 + " 0\n")
            clause_count += 1
    return clause_count
