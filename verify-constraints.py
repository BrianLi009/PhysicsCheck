import sys
import networkx as nx
import subprocess
from networkx.algorithms import isomorphism
import itertools
sys.path.insert(0, './gen_instance')
from pysat.formula import CNF 

def check_squarefree(G):
    square_graph = nx.Graph()
    edge_lst = [(1, 2), (2, 3), (3, 4), (4, 1)]
    square_graph.add_edges_from(edge_lst)
    gm = isomorphism.GraphMatcher(G, square_graph)
    if gm.subgraph_is_monomorphic():
        return False
    else:
        return True

def check_non_colorable(edge_lst, n):
    """
    given a list of edges, return a valid coloring if possible
    """
    cnf = CNF()
    clause = []
    edge_lst = [[z+1 for z in y] for y in edge_lst]
    for edge in edge_lst:
        clause = clause + [[-edge[0],-edge[1]]]
    vertices_lst = list(range(1, (max(max(edge_lst,key=lambda item:item[1])))+1))
    potential_triangles = list(itertools.combinations(vertices_lst, 3))
    for triangle in potential_triangles:
        v1 = triangle[0]
        v2 = triangle[1]
        v3 = triangle[2]
        if ([v1, v2] in edge_lst or [v2,v1] in edge_lst) and ([v2, v3] in edge_lst or [v3, v2] in edge_lst) and ([v1, v3] in edge_lst or [v3,v1] in edge_lst):
            clause = clause + [[v1,v2,v3]]
            clause = clause + [[-v1, -v2]]
            clause = clause + [[-v2, -v3]]
            clause = clause + [[-v1, -v3]]
        """
        if the triangle exists in this particular graph, it must satisfy 010 coloring
        """
    for c in clause:
        cnf.append(c)
    cnf.to_file("non_colorable_check"+"_"+str(n))
    

def check_triangle(G):
    check_dict = {}
    for v in G.nodes():
        check_dict[v] = False
        for e in itertools.combinations(list(G.neighbors(v)), 2):
            if e in G.edges():
                check_dict[v] = True
                break
    return ('False' not in check_dict)


def check_minimum_degree(G):
    degree_sequence = [d for n, d in G.degree()]
    degree_sequence.sort()
    if degree_sequence[0] >= 3:
        return True
    else:
        return False

def maple_to_edges(input, v):
    str_lst = input.split()[1:-1]
    edge_lst = []
    for j in range(0, v):
        for i in range(0,v):
            if i < j:
                edge_lst.append((i,j))
    actual_edges = []
    for i in str_lst:
        indicator = int(i)
        if indicator > 0:
            actual_edges.append(edge_lst[int(i)-1])
    return actual_edges

def verify(g, n):
    edge_lst = maple_to_edges(g, int(n))
    
    G = nx.Graph()
    G.add_edges_from(edge_lst)
    if not check_minimum_degree(G) or not check_squarefree(G) or not check_triangle(G):
        f = open("not_verified_"+str(n), "a")
        f.write(g + "\n")
        f.close()
    check_non_colorable(edge_lst, n)


if __name__ == "__main__":
    verify(sys.argv[1], sys.argv[2])


"""g = "a -1 -2 -3 -4 -5 -6 -7 -8 -9 -10 -11 -12 -13 -14 -15 -16 -17 -18 -19 -20 21 -22 -23 -24 -25 -26 27 28 -29 -30 -31 -32 33 -34 -35 -36 -37 -38 -39 40 -41 -42 -43 44 -45 -46 -47 48 -49 -50 -51 -52 53 54 55 -56 -57 58 59 -60 -61 62 -63 -64 -65 -66 -67 68 -69 -70 71 -72 73 -74 -75 -76 -77 78 -79 80 -81 82 -83 84 -85 -86 -87 -88 -89 -90 -91 -92 93 94 -95 -96 -97 -98 -99 -100 -101 102 -103 -104 105 106 -107 -108 -109 110 111 -112 -113 114 -115 -116 -117 -118 119 -120 121 -122 -123 124 -125 -126 -127 -128 -129 130 -131 -132 -133 -134 -135 -136 137 -138 139 -140 -141 -142 -143 -144 -145 -146 -147 148 -149 -150 -151 152 -153 154 155 -156 -157 -158 -159 -160 -161 -162 -163 -164 -165 166 -167 -168 -169 170 -171 0"
verify(g, 19)"""