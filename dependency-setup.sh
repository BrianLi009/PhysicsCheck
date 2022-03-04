#!/bin/bash

#install maplesat-ks
if [ -d maplesat-ks ]
then
    echo "maplesat-ks installed"
    cd maplesat-ks
    git checkout unembeddable-subgraph-check
    make
    cd -
else
    git clone git@github.com:curtisbright/maplesat-ks.git maplesat-ks
    #git stash
    cd maplesat-ks
    git checkout unembeddable-subgraph-check
    make
    cd -
fi 

#install cadical
if [ -d cadical ]
then
    echo "cadical installed"
    #cd ..
else
    git clone https://github.com/arminbiere/cadical.git cadical
    cd cadical
    ./configure
    make
    cd ..
fi

cd embedability
pip install networkx
pip install z3-solver
cd ..

cd gen_cubes/march_cu
make
cd ..