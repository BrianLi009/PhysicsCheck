#!/bin/bash

# Script to apply a cube to a CNF instance by adjoining the literals in the cube as unit clauses

# Ensure parameters are specified on the command-line
if [ -z "$3" ]
then
    echo "Need instance filename, cube filename, and the index of the cube to adjoin (one-based indexing)"
    exit
fi

f=$1 # Instance filename
c=$2 # Filename containing cubes
i=$3 # Index of the cube to adjoin

unitlines=$(($(head -n "$i" "$c" | tail -n 1 | xargs -n 1 | wc -l)-2))
numvars=$(head -n 1 "$f" | cut -d' ' -f3)
numlines=$(head -n 1 "$f" | cut -d' ' -f4)
newlines=$((numlines+unitlines))

# Write instance with adjoined cube
echo "p cnf $numvars $newlines"
tail "$f" -n +2
head -n "$i" "$c" | tail -n 1 | xargs -n 1 | tail -n +2 | head -n -1 | sed 's/$/ 0/'
