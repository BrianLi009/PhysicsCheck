#!/bin/bash

n=$1 #order

python3 gen_instance/generate.py $n #generate the instance of order n

if cd maplesat-ks
then
    echo "maplesat-ks installed"
    git stash
    git checkout unembeddable-subgraph-check
else
    git clone https://github.com/curtisbright/maplesat-ks.git maplesat-ks
    git stash
    git checkout unembeddable-subgraph-check
    cd maplesat-ks
fi 
#clone maplesat-ks if it does not
make
cd -

#generate non canonical subgraph
./run-subgraph-generation.sh -i $n constraints_17 10

#append blocking clauses to the instance
cd $n
cat *.noncanonical > all.noncanonical
cd -
cat $n/all.noncanonical >> constraints_$n

./maplesat-ks/simp/maplesat_static constraints_$n -no-pre -exhaustive=$n.exhaust -order=$n

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