#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    This script will install and compile all required dependency and packages, including maplesat-ks, cadical, networkx, z3-solver, and march_cu from cube and conquer

Usage:
    ./dependency-setup.sh 

" && exit

echo "prerequisite: pip and make installed"

#install maplesat-ks
if [ -d maplesat-ks ] && [ -f maplesat-ks/simp/maplesat_static ]
then
    echo "maplesat-ks installed and binary file compiled"
else
    cd maplesat-ks
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

required_version="2.5"
installed_version=$(pip3 show networkx | grep Version | awk '{print $2}')

if [[ "$(printf '%s\n' "$installed_version" "$required_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo "need to install networkx version newer than $required_version"
    pip3 install --upgrade networkx
    echo "networkx has been successfully updated."
else
    echo "networkx version $installed_version is already installed and newer than $required_version"
fi

if pip3 list | grep z3-solver
then
    echo "z3-solver package installed"
else 
    pip3 install z3-solver
fi

if [ -f gen_cubes/march_cu/march_cu ]
then
    echo "march installed and binary file compiled"
else
    cd gen_cubes/march_cu
    make
    cd -
fi

if [ -f drat-trim/drat-trim ]
then
    echo "drat-trim installed and binary file compiled"
else
    cd drat-trim
    make
    cd -
fi

echo "all dependency properly installed"
