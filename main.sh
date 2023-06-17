#!/bin/bash
# Ensure parameters are specified on the command-line

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    Updated on 2023-01-25
    This is a driver script that handles generating the SAT encoding, generating non-canonical subgraph blocking clauses,
    simplify instance using CaDiCaL, solve the instance using maplesat-ks, then finally determine if a KS system exists for a certain order.

Usage:
    ./main.sh [-p] [-m] n t s b r
    If only parameter n is provided, default run ./main.sh n c 100000 2 2 0

Options:
    [-d]: cubing/solving in parallel
    <n>: the order of the instance/number of vertices in the graph
    <p>:
    <q>:
    <o>: simplification option, option c means simplifying for t conflicts, option v means simplify until t% of variables are eliminated
    <t>: conflicts for which to simplify each time CaDiCal is called
    <s>: option for simplification, takes in argument 1 (before adding noncanonical clauses), 2 (after), 3(both)
    <b>: option for noncanonical blocking clauses, takes in argument 1 (pre-generated), 2 (real-time-generation), 3 (no blocking clauses)
    <r>: number of variable to remove in cubing, if not passed in, assuming no cubing needed
" && exit

while getopts "pm" opt
do
    case $opt in
        p) d="-p" ;;
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
p=$2
q=$3
o=${4:-c} #simplification option, option "c" means simplifying for t conflicts, option "v" means simplify until t% of variables are eliminated
t=${5:-100000} #conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate
s=${6:-2} #by default we only simplify the instance using CaDiCaL after adding noncanonical blocking clauses
b=${7:-2} #by default we generate noncanonical blocking clauses in real time
r=${8:-0} #number of variables to eliminate until the cubing terminates

#step 2: setp up dependencies
dir="${n}_${p}_${q}_${o}_${t}_${s}_${b}_${r}"
./dependency-setup.sh
 
#step 3 and 4: generate pre-processed instance
dir="."

if [ -f constraints_${n}_${p}_${q}_${o}_${t}_${s}_${b}_${r}_final.simp.log ]
then
    echo "Instance with these parameters has already been solved."
    exit 0
fi

module load python/3.10
./generate-simp-instance.sh $n $p $q $o $t $s $b $r

#if [ -f "$n.exhaust" ]
#then
#    rm $n.exhaust
#fi
#
#if [ -f "embedability/$n.exhaust" ]
#then
#    rm embedability/$n.exhaust
#fi

#need to fix the cubing part for directory pointer
#step 5: cube and conquer if necessary, then solve
if [ "$r" != "0" ]
then

    dir="${n}_${p}_${q}_${o}_${t}_${s}_${b}_${r}"
    ./3-cube-merge-solve.sh $d $m $n $r constraints_${n}_${p}_${q}_${o}_${t}_${s}_${b}_${r}_final.simp $dir
else
    ./maplesat-solve-verify.sh $n -no-pre -no-pseudo-test -minclause constraints_${n}_${p}_${q}_${o}_${t}_${s}_${b}_${r}_final.simp

#step 6: checking if there exist clique sizes>=p or independent set >=q
echo "checking max clique size..."
./4-check-clique-size.sh $n $p $q

# to add: this section returns any unsat orders or smthg

dir="${n}_${p}_${q}_${o}_${t}_${s}_${b}_${r}"
command="./summary.sh $n $dir $r"
echo $command
eval $command
