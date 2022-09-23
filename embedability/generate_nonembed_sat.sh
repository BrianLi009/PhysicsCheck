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
    ./check_embedability.sh [-s] [-p] [-v] n

Options:
    [-s]: check if a graph contains a minimal unembeddable subgraph, if it does, it's not embeddable
    [-p]: applying proposition 1 and skip graph with vertex of degree less than 2
    [-v]: very satisfiable embeddability result
    <n>: the order of the instance/number of vertices in the graph
" && exit

while getopts "spv" opt
do
	case $opt in
	s) s="-s" ;;
        p) p="-p" ;;
        v) v="-v" ;;
	esac
done
shift $((OPTIND-1))

using_subgraph=False
if [ "$s" == "-s" ]
	then
        echo "enabling using minimal noembeddable subgraph"
		using_subgraph=True
	fi

prop1=False
if [ "$p" == "-p" ]
	then
        echo "enable applying proposition 1"
		prop1=True
	fi

verify=False
if [ "$v" == "-v" ]
	then
        echo "enable embeddability verification"
		verify=True
	fi

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

if pip3 list | grep networkx
then
    echo "networkx package installed"
else 
    pip3 install networkx
fi

if pip3 list | grep z3-solver
then
    echo "z3-solver package installed"
else 
    pip3 install z3-solver
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
echo "running embeddability check on all graphs"

while read line; do
    python3 main.py "$line" "$n" "$index" $using_subgraph False nonembed_graph_sat_$n.txt embed_graph_sat_$n.txt $prop1 $verify
done < squarefree_$n.exhaust


end=`date +%s.%N`
runtime=$( echo "$end - $start" | bc -l )

echo "total runtime is $runtime"

'
