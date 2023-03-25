#!/bin/bash

while getopts "apsbm" opt
do
        case $opt in
        p) a="-p" ;;
        m) m="-m" ;;
        esac
done
shift $((OPTIND-1))


n=$1 #order
p=$2
q=$3
o=${4:-c} #simplification option, option "c" means simplifying for t conflicts, option "v" means simplify until t% of variables are eliminated
t=${5:-100000} #conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate
s=${6:-2} #by default we only simplify the instance using CaDiCaL after adding noncanonical blocking clauses
b=${7:-2} #by default we generate noncanonical blocking clauses in real time
r=${8:-0} #number of variables to eliminate until the cubing terminates

function readtime() {
	#tmp=$(grep "CPU" $2 2>/dev/null | xargs | cut -d' ' -f4)
	tmp=$(grep "CPU" $2 2>/dev/null | awk '{sum+=$4} END {print sum}')
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

dir="${n}_${p}_${q}_${o}_${t}_${s}_${b}_${r}"

if [ ! -d $dir/${n}-solve ]
then
	echo "log files not found"
	exit 0
fi

printf " n    Solving   Simplifying   Cubing (if enabled) \n"

if [ ! -f $dir/${n}-solve/constraints_${n}_${p}_${q}_${o}_${t}_${s}_${b}_${r}_final.simp.log ]
then
	cat $dir/${n}-solve/*-solve.log >> $dir/${n}-solve/constraints_${n}_${p}_${q}_${o}_${t}_${s}_${b}_${r}_final.simp.log
fi

readtime "run" "$dir/${n}-solve/constraints_${n}_${p}_${q}_${o}_${t}_${s}_${b}_${r}_final.simp.log"
	simptime=$(grep "total process time since initialization" $dir/log/constraints_${n}_${p}_${q}_${o}_${t}_${s}_${b}.noncanonical.simp* | awk '{$1=$1};1' | cut -d' ' -f7 | paste -sd+)
	simptime=$(echo "($simptime)/60" | bc -l)

if [ "$r" != "0" ] 
then
    cubetime=$(grep -r 'time' $dir/${n}-log/*.log | cut -f4 -d ' ' | awk '{s+=$1} END {print s}' )
	cubetime=$(echo "($cubetime)/60" | bc -l)
else
    cubetime=0
fi

	printf "%1d %s m %11.2f m %19.2f m\n" $n "$run" "$simptime" "$cubetime"
