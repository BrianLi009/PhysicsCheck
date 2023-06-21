#!/bin/bash

# Ensure parameters are specified on the command-line

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    Updated on 2023-01-25
    This is a driver script that handles generating the SAT encoding, generating non-canonical subgraph blocking clauses,
    simplify instance using CaDiCaL, solve the instance using maplesat-ks, then finally determine if a KS system exists for a certain order.

Usage:
    ./main.sh [-p] [-m] n t s b r
    If only parameter n is provided, default run ./main.sh n c 10000 2 2 0

Options:
    [-p]: cubing/solving in parallel
    [-m]: using -m parameter for cubing, calling solver on each cube for a small amount of time
    <n>: the order of the instance/number of vertices in the graph
    <t>: conflicts for which to simplify each time CaDiCal is called
    <s>: option for simplification, takes in argument 1 (before adding noncanonical clauses), 2 (after), 3(both)
    <b>: option for noncanonical blocking clauses, takes in argument 1 (pre-generated), 2 (real-time-generation), 3 (no blocking clauses)
    <r>: number of variable to remove in cubing, if not passed in, assuming no cubing needed
    <a>: amount of additional variables to remove for each cubing call
" && exit

while getopts "pm" opt
do
    case $opt in
        p) p="-p" ;;
        m) m="-m" ;;
        *) echo "Invalid option: -$OPTARG. Only -p and -m are supported. Use -h or --help for help" >&2
           exit 1 ;;
    esac
done
shift $((OPTIND-1))

#step 1: input parameters
if [ -z "$1" ]
then
    echo "Need instance order (number of vertices) and number of simplification, use -h or --help for further instruction"
    exit
fi

n=$1 #order
t=${2:-10000} #conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate
s=${3:-2} #by default we only simplify the instance using CaDiCaL after adding noncanonical blocking clauses
b=${4:-2} #by default we generate noncanonical blocking clauses in real time
r=${5:-0} #num of var to eliminate during first cubing stage
a=${6:-10} #amount of additional variables to remove for each cubing call

#step 2: setp up dependencies
./dependency-setup.sh
 
#step 3 and 4: generate pre-processed instance

dir="."

if [ -f constraints_${n}_${t}_${s}_${b}_${r}_${a}_final.simp.log ]
then
    echo "Instance with these parameters has already been solved."
    exit 0
fi

./generate-simp-instance.sh $n $t $s $b $r $a

if [ -f "$n.exhaust" ]
then
    rm $n.exhaust
fi

if [ -f "embedability/$n.exhaust" ]
then
    rm embedability/$n.exhaust
fi

#need to fix the cubing part for directory pointer
#step 5: cube and conquer if necessary, then solve
if [ "$r" != "0" ] 
then
    dir="${n}_${t}_${s}_${b}_${r}_${a}"
    ./3-cube-merge-solve-iterative-learnt.sh $p $n constraints_${n}_${t}_${s}_${b}_${r}_${a}_final.simp $dir $r $t $a
    command="./summary-iterative.sh $dir $r $a $n"
    echo $command
    eval $command
    #join all exhaust file together and check embeddability
    find "$dir" -type f -name "*.exhaust" -exec cat {} + > "$dir/$n.exhaust"
    ./verify.sh $dir/$n.exhaust $n
    ./4-check-embedability.sh $n $dir/$n.exhaust
else
    ./maplesat-solve-verify.sh $n constraints_${n}_${t}_${s}_${b}_${r}_${a}_final.simp $n.exhaust
    #step 5.5: verify all constraints are satisfied
    ./verify.sh $n.exhaust $n

    #step 6: checking if there exist embeddable solution
    echo "checking embeddability of KS candidates using Z3..."
    ./4-check-embedability.sh $n $n.exhaust

    #output the number of KS system if there is any
    echo "$(wc -l < $n.exhaust) Kochen-Specker candidates were found."
    echo "$(wc -l < $n.exhaust-embeddable.txt) Kochen-Specker solutions were found."
fi
