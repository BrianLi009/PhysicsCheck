#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" -o "$#" -ne 1 ] && echo "
Description:
    Updated on 2023-01-11
    This script call the python file generate.py in gen_instance to generate the SAT encoding for a Kochen Specker candidates. Such candidate satisfies the following condition:
    1. The graph is squarefree, hence does not contain C4 subgraph
    2. All vertices are part of a triangle
    3. Graph is not 010-colorable (refer to the paper for definition)
    4. Minimum degree of each vertex is 3
    5. We also applied the cubic isomorphism blocking clauses

Usage:
    ./1-instance-generation.sh n

Options:
    <n>: the order of the instance/number of vertices in the graph
    
" && exit

n=$1 #order

if [ -f constraints_$n ]
then
    echo "instance already generated"
else
    python3 gen_instance/generate.py $n #generate the instance of order n
fi