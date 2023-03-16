#!/bin/bash

n=$1 #order
o=${2:-c} #simplification option, option "c" means simplifying for t conflicts, option "v" means simplify until t% of variables are eliminated
t=${3:-100000} #conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate
s=${4:-2} #by default we only simplify the instance using CaDiCaL after adding noncanonical blocking clauses
b=${5:-2} #by default we generate noncanonical blocking clauses in real time
r=${6:-0} #number of variables to eliminate until the cubing terminates

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

echo ${n}-solve
if [ ! -d ${n}-solve ]
then
	echo "log files not found"
	exit 0
fi

printf " n    Solving   Simplifying\n"

if [ ! -f ${n}-solve/constraints_${n}_${o}_${t}_${s}_${b}_final.simp.log ]
then
	cat ${n}-solve/*-solve.log >> ${n}-solve/constraints_${n}_${o}_${t}_${s}_${b}_final.simp.log
fi

readtime "run" "${n}-solve/constraints_${n}_${o}_${t}_${s}_${b}_final.simp.log"
	simptime=$(grep "total process time since initialization" log/constraints_${n}_${o}_${t}_${s}_${b}.noncanonical.simp* | awk '{$1=$1};1' | cut -d' ' -f7 | paste -sd+)
	simptime=$(echo "($simptime)/60" | bc -l)
	printf "%2d %s m %11.2f m\n" $n "$run" "$simptime"