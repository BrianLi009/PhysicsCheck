import itertools
from itertools import combinations

def generate_implication_clause(X, Y):
    clause = []
    for x in X:
        clause.append(-x)
    for y in Y:
        clause.append(y)
    return clause

def conway(n, edge_dict, tri_dict, ind_var_dict, vs, t, cnf, var_count, fixed = False):
    #at least vs vertices are connected to at least t triangles
    clause_count = 0
    cnf_file = open(cnf, 'a+')
    vertices_lst = list(range(1, n+1))

    #needed if triangle constraint is not on
    """for triangle in list(itertools.combinations(vertices_lst, 3)):
        # the following encoding are applied in every possible triangle in the graph
        # given a triangle, if encode the equivalence relation
        v_1 = triangle[0]
        v_2 = triangle[1]
        v_3 = triangle[2]
        vertices = [v_1, v_2, v_3]
        vertices.sort()
        edge_1 = (vertices[0], vertices[1])
        edge_2 = (vertices[1], vertices[2])
        edge_3 = (vertices[0], vertices[2])
        cnf_file.write('{} {} 0\n'.format(str(edge_dict[edge_1]), str(-tri_dict[triangle])))
        cnf_file.write('{} {} 0\n'.format(str(edge_dict[edge_2]), str(-tri_dict[triangle])))
        cnf_file.write('{} {} 0\n'.format(str(edge_dict[edge_3]), str(-tri_dict[triangle])))
        cnf_file.write('{} {} {} {} 0\n'.format(str(-edge_dict[edge_1]), str(-edge_dict[edge_2]), str(-edge_dict[edge_3]), str(tri_dict[triangle])))
        clause_count += 4"""
    
    all_tri = list(itertools.combinations(vertices_lst, 3))
    ind_var_lst = []
    for v in range(1, n+1):
        ind_var = var_count + 1 # not ind_var or clause, ind_var or not clause for every clause
        ind_var_lst.append(ind_var)
        ind_var_dict[ind_var] = v
        var_count += 1
        v_tri_lst = [tri for tri in all_tri if v in tri] #triangles containing v
        #want to include that at least t of the vars are True
        extra_var_dict = {}
        for i in range(0, len(v_tri_lst)+1): #0 to n
            for j in range(0, t+1): #0 to t
                extra_var_dict[(i,j)] = var_count + 1
                var_count += 1
        for j in range(1, t+1): # s0,j will be false for 1 ≤ j ≤ t
            clause = "-" + str(extra_var_dict[(0,j)])
            cnf_file.write("-" + str(ind_var) + " " + clause + " 0\n")
            clause_count += 1
        for i in range(0, len(v_tri_lst)+1): # si,0 will be true for 0 ≤ i ≤ n
            clause = str(extra_var_dict[(i,0)])
            cnf_file.write("-" + str(ind_var) + " " + clause + " 0\n")
            clause_count += 1
        for i in range(1, len(v_tri_lst)+1):
            for j in range(1, t+1):
                clause_1 = "-" + str(extra_var_dict[(i-1,j)]) + " " + str(extra_var_dict[(i,j)])
                clause_2 = "-" + str(tri_dict[v_tri_lst[i-1]]) + " " + "-" + str(extra_var_dict[(i-1,j-1)]) + " " + str(extra_var_dict[(i,j)])
                clause_3 = "-" + str(extra_var_dict[(i,j)]) + " " + str(extra_var_dict[(i-1,j)]) + " " + str(tri_dict[v_tri_lst[i-1]])
                clause_4 = "-" + str(extra_var_dict[(i,j)]) + " " + str(extra_var_dict[(i-1,j)]) + " " + str(extra_var_dict[(i-1,j-1)])
                cnf_file.write("-" + str(ind_var) + " " + clause_1 + " 0\n")
                cnf_file.write("-" + str(ind_var) + " " + clause_2 + " 0\n")
                cnf_file.write("-" + str(ind_var) + " " + clause_3 + " 0\n")
                cnf_file.write("-" + str(ind_var) + " " + clause_4 + " 0\n")
                clause_count += 4
        clause = str(extra_var_dict[(len(v_tri_lst),t)])
        cnf_file.write("-" + str(ind_var) + " " + clause + " 0\n")
        clause_count += 1
    combinations_lst = list(combinations(ind_var_lst, int(len(ind_var_lst))-int(vs)+1))
    # Print the combinations
    for combination in combinations_lst:
        constraint_1 = ' '.join(str(value) for value in combination)
        cnf_file.write(constraint_1 + " 0\n")
        clause_count += 1
    if fixed:
        all_ind_vars = list(ind_var_dict.keys())
        mid_tri_lst = list(combinations(all_ind_vars, 3))
        #for each 3-combination of the indicator variables in ind_var_dict (i1, i2, i3), encode the clause (i1 and i2 and i3) -> triangle ind_var_dict[i1], ind_var_dict[i2], ind_var_dict[i3]
        #not i1 or not i2 or not i3 or triangle 
        for comb in mid_tri_lst:
            i1, i2, i3 = comb[0], comb[1], comb[2]
            tri_1, tri_2, tri_3 = ind_var_dict[i1], ind_var_dict[i2], ind_var_dict[i3]
            if tri_1 != tri_2 and tri_1 != tri_3 and tri_2 != tri_3:
                tri = [tri_1, tri_2, tri_3]
                tri.sort()
                clause = "-" + str(i1) + " " + "-" + str(i2) + " " + "-" + str(i3) + " " + str(tri_dict[(tri[0], tri[1], tri[2])])
                cnf_file.write(clause + " 0\n")
                clause_count += 1
    return var_count, clause_count, ind_var_dict
