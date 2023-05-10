#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    This script further filter nonembeddable subgraphs under real vectors and output nonembeddable subgraphs
    under complex vectors. 
Usage:
    ./generate_nonembed_sat.sh [-v] f n

Options:
    [-v]: very satisfiable embeddability result
    <f>: a file containing unembeddable subgraph under real vectors
    <n>: the order of the instance/number of vertices in the graph
" && exit

verify=False
if [ "$v" == "-v" ]
	then
        echo "enable embeddability verification"
		verify=True
	fi

f=$1
n=$2

if [ $# -eq 0 ]; then
    echo "Need to provide file name and order of unembedable subgraph"
    exit 1
fi

if dpkg --verify python3 2>/dev/null; then echo "python3 installed"; else echo "need to update to python3"; exit 1; fi

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

#if txt or log already exist, notify user
if test -f "${f}_nonembed_c.txt"
then
    echo "${f}_nonembed_c.txt exists"
    exit 0
else
    touch ${f}_nonembed_c.txt
fi

echo "Embedability check using Z3 started"

#add a parameter for starting count
start=`date +%s.%N`
index=0
echo "running embeddability check on all graphs"

python3 main-c.py $f "$n" "$index" ${f}_nonembed_c.txt ${f}_embed_c.txt $verify

end=`date +%s.%N`
runtime=$( echo "$end - $start" | bc -l )

echo "total runtime is $runtime"