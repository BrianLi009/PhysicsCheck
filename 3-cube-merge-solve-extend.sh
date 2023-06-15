#!/bin/bash
#SBATCH --account=def-vganesh
#SBATCH --mem-per-cpu=4G
#SBATCH --time=30:00:00

while getopts "apsbm" opt
do
	case $opt in
        p) p="-p" ;;
	esac
done
shift $((OPTIND-1))

[ "$1" = "-h" -o "$1" = "--help" -o "$#" -le 2 ] && echo "
Description:
    This script generate cubes for the instance using the incremental cubing technique, then adjoin the deepest cubing file with the instance
    line by line, creating multiple separate instances with a cube embedded in it. Then maplesat-ks is being called to solve each instance. Then the timeouted
    cube will be cubed further and solved. This process is repeated until all cubes are solved.
    Both cubing and solving can be done in parallel.

Usage:
    ./3-cube-merge-solve.sh [-p] n f d o t v1 v2 v3 ...

Options:
    [-p]: cubing/solving in parallel
    <n>: the order of the instance/number of vertices in the graph
    <f>: file name of the current SAT instance
    <d>: directory to store files into
    <o>: simplification option, option c means simplifying for t conflicts, option v means simplify until t% of variables are eliminated
    <t>: conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate, depending on the <o> option
" && exit

n=$1 #order
f=$2 #instance file name
d=$3 #directory to store into
o=$4 #simplification option, option "c" means simplifying for t conflicts, option "v" means simplify until t% of variables are eliminated
t=$5 #for the cube-instance, conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate

if [ "$o" != "c" ] && [ "$o" != "v" ]
then
    echo "Need simplification option, option "c" means simplifying for t conflicts, option "v" means simplify until t% of variables are eliminated"
    exit
fi

current_dir=$d
mkdir -p $current_dir/$n-solve
mkdir -p $current_dir/simp
mkdir -p $current_dir/log

highest_num=-2

echo "Amount of variables to eliminate incrementally:"
while [ $# -gt 5 ]; do
    v=$6
    echo $v
    current_dir=$d
    highest_num=$((highest_num+2))
    if [ "$p" == "-p" ]
    then
        echo "cubing in parallel..."
        ./gen_cubes/cube.sh -a -p $n $f $v $current_dir $highest_num
    fi
        if [ "$p" != "-p" ]
    then
        echo "cubing sequentially..."
        ./gen_cubes/cube.sh -a $n $f $v $current_dir $highest_num
    fi
    echo "this stage of cubing is complete with $v variables eliminated"

    #find the deepest cube file
    files=$(ls $current_dir/$n-cubes/*.cubes)
    highest_num=$(echo "$files" | awk -F '[./]' '{print $(NF-1)}' | sort -nr | head -n 1)
    echo "currently the cubing depth is $highest_num"
    cube_file=$current_dir/$n-cubes/$highest_num.cubes
    cp $(echo $cube_file) .
    cube_file=$(echo $cube_file | sed 's:.*/::')

    numline=$(< $cube_file wc -l)
    new_index=$((numline))

    mkdir -p $current_dir/$n-solve/$v
    for i in $(seq 1 $new_index) #1-based indexing for cubes
    do 
        command1="./gen_cubes/apply.sh $f $cube_file $i > $current_dir/simp/$cube_file$i.adj"
        if [ "$o" == "c" ]
            then
                command2="./simplification/simplify-by-conflicts.sh $current_dir/simp/$cube_file$i.adj $n $t >> $current_dir/$n-solve/$v/$i-solve.log"
            else
                command2="./simplification/simplify-by-var-removal.sh $n '$current_dir/simp/$cube_file$i.adj' $t >> $current_dir/$n-solve/$v/$i-solve.log"
            fi
        command3="./maplesat-ks/simp/maplesat_static $current_dir/simp/$cube_file$i.adj.simp -no-pre -no-pseudo-test -order=$n -minclause >> $current_dir/$n-solve/$v/$i-solve.log"
        command="$command1 && $command2 && $command3"
        echo $command >> $current_dir/$n-solve/$v/solve.commands
        if [ "$p" != "-p" ]
        then
	    if [ $# -gt 6 ]
	    then
            	timeout 1000s bash -c "eval $command"
	    else 
	        bash -c "eval $command"
	    fi
        fi
    done
    echo "cubing time for $v (excludes previous layers):"
    grep -r 'time' $current_dir/$n-log/*.log | cut -f4 -d ' ' | awk '{s+=$1} END {print s}'
    echo "simplification time during cubing for $v (excludes previous layers):"
    #grep -r "total process time since initialization" $current_dir/$n-log/*.simp | cut -d' ' -f15 | awk '{s+=$1} END {print s}'
    grep -h "c total process time since initialization: * *[0-9]*\.*[0-9]*" $current_dir/$n-log/*.simp | awk '{total += $(NF-1)} END {print "Total time: " total " seconds"}'
    


    if [ "$p" == "-p" ]
    then
        echo "solving in parallel ..."
        parallel --will-cite < $current_dir/$n-solve/solve.commands
    fi

    ./extended-cube.sh 1 $new_index $current_dir/$n-solve/$v $current_dir/$n-cubes
    shift
done

