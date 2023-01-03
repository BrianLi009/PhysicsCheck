import itertools

def conway(n, edge_dict, tri_dict, v, t, cnf):
    #vertex v is connected to at least t triangles
    clause_count = 0
    cnf_file = open(cnf, 'a+')
    vertices_lst = list(range(1, n+1))
    all_tri = list(itertools.combinations(vertices_lst, 3))
    v_tri_lst = [tri for tri in all_tri if v in tri]
    tr_sublst = itertools.combinations(v_tri_lst, int(len(v_tri_lst)-t))
    for comb in tr_sublst:
        clause_lst = []
        for tri in comb:
            clause_lst.append(str(tri_dict[tri]))
        clause = ' '.join(clause_lst)
        cnf_file.write(clause + " 0\n")
        clause_count += 1
    return clause_count