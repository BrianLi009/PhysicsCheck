#!/bin/bash

n=$1 #order
f=$2 #input file
o=$3 #output .verify file

# Verify DRAT proof
./drat-trim/drat-trim $f $f.drat -f | tee $o
if ! grep -E "s DERIVATION|s VERIFIED" -q $o
then
	echo "ERROR: Proof not verified"
fi
# Verify trusted clauses
if [ -f "$f.perm" ]; then
	grep 't' $f.drat | ./drat-trim/check-perm.py $n $f.perm | tee $f.permcheck
	if ! grep "VERIFIED" -q $f.permcheck
	then
		echo "ERROR: Trusted clauses not verified"
	fi
fi
