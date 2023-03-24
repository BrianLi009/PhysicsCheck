#!/bin/bash
#SBATCH --account=def-vganesh
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --time=30:00:00
#SBATCH --mem-per-cpu=8G

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
    ./gen_cubes/cube.sh -p $m $n $f $r
fi

if [ "$p" != "-p" ]
then
    echo "cubing sequentially..."
    ./gen_cubes/cube.sh $m $n $f $r
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
    command3="./maplesat-ks/simp/maplesat_static simp/$cube_file$i.adj.simp -no-pre -no-pseudo-test -order=$n -minclause >> $n-solve/$i-solve.log"
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

#cat $n-solve/*-solve.exhaust >> $n.exhaust
