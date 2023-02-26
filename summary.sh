#!/bin/bash

function readtime() {
	tmp=$(grep "CPU" $2 2>/dev/null | xargs | cut -d' ' -f4)
	tmp=$(awk "BEGIN { print $tmp }" 2>/dev/null)
	tmp=$(echo $tmp/60 | bc -l 2>/dev/null)
	if [ ! -z "$tmp" ]
	then
		eval "$1=$(printf \"%10.2f\" $tmp)"
	else
		spaces=$(printf "%0.s " {1..10})
		eval "$1=\"$spaces\""
	fi
}

printf " n    Solving   Simplifying\n"
for i in `seq 1 22`
do
	if [ ! -f solvelog/constraints_${i}_c_100000_2_2.simp2.log ]
	then
		continue
	fi
	readtime "run" "solvelog/constraints_${i}_c_100000_2_2.simp2.log"
	simptime=$(grep "total process time since initialization" log/constraints_${i}_c_100000_2_2.noncanonical.simp* | awk '{$1=$1};1' | cut -d' ' -f7 | paste -sd+)
	simptime=$(echo "($simptime)/60" | bc -l)
	printf "%2d %s m %11.2f m\n" $i "$run" "$simptime"
done
