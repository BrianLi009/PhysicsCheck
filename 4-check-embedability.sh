#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    Given kochen specker candidates, this script check whether a candidate is indeed
    a kochen specker graph. If a graph is embedabble, and satisfy all constraints specified
    in gen_instance/generate.py

Usage:
    ./4-check-embedability.sh n

Options:
    <n>: the order of the instance/number of vertices in the graph
" && exit

n=$1 #order

cp $n.exhaust embedability

cd embedability
if [ -f min_nonembed_graph_10-12.txt ]
then
    echo "using precomputed minimum nonembedable subgraph"
else
    echo "need to compute minimum nonembedable subgraph"
    touch min_nonembed_graph_10-12.txt
    ./generate_nonembed_sat.sh 10
    ./generate_nonembed_sat.sh 11
    ./generate_nonembed_sat.sh 12
    #need to append all output file together as min_nonembed_graph_10-12.txt
    #this part to be finished
fi 
./check_embedability.sh -s $n

cd -
