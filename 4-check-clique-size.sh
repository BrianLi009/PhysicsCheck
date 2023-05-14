#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" -o "$#" -ne 1 ] && echo "
Description:
    Updated on 2023-01-11
    Given Ramsey graph candidate, this script check whether a candidate is indeed
    a Ramsey graph via max clique size per colour.

Usage:
    ./4-check-clique-size.sh n p q

Options:
    <n>: the order of the instance/number of vertices in the graph
    <p>: p
    <q>: q
" && exit

n=$1 #order
p=$2
q=$3

#source ENV/bin/activate

#while [ $n -le 22 ] #less than order of R(n;p,q)
#do
python3 verify.py $n $p $q
#n=$((n+1))
#done





#touch $n.exhaust

#cp $n.exhaust embedability

#cd embedability
#if [ -f min_nonembed_graph_10-12.txt ]
#then
#    echo "using precomputed minimum nonembedable subgraph"
#else
#    echo "need to compute minimum nonembedable subgraph"
#    touch min_nonembed_graph_10-12.txt
#    ./generate_nonembed_sat.sh 10
#    ./generate_nonembed_sat.sh 11
#    ./generate_nonembed_sat.sh 12
#    #need to append all output file together as min_nonembed_graph_10-12.txt
#    #this part to be finished, currently it does not affect the main pipeline as min_nonembed_graph_10-12.txt has already been generated
#fi 
#./check_embedability.sh -s $n
#
#cd ..
