#!/bin/bash

while getopts "l" opt
do
	case $opt in
        l) l="-l" ;;
	esac
done
shift $((OPTIND-1))

n=$1 #order
f=$2 #instance file name
#e=$3 #exhaustive file name

[ "$1" = "-h" -o "$1" = "--help" -o "$#" -ne 2 ] && echo "
Description:
    Script for solving and generating drat proof for instance

Usage:
    ./maplesat-solve-verify.sh n f e

Options:
    [-l]: generate learnt clauses
    <n>: the order of the instance/number of vertices in the graph
    <f>: file name of the CNF instance to be solved
    <e>: file name to output exhaustive SAT solutions
" && exit

if [ "$l" == "-l" ]
then
    echo "MapleSAT will output short learnt clause"
    ./maplesat-ks/simp/maplesat_static $f $f.drat -perm-out=$f.perm -no-pseudo-test -order=$n -no-pre -minclause -short-out=$f.unit -noncanonical-out=$f.noncanonical | tee $f.log #removed exhaustive here, -max-proof-size=3072
else
    ./maplesat-ks/simp/maplesat_static $f $f.drat -perm-out=$f.perm -order=$n -no-pre -no-pseudo-test -minclause | tee $f.log #removed exhaustive here
fi

# Verify DRAT proof
./proof-module.sh $n $f $f.verify
