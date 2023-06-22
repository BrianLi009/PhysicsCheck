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
e=$3 #exhaustive file name

[ "$1" = "-h" -o "$1" = "--help" -o "$#" -ne 3 ] && echo "
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
    echo "MapleSAT will output short learnt clauses"
    ./maplesat-ks/simp/maplesat_static $f $f.drat -perm-out=$f.perm -exhaustive=$e -order=$n -no-pre -minclause -short-out=$f.unit -noncanonical-out=$f.noncanonical -max-proof-size=7168 -unembeddable-check=1 -unembeddable-out="$f.nonembed" | tee $f.log
else
    ./maplesat-ks/simp/maplesat_static $f $f.drat -perm-out=$f.perm -exhaustive=$e -order=$n -no-pre -minclause -max-proof-size=7168 -unembeddable-check=1 -unembeddable-out="$f.nonembed" | tee $f.log
fi

./proof-module.sh $n $f $f.verify
