#!/usr/bin/python

import sys
import networkx as nx
from networkx.algorithms import isomorphism
import itertools
sys.path.insert(0, './gen_instance')
from pysat.formula import CNF 
import subprocess

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
        for i in range(0, j):
            edge_lst.append((i,j))
    actual_edges = []
    for i in str_lst:
        indicator = int(i)
        if indicator > 0:
            actual_edges.append(edge_lst[int(i)-1])
    return actual_edges

def verify_single(g, n):
    edge_lst = maple_to_edges(g, int(n))
    G = nx.Graph()
    G.add_edges_from(edge_lst)
    if not check_minimum_degree(G) or not check_squarefree(G) or not check_triangle(G):
        f = open("not_verified_"+str(n), "a")
        f.write(g + "\n")
        f.close()
    check_non_colorable(edge_lst, n)
    cnf_file = "non_colorable_check_" + str(n)
    result = subprocess.call(["cadical/build/cadical", cnf_file], stdout=subprocess.DEVNULL)
    
    if result != 20:
        with open(f"not_verified_{n}", "a") as file:
            file.write(g + " \n")

def verify(file_to_verify, n):
    with open(file_to_verify) as f:
        for line in f:
            line = line.rstrip()
            verify_single(line, n)
            
if __name__ == "__main__":
    verify(sys.argv[1], sys.argv[2])