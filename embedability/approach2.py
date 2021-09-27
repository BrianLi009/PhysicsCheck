from bns_mod_di import *
import networkx as nx
from networkx.algorithms import isomorphism

"""big_g = nx.from_graph6_bytes(bytes("IqKaK?X@w", encoding='ascii'))
small_g = nx.from_graph6_bytes(bytes("I???????G", encoding='ascii'))
GM = isomorphism.GraphMatcher(big_g, small_g)
print (GM.subgraph_is_isomorphic())"""


file1 = open('squarefree_10_connected_reverse.txt', 'r')
Lines = file1.readlines()
count = 0
blocked_graph = []
for line in Lines:
    count += 1
    if count > 0:
        #print ("entered")
        x=list(line.split(': '))
        g6_string = x[-1][:-1]
        #if this is a subgraph of one of the blocked graph, continue
        #print (blocked_graph)
        for big_graph in blocked_graph:
            big_g = nx.from_graph6_bytes(bytes(big_graph, encoding='ascii'))
            small_g = nx.from_graph6_bytes(bytes(g6_string, encoding='ascii'))
            GM = isomorphism.GraphMatcher(big_g, small_g)
            if GM.subgraph_is_isomorphic():
                print (g6_string + " is a subgraph")
                continue
        #print (g6_string)
        graph_dict = g6_to_dict(g6_string)
        assignments = find_assignments(graph_dict, str(count))
        #print (assignments)
        #print ("solving assignment")
        assignment = assignments[0]
        determine_embed(graph_dict, assignment, str(count))
        with open('embed_result.txt', 'r+') as f:
            if ('  ' + str(count) + ', sat' in f.read()):
                f.write('\n' + g6_string + '\n')
                blocked_graph.append(g6_string)
                print ((g6_string) + (" blocked"))
            else:
                f.write('\n' + g6_string + '\n')