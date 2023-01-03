import itertools

def mindegree(n, edge_dict, cnf):
    clause_count = 0
    cnf_file = open(cnf, 'a+')
    vertices_lst = list(range(1, n+1))
    if n <= 3:
        for v in vertices_lst:
            cnf_file.write(str(-v) + " 0\n")
            clause_count += 1
    else:
        for v in vertices_lst:
            #pick a vertex
            vertices_lst_copy = vertices_lst.copy()
            vertices_lst_copy.remove(v)
            for choice in list(itertools.combinations(vertices_lst_copy, n-3)):
                # a conjunction over all subsets of size n-3
                constraint_1_lst = []
                for v_2 in choice:
                    edge = tuple(sorted((v, v_2)))
                    constraint_1_lst.append(str(edge_dict[edge]))
                constraint_1 = ' '.join(constraint_1_lst)
                cnf_file.write(constraint_1 + " 0\n")
                clause_count += 1
    return clause_count
