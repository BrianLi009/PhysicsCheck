#!/bin/bash

n=$1 #order
f=$2 #instance file name
d=$3 #directory to store into
v=$4 #num of var to eliminate during each cubing stage
t=$5 #num of conflicts for simplification
s=$6 #amount of timeout for each solving
a=$7 #amount of additional variables to remove for each cubing call

mkdir -p $d/$n-solve
mkdir -p $d/simp
mkdir -p $d/log

./gen_cubes/cube.sh -a $n $f $v $d

files=$(ls $d/$n-cubes/*.cubes)
highest_num=$(echo "$files" | awk -F '[./]' '{print $(NF-1)}' | sort -nr | head -n 1)
echo "currently the cubing depth is $highest_num"
cube_file=$d/$n-cubes/$highest_num.cubes
cp $(echo $cube_file) .
cube_file=$(echo $cube_file | sed 's:.*/::')

numline=$(< $cube_file wc -l)
new_index=$((numline))

mkdir -p $d/$n-solve/$v

for i in $(seq 1 $new_index) #1-based indexing for cubes
    do 
        command1="./gen_cubes/apply.sh $f $cube_file $i > $d/simp/$cube_file$i.adj"
        command2="./simplification/simplify-by-conflicts.sh $d/simp/$cube_file$i.adj $n $t >> $d/$n-solve/$v/$i-solve.log"
        #command3="./maplesat-solve.sh $n $d/simp/$cube_file$i.adj.simp $d/$n-solve/$v/$i-solve.exhaust
        command3="./maplesat-ks/simp/maplesat_static $d/simp/$cube_file$i.adj.simp -no-pre -exhaustive=$d/$n-solve/$v/$i-solve.exhaust -order=$n -minclause >> $d/$n-solve/$v/$i-solve.log"
        command="$command1 && $command2 && $command3"
        echo $command >> $d/$n-solve/$v/solve.commands
        eval $command1
        eval $command2
        timeout ${s}s bash -c "eval $command3"
    done

for i in $(seq 1 $new_index)
    do
        file="$d/$n-solve/$v/$i-solve.log"
        if grep -q "UNSATISFIABLE" $file 
        then
                #do something
                continue
        elif grep -q "SATISFIABLE" $file
        then
                #do something
                continue
        else
                echo $file is not solved
                #command="./3-cube-merge-solve-extend-simp.sh $n $d/simp/${cube_file}${i}.adj.simp ${d}_${i} $((v+10)) $t $s"
                command="./3-cube-merge-solve-iterative.sh $n $f $d $(($v + $a)) $t $s $a"
                echo $command
                echo $command >> ${n}-iterative.commands
                eval $command
        fi
done