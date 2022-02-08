#!/bin/bash

#set -x

while getopts "pi" opt
do
	case $opt in
		p)	p="-no-pseudo-test" ;;
		i)	i="inc" ;;
	esac
done
shift $((OPTIND-1))

# Ensure order is given on the command-line
if [ -z "$3" ]
then
	echo "Usage: $0 [-p] [-i] n f k"
	echo "  n is the instance order"
	echo "  f is the instance filename"
	echo "  k is the order of the subgraphs to search for"
	echo "Options:"
	echo "  -p uses a full canonical test"
	echo "  -i searches subgraph orders incrementally"
	exit
fi

n=$1 # Instance order
f=$2
k=$3
dir=$n$p
mkdir -p "$dir"

if [ "$i" == "" ]
then
	i=$k # Subgraph order
	rm "$dir"/"$i"-solo.exhaust "$dir"/"$i"-solo.noncanonical "$dir"/subgraph-gen-solo-"$i".log 2>/dev/null
	start=$(date +%s.%N)
	command="./maplesat-ks/simp/maplesat_static -order=$n -max-exhaustive-var=$((i*(i-1)/2)) -skip-last=$((n-i)) -exhaustive=$dir/$i-solo.exhaust -no-pre $f -keep-blocking=2 -noncanonical-out=$dir/$i-solo.noncanonical $p | tee $dir/subgraph-gen-solo-$i.log"
	echo "$command"
	eval "$command"
	end=$(date +%s.%N)
	runtime=$( echo "$end - $start" | bc -l )
	sols=$( wc -l "$dir"/"$i"-solo.exhaust | cut -d' ' -f1 )
	noncanon=$( wc -l "$dir"/"$i"-solo.noncanonical | cut -d' ' -f1 )
	echo "Order $i: $sols canonical solutions and $noncanon noncanonical solutions in $runtime seconds"
else	
	# If the incremental option was provided then search for subgraphs incrementally starting from order 3
	i=3
	rm "$dir"/$i.exhaust "$dir"/$i.noncanonical "$dir"/subgraph-gen-$i.log 2>/dev/null
	start=$(date +%s.%N)
	command="./maplesat-ks/simp/maplesat_static -order=$n -max-exhaustive-var=$((i*(i-1)/2)) -skip-last=$((n-i)) -exhaustive=$dir/$i.exhaust -no-pre $f -keep-blocking=2 -noncanonical-out=$dir/$i.noncanonical $p > $dir/subgraph-gen-$i.log"
	echo "$command"
	eval "$command"
	end=$(date +%s.%N)
	runtime=$( echo "$end - $start" | bc -l )
	sols=$( wc -l "$dir"/$i.exhaust | cut -d' ' -f1 )
	noncanon=$( wc -l "$dir"/$i.noncanonical | cut -d' ' -f1 )
	echo "Order $i: $sols canonical solutions and $noncanon noncanonical solutions in $runtime seconds"

	for i in $(seq 4 "$k")
	do
		cat "$f" "$dir"/$((i-1)).noncanonical > "${f}"_"${n}"_$((i-1))
		lines=$(wc -l < "${f}"_"${n}"_$((i-1)))
		sed -i -E "s/p cnf ([0-9]*) ([0-9]*)/p cnf \1 $((lines-1))/" "${f}"_"${n}"_$((i-1))
		rm "$dir"/"$i".exhaust "$dir"/"$i".noncanonical "$dir"/subgraph-gen-"$i".log 2>/dev/null
		start=$(date +%s.%N)
		command="./maplesat-ks/simp/maplesat_static -order=$n -max-exhaustive-var=$((i*(i-1)/2)) -skip-last=$((n-i)) -exhaustive=$dir/$i.exhaust -no-pre ${f}_${n}_$((i-1)) -keep-blocking=2 -noncanonical-out=$dir/$i.noncanonical $p > $dir/subgraph-gen-$i.log"
		echo "$command"
		eval "$command"
		end=$(date +%s.%N)
		runtime=$( echo "$end - $start" | bc -l )
		sols=$( wc -l "$dir"/"$i".exhaust | cut -d' ' -f1 )
		noncanon=$( wc -l "$dir"/"$i".noncanonical | cut -d' ' -f1 )
		echo "Order $i: $sols canonical solutions and $noncanon noncanonical solutions in $runtime seconds"
	done
fi
