#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    Updated on 2023-02-22
    This is a driver script that generates pre-processed SAT instance without cubing or solving it

Usage:
    ./generate-simp-instance.sh n t s b
    If only parameter n is provided, default run ./main.sh n c 100000 2 2

Options:
    <n>: the order of the instance/number of vertices in the graph
    <t>: conflicts for which to simplify each time CaDiCal is called
    <s>: option for simplification, takes in argument 1 (before adding noncanonical clauses), 2 (after), 3(both)
    <b>: option for noncanonical blocking clauses, takes in argument 1 (pre-generated), 2 (real-time-generation), 3 (no blocking clauses)
    <r>: cubing parameter, for naming only
" && exit

if [ -z "$1" ]
then
    echo "Need instance order (number of vertices), use -h or --help for further instruction"
    exit
fi

n=$1 #order
t=${2:-10000} #conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate
s=${3:-2} #by default we only simplify the instance using CaDiCaL after adding noncanonical blocking clauses
b=${4:-2} #by default we generate noncanonical blocking clauses in real time
r=${5:-0} #cubing parameter, for naming only
a=${6:-10} #for naming only

if [ -f constraints_${n}_${t}_${s}_${b}_${r}_${a}_final.simp ]
then
    echo "instance with the same parameter has already been generated"
    exit 0
fi

#step 3: generate instances
./1-instance-generation.sh $n

instance_tracking=constraints_$n

if [ "$s" -eq 1 ] || [ "$s" -eq 3 ]
then
    simp1=constraints_${n}_${t}_${s}_${b}_${r}_${a}.simp1
    cp $instance_tracking constraints_${n}_${t}_${s}_${b}_${r}_${a}
    if [ -f $simp1 ]
    then
        echo "$simp1 already exist, skip simplification"
    else
        ./simplification/simplify-by-conflicts.sh constraints_${n}_${t}_${s}_${b}_${r}_${a} $n $t
        mv constraints_${n}_${t}_${s}_${b}_${r}_${a}.simp $simp1
        rm constraints_${n}_${t}_${s}_${b}_${r}_${a}
    instance_tracking=$simp1
    fi
fi
if [ "$s" -eq 2 ]
then
    echo "skipping the first simplification"
fi

#step 4: generate non canonical subgraph

simp_non=constraints_${n}_${t}_${s}_${b}_${r}_${a}.noncanonical
if [ "$b" -eq 2 ]
then
    if [ -f $simp_non ]
    then
        echo "$simp_non already exist, skip adding non canonical subgraph"
    else
        cp $instance_tracking $simp_non
        ./2-add-blocking-clauses.sh $n 12 $simp_non
    fi
    instance_tracking=$simp_non
fi
if [ "$b" -eq 1 ]
then
    if [ -f $simp_non ]
    then
        echo "$simp_non already exist, skip adding non canonical subgraph"
    else
        cp $instance_tracking $simp_non
        for file in non_can/*.noncanonical
        do
            cat $file >> $simp_non
            lines=$(wc -l < "$simp_non")
            sed -i -E "s/p cnf ([0-9]*) ([0-9]*)/p cnf \1 $((lines-1))/" "$simp_non"
        done
    fi
    instance_tracking=$simp_non
fi
if [ "$b" -eq 3 ]
then
    echo "not using noncanonical blocking clauses"
fi

if [ "$s" -eq 2 ] || [ "$s" -eq 3 ]
simp2=constraints_${n}_${t}_${s}_${b}_${r}_${a}.simp2
then
    if [ -f $simp2 ]
    then
        echo "$simp2 already exist, skip simplification"
    else
        ./simplification/simplify-by-conflicts.sh $instance_tracking $n $t
        mv $instance_tracking.simp $simp2
    fi
    instance_tracking=$simp2
fi
if [ "$s" -eq 1 ]
then
    echo "skipping the second simplification"
fi

echo "preprocessing complete. final instance is $instance_tracking. Renaming it as constraints_${n}_${t}_${s}_${b}_${r}_${a}_final.simp"

mv $instance_tracking constraints_${n}_${t}_${s}_${b}_${r}_${a}_final.simp
