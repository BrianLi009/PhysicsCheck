#!/bin/bash

# Ensure parameters are specified on the command-line
if [ -z "$4" ]
then
    echo "Need base instance filename, file containing clauses to concatenate, file containing cube to apply, and the index of the cube to adjoin (one-based indexing)"
    exit
fi

f=$1 # Instance filename
l=$2 # Filename containing clauses
c=$3 # Filename containing cubes
i=$4 # Index of the cube to adjoin

numvars=$(head -n 1 "$f" | cut -d' ' -f3) # Number of variables in instance
numlines1=$(head -n 1 "$f" | cut -d' ' -f4) # Number of base clauses
numlines2=$(wc -l < "$l") # Number of additional clauses
numlines3=$(($(head -n "$i" "$c" | tail -n 1 | xargs -n 1 | wc -l)-2)) # Number of literals in cube to be applied
newlines=$((numlines1+numlines2+numlines3)) # Number of clauses to output

echo "p cnf $numvars $newlines" # Header
tail "$f" -n +2 # Original clauses
sed 's/ 0.*/ 0/' "$l" # Additional clauses
head -n "$i" "$c" | tail -n 1 | xargs -n 1 | tail -n +2 | head -n -1 | sed 's/$/ 0/' # Apply cube to instance
