import math
import csv

def gen_implication_clause(a,b):
    clause=[]
    if 'F' in a or 'T' in b: #whole clause is T if any variable in is T
        pass
    else:
        for i in a:
            if  i == 'T': #False variables in a DNF dont contribute.... does this give upper though??
                continue
            else:
                clause.append(str(-(i)))#pattern in the 4 clauses, a is always -ive
        for j in b:
            if j == 'F':
                continue
            else:
                clause.append(str(j))#pattern in the 4 clauses, b is always +ive
        #clause.append("0"+"\n")
        return(clause)

# Generate clauses encoding that between lower and upper variables in X are assigned true (using sequential counters)
def generate_degree_clauses(X, lower, upper, start_var, cnf_file):
    global total_vars
    clauses = []
    total_vars=start_var
    n = len(X)
    k = upper+1

    S = [[0 for j in range(k+1)] for i in range(n+1)]

    for i in range(n+1):
        S[i][0] = 'T'

    for j in range(1, k+1):
        S[0][j] = 'F'

    S[n][lower] = 'T' #at least lower are T
    S[n][k] = 'F' #upper +1 is F

    # Define new auxiliary variables (and updates the global variable total_vars)
    for i in range(n+1):
        for j in range(k+1):
            if S[i][j] == 0:
                total_vars += 1
                S[i][j] = total_vars

    # Generate clauses encoding cardinality constraint
    for i in range(1, n+1):
        for j in range(1, k+1):
            clauses.append(gen_implication_clause({S[i-1][j]}, {S[i][j]}))
            clauses.append(gen_implication_clause({X[i-1], S[i-1][j-1]}, {S[i][j]}))
            clauses.append(gen_implication_clause({S[i][j]}, {S[i-1][j], X[i-1]}))
            clauses.append(gen_implication_clause({S[i][j]}, {S[i-1][j], S[i-1][j-1]}))
    clauses = [i for i in clauses if i is not None]
    clause_count=0
    
    cnf = open(cnf_file, 'a+')
    for clause in clauses:
        string_lst = []
        for var in clause:
            string_lst.append(str(var))
        string = ' '.join(string_lst)
        #print(string)
        cnf.write(string + " 0\n")
        clause_count += 1
    
    return(total_vars,clause_count)
