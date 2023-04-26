#!/bin/bash

n=$1 #n
f=$2 #cnf file name
c=$3 #current directory (of org instance)
d=$4 #cube cube name
t=$5 #number of simps conflicts
i=$6 #cube number
#s=$7 #slurm task index

current_dir=${c}_no_pseudo
cube_file=$d

echo $i > random_cube_testing/$current_dir/$n-solve/$i-solve.log
echo $i > random_cube_testing/$current_dir/$n-solve/$i-solve.simplog

./gen_cubes/apply.sh $f $cube_file $i > random_cube_testing/$current_dir/simp/$i.adj
./simplification/simplify-by-conflicts.sh random_cube_testing/$current_dir/simp/$i.adj $n $t >> random_cube_testing/$current_dir/$n-solve/$i-solve.simplog
./maplesat-ks/simp/maplesat_static random_cube_testing/$current_dir/simp/$i.adj.simp -no-pre -order=$n -minclause >> random_cube_testing/$current_dir/$n-solve/$i-solve.log

