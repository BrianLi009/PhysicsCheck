#!/bin/bash

n=$1 #order

python3 gen_instance/generate.py $n #generate the instance of order n

if cd maplesat-ks
then
    echo "maplesat-ks installed"
else
    git clone https://github.com/curtisbright/maplesat-ks.git maplesat-ks
    cd maplesat-ks
fi 
#clone maplesat-ks if it does not
make
cd -

./maplesat-ks/simp/maplesat_static constraints_$n -no-pre -exhaustive=$n.exhaust -order=$n