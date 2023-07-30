#!/bin/bash
#SBATCH --account=def-vganesh
#SBATCH --time=40:00:00
#SBATCH --mem-per-cpu=4G

n=$1 #order
f=$2 #instance file name
d=$3 #directory to store into
v=$4 #num of var to eliminate during first cubing stage
t=$5 #num of conflicts for simplification
a=$6 #amount of additional variables to remove for each cubing call
f2=${7:-$2} #smaller instance to cube on

#we want the script to: cube, for each cube, submit sbatch to solve, if not solved, call the script again

mkdir -p $d/$v/$n-solve
mkdir -p $d/$v/simp
mkdir -p $d/$v/log
mkdir -p $d/$v/$n-cubes

di="$d/$v"
./gen_cubes/cube.sh -a -p $n $f2 $v $di

files=$(ls $d/$v/$n-cubes/*.cubes)
highest_num=$(echo "$files" | awk -F '[./]' '{print $(NF-1)}' | sort -nr | head -n 1)
echo "currently the cubing depth is $highest_num"
cube_file=$d/$v/$n-cubes/$highest_num.cubes
cube_file_name=$(echo $cube_file | sed 's:.*/::')
new_cube=$((highest_num + 1))

numline=$(< $cube_file wc -l)
new_index=$((numline))

for j in $(seq 1 5 $new_index) #1-based indexing for cubes
    do
    echo "#!/bin/bash" > $d/$v/simp/$j-solve.sh
    echo "#SBATCH --account=def-vganesh" >> $d/$v/simp/$j-solve.sh
    echo "#SBATCH --time=3-00:00" >> $d/$v/simp/$j-solve.sh
    echo "#SBATCH --mem-per-cpu=2G" >> $d/$v/simp/$j-solve.sh
    for i in $(seq $j $(($j+4)))
        do
                child_instance="$d/$v/simp/${highest_num}.cubes${i}.adj.simp"
                command1="./gen_cubes/apply.sh $f $cube_file $i > $d/$v/simp/$cube_file_name$i.adj"
                command2="./simplification/simplify-by-conflicts.sh $d/$v/simp/$cube_file_name$i.adj $n $t >> $d/$v/$n-solve/$i-solve.log"
                command3="./maplesat-solve-verify.sh -l $n $d/$v/simp/$cube_file_name$i.adj.simp  >> $d/$v/$n-solve/$i-solve.log"
                command4="if ! grep -q 'UNSATISFIABLE' '$d/$v/$n-solve/$i-solve.log'; then sbatch $child_instance-cube.sh; fi"
                command="$command1 && $command2 && $command3 && $command4"
                echo $command >> $d/$v/simp/$j-solve.sh
                #echo $command4 >> $d/$v/simp/$j-solve.sh
                child_instance="$d/$v/simp/${highest_num}.cubes${i}.adj.simp"
        command5="./gen_cubes/concat.sh $child_instance $child_instance.noncanonical > $child_instance.temp; ./gen_cubes/concat.sh $child_instance.temp $child_instance.unit > $child_instance.learnt; ./3-cube-merge-solve-iterative-learnt-cc.sh $n $child_instance.learnt '$d/$v-$i' $(($v + $a)) $t $a"
        echo "#!/bin/bash" > $child_instance-cube.sh
        echo "#SBATCH --account=def-vganesh" >> $child_instance-cube.sh
        echo "#SBATCH --ntasks-per-node=4" >> $child_instance-cube.sh
        echo "#SBATCH --time=2-00:00" >> $child_instance-cube.sh
        echo "#SBATCH --mem-per-cpu=4G" >> $child_instance-cube.sh
        echo $command5 >> $child_instance-cube.sh
        done
        sbatch $d/$v/simp/$j-solve.sh
    done
