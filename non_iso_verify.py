import networkx as nx
import itertools
from networkx.algorithms import isomorphism
import sys

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

def get_hash(G):
    return nx.weisfeiler_lehman_graph_hash(G)

def verify(f, n):
    f_log = open(str(n) + ".isomorphism", "w")
    with open(f) as f:
        lines = f.readlines()
    hash_table = {}
    for line in lines:
        edge_lst = maple_to_edges(line, int(n))
        G = nx.Graph()
        G.add_edges_from(edge_lst)
        hash = get_hash(G)
        if hash in hash_table:
            for i in range(len(hash_table[hash])):
                G1 = hash_table[hash][i]
                if nx.is_isomorphic(G1, G):
                    print ("found isomorphic candidates, logging it")
                    f_log.write(line)
                else:
                    hash_table[hash].append(G)
        else:
            hash_table[hash] = [G]
        

if __name__ == "__main__":
    #input filename, order
    verify(sys.argv[1], sys.argv[2])