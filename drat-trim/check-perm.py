#!/usr/bin/env python3

# This script takes a list of trusted clauses in a DRAT proof and a list of permutations and verifies that
# applying the ith permutation to the ith clause produces a clause blocking a lex-smaller object

import sys
import fileinput
import time
start = time.time()

verbose = "-v" in sys.argv
if verbose: sys.argv.remove("-v")

# Return inverse of permutation
def inv(p):
	p_inv = ['*' for i in range(n)]
	for i in range(n):
		p_inv[p[i]] = i
	return p_inv

# Convert literal vector vec to a matrix
def to_matrix(vec):
	M = [['._'+str(min(i,j))+'_'+str(max(i,j)) for i in range(n)] for j in range(n)]
	for l in vec:
		i = d_i[abs(l)]
		j = d_j[abs(l)]
		if l > 0:
			M[i][j] = 1
			M[j][i] = 1
		elif l < 0:
			M[i][j] = 0
			M[j][i] = 0
	return M

# Convert literal vector vec to a matrix and permute the rows and columns using permutation p
def to_matrix_perm(vec, p):
	M = [['._'+str(min(inv(p)[i],inv(p)[j]))+'_'+str(max(inv(p)[i],inv(p)[j])) for i in range(n)] for j in range(n)]
	for l in vec:
		i = p[d_i[abs(l)]]
		j = p[d_j[abs(l)]]
		if l > 0:
			M[i][j] = 1
			M[j][i] = 1
		elif l < 0:
			M[i][j] = 0
			M[j][i] = 0
	return M

# Return a string representation of matrix M
def to_string(M):
	s = ""
	for i in range(n):
		for j in range(n):
			s += str(M[i][j])[0]
		s += "\n"
	return s[:-1]

# Return a string with matrices M1 and M2 side by side
def to_string_dual(M1, M2):
	s = ""
	for i in range(n):
		for j in range(n):
			s += str(M1[i][j])[0]
		s += " | "
		for j in range(n):
			s += str(M2[i][j])[0]
		s += "\n"
	return s[:-1]

# Returns true if M1 is strictly lexicographically smaller than M2
def matrix_lex(M1, M2):
	for i in range(n):
		for j in range(i):
			if M1[i][j] == 0 and M2[i][j] == 1:
				return True
			elif M1[i][j] == 0:
				continue
			elif M2[i][j] == 1:
				continue
			elif M1[i][j] == 1 and M2[i][j] == 0:
				return False
			elif M1[i][j] != M2[i][j]:
				if verbose:
					print(str(M1[i][j]) + " != " + str(M2[i][j]))
				return False
	return False

# Extend given permutation to a full permutation of {0, ..., n-1}
def extend_perm(p):
	for i in range(n):
		if not(i in p):
			p.append(i)

if len(sys.argv) <= 2:
	print("Need order and filename of permutation witnesses on the command-line (and clauses to check on standard input)")
	quit()

n = int(sys.argv[1])
permfile = sys.argv[2]

c = 1
d_i = dict()
d_j = dict()
for i in range(n):
	for j in range(i):
		d_i[c] = i
		d_j[c] = j
		c += 1

lines = sys.stdin.readlines()

c = 0
sols = 0
for perm in fileinput.input(permfile):
	line = lines[c]
	line = line.split()
	
	assert(line[0] == 't')
	assert(line[-1] == '0')
	line = list(map(lambda x: -int(x), line[1:-1]))

	if "Complete solution" in perm:
		assert(len(line) == n*(n-1)/2)
		sols += 1
		c += 1
		continue

	perm = list(map(int, perm.split()))
	origperm = list(perm)
	extend_perm(perm)
	perm = inv(perm)

	M1 = to_matrix(line)
	M2 = to_matrix_perm(line, perm)
	lex = matrix_lex(M2, M1)

	if not(lex) or verbose:
		print(origperm, perm, line, lex)
		print(to_string_dual(to_matrix_perm(line, perm), to_matrix(line)))

	assert(lex)
	c += 1

if c == len(lines):
	print("VERIFIED: All {} noncanonical blocking clauses verified with {} complete solutions found ({} sec)".format(len(lines), sols, round(time.time() - start, 2)))
else:
	print("Verified {} of {} noncanonical blocking clauses".format(c, len(lines)))
