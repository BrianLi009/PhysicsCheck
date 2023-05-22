#!/bin/bash

# Ensure parameters are specified on the command-line

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    Updated on 2023-01-25
    This is a driver script that handles generating the SAT encoding, generating non-canonical subgraph blocking clauses,
    simplify instance using CaDiCaL, solve the instance using maplesat-ks, then finally determine if a KS system exists for a certain order.

Usage:
    ./main.sh [-p] [-m] n o t s b r
    If only parameter n is provided, default run ./main.sh n c 100000 2 2 0

Options:
    [-p]: cubing/solving in parallel
    [-m]: using -m parameter for cubing, calling solver on each cube for a small amount of time
    <n>: the order of the instance/number of vertices in the graph
    <o>: simplification option, option c means simplifying for t conflicts, option v means simplify until t% of variables are eliminated
    <t>: conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate, depending on the <o> option
    <s>: option for simplification, takes in argument 1 (before adding noncanonical clauses), 2 (after), 3(both)
    <b>: option for noncanonical blocking clauses, takes in argument 1 (pre-generated), 2 (real-time-generation), 3 (no blocking clauses)
    <r>: number of variable to remove in cubing, if not passed in, assuming no cubing needed
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
o=${2:-c} #simplification option, option "c" means simplifying for t conflicts, option "v" means simplify until t% of variables are eliminated
t=${3:-100000} #conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate
s=${4:-2} #by default we only simplify the instance using CaDiCaL after adding noncanonical blocking clauses
b=${5:-2} #by default we generate noncanonical blocking clauses in real time
r=${6:-0} #number of variables to eliminate until the cubing terminates

if [ "$o" != "c" ] && [ "$o" != "v" ]
then
    echo "Need simplification option, option "c" means simplifying for t conflicts, option "v" means simplify until t% of variables are eliminated"
    exit
fi

#step 2: setp up dependencies
./dependency-setup.sh
 
#step 3 and 4: generate pre-processed instance

dir="."

if [ -f constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp.log ]
then
    echo "Instance with these parameters has already been solved."
    exit 0
fi

./generate-simp-instance.sh $n $o $t $s $b $r

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
    dir="${n}_${o}_${t}_${s}_${b}_${r}"
    ./3-cube-merge-solve.sh $p $m $n $r constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp $dir
else
    ./maplesat-ks/simp/maplesat_static constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp.drat -perm-out=constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp.perm -exhaustive=$n.exhaust -order=$n | tee constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp.log
    # Verify DRAT proof
    ./drat-trim/drat-trim constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp.drat | tee constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp.verify
    if ! grep "s VERIFIED" -q constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp.verify
    then
        echo "ERROR: Proof not verified"
    fi
    # Verify trusted clauses in proof
    grep 't' constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp.drat | ./drat-trim/check-perm.py $n constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp.perm | tee constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp.permcheck
    if ! grep "VERIFIED" -q constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp.permcheck
    then
        echo "ERROR: Trusted clauses not verified"
    fi
fi

#step 5.5: verify all constraints are satisfied
./verify.sh $n.exhaust $n

#step 6: checking if there exist embeddable solution
echo "checking embeddability of KS candidates using Z3..."
./4-check-embedability.sh $n

#output the number of KS system if there is any
echo "$(wc -l < $n.exhaust) Kochen-Specker candidates were found."
echo "$(wc -l < $n.exhaust-embeddable.txt) Kochen-Specker solutions were found."

command="./summary.sh $n $o $t $s $b $r"
echo $command
eval $command
