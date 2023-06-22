#!/bin/bash

while getopts "p" opt
do
	case $opt in
		p)	p="-no-pseudo-test" ;;
	esac
done
shift $((OPTIND-1))

# Ensure necessary parameters are given on the command-line
if [ -z "$3" ]
then
	echo "Usage: $0 [-p] n f k"
	echo "  n is the instance order"
	echo "  f is the instance filename"
	echo "  k is the order of the subgraphs to search for"
	echo "Options:"
	echo "  -p uses a full canonical test"
	exit
fi

n=$1 # Instance order
f=$2
k=$3
dir=$n$p
mkdir -p "$dir"

i=$k # Subgraph order
rm "$dir"/"$i"-solo.exhaust "$dir"/"$i"-solo.noncanonical "$dir"/subgraph-gen-solo-"$i".log 2>/dev/null
start=$(date +%s.%N)
command="./maplesat-ks/simp/maplesat_static -order=$n -max-exhaustive-var=$((i*(i-1)/2)) -skip-last=$((n-i)) -exhaustive=$dir/$i-solo.exhaust -no-pre $f $f.drat -perm-out=$f.perm -keep-blocking=2 -noncanonical-out=$dir/$i-solo.noncanonical -minclause $p | tee $dir/subgraph-gen-solo-$i.log"
echo "$command"
eval "$command"
end=$(date +%s.%N)
runtime=$( echo "$end - $start" | bc -l )
sols=$( wc -l "$dir"/"$i"-solo.exhaust | cut -d' ' -f1 )
noncanon=$( wc -l "$dir"/"$i"-solo.noncanonical | cut -d' ' -f1 )
echo "Order $i: $sols canonical solutions and $noncanon noncanonical solutions in $runtime seconds"

./proof-module.sh $k $f $dir/subgraph-gen-solo-$i.verify
