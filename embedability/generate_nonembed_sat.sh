#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    This script generates all nonembedable subgraph of order n, by first calling maplesat-ks
    to generate all squarefree graph of order n, then run embedability check on every graph,
    output those that results in unsat. This list is used to fast check embedability or larger
    graph. 
    
    Note: this script is currently outputting graphs in edge-variable format, but graphs6 format
    is being used to store all minimum nonembedable subgraph (see min_nonembed_graph_10-12.txt).

Usage:
    ./generate_nonembed_sat n

Options:
    <n>: the order of the instance/number of vertices in the graph
" && exit

#generate nonembedable subgraphs

#set -x

n=$1

if [ $# -eq 0 ]; then
    echo "Need to provide order of unembedable subgraph"
    exit 1
fi

cd ..

if dpkg --verify python3 2>/dev/null; then echo "python3 installed"; else echo "need to update to python3"; exit 1; fi

#install maplesat-ks
if [ -d maplesat-ks ] && [ -f maplesat-ks/simp/maplesat_static ]
then
    echo "maplesat-ks installed and binary file compiled"
else
    git clone git@github.com:curtisbright/maplesat-ks.git maplesat-ks
    #git stash
    cd maplesat-ks
    git checkout unembeddable-subgraph-check
    make
    cd -
fi 

if pip list | grep networkx
then
    echo "networkx package installed"
else 
    pip install networkx
fi

if pip list | grep z3-solver
then
    echo "z3-solver package installed"
else 
    pip install z3-solver
fi

if [ -f squarefree_$n.exhaust ]
then
    echo "instance already solved"
else
	python3 gen_instance/generate_squarefree_only.py $n
    ./maplesat-ks/simp/maplesat_static squarefree_constraints_$n -no-pre -exhaustive=squarefree_$n.exhaust -order=$n
fi

#cp squarefree_constraints_$n embedability
cp squarefree_$n.exhaust embedability

cd embedability

#if txt or log already exist, notify user
if test -f "nonembed_graph_sat_$n.txt"
then
    echo "nonembed_graph_sat_$n.txt exists"
    exit 0
else
    touch nonembed_graph_sat_$n.txt
fi

echo "Embedability check using Z3 started"

#add a parameter for starting count
start=`date +%s.%N`
index=0
while read line; do
    python3 main.py "$line" $n $index False nonembed_graph_sat_$n.txt
done < squarefree_$n.exhaust

end=`date +%s.%N`
runtime=$( echo "$end - $start" | bc -l )

echo "total runtime is $runtime"

#filtering all output and only keep minimal nonembeddable subgraph
python3 analyze_subgraph.py $n