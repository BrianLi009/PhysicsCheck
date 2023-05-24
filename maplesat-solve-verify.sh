#!/bin/bash

n=$1 #order
f=$2 #instance file name
e=$3 #exhaustive file name

[ "$1" = "-h" -o "$1" = "--help" -o "$#" -ne 3 ] && echo "
Description:
    Script for solving and generating drat proof for instance

Usage:
    ./maplesat-solve-verify.sh n f e

Options:
    <n>: the order of the instance/number of vertices in the graph
    <f>: file name of the CNF instance to be solved
    <e>: file name to output exhaustive SAT solutions
" && exit


./maplesat-ks/simp/maplesat_static $f $f.drat -perm-out=$f.perm -exhaustive=$e -order=$n -no-pre -minclause | tee $f.log
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