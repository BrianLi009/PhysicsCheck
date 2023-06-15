#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" -o "$#" -le 3 ] && echo "
Description:
    Updated on 2023-01-11
    This script call the python file generate.py in gen_instance to generate the SAT encoding for Ramsey graphs R(n;p,q). Such candidate satisfies the following condition:
    1. The graph is complete on n vertices.
    2. There does not exist a blue p-clique. 
    3. There does exist a red q-clique.
    4. We also applied the cubic isomorphism blocking clauses

Usage:
    ./1-instance-generation.sh n p q

Options:
    <n>: the order of the instance/number of vertices in the graph
    <p>: as in R(p,q)
    <q>: as in R(p,q)
    
" && exit

n=$1 #order
p=$2
q=$3
l=${4:-0}
u=${5:-0}


if [ -f constraints_${n}_${p}_${q} ]
then
    echo "instance already generated"
else
    python3 gen_instance/generate.py $n $p $q $l $u #generate the instance of order n for p,q
fi
