#!/bin/bash

# Ensure parameters are specified on the command-line
if [ -z "$5" ]
then
    echo "Need order, base instance filename, file containing clauses to concatenate, file containing cube to apply, and the index of the cube to adjoin (one-based indexing)"
    exit
fi

n=$1 # Order
f=$2 # Instance filename
l=$3 # Filename containing clauses
c=$4 # Filename containing cubes
i=$5 # Index of the cube to adjoin
m=$((n*(n-1)/2)) # Number of edge variables

numvars=$(head -n 1 "$f" | cut -d' ' -f3) # Number of variables in instance
numlines1=$(head -n 1 "$f" | cut -d' ' -f4) # Number of base clauses
numlines2=$(awk "sqrt(\$(NF-1)*\$(NF-1))<=$m" "$l" | wc -l | cut -d' ' -f1) # Number of additional clauses
numlines3=$(($(head -n "$i" "$c" | tail -n 1 | xargs -n 1 | wc -l)-2)) # Number of literals in cube to be applied
newlines=$((numlines1+numlines2+numlines3)) # Number of clauses to output

echo "p cnf $numvars $newlines" # Header
tail "$f" -n +2 # Original clauses
awk "sqrt(\$(NF-1)*\$(NF-1))<=$m" "$l" | sed 's/ 0.*/ 0/' # Additional clauses defining edge variables
head -n "$i" "$c" | tail -n 1 | xargs -n 1 | tail -n +2 | head -n -1 | sed 's/$/ 0/' # Apply cube to instance
