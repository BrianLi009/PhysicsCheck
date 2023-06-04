#!/bin/bash

while getopts "apsbm" opt
do
        case $opt in
        p) a="-p" ;;
        m) m="-m" ;;
        esac
done
shift $((OPTIND-1))


[ "$1" = "-h" -o "$1" = "--help" -o "$#" = 0 ] && echo "
Description:
    Print out runtime summary given logs

Usage:
	<n>: #order
	<o>: default c, simplification option, option "c" means simplifying for t conflicts, option "v" means simplify until t% of variables are eliminated
	<t>: default 100000, conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate
	<s>: default 2, by default we only simplify the instance using CaDiCaL after adding noncanonical blocking clauses
	<b>: default 2, by default we generate noncanonical blocking clauses in real time
	<r>: default 0, number of variables to eliminate until the cubing terminates

Note:
	These variables are only used to identify the folder name of the logs
" && exit

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


if [ "$r" != "0" ] 
then
    dir="${n}_${p}_${q}_${o}_${t}_${s}_${b}_${r}"
	echo "expecting log files in '$dir/${n}-solve/'"
	if [ ! -d $dir/${n}-solve ]
	then
		echo "log files not found"
		exit 0
	fi  
	simptime=0
	for logfile in $dir/${n}-solve/*-solve.log; do
		# Extract simptime from current logfile and add it to the total
		time=$(grep "total process time since initialization" "$logfile" | awk '{$1=$1};1' | cut -d' ' -f7 | paste -sd+)
		simptime=$(echo "$simptime + $time" | bc)
	done

	run=0
	max_time=0
	for logfile in $dir/simp/*.log; do
		# Extract simptime from current logfile and add it to the total
		#time=$(grep "CPU time" "$logfile" | awk '{$1=$1};1' | cut -d' ' -f7 | paste -sd+)
		time=$(grep "CPU time" "$logfile" | grep -oP '\d+\.\d{3}')
		time=$(echo "($time)/60" | bc -l)
		run=$(echo "$run + $time" | bc)
		max_time=$(awk -v t=$time -v max=$max_time 'BEGIN{print (t>max)?t:max}')
	done

	simptime=$(echo "($simptime)/60" | bc -l)
	cubetime=$(grep -r 'time' $dir/${n}-log/*.log | cut -f4 -d ' ' | awk '{s+=$1} END {print s}' )
	cubetime=$(echo "($cubetime)/60" | bc -l)

	max_time=$(echo "($max_time)/60" | bc -l)
	printf "maximum solvetime for a cube: %10.2f m \n" $max_time
else
    echo "expecting log files in the main directory"
	cubetime=0
	if [ ! -f constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp.log ]
	then
		echo "log file 'constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp.log' not found"
		exit 0
	fi
	readtime "run" "constraints_${n}_${o}_${t}_${s}_${b}_${r}_final.simp.log"
	simptime=$(grep "total process time since initialization" log/constraints_${n}_${o}_${t}_${s}_${b}_${r}.noncanonical.simp* | awk '{$1=$1};1' | cut -d' ' -f7 | paste -sd+)
	simptime=$(echo "($simptime)/60" | bc -l)
	#run=$(grep "CPU time" log/constraints_${n}_${o}_${t}_${s}_${b}_${r}.noncanonical.simp* | grep -oP '\d+\.\d{3}')
fi


printf " n    Solving   Simplifying   Cubing \n"

printf "%1d %10.2f m %10.2f m %10.2f m\n" $n "$run" "$simptime" "$cubetime"
