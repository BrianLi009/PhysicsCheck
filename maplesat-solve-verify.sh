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
    echo "MapleSAT will output learnt clause"
    ./maplesat-ks/simp/maplesat_static $f $f.drat -perm-out=$f.perm -exhaustive=$e -order=$n -no-pre -minclause -unit-out=$f.unit -noncanonical-out=$f.noncanonical| tee $f.log
else
    ./maplesat-ks/simp/maplesat_static $f $f.drat -perm-out=$f.perm -exhaustive=$e -order=$n -no-pre -minclause | tee $f.log
fi

# Verify DRAT proof
./drat-trim/drat-trim $f $f.drat | tee $f.verify
if ! grep "s VERIFIED" -q $f.verify
then
    echo "ERROR: Proof not verified"
fi
# Verify trusted clauses in proof
grep 't' $f.drat | ./drat-trim/check-perm.py $n $f.perm | tee $f.permcheck
if ! grep "VERIFIED" -q $f.permcheck
then
    echo "ERROR: Trusted clauses not verified"
fi