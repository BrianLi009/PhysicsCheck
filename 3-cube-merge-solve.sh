#!/bin/bash

while getopts "apsbm" opt
do
	case $opt in
        p) p="-p" ;;
        m) m="-m" ;;
	esac
done
shift $((OPTIND-1))

[ "$1" = "-h" -o "$1" = "--help" -o "$#" -le 2 ] && echo "
Description:
    Updated on 2023-01-11
    This script generate cubes for the instance using the incremental cubing technique, then adjoin the deepest cubing file with the instance
    line by line, creating multiple separate instances with a cube embedded in it. Then maplesat-ks is being called to solve each instance.
    Both cubing and solving can be done in parallel.

Usage:
    ./3-cube-merge-solve.sh [-p] [-m] n r f o t

Options:
    [-p]: cubing/solving in parallel
    [-m]: cubing with -m parameter (run MapleSAT on each cube for small number of conflicts and stop cubing a cube if UNSAT)
    <n>: the order of the instance/number of vertices in the graph
    <r>: number of variables to eliminate before cubing is terminated
    <f>: file name of the current SAT instance
    <d>: directory to store files into
    <o>: simplification option, option c means simplifying for t conflicts, option v means simplify until t% of variables are eliminated
    <t>: conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate, depending on the <o> option
" && exit
 
n=$1 #order
r=$2 #number of variables to eliminate
f=$3 #instance file name
d=${4:-.} #directory to store into
o=${5:-c} #simplification option, option "c" means simplifying for t conflicts, option "v" means simplify until t% of variables are eliminated
t=${6:-100000} #for the cube-instance, conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate

if [ "$o" != "c" ] && [ "$o" != "v" ]
then
    echo "Need simplification option, option "c" means simplifying for t conflicts, option "v" means simplify until t% of variables are eliminated"
    exit
fi

current_dir=$d
mkdir -p $current_dir/$n-solve

mkdir -p $current_dir/simp
mkdir -p $current_dir/log

if [ "$p" == "-p" ]
then
    echo "cubing in parallel..."
    ./gen_cubes/cube.sh -p $m $n $f $r $current_dir
fi

if [ "$p" != "-p" ]
then
    echo "cubing sequentially..."
    ./gen_cubes/cube.sh $m $n $f $r $current_dir
    echo "cubing complete"
fi

#find the deepest cube file
files=$(ls $current_dir/$n-cubes/*.cubes)
echo $files
highest_num=$(echo "$files" | awk -F '[./]' '{print $(NF-1)}' | sort -nr | head -n 1)
echo $highest_num
cube_file=$current_dir/$n-cubes/$highest_num.cubes
cp $(echo $cube_file) .

cube_file=$(echo $cube_file | sed 's:.*/::')

numline=$(< $cube_file wc -l)
new_index=$((numline))
for i in $(seq 1 $new_index) #1-based indexing for cubes
do 
    command1="./gen_cubes/apply.sh $f $cube_file $i > $current_dir/simp/$cube_file$i.adj"
    if [ "$o" == "c" ]
        then
            command2="./simplification/simplify-by-conflicts.sh $current_dir/simp/$cube_file$i.adj $n $t >> $current_dir/$n-solve/$i-solve.log"
        else
            command2="./simplification/simplify-by-var-removal.sh $n '$current_dir/simp/$cube_file$i.adj' $t >> $current_dir/$n-solve/$i-solve.log"
        fi
    command3="./maplesat-ks/simp/maplesat_static $current_dir/simp/$cube_file$i.adj.simp -no-pre -no-pseudo-test -order=$n -minclause >> $current_dir/$n-solve/$i-solve.log"
    command="$command1 && $command2 && $command3"
    echo $command >> $current_dir/$n-solve/solve.commands
    if [ "$p" != "-p" ]
    then
        eval $command
    fi
done

if [ "$p" == "-p" ]
then
    echo "solving in parallel ..."
	parallel --will-cite < $current_dir/$n-solve/solve.commands
fi
