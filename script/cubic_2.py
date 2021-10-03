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

def generate_lex_clauses(X, Y, strict, total_vars):
    clauses = []
    n = len(X)
    clauses = clauses + [generate_implication_clause({X[0]}, {Y[0]})]
    clauses = clauses + [generate_implication_clause({X[0]}, {total_vars+1})]
    clauses = clauses + [generate_clause({Y[0], total_vars+1})]
    for k in range(1, n-1):
        clauses = clauses + [generate_implication_clause({total_vars+k}, {-X[k], Y[k]})]
        clauses = clauses + [generate_implication_clause({total_vars+k}, {-X[k], total_vars+k+1})]
        clauses = clauses + [generate_implication_clause({total_vars+k}, {Y[k], total_vars+k+1})]
    if strict:
        clauses = clauses + [generate_implication_clause({total_vars+n-1}, {-X[n-1]})]
        clauses = clauses + [generate_implication_clause({total_vars+n-1}, {Y[n-1]})]
    else:
        clauses = clauses + [generate_implication_clause({total_vars+n-1}, {-X[n-1], Y[n-1]})]
    return clauses

def generate_lex(n, total_vars=0):
    clauses = []
    B = [[0 for j in range(n)] for i in range(n)]
    for j in range(n):
	    for i in range(j):
                total_vars += 1
                B[i][j] = total_vars
                B[j][i] = total_vars
    for j in range(n):
        for i in range(j):
            clauses = clauses + generate_lex_clauses(B[i][:i]+B[i][i+1:j]+B[i][j+1:], B[j][:i]+B[j][i+1:j]+B[j][j+1:], False, total_vars)
    return clauses