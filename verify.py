<<<<<<< HEAD
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
<<<<<<< HEAD
        with open(f"verification/verified_{p}_{q}.log", "a") as f:
            f.write(f"{n}:SAT \n")
            f.write([nx.graph_clique_number(G_blue),nx.graph_clique_number(G_red)])

if __name__ == "__main__":
    verify(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
=======
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
>>>>>>> upstream/master
