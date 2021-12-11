#!/bin/bash

# Script to apply a cube to an instance and then simplify the resulting instance using CaDiCaL (keeping edge variables)

# Ensure parameters are specified on the command-line
if [ -z "$3" ]
then
    echo "Need instance order, filename, cube filename, and the index of the cube to adjoin (one-based indexing)"
    exit
fi

n=$1 # Instance order
f=$2 # Instance filename
c=$3 # Filename containing cubes
i=$4 # Index of the cube to adjoin
m=$((n*(n+1)/2)) # Number of edge variables

dir=$n-adj # Directory to store temporary files
cnf=$dir/$i.cnf # Simplified instance
ext=$dir/$i.ext # Extension stack
log=$dir/$i.log # Simplification log

mkdir -p "$dir"

# Use CaDiCaL to simplify instance with adjoined cube
./apply.sh "$f" "$c" "$i" | ./cadical -f -n -c 20000 -o "$cnf" -e "$ext" > "$log"

# Write simplified instance with extension stack
numvars=$(head -n 1 "$cnf" | cut -d' ' -f3)
numlines=$(head -n 1 "$cnf" | cut -d' ' -f4)
extlines=$(awk "sqrt(\$(NF-1)*\$(NF-1))<=$m" "$ext" | wc -l | cut -d' ' -f1)
newlines=$((numlines+extlines))

echo "p cnf $numvars $newlines"
tail "$cnf" -n +2
awk "sqrt(\$(NF-1)*\$(NF-1))<=$m" "$ext" | sed 's/ 0.*/ 0/'
