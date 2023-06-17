#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" -o "$#" -ne 2 ] && echo "
Description:
    Updated on 2023-01-11
    Given kochen specker candidates, this script check whether a candidate is indeed
    a kochen specker graph. If a graph is embedabble, and satisfy all constraints specified
    in gen_instance/generate.py. We require the file n.exhaust to be generated

Usage:
    ./4-check-embedability.sh n f

Options:
    <n>: the order of the instance/number of vertices in the graph
    <f>: filename
" && exit

n=$1 #order
f=$2

if [ -f ./embedability/min_nonembed_graph_10-12.txt ]
then
    echo "found precomputed minimum nonembedable subgraph"
else
    echo "need to compute minimum nonembedable subgraph"
    touch min_nonembed_graph_10-12.txt
    ./generate_nonembed_sat.sh 10
    ./generate_nonembed_sat.sh 11
    ./generate_nonembed_sat.sh 12
    #need to append all output file together as min_nonembed_graph_10-12.txt
    #this part to be finished, currently it does not affect the main pipeline as min_nonembed_graph_10-12.txt has already been generated
fi 
./embedability/check_embedability.sh -s $n $f
