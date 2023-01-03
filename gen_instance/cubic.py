#https://www.cs.cmu.edu/~mheule/publications/MiCS.pdf

def generate_clause(X):
    clause = []
    for x in X:
        clause.append(x)
    return clause

def generate_implication_clause(X, Y):
    clause = []
    for x in X:
        clause.append(-x)
    for y in Y:
        clause.append(y)
    return clause

# Generate clauses encoding that the vector X is lexicographically less than (or equal to if strict is false) vector Y
def generate_lex_clauses(X, Y, strict, total_vars):
    clauses = []
    n = len(X)
    clauses.append(generate_implication_clause({X[0]}, {Y[0]}))
    clauses.append(generate_implication_clause({X[0]}, {total_vars+1}))
    clauses.append(generate_clause({Y[0], total_vars+1}))
    for k in range(1, n-1): 
        clauses.append(generate_implication_clause({total_vars+k}, {-X[k], Y[k]}))
        clauses.append(generate_implication_clause({total_vars+k}, {-X[k], total_vars+k+1}))
        clauses.append(generate_implication_clause({total_vars+k}, {Y[k], total_vars+k+1}))
    if strict:
        clauses.append(generate_implication_clause({total_vars+n-1}, {-X[n-1]}))
        clauses.append(generate_implication_clause({total_vars+n-1}, {Y[n-1]}))
    else:
        clauses.append(generate_implication_clause({total_vars+n-1}, {-X[n-1], Y[n-1]}))
    return (clauses, total_vars+n-1)

def cubic(n, count, cnf):
    clause_count = 0
    cnf_file = open(cnf, 'a+')
    clauses = []
    total_vars = 0
    B = [[0 for j in range(n)] for i in range(n)]
    for j in range(n):
        for i in range(j):
                total_vars += 1
                B[i][j] = total_vars
                B[j][i] = total_vars
    for j in range(n):
        for i in range(j):
            clause, count = generate_lex_clauses(B[i][:i]+B[i][i+1:j]+B[i][j+1:], B[j][:i]+B[j][i+1:j]+B[j][j+1:], False, count) #generate the lex constraint here A_{ij} \leq A_{ji}
            #print (count)
            clauses += clause
    for clause in clauses:
        string_lst = []
        for var in clause:
            string_lst.append(str(var))
        string = ' '.join(string_lst)
        cnf_file.write(string + " 0\n")
        clause_count += 1
    return count, clause_count
