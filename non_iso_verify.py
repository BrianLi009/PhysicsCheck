import networkx as nx
import itertools

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

def get_hash(G):
    return nx.to_graph6_bytes(G)

def verify(f, n):
    with open(f) as f:
        lines = f.readlines()
    hash_lst = []
    # Create list of graphs
    for line in lines:
        edge_lst = maple_to_edges(line, int(n))
        G = nx.Graph()
        G.add_edges_from(edge_lst)
        hash = get_hash(G)
        if hash not in hash_lst:
            hash_lst.append(hash)
        else:
            print (hash)
            print ("found duplicates")
    print ("verified")

"""if __name__ == "__main__":
    #input filename, order
    verify(sys.argv[1], sys.argv[2])"""

verify("19.exhaust", 19)