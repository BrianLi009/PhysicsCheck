#!/bin/bash

function readtime() {
	tmp=$(grep "CPU" $2 2>/dev/null | xargs | cut -d' ' -f4)
	tmp=$(awk "BEGIN { print $tmp }")
	tmp=$(echo $tmp/60 | bc -l)
	if [ ! -z "$tmp" ]
	then
		eval "$1=$(printf \"%10.2f\" $tmp)"
	else
		spaces=$(printf "%0.s " {1..10})
		eval "$1=\"$spaces\""
	fi
}

printf " n    Solving\n"
for i in `seq 1 22`
do
	if [ ! -f solvelog/constraints_${i}_c_100000_2_2.simp2.log ]
	then
		continue
	fi
	readtime "run" "solvelog/constraints_${i}_c_100000_2_2.simp2.log"
	printf "%2d %s m\n" $i "$run"
done
