
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
    ./3-cube-merge-solve.sh [-p] n r f

Options:
    [-p]: cubing/solving in parallel
    <n>: the order of the instance/number of vertices in the graph
    <r>: number of variables to eliminate before cubing is terminated
    <f>: file name of the current SAT instance
" && exit

n=$1 #order
r=$2 #number of variables to eliminate
f=$3 #instance file name

mkdir -p $n-solve
start=`date +%s`
echo $start
if [ "$p" == "-p" ]
then
    echo "cubing in parallel..."
    ./gen_cubes/cube.sh -p -m $n $f $r
fi

if [ "$p" != "-p" ]
then
    echo "cubing sequentially..."
    ./gen_cubes/cube.sh -m $n $f $r
fi
end=`date +%s`
echo $end
#find the deepest cube file

start=`date +%s`
echo $start
files=$(ls ./$n-cubes/*.cubes)
highest_num=$(echo "$files" | awk -F '[./]' '{print $4}' | sort -nr | head -n 1)
cube_file=./$n-cubes/$highest_num.cubes
cp $(echo $cube_file) .

cube_file=$(echo $cube_file | sed 's:.*/::')

numline=$(< $cube_file wc -l)
new_index=$((numline-1))
for i in $(seq 0 $new_index)
do
    command="./simplification/adjoin-cube-simplify.sh $n $f $cube_file $i 50 >> $n-solve/$i-solve.log && ./maplesat-ks/simp/maplesat_static simplified-cube-instance/$cube_file$i.adj.simp -no-pre -minclause -no-pseudo-test -order=$n >> $n-solve/$i-solve.log"
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
end=`date +%s`
echo $end
#cat $n-solve/*-solve.exhaust >> $n.exhaust

