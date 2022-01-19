import itertools

def squarefree(n, edge_dict):
    """
    input number of vertices n, and the variable dictionary, generate the SAT encoding for squarefree graph
    return a list of tuple, where each tuple is a clause, and each integer is a variable
    """
    constraint = []
    vertices_lst = list(range(1, n+1))
    all_comb = list(itertools.combinations(vertices_lst, 4)) #list of all possible squares
    """
    edge_lst contains all possible edges expressed by v1,v2
    all_comb represents all possible combination of 4 vertices that makes a square
    """
    for square in all_comb:
        all_edges = list(itertools.combinations(square, 2)) #find all edges within this square
        constraint_1 = [-edge_dict[all_edges[0]],-edge_dict[all_edges[2]], -edge_dict[all_edges[3]], -edge_dict[all_edges[5]]]
        constraint_2 = [-edge_dict[all_edges[1]],-edge_dict[all_edges[2]], -edge_dict[all_edges[3]], -edge_dict[all_edges[4]]]
        constraint_3 = [-edge_dict[all_edges[0]],-edge_dict[all_edges[1]], -edge_dict[all_edges[4]], -edge_dict[all_edges[5]]]
        constraint = constraint + [constraint_1, constraint_2, constraint_3]
    """
    add the constraints of each square
    """
    return constraint