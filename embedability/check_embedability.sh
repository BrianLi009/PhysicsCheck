#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    This script takes in an exhaust file with kochen specker candidates, and determine whether each
    of them is embeddable, if it is embeddable, then it will be outputted into a file as a Kochen
    Specker graph. We require the existance of n.exhaust in the directory.

Usage:
    ./check_embedability.sh [-s] [-p] [-v] n

Options:
    [-s]: check if a graph contains a minimal unembeddable subgraph, if it does, it's not embeddable
    [-p]: applying proposition 1 and skip graph with vertex of degree less than 2
    [-v]: verify satisfiable embeddability result
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

n=$1

index=0

touch embeddable_$n.txt

while read line; do
    python3 main.py "$line" "$n" "$index" $using_subgraph False nonembeddable_$n.txt embeddable_$n.txt $prop1 $verify
done < $n.exhaust

cd ..

cp embedability/embeddable_$n.txt .
sort -u embeddable_$n.txt -o ks_solution_uniq_$n.exhaust
rm embeddable_$n.txt

