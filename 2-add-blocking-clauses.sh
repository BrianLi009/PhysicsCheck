#!/bin/bash
n=$1 #
o=$2 #subgraph's order
f=$3 #instance file name
#generate non canonical subgraph
./run-subgraph-generation.sh $n $f $o

cd $n
cat *.noncanonical > all.noncan
cd -
cat $n/all.noncan >> $f
#concanate all blocking clauses and add them to the file
lines=$(wc -l < "$f")
sed -i -E "s/p cnf ([0-9]*) ([0-9]*)/p cnf \1 $((lines-1))/" "$f"