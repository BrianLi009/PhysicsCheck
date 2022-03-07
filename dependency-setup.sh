#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    This script will install and compile all required dependency and packages, including maplesat-ks, cadical, networkx, z3-solver, and march_cu from cube and conquer

Usage:
    ./dependency-setup.sh 

" && exit

#install maplesat-ks
if [ -d maplesat-ks ] && [ -f maplesat-ks/simp/maplesat_static ]
then
    echo "maplesat-ks installed and binary file compiled"
else
    git clone git@github.com:curtisbright/maplesat-ks.git maplesat-ks
    #git stash
    cd maplesat-ks
    git checkout unembeddable-subgraph-check
    make
    cd -
fi 

#install cadical
if [ -d cadical ] && [ -f cadical/build/cadical ]
then
    echo "cadical installed and binary file compiled"
else
    git clone https://github.com/arminbiere/cadical.git cadical
    cd cadical
    ./configure
    make
    cd ..
fi

if pip list | grep networkx
then
    echo "networkx package installed"
else 
    pip install networkx
fi

if pip list | grep z3-solver
then
    echo "z3-solver package installed"
else 
    pip install z3-solver
fi

if [ -f gen_cubes/march_cu/march_cu ]
then
    echo "march installed and binary file compiled"
else
    cd gen_cubes/march_cu
    make
    cd -
fi

echo "all dependency properly installed"