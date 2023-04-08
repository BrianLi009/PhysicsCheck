import itertools
import math
import networkx as nx
import csv
import sys

def verify(n,p,q): 
    vertices=range(1,n+1)
    edge_dict={}
    edge_counter=0
    edges =itertools.combinations(vertices,2)
    

    for j in range(1, n+1):             #regenerating the edge variables
        for i in range(1, n+1):
            if i < j:
                edge_counter += 1
                edge_dict[(i,j)] = edge_counter
                
    with open(f"verification/assignment_{n}_{p}_{q}.log") as csv_file: #read in file
        csv_reader = csv.reader(csv_file, delimiter=" ")
        for row in csv_reader:
            file1=row
    file1=file1[0:math.comb(n,2)] # take only first nC2 of input file (additional vars are from cubic constraint during generation)
    rev_edges=list(map(int, file1)) #edge assignment as list of integers
    
    G_blue = nx.Graph()
    G_blue.add_nodes_from([1, n])
    G_red = nx.Graph()
    G_red.add_nodes_from([1, n])
    
    for i in range(1,math.comb(n,2)+1): #search through edge vars. Starts at 1
        if rev_edges[i-1] > 0: #if edge assignment is positive, add it to blue graph
            e=list(edge_dict.keys())[list(edge_dict.values()).index((i))]
            G_blue.add_edge(*e)
        else:
            e=list(edge_dict.keys())[list(edge_dict.values()).index((i))]
            G_red.add_edge(*e)
            
    if nx.graph_clique_number(G_blue) >= q or nx.graph_clique_number(G_red) >= p: #encoding: all cliques of size p must have a blue (positive) edge. 98% sure
        with open(f"verification/verified_{p}_{q}.log", "a") as f:
            f.write(f"{n}:UNSAT \n") # ie if there is a red clique of size p (and...), then unsat. As we are searching for all p cliques containing 1 blue edge
            f.write(nx.graph_clique_number(G_blue))
            f.write(nx.graph_clique_number(G_red))
    else:
        with open(f"verification/verified_{p}_{q}.log", "a") as f:
            f.write(f"{n}:SAT \n")
            f.write([nx.graph_clique_number(G_blue),nx.graph_clique_number(G_red)])

if __name__ == "__main__":
    verify(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
