#!/bin/bash

# Ensure parameters are specified on the command-line

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    This is a driver script that handles generating the SAT encoding, generating non-canonical subgraph blocking clauses,
    simplify instance using CaDiCaL, solve the instance using maplesat-ks, then finally determine if a KS system exists for a certain order.

Usage:
    ./main.sh n o s r

Options:
    <n>: the order of the instance/number of vertices in the graph
    <o>: two options here, option "t" means simplification for t times, option "s" means simplification for a total of s seconds
    <s>: number of times(t) to simplify the instance using CaDiCaL with default value 3 / or by total number of seconds (s)
    <r>: number of variable to remove in cubing, if not passed in, assuming no cubing needed
" && exit

set -x

#step 1: input parameters
if [ -z "$1" ]
then
    echo "Need instance order (number of vertices) and number of simplification, use -h or --help for further instruction"
    exit
fi

n=$1 #order
s=${2:-3} #number of time to simplify each to simplification is called or amount of seconds
r=${3:-0} #number of variables to eliminate until the cubing terminates

#step 2: setp up dependencies
./dependency-setup.sh

#step 3: generate instances
./1-instance-generation.sh $n

#simplify s times

simp1=constraints_${n}_${s}.simp1
if [ -f $simp1 ]
then
    echo "$simp1 already exist, skip simplification"
else
    ./simplification/simplify.sh constraints_$n $s
    mv constraints_$n.simp $simp1
fi

#step 4: generate non canonical subgraph

simp_non=constraints_$n.non_can_${s}.simp1
if [ -f $simp_non ]
then
    echo "$simp_non already exist, skip adding non canoniacl subgraph"
else
    cat $simp1 >> $simp_non
    ./2-add-blocking-clauses.sh $n 12 $simp_non
fi

#simplify s seconds again
simp2=constraints_${n}_${s}.simp2
if [ -f $simp2 ]
then
    echo "$simp2 already exist, skip simplification"
else
    ./simplification/simplify.sh $simp_non $s
    mv $simp_non.simp $simp2
fi

if [ -f $n.exhaust ]
then
    rm $n.exhaust
fi

if [ -f embedability/$n.exhaust ]
then
    rm embedability/$n.exhaust
fi

#step 5: cube and conquer if necessary, then solve
if [ "$r" != "0" ] 
then 
    ./3-cube-merge-solve.sh $n $r $simp2
else
    ./maplesat-ks/simp/maplesat_static $simp2 -no-pre -exhaustive=$n.exhaust -order=$n
fi

#step 5.5: verify all constraints are satisfied
./verify-constraints.sh $n.exhaust $n

#step 6: checking if there exist embeddable solution
echo "checking embeddability of KS candidates using Z3..."
./4-check-embedability.sh $n

#output the number of KS system if there is any
echo "$(wc -l $n.exhaust) kochen specker candidates were found."
echo "$(wc -l ks_solution_uniq_$n.exhaust) kochen specker solutions were found."
