#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" -o "$#" -ne 5 ] && echo "
Description:
    Updated on 2023-01-11
    This script generate cubes for the instance using the incremental cubing technique, then adjoin the deepest cubing file with the instance
    line by line, creating multiple separate instances with a cube embedded in it. Then maplesat-ks is being called to solve each instance (in parallel).

Usage:
    ./3-cube-merge-solve.sh n r f c p

Options:
    <n>: the order of the instance/number of vertices in the graph
    <r>: number of variables to eliminate before cubing is terminated
    <f>: file name of the current SAT instance
    <c>: option to enable the -s option in cubing, 1 to enable and 0 to disable
    <p>: option to enable the -p option in cubing, 1 to enable and 0 to disable
" && exit
 
n=$1 #order
r=$2 #number of variables to eliminate
f=$3 #instance file name
c=$4 #the -s option in cubing
p=$5 #the -p option in cubing

if [ "$c" -eq 1 ] && [ "$p" -eq 1 ]
then
     echo "both -s, -p enabled"
    ./gen_cubes/cube.sh -p -s $n $f $r #cube till r varaibles are eliminated
    echo "WARNING: solving option for -s not yet implemented as it is not used in the default pipeline"
    exit 0
fi

if [ "$c" -eq 1 ] && [ "$p" -eq 0 ]
then
     echo "-s enabled"
    ./gen_cubes/cube.sh -s $n $f $r #cube till r varaibles are eliminated
    echo "solving option for -s not yet implemented"
    echo "WARNING: solving option for -s not yet implemented as it is not used in the default pipeline"
    exit 0
fi

if [ "$c" -eq 0 ] && [ "$p" -eq 1 ]
then
     echo "-p enabled"
    ./gen_cubes/cube.sh -p $n $f $r #cube till r varaibles are eliminated
fi

if [ "$c" -eq 0 ] && [ "$p" -eq 0 ]
then
     echo "both -s, -p disabled"
    ./gen_cubes/cube.sh $n $f $r #cube till r varaibles are eliminated
fi

:
#find the deepest cube file
files=$(ls ./$n-cubes/*.cubes)
highest_num=$(echo "$files" | awk -F '[./]' '{print $4}' | sort -nr | head -n 1)
cube_file=./$n-cubes/$highest_num.cubes
cp $(echo $cube_file) .

cube_file=$(echo $cube_file | sed 's:.*/::')

numline=$(< $cube_file wc -l)
new_index=$((numline-1))
for i in $(seq 0 $new_index)
do 
    ./simplification/adjoin-cube-simplify.sh $n $f $cube_file $i 50
    #join the cube to the instance, simplified until 50% of the variables are eliminated
    ./maplesat-ks/simp/maplesat_static simplified-cube-instance/$cube_file$i.adj.simp -no-pre -exhaustive=$n.exhaust -order=$n
done


#this is still in the work, when -s option enabled, the script should be different.
