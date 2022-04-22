import networkx as nx
import sys
from networkx.algorithms import isomorphism

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

def produce(n):
    """produce the corresponding graph from the embedability output"""
    my_file = open("nonembed_graph_sat_" + str(n) + ".txt", "r")
    content = my_file.read()
    min_non_subgraphs = content.split("\n")
    my_file.close()
    return min_non_subgraphs

def subgraph_check(order, subgraph):
    for graph in produce(order):
        g = nx.Graph(maple_to_edges(graph, order))
        string = subgraph
        comparison = nx.from_graph6_bytes(bytes(string, encoding='utf-8'))
        gm = isomorphism.GraphMatcher(g, comparison)
        if gm.subgraph_is_monomorphic():
            print (graph)

#subgraph_check(11, "I?qa``eeO")

def filter_non_minimal_10():
    try:
        file_10 = open("min_nonembed_graph_sat_10.txt", "r")
        content = file_10.read()
        graph_lst_10 = content.split("\n")
        if '' in graph_lst_10:
            graph_lst_10.remove('')
        file_10.close()
    except:
        print ("make sure all files are generated")
        sys.exit(1)
    temp_lst_10 = graph_lst_10.copy()
    for graph in graph_lst_10:
        for g in graph_lst_10:
            if graph != g:
                GM = isomorphism.GraphMatcher(nx.Graph(maple_to_edges(graph, 10)), nx.Graph(maple_to_edges(g, 10)))
                if GM.subgraph_is_monomorphic():
                    if graph in temp_lst_10:
                        temp_lst_10.remove(graph)
    f = open("min_nonembed_graph_sat_10.txt", "w")
    for item in temp_lst_10:
        f.write(item + "\n")
    f.close()

def filter_non_minimal_11():
    try:
        file_11 = open("nonembed_graph_sat_11.txt", "r")
        content = file_11.read()
        graph_lst_11 = content.split("\n")
        if '' in graph_lst_11:
            graph_lst_11.remove('')
        file_11.close()
        file_10 = open("min_nonembed_graph_sat_10.txt", "r")
        content = file_10.read()
        graph_lst_10 = content.split("\n")
        if '' in graph_lst_10:
            graph_lst_10.remove('')
        file_10.close()
    except:
        print ("make sure all files are generated")
        sys.exit(1)
    temp_lst_11 = graph_lst_11.copy()
    for graph in graph_lst_11:
        for g in graph_lst_11:
            if graph != g:
                GM = isomorphism.GraphMatcher(nx.Graph(maple_to_edges(graph, 11)), nx.Graph(maple_to_edges(g, 11)))
                if GM.subgraph_is_monomorphic():
                    if graph in temp_lst_11:
                        temp_lst_11.remove(graph)
    for graph in graph_lst_11:
        for g in graph_lst_10:
            GM = isomorphism.GraphMatcher(nx.Graph(maple_to_edges(graph, 11)), nx.Graph(maple_to_edges(g, 10)))
            if GM.subgraph_is_monomorphic():
                if graph in temp_lst_11:
                    temp_lst_11.remove(graph)
    f = open("min_nonembed_graph_sat_11.txt", "w")
    for item in temp_lst_11:
        f.write(item + "\n")
    f.close()

def filter_non_minimal_12():
    try:
        file_12 = open("nonembed_graph_sat_12.txt", "r")
        content = file_12.read()
        graph_lst_12 = content.split("\n")
        if '' in graph_lst_12:
            graph_lst_12.remove('')
        file_12.close()
        file_11 = open("min_nonembed_graph_sat_11.txt", "r")
        content = file_11.read()
        graph_lst_11 = content.split("\n")
        if '' in graph_lst_11:
            graph_lst_11.remove('')
        file_11.close()
        file_10 = open("min_nonembed_graph_sat_10.txt", "r")
        content = file_10.read()
        graph_lst_10 = content.split("\n")
        if '' in graph_lst_10:
            graph_lst_10.remove('')
        file_10.close()
    except:
        print ("make sure all files are generated")
        sys.exit(1)
    temp_lst_12 = graph_lst_12.copy()
    for graph in graph_lst_12:
        for g in graph_lst_12:
            if graph != g:
                GM = isomorphism.GraphMatcher(nx.Graph(maple_to_edges(graph, 12)), nx.Graph(maple_to_edges(g, 12)))
                if GM.subgraph_is_monomorphic():
                    if graph in temp_lst_12:
                        temp_lst_12.remove(graph)
    for graph in graph_lst_12:
        for g in graph_lst_10:
            GM = isomorphism.GraphMatcher(nx.Graph(maple_to_edges(graph, 12)), nx.Graph(maple_to_edges(g, 10)))
            if GM.subgraph_is_monomorphic():
                if graph in temp_lst_12:
                    temp_lst_12.remove(graph)
    for graph in graph_lst_12:
        for g in graph_lst_11:
            GM = isomorphism.GraphMatcher(nx.Graph(maple_to_edges(graph, 12)), nx.Graph(maple_to_edges(g, 11)))
            if GM.subgraph_is_monomorphic():
                if graph in temp_lst_12:
                    temp_lst_12.remove(graph)
    f = open("min_nonembed_graph_sat_12.txt", "w")
    for item in temp_lst_12:
        f.write(item + "\n")
    f.close()

def verify(n):
    """n has to be either 10, 11, or 12"""
    if int(n) == 10:
        print ("entered")
        filter_non_minimal_10()
    elif int(n) == 11:
        filter_non_minimal_11()
    elif int(n) == 12:
        filter_non_minimal_12()
    else:
        print ("currently only taking order 10, 11, or 12 for analyze_subgraph.py")

if __name__ == "__main__":
    verify(sys.argv[1])

"""file_12 = open("min_nonembed_graph_sat_12.txt", "r")
content = file_12.read()
graph_lst_12 = content.split("\n")
if '' in graph_lst_12:
    graph_lst_12.remove('')
file_12.close()

for graph in graph_lst_12:
    g = nx.Graph(maple_to_edges(graph, 12))
    string = "K`?LAQOP@KbK"
    comparison = nx.from_graph6_bytes(bytes(string, encoding='utf-8'))
    GM = isomorphism.GraphMatcher(g, comparison)
    if GM.is_isomorphic():
        print (graph_lst_12.index(graph))"""