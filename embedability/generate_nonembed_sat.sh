#!/bin/bash

set -x

#generate nonembedable subgraphs

n=$1
cd ..

if [ -f squarefree_constraints_$n ]
then
    echo "instance already gengerated"
else
    python3 gen_instance/generate_squarefree_only.py $n
fi

if [ -f squarefree_$n.exhaust ]
then
    echo "instance already solved"
else
    ./maplesat-ks/simp/maplesat_static squarefree_constraints_$n -no-pre -exhaustive=squarefree_$n.exhaust -order=$n
fi

cp squarefree_constraints_$n embedability
cp squarefree_$n.exhaust embedability

cd embedability

touch embed_result_$n.txt

set -e 
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
done < squarefree_$n.exhaust

