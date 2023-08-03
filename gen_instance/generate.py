import sys
import itertools
from cubic import cubic
import math
import csv
import subprocess
from degree_constraints import generate_degree_clauses

#requires that the cnf file does not exist
def generate(n, p, q,lower=0,upper=0):

    vertices=range(1,n+1)
    edge_dict={}
    edge_counter=0

    for j in range(1, n+1):             #generating the edge variables
        for i in range(1, j):
            edge_counter += 1
            edge_dict[(i,j)] = edge_counter

    for clique in itertools.combinations(vertices,p):
        constraint=""
        for j in itertools.combinations(clique,2):
            constraint+=str(-edge_dict[j])+" "
        with open(f"./constraints_temp_{n}_{p}_{q}", 'a') as f: #p-cliques
            f.write(constraint + "0" + "\n")

    for clique in itertools.combinations(vertices,q):
        constraint=""
        for j in itertools.combinations(clique,2):
            constraint+=str(edge_dict[j])+" "
        with open(f"./constraints_temp_{n}_{p}_{q}", 'a') as f: #q-cliques
           f.write(constraint + "0" + "\n")


    count,clause_count= cubic(n, math.comb(n,2),f"constraints_temp_{n}_{p}_{q}") # write cubic constraints to file and count their total variables, and num_cubic constriants
    #clause_count =str(clause_count+math.comb(n,p)+math.comb(n,q))
    
    if lower>0:
        for i in range(1,n+1):
            deg_count,deg_clause=generate_degree_clauses([edge_dict[key] for key in edge_dict if i in key],lower,upper,count,f"constraints_temp_{n}_{p}_{q}")
            print(deg_count)
            clause_count +=deg_clause
            count=deg_count #+= built into generate_degree_clauses

    count=str(count)
    clause_count =str(clause_count+math.comb(n,p)+math.comb(n,q))
    proc1=subprocess.Popen(["./gen_instance/combine.sh",str(n), str(p), str(q), count, clause_count]) # call a bash file to combine cubic constraints and 1st line of cnf file
    proc1.wait()

if __name__ == "__main__":
    generate(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]))
