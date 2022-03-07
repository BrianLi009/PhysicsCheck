#!/bin/bash

# Ensure necessary parameters are provided on the command-line
if [ -z "$2" ]
then
	echo "Need base instance and file containing clauses to concatenate to base instance"
	exit
fi

f=$1 # Base instance
l=$2 # File containing clauses to concatenate

numvars=$(head -n 1 "$f" | cut -d' ' -f3)
numlines1=$(head -n 1 "$f" | cut -d' ' -f4)
numlines2=$(wc -l < "$l")
newlines=$((numlines1+numlines2))

echo "p cnf $numvars $newlines"
tail "$f" -n +2 
sed 's/ 0.*/ 0/' "$l" 
