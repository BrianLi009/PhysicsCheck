#!/bin/bash

n=$1 #order
f=$2 #instance file name
d=$3 #directory to store into
v=$4 #num of var to eliminate during each cubing stage
t=$5 #num of conflicts for simplification
s=$6 #amount of timeout for each solving
a=$7 #amount of additional variables to remove for each cubing call
b=${8:-0} #starting cubing depth, default is 0
c=${9:-} #cube file to build on if exist

mkdir -p $d/$v/$n-solve
mkdir -p $d/$v/simp
mkdir -p $d/$v/log
mkdir -p $d/$v/$n-cubes

if [ -n "$c" ]; then
    echo "iterating $c..."
    cp $c $d/$v/$n-cubes
fi

echo "Cubing starting at depth $b"
di="$d/$v"
./gen_cubes/cube.sh -a $n $f $v $di $b

files=$(ls $d/$v/$n-cubes/*.cubes)
highest_num=$(echo "$files" | awk -F '[./]' '{print $(NF-1)}' | sort -nr | head -n 1)
echo "currently the cubing depth is $highest_num"
cube_file=$d/$v/$n-cubes/$highest_num.cubes
cp $(echo $cube_file) .
cube_file=$(echo $cube_file | sed 's:.*/::')
new_cube=$((highest_num + 1))
new_cube_file=$d/$v/$n-cubes/$new_cube.cubes

numline=$(< $cube_file wc -l)
new_index=$((numline))

for i in $(seq 1 $new_index) #1-based indexing for cubes
    do 
        command1="./gen_cubes/apply.sh $f $cube_file $i > $d/$v/simp/$cube_file$i.adj"
        command2="./simplification/simplify-by-conflicts.sh $d/$v/simp/$cube_file$i.adj $n $t >> $d/$v/$n-solve/$i-solve.log"
        command3="./maplesat-solve-verify.sh $n $d/$v/simp/$cube_file$i.adj.simp $d/$v/$n-solve/$i-solve.exhaust >> $d/$v/$n-solve/$i-solve.log"
        command="$command1 && $command2 && $command3"
        echo $command >> $d/$v/$n-solve/solve.commands
        eval $command1
        eval $command2
        timeout ${s}s bash -c "eval $command3"
    done

all_solved="T"
for i in $(seq 1 $new_index)
    do
        file="$d/$v/$n-solve/$i-solve.log"
        if grep -q "UNSATISFIABLE" $file 
        then
                #do something
                continue
        elif grep -q "SATISFIABLE" $file
        then
                #do something
                continue
        else
                all_solved="F"
                echo $file is not solved
                sed -n "${i}p" $cube_file >> $new_cube_file
        fi
done

if [[ "$all_solved" == "T" ]]; then
    echo "successfully solved all cubes, terminating"
else
    command="./3-cube-merge-solve-iterative.sh $n $f $d $(($v + $a)) $t $s $a $(($highest_num+2)) $new_cube_file"
    echo $command
    echo $command >> ${n}-iterative.commands
    eval $command
fi