#!/bin/bash

# Ensure order is given on the command-line
if [ -z $1 ]
then
	echo "Need instance order and (optionally) the order of the subgraphs to search for"
	exit
fi

n=$1 # Instance order
mkdir -p $1

if [ ! -z $2 ]
then
	i=$2 # Subgraph order
	start=`date +%s.%N`
	command="./maplesat_static -order=$n -max-exhaustive-var=$((i*(i-1)/2)) -skip-last=$((n-i)) -exhaustive=$n/$i-solo.exhaust -no-pre constraints_half_$n -keep-blocking=2 -noncanonical-out=$n/$i-solo.noncanonical | tee $n/subgraph-gen-solo-$i.log"
	echo $command
	eval $command
	end=`date +%s.%N`
	runtime=$( echo "$end - $start" | bc -l )
	sols=$( wc -l $n/$i-solo.exhaust | cut -d' ' -f1 )
	noncanon=$( wc -l $n/$i-solo.noncanonical | cut -d' ' -f1 )
	echo "Order $i: $sols canonical solutions and $noncanon noncanonical solutions in $runtime seconds"
else	
	# If no subgraph order was provided then incrementally search for subgraphs from order 3 to order 11
	i=3
	start=`date +%s.%N`
	command="./maplesat_static -order=$n -max-exhaustive-var=$((i*(i-1)/2)) -skip-last=$((n-i)) -exhaustive=$n/$i.exhaust -no-pre constraints_half_$n -keep-blocking=2 -noncanonical-out=$n/$i.noncanonical > $n/subgraph-gen-$i.log"
	echo $command
	eval $command
	end=`date +%s.%N`
	runtime=$( echo "$end - $start" | bc -l )
	sols=$( wc -l $n/$i.exhaust | cut -d' ' -f1 )
	noncanon=$( wc -l $n/$i.noncanonical | cut -d' ' -f1 )
	echo "Order $i: $sols canonical solutions and $noncanon noncanonical solutions in $runtime seconds"

	for i in `seq 4 11`
	do
		start=`date +%s.%N`
		command="./maplesat_static -order=$n -max-exhaustive-var=$((i*(i-1)/2)) -skip-last=$((n-i)) -exhaustive=$n/$i.exhaust -no-pre constraints_half_$n -assumptions=$n/$((i-1)).exhaust -keep-blocking=2 -noncanonical-out=$n/$i.noncanonical > $n/subgraph-gen-$i.log"
		echo $command
		eval $command
		end=`date +%s.%N`
		runtime=$( echo "$end - $start" | bc -l )
		sols=$( wc -l $n/$i.exhaust | cut -d' ' -f1 )
		noncanon=$( wc -l $n/$i.noncanonical | cut -d' ' -f1 )
		echo "Order $i: $sols canonical solutions and $noncanon noncanonical solutions in $runtime seconds"
	done
fi
