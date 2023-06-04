[ "$1" = "-h" -o "$1" = "--help" -o "$#" -le 2 ] && echo "
Description:
    Updated on 2023-04-25
    This script solve a single cube.

Usage:
    ./solve-single-cube.sh 

Options:
    <n>: the order of the instance/number of vertices in the graph
    <f>: file name of the current SAT instance
    <c>: file name of the cube
    <i>: index of the cube (1-indexing)
    <d>: directory to store output files into
    <o>: simplification option, option c means simplifying for t conflicts, option v means simplify until t% of variables are eliminated
    <t>: conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate, depending on the <o> option
" && exit

n=$1 #order
f=$2 #instance file name
c=$3 #file name of the cube
i=$4 #index of the cube
d=${5:-.} #directory to store into
o=${6:-c} #simplification option, option "c" means simplifying for t conflicts, option "v" means simplify until t% of variables are eliminated
t=${7:-10000} #for the cube-instance, conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate

dir_path=$(dirname "$c")

if [ ! -d "$d/simp/$dir_path" ]; then
  echo "creating directory $d/simp/$dir_path"
  mkdir -p "$d/simp/$dir_path"
fi

if [ ! -d "$d/$n-solve" ]; then
  echo "creating directory $d/$n-solve"
  mkdir -p "$d/$n-solve"
fi

if [ ! -f $d/simp/$c$i.adj ]
then
    ./gen_cubes/apply.sh $f $c $i >> $d/simp/$c$i.adj
fi

if [ "$o" == "c" ]
    then
        ./simplification/simplify-by-conflicts.sh $d/simp/$c$i.adj $n $t
    else
        ./simplification/simplify-by-var-removal.sh $n '$d/simp/$c$i.adj' $t
    fi

command="./maplesat-solve-verify.sh $n $d/simp/$c$i.adj.simp $d/$n-solve/$i-solve.exhaust"

echo $command
eval $command

#verify colorability
./verify.sh $d/$n-solve/$i-solve.exhaust $n

#verify embeddability

./embedability/check_embedability.sh -s -v $n $d/$n-solve/$i-solve.exhaust

