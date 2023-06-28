import itertools
from itertools import combinations

def conway(n, edge_dict, tri_dict, vs, t, cnf, var_count):
    #at least vs vertices are connected to at least t triangles
    clause_count = 0
    cnf_file = open(cnf, 'a+')
    vertices_lst = list(range(1, n+1))
    all_tri = list(itertools.combinations(vertices_lst, 3))
    ind_var_lst = []
    for v in range(1, n+1):
        ind_var = var_count + 1 # not ind_var or clause, ind_var or not clause for every clause
        ind_var_lst.append(ind_var)
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
            #cnf_file.write(str(ind_var) + " " + "-" + clause + " 0\n")
            clause_count += 1
        for i in range(0, len(v_tri_lst)+1): # si,0 will be true for 0 ≤ i ≤ n
            clause = str(extra_var_dict[(i,0)])
            cnf_file.write("-" + str(ind_var) + " " + clause + " 0\n")
            #cnf_file.write(str(ind_var) + " " + "-" + clause + " 0\n")
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
    return var_count, clause_count