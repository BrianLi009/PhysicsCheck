#!/bin/bash

# Ensure parameters are specified on the command-line

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    This is a driver script that handles generating the SAT encoding, generating non-canonical subgraph blocking clauses,
    simplify instance using CaDiCaL, solve the instance using maplesat-ks, then finally determine if a KS system exists for a certain order.

Usage:
    ./main.sh n s r

Options:
    <n>: the order of the instance/number of vertices in the graph
    <s>: number of times to simplify the instance using CaDiCaL with default value 3
    <r>: number of variable to remove in cubing, if not passed in, assuming no cubing needed
" && exit

if [ -z "$1" ]
then
    echo "Need instance order (number of vertices) and number of simplification, use -h or --help for further instruction"
    exit
fi

n=$1 #order
s=${2:-3}
r=${3:-0}

if [ -d constraints_$n ]
then
    echo "instance already generated"
else
    python3 gen_instance/generate.py $n #generate the instance of order n
fi

#install maplesat-ks
if [ -d maplesat-ks ]
then
    echo "maplesat-ks installed"
    #git stash
    #git checkout unembeddable-subgraph-check
    #cd -
else
    git clone git@github.com:curtisbright/maplesat-ks.git maplesat-ks
    #git stash
    cd maplesat-ks
    git checkout unembeddable-subgraph-check
    make
    cd -
fi 
#clone maplesat-ks if it does not

#install cadical
if [ -d cadical ]
then
    echo "cadical installed"
    #cd -
else
    git clone https://github.com/arminbiere/cadical.git cadical
    cd cadical
    ./configure
    make
    cd -
fi

#generate non canonical subgraph
./run-subgraph-generation.sh $n constraints_$n 12

#append blocking clauses to the instance
cd $n
cat *.noncanonical > all.noncanonical
cd -
cat $n/all.noncanonical >> constraints_$n
lines=$(wc -l < "constraints_$n")
sed -i -E "s/p cnf ([0-9]*) ([0-9]*)/p cnf \1 $((lines-1))/" "constraints_$n"

#simplify s times
if [ -d constraints_$n.simp ]
then
    echo "instance already simplified"
else
    ./simplify.sh constraints_$n $s
fi 

if [ "$r" != "0" ] 
then 
    cp cadical gen_cubes
    cp constraints_$n.simp gen_cubes
    cd gen_cubes
    cd march_cu
    make
    cd ..
    ./cube.sh $n constraints_$n.simp $r #cube till r varaibles are eliminated
    #now adjoin them and create separate instances
    cd ..
    cube_file=$(find . -type f -wholename "./gen_cubes/$n-cubes/*.cubes" -exec grep -H -c '[^[:space:]]' {} \; | sort -nr -t":" -k2 | awk -F: '{print $1; exit;}')
    cp $(echo $cube_file) .
    cube_file=$(echo $cube_file | sed 's:.*/::')
    numline=$(< $cube_file wc -l)
    new_index=$((numline-1))
    for i in $(seq 0 $new_index)
    do
        ./adjoin-cube-simplify.sh constraints_$n.simp $cube_file $i 50
        ./maplesat-ks/simp/maplesat_static $cube_file$i.adj.simp -no-pre -exhaustive=$n.exhaust -order=$n
    done
else
    ./maplesat-ks/simp/maplesat_static constraints_$n.simp -no-pre -exhaustive=$n.exhaust -order=$n
fi

#checking if there exist embeddable solution

cp $n.exhaust embedability

cd embedability
pip install networkx
pip install z3-solver
touch embed_result.txt
./check_embedability.sh $n

cd -
mv embedability/ks_solution_$n.exhaust .
sort -u ks_solution_$n.exhaust -o ks_solution_uniq_$n.exhaust
rm  ks_solution_$n.exhaust
echo "$(wc -l ks_solution_uniq_$n.exhaust) kochen specker solutions were found."
