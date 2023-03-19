#!/bin/bash

while getopts "apsbm" opt
do
	case $opt in
        p) p="-p" ;;
	esac
done
shift $((OPTIND-1))

[ "$1" = "-h" -o "$1" = "--help" -o "$#" -ne 3 ] && echo "
Description:
    Updated on 2023-01-11
    This script generate cubes for the instance using the incremental cubing technique, then adjoin the deepest cubing file with the instance
    line by line, creating multiple separate instances with a cube embedded in it. Then maplesat-ks is being called to solve each instance.
    Both cubing and solving can be done in parallel.

Usage:
    ./3-cube-merge-solve.sh [-p] n r f o t

Options:
    [-p]: cubing/solving in parallel
    <n>: the order of the instance/number of vertices in the graph
    <r>: number of variables to eliminate before cubing is terminated
    <f>: file name of the current SAT instance
    <o>: simplification option, option c means simplifying for t conflicts, option v means simplify until t% of variables are eliminated
    <t>: conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate, depending on the <o> option
" && exit
 
n=$1 #order
r=$2 #number of variables to eliminate
f=$3 #instance file name
o=${4:-c} #simplification option, option "c" means simplifying for t conflicts, option "v" means simplify until t% of variables are eliminated
t=${5:-100000} #for the cube-instance, conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate

if [ "$o" != "c" ] && [ "$o" != "v" ]
then
    echo "Need simplification option, option "c" means simplifying for t conflicts, option "v" means simplify until t% of variables are eliminated"
    exit
fi

mkdir -p $n-solve

if [ "$p" == "-p" ]
then
    echo "cubing in parallel..."
    ./gen_cubes/cube.sh -p $n $f $r
fi

if [ "$p" != "-p" ]
then
    echo "cubing sequentially..."
    ./gen_cubes/cube.sh $n $f $r
fi

#find the deepest cube file
files=$(ls ./$n-cubes/*.cubes)
highest_num=$(echo "$files" | awk -F '[./]' '{print $4}' | sort -nr | head -n 1)
cube_file=./$n-cubes/$highest_num.cubes
cp $(echo $cube_file) .

cube_file=$(echo $cube_file | sed 's:.*/::')

numline=$(< $cube_file wc -l)
new_index=$((numline))
for i in $(seq 1 $new_index) #1-based indexing for cubes
do 
    command1="./gen_cubes/apply.sh $f $cube_file $i > simp/$cube_file$i.adj"
    if [ "$o" == "c" ]
        then
            command2="./simplification/simplify-by-conflicts.sh simp/$cube_file$i.adj $n $t >> $n-solve/$i-solve.log"
        else
            command2="./simplification/simplify-by-var-removal.sh $n 'simp/$cube_file$i.adj' $t >> $n-solve/$i-solve.log"
        fi
    command3="./maplesat-ks/simp/maplesat_static simp/$cube_file$i.adj.simp -no-pre -exhaustive=$n-solve/$i-solve.exhaust -order=$n -minclause >> $n-solve/$i-solve.log"
    command="$command1 && $command2 && $command3"
    echo $command >> $n-solve/solve.commands
    if [ "$p" != "-p" ]
    then
        eval $command
    fi
done

if [ "$p" == "-p" ]
then
    echo "solving in parallel ..."
	parallel --will-cite < $n-solve/solve.commands
fi

cat $n-solve/*-solve.exhaust >> $n.exhaust
