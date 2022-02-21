#!/bin/bash

# Ensure parameters are specified on the command-line

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    This is a driver script that handles generating the SAT encoding, generating non-canonical subgraph blocking clauses,
    simplify instance using CaDiCaL, solve the instance using maplesat-ks, then finally determine if a KS system exists for a certain order.
    
Usage:
    ./main.sh <n> <s>

Options:
    <n>: the order of the instance/number of vertices in the graph
    <s>: number of times to simplify the instance using CaDiCaL
" && exit

if [ -z "$1" ]
then
    echo "Need instance order (number of vertices) and number of simplification, use -h or --help for further instruction"
    exit
fi

n=$1 #order

python3 gen_instance/generate.py $n #generate the instance of order n

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
./simplify.sh constraints_$n $s

./maplesat-ks/simp/maplesat_static constraints_$n.simp -no-pre -exhaustive=$n.exhaust -order=$n

#checking if there exist embeddable solution

cp $n.exhaust embedability

cd embedability
touch embed_result.txt

count=0
while read line; do
    index=0
    while ! grep -q "  $count  " embed_result.txt; do
        python3 main.py "$line" $n $count $index
        if ! grep -q "  $count  " embed_result.txt; then
            timeout 10 python3 test.py
        fi
        index=$((index+1))
    done
    count=$((count+1))
done < $n.exhaust

#output the ks system if there is any
touch ks_solution_$n.exhaust
while read p; do
	if [[ $p == *"  sat"* ]]; then
		index=$(echo $p | cut -d ' ' -f1)
		sed "${index}q;d" $n.exhaust >> ks_solution_$n.exhaust	
	fi
done < embed_result.txt

cd -
mv embedability/ks_solution_$n.exhaust .
sort -u ks_solution_$n.exhaust -o ks_solution_uniq_$n.exhaust
rm  ks_solution_$n.exhaust
echo "$(wc -l ks_solution_uniq_$n.exhaust) kochen specker solutions were found."
