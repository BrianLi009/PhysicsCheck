#!/bin/bash

# Ensure parameters are specified on the command-line

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    This is a driver script that handles generating the SAT encoding, generating non-canonical subgraph blocking clauses,
    simplify instance using CaDiCaL, solve the instance using maplesat-ks, then finally determine if a KS system exists for a certain order.

Usage:
    ./main.sh n o t s b r c p

Options:
    <n>: the order of the instance/number of vertices in the graph
    <o>: simplification option, option t means simplifying for t seconds, option v means simplify until v% of variables are eliminated
    <t>: time in seconds for which to simplify each time CaDiCal is called, or % of variables to eliminate
    <s>: option for simplifiation, takes in argument 1 (before), 2 (after), 3(both)
    <b>: option for noncanonical blocking clauses, takes in argument 1 (pre-generated), 2 (real-time-generation), 3 (no blocking clauses)
    <r>: number of variable to remove in cubing, if not passed in, assuming no cubing needed
    <c>: -s apply CaDiCaL on the instances simplified on the previous depth, takes in 1 (on), 0 (off)
    <p>: cubing in parallel, 1 (on), 0 (off), default turn off parallel cubing
" && exit

#step 1: input parameters
if [ -z "$1" ]
then
    echo "Need instance order (number of vertices) and number of simplification, use -h or --help for further instruction"
    exit
fi

#set -x

n=$1 #order
o=$2 #simplification option, option "t" means simplifying for t seconds, option "v" means simplify until v% of variables are eliminated
t=${3:-3} #time in seconds for which to simplify each time CaDiCal is called, or % of variables to eliminate
s=${4:-3} #by default we simplify twice, before and after noncanonical blocking clauses
b=${5:-2} #by default we generate noncanonical blocking clauses in real time
r=${6:-0} #number of variables to eliminate until the cubing terminates
c=${7:-1} #-s apply CaDiCaL on the instances simplified on the previous depth
p=${8:-0} #default turn off parallel cubing

if [ "$o" != "s" ] && [ "$o" != "v" ]
then
    echo "Need simplification option, option "t" means simplifying for t seconds, option "v" means simplify until v% of variables are eliminated"
    exit
fi

#step 2: setp up dependencies
./dependency-setup.sh

#step 3: generate instances
./1-instance-generation.sh $n

simp1=constraints_${n}_${o}_${t}_${s}_${b}.simp1
cp constraints_$n constraints_${n}_${o}_${t}_${s}_${b}
if [ "$s" -eq 1 ] || [ "$s" -eq 3 ]
then
    if [ -f $simp1 ]
    then
        echo "$simp1 already exist, skip simplification"
    else
        if [ "$o" == "s" ]
        then
            ./simplification/simplify.sh constraints_${n}_${o}_${t}_${s}_${b} $n $t
        else
            ./simplification/simplify-by-var-removal.sh $n "constraints_${n}_${o}_${t}_${s}_${b}" $t
        fi
        mv constraints_${n}_${o}_${t}_${s}_${b}.simp $simp1
    fi
fi
if [ "$s" -eq 2 ]
then
    echo "skipping the first simplification"
    cp constraints_$n $simp1
fi

#step 4: generate non canonical subgraph

simp_non=constraints_$n.non_can_${t}_${s}_${b}.simp1
if [ "$b" -eq 2 ]
then
    if [ -f $simp_non ]
    then
        echo "$simp_non already exist, skip adding non canonical subgraph"
    else
        cp $simp1 $simp_non
        ./2-add-blocking-clauses.sh $n 12 $simp_non
    fi
fi
if [ "$b" -eq 1 ]
then
    if [ -f $simp_non ]
    then
        echo "$simp_non already exist, skip adding non canoniacl subgraph"
    else
        cp $simp1 $simp_non
        for file in non_can/*.noncanonical
        do
            cat $file >> $simp_non
            lines=$(wc -l < "$simp_non")
            sed -i -E "s/p cnf ([0-9]*) ([0-9]*)/p cnf \1 $((lines-1))/" "$simp_non"
        done
    fi
fi
if [ "$b" -eq 3 ]
then
    cp $simp1 $simp_non
fi

simp2=constraints_${n}_${o}_${t}_${s}_${b}.simp2
if [ "$s" -eq 2 ] || [ "$s" -eq 3 ]
then
    if [ -f $simp2 ]
    then
        echo "$simp2 already exist, skip simplification"
    else
        if [ "$o" == "s" ]
        then
            ./simplification/simplify.sh $simp_non $n $t
        else
            ./simplification/simplify-by-var-removal.sh $n $simp_non $t
        fi
        cp $simp_non.simp $simp2
    fi
fi
if [ "$s" -eq 1 ]
then
    echo "skipping the second simplification"
    cp $simp_non $simp2
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
    ./3-cube-merge-solve.sh $n $r $simp2 $c $p
else
    ./maplesat-ks/simp/maplesat_static $simp2 -no-pre -exhaustive=$n.exhaust -order=$n
fi

#step 5.5: verify all constraints are satisfied
./verify.sh $n.exhaust $n

#step 6: checking if there exist embeddable solution
echo "checking embeddability of KS candidates using Z3..."
./4-check-embedability.sh $n

#output the number of KS system if there is any
echo "$(wc -l $n.exhaust) kochen specker candidates were found."
echo "$(wc -l ks_solution_uniq_$n.exhaust) kochen specker solutions were found."
