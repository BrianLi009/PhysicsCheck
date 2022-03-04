#!/bin/bash

set -x 
n=$1 #order

cp $n.exhaust embedability

cd embedability
if [ -f min_nonembed_graph_10-12.txt ]
then
    touch embed_result.txt
    echo "using precomputed minimum nonembedable subgraph"
else
    echo "need to compute minimum nonembedable subgraph"
    touch subgraph_embed_result.txt
    ./generate_nonembed_sat.sh 10
    ./generate_nonembed_sat.sh 11
    ./generate_nonembed_sat.sh 12
    rm embed_result.txt
    #this part to be finished
fi 
./check_embedability.sh $n