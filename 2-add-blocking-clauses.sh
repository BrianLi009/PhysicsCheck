#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" -o "$#" -ne 3 ] && echo "
Description:
    Updated on 2023-01-11
    This script generate non-canonical blocking clauses of order o using maplesat-ks, then concanate the clauses into the instance.

Usage:
    ./2-add-blocking-clauses.sh n o f

Options:
    <n>: the order of the instance/number of vertices in the graph
    <o>: the size of the noncanonical subgraph we want to generate and block
    <f>: file name of the current SAT instance
" && exit

n=$1 #order of the graph we are solving
o=$2 #subgraph's order
f=$3 #instance file name
#generate non canonical subgraph
./run-subgraph-generation.sh $n $f $o

#concanate all blocking clauses and add them to the file
cat $n/$o-solo.noncanonical >> $f
lines=$(wc -l < "$f")
sed -i -E "s/p cnf ([0-9]*) ([0-9]*)/p cnf \1 $((lines-1))/" "$f"