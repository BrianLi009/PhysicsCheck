import sys
import itertools
from cubic import cubic
import math
import csv
import subprocess

#requires that the cnf file does not exist
def generate(n, p, q):

    vertices=range(1,n+1)
    edge_dict={}
    edge_counter=0

    for j in range(1, n+1):             #generating the edge variables
        for i in range(1, n+1):
            if i < j:
                edge_counter += 1
                edge_dict[(i,j)] = edge_counter

    for clique in itertools.combinations(vertices,p):
        constraint=""
        for j in itertools.combinations(clique,2):
            constraint+=str(edge_dict[j])+" "
        with open(f"./constraints_temp_{n}_{p}_{q}", 'a') as f: #p-cliques
            f.write(constraint + "0" + "\n")

    for clique in itertools.combinations(vertices,q):
        constraint=""
        for j in itertools.combinations(clique,2):
            constraint+=str(-edge_dict[j])+" "
        with open(f"./constraints_temp_{n}_{p}_{q}", 'a') as f: #q-cliques
           f.write(constraint + "0" + "\n")


    count,clause_count= cubic(n, math.comb(n,2),f"constraints_temp_{n}_{p}_{q}") # write cubic constraints to file and count their total variables, and num_cubic constriants
    clause_count =str(clause_count+math.comb(n,p)+math.comb(n,q))
    count=str(count)
    proc1=subprocess.Popen(["./combine.sh",str(n), str(p), str(q), count, clause_count]) # call a bash file to combine cubic constraints and 1st line of cnf file
    proc1.wait()

if __name__ == "__main__":
    generate(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
