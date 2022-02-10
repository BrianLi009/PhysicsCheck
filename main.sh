#!/bin/bash

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
#./run-subgraph-generation.sh $n constraints_$n 11
./run-subgraph-generation.sh $n constraints_$n 12

#append blocking clauses to the instance
cd $n
cat *.noncanonical > all.noncanonical
cd -
cat $n/all.noncanonical >> constraints_$n
lines=$(wc -l < "constraints_$n")
chmod u+x constraints_$n
sed -i -E "s/p cnf ([0-9]*) ([0-9]*)/p cnf \1 $((lines-1))/" "constraints_$n"

#simplify 3 times
./simplify.sh constraints_$n 3

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

#todo: add minimum subgraph check for candidates