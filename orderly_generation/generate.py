from canonical import *
from cubic import *
from relabel import *
from pysat.formula import CNF

def generate_encoding(n):
    cnf = CNF()
    total_clause = []
    canonical = generate_canonical_clauses(n)
    cubic = block_iso(n)
    max_label = math.comb(n,2)*2+n**2+(math.comb(n,2)-1)
    relabeled_dict = {}
    for constraint in canonical:
        total_clause = total_clause + [constraint]
        cnf.append(constraint)
    for constraint in cubic:
        #print ("original:")
        #print (constraint)
        relabelled = relabel_cubic(constraint, n, max_label, relabeled_dict)
        constraint = relabelled[0]
        max_label = relabelled[1]
        relabeled_dict = relabelled[2]
        #print ("relabled to upper triangle")
        #print (constraint)
        constraint = relabel_from_matching(constraint, matching(n))
        #print ("relabled to column wise: ")
        #print (constraint)
        constraint = process_cubic_A_B(constraint, n)
        total_clause = total_clause + [constraint]
        #print ("move from matrix A to B")
        #print (constraint)
        cnf.append(constraint)
    cnf.to_file('orderly_cubic' + str(n))
    return total_clause

generate_encoding(17)