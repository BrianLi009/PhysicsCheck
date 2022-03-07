#!/bin/bash

# Ensure parameters are specified on the command-line

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    This is a driver script that handles generating the SAT encoding, generating non-canonical subgraph blocking clauses,
    simplify instance using CaDiCaL, solve the instance using maplesat-ks, then finally determine if a KS system exists for a certain order.

Usage:
    ./main.sh n s r

Options:
    <n>: the order of the instance/number of vertices in the graph
    <s>: number of times to simplify the instance using CaDiCaL with default value 3
    <r>: number of variable to remove in cubing, if not passed in, assuming no cubing needed
" && exit

#step 1: input parameters
if [ -z "$1" ]
then
    echo "Need instance order (number of vertices) and number of simplification, use -h or --help for further instruction"
    exit
fi

n=$1 #order
s=${2:-3} #number of time to simplify each to simplification is called
r=${3:-0} #number of variables to eliminate until the cubing terminates

#step 2: setp up dependencies
./dependency-setup.sh

#step 3: generate instances
./1-instance-generation.sh $n

#simplify s times
if [ -f constraints_$n.simp1 ]
then
    echo "constraints_$n.simp1 already exist, skip simplification"
else
    ./simplify.sh constraints_$n $s
    mv constraints_$n.simp constraints_$n.simp1
fi

#step 4: generate non canonical subgraph
./2-add-blocking-clauses.sh $n 12 constraints_$n.simp1

#simplify s times again
if [ -f constraints_$n.simp2 ]
then
    echo "constraints_$n.simp2 already exist, skip simplification"
else
    ./simplify.sh constraints_$n.simp1 $s
    mv constraints_$n.simp1.simp constraints_$n.simp2
fi

if [[ $(wc -l <constraints_$n.simp2) -ge 3 ]] #if the constraint file only has two lines or less after simplification, output unsat
then 
    #step 5: cube and conquer if necessary, then solve
    if [ "$r" != "0" ] 
    then 
        ./3-cube-merge-solve.sh $n $r constraints_$n.simp2
    else
        ./maplesat-ks/simp/maplesat_static constraints_$n.simp2 -no-pre -exhaustive=$n.exhaust -order=$n
    fi

    #step 6: checking if there exist embeddable solution
    ./4-check-embedability.sh $n

    #output the number of KS system is there is any
    echo "$(wc -l ks_solution_uniq_$n.exhaust) kochen specker solutions were found."
else 
    echo "No kochen specker candidates are found, thus no Kochen Specker solution can exist"
    echo "0 kochen specker solution were found"
fi 
