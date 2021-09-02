n = 5

if n <= 2:
	print ("Order must be 3 or greater")
	quit()

# Number of variables in adjacency matrix
N = int(n*(n-1)/2)

# Counter for # of variables used in SAT instance
total_vars = 0
# List to hold clauses of SAT instance
clauses = []

# Generate a clause containing the literals in the set X
def generate_clause(X):
	clause = ""
	for x in X:
		clause += str(x) + " "
	clauses.append(clause + "0")

# Generate a clause specifying (x1 & ... & xn) -> (y1 | ... | yk)
# where X = {x1, ..., xn} and Y = {y1, ..., yk}
def generate_implication_clause(X, Y):
	clause = ""
	for x in X:
		clause += str(-x) + " "
	for y in Y:
		clause += str(y) + " "
	clauses.append(clause + "0")

# Generate clauses encoding that at most one variable in X is assigned true
def generate_at_most_one_clauses(X):
	n = len(X)
	for i in range(n):
		for j in range(i+1, n):
			generate_clause({-X[i], -X[j]})

# Generate clauses encoding exactly one variable in X is assigned true
def generate_exactly_one_clauses(X):
	generate_at_most_one_clauses(X)
	generate_clause(X)

# Generate clauses encoding that the vector X is lexicographically less than (or equal to if strict is false) vector Y
def generate_lex_clauses(X, Y, strict):
	global total_vars
	n = len(X)

	generate_implication_clause({X[0]}, {Y[0]})
	generate_implication_clause({X[0]}, {total_vars+1})
	generate_clause({Y[0], total_vars+1})
	for k in range(1, n-1):
		generate_implication_clause({total_vars+k}, {-X[k], Y[k]})
		generate_implication_clause({total_vars+k}, {-X[k], total_vars+k+1})
		generate_implication_clause({total_vars+k}, {Y[k], total_vars+k+1})
	if strict:
		generate_implication_clause({total_vars+n-1}, {-X[n-1]})
		generate_implication_clause({total_vars+n-1}, {Y[n-1]})
	else:
		generate_implication_clause({total_vars+n-1}, {-X[n-1], Y[n-1]})

	total_vars += n-1

# Variables for A
A = [[0 for j in range(n)] for i in range(n)]
# Variables for B
B = [[0 for j in range(n)] for i in range(n)]
# Variables for P
P = [[0 for j in range(n)] for i in range(n)]

# Assign variables to entries of A
for j in range(n):
	for i in range(j):
		total_vars += 1
		A[i][j] = total_vars
		A[j][i] = total_vars

# Assign variables to entries of B
for j in range(n):
	for i in range(j):
		total_vars += 1
		B[i][j] = total_vars
		B[j][i] = total_vars

# Assign variables to entries of P
for i in range(n):
	for j in range(n):
		total_vars += 1
		P[i][j] = total_vars

# Exactly one entry in each row and column of P is 1
for i in range(n):
	generate_exactly_one_clauses([P[i][j] for j in range(n)])
	generate_exactly_one_clauses([P[j][i] for j in range(n)])

# Clauses which define B = P * A * P^(-1)
for i in range(n):
	for j in range(n):
		for k in range(n):
			for l in range(n):
				if i != j and k != l:
					generate_implication_clause({A[i][j], P[i][k], P[j][l]}, {B[k][l]})
					generate_implication_clause({B[k][l], P[i][k], P[j][l]}, {A[i][j]})

# Clauses which encode the cubic ordering constraint on B
"""for j in range(n):
	for i in range(j):
		generate_lex_clauses(B[i][:i]+B[i][i+1:j]+B[i][j+1:], B[j][:i]+B[j][i+1:j]+B[j][j+1:], False)"""

# Clauses which encode B is lex smaller than A
generate_lex_clauses(range(N+1,2*N+1), range(1,N+1), True)

# Output SAT instance in DIMACS format
f = open("orderly_cubic_" + str(n), "w")
f.write("p cnf {0} {1}".format(total_vars, len(clauses)) + "\n")
for clause in clauses:
	f.write(clause + "\n")
f.close()
