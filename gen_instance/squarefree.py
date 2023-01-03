import itertools

def squarefree(n, edge_dict, cnf):
    """
    input number of vertices n, and the variable dictionary, generate the SAT encoding for squarefree graph
    return a list of tuple, where each tuple is a clause, and each integer is a variable
    """
    clause_count = 0
    cnf_file = open(cnf, 'a+')
    vertices_lst = list(range(1, n+1))
    all_comb = list(itertools.combinations(vertices_lst, 4)) #list of all possible squares
    """
    edge_lst contains all possible edges expressed by v1,v2
    all_comb represents all possible combination of 4 vertices that makes a square
    """
    for square in all_comb:
        all_edges = list(itertools.combinations(square, 2)) #find all edges within this square
        cnf_file.write('{} {} {} {} 0\n'.format(str(-edge_dict[all_edges[0]]), str(-edge_dict[all_edges[2]]), str(-edge_dict[all_edges[3]]), str(-edge_dict[all_edges[5]])))
        cnf_file.write('{} {} {} {} 0\n'.format(str(-edge_dict[all_edges[1]]), str(-edge_dict[all_edges[2]]), str(-edge_dict[all_edges[3]]), str(-edge_dict[all_edges[4]])))
        cnf_file.write('{} {} {} {} 0\n'.format(str(-edge_dict[all_edges[0]]), str(-edge_dict[all_edges[1]]), str(-edge_dict[all_edges[4]]), str(-edge_dict[all_edges[5]])))
        clause_count += 3
    return clause_count
