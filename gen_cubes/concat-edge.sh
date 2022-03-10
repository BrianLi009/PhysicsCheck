#!/bin/bash

# Ensure necessary parameters are provided on the command-line
if [ -z "$2" ]
then
	echo "Need order, base instance, and file containing clauses to concatenate to base instance"
	exit
fi

n=$1 # Order
f=$2 # Base instance
l=$3 # Clauses to concatenate
m=$((n*(n-1)/2)) # Number of edge variables

numvars=$(head -n 1 "$f" | cut -d' ' -f3)
numlines1=$(head -n 1 "$f" | cut -d' ' -f4)
numlines2=$(awk "sqrt(\$(NF-1)*\$(NF-1))<=$m" "$l" | wc -l | cut -d' ' -f1)
newlines=$((numlines1+numlines2))

echo "p cnf $numvars $newlines"
tail "$f" -n +2
awk "sqrt(\$(NF-1)*\$(NF-1))<=$m" "$l" | sed 's/ 0.*/ 0/' # Additional clauses defining edge variables
