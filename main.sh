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

#step 1: input parameters
if [ -z "$1" ]
then
    echo "Need instance order (number of vertices) and number of simplification, use -h or --help for further instruction"
    exit
fi

n=$1 #order
o=$2 #option for simplification
s=${3:-3} #number of time to simplify each to simplification is called or amount of seconds
r=${4:-0} #number of variables to eliminate until the cubing terminates

#step 2: setp up dependencies
./dependency-setup.sh

#step 3: generate instances
./1-instance-generation.sh $n

#simplify s times
if [ -f constraints_$n.simp1 ]
then
    echo "constraints_$n.simp1 already exist, skip simplification"
else
    ./simplification/simplify.sh constraints_$n $o $s
    mv constraints_$n.simp constraints_$n.simp1
fi

#step 4: generate non canonical subgraph
if [ -f constraints_$n.non_can.simp1 ]
then
    echo "constraints_$n.non_can.simp1 already exist, skip adding non canoniacl subgraph"
else
    cat constraints_$n.simp1 >> constraints_$n.non_can.simp1
    ./2-add-blocking-clauses.sh $n 12 constraints_$n.non_can.simp1
fi

#simplify s times again
if [ -f constraints_$n.simp2 ]
then
    echo "constraints_$n.simp2 already exist, skip simplification"
else
    ./simplification/simplify.sh constraints_$n.non_can.simp1 $o $s
    mv constraints_$n.non_can.simp1.simp constraints_$n.simp2
fi

#step 5: cube and conquer if necessary, then solve
if [ "$r" != "0" ] 
then 
    ./3-cube-merge-solve.sh $n $r constraints_$n.simp2
else
    ./maplesat-ks/simp/maplesat_static constraints_$n.simp2 -no-pre -exhaustive=$n.exhaust -order=$n
fi

#step 6: checking if there exist embeddable solution
echo "checking embeddability of KS candidates using Z3..."
./4-check-embedability.sh $n

#output the number of KS system if there is any
echo "$(wc -l $n.exhaust) kochen specker candidates were found."
echo "$(wc -l ks_solution_uniq_$n.exhaust) kochen specker solutions were found."
