#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" -o "$#" -ne 3 ] && echo "
Description:
	Updated on 2023-01-11
	This script simplify the instance, add back edge blocking clauses, then repeat
	until a certain percentage of variables are eliminated

Usage:
	./simplify-by-var-removal n f p

Options:
	<n>: the order of the instance/number of vertices in the graph
	<f>: file name of the current SAT instance
	<p>: percentage of variables to eliminate (1-100)
" && exit

n=$1
f="$2"
p="$3"
m=$((n*(n-1)/2))

sub_dir=$(echo "${f%%/*}")
#Directory to log simplification output
mkdir -p log/$sub_dir

# Directory for simplified output
mkdir -p simp/$sub_dir

# Simplify until at least p percent of variables have been removed
./cadical/build/cadical "$f" -o simp/"$f".simp1 -e simp/"$f".ext1 -n -c 200000 | tee log/"$f".simp1
for i in $(seq 1 100)
do
	vars_remaining=$(grep "c [*]" log/"$f".simp"$i" | tail -n 1 | rev | cut -d' ' -f1 | rev | sed 's/.$//')
	if (( vars_remaining < 100 - p ))
	then
		break
	fi
	./cadical/build/cadical simp/"$f".simp"$i" -o simp/"$f".simp$((i+1)) -e simp/"$f".ext$((i+1)) -n -c 200000 | tee log/"$f".simp$((i+1))
done

# Number of variables and lines in the final simplified instance
numvars=$(head -n 1 simp/"$f".simp"$i" | cut -d' ' -f3)
numlines=$(head -n 1 simp/"$f".simp"$i" | cut -d' ' -f4)

# Lines in reconstruction stack
extlines_total=0
for j in $(seq 1 "$i")
do
	extlines_j=$(awk "sqrt(\$(NF-1)*\$(NF-1))<=$m" "simp/"$f".ext$j" | wc -l | cut -d' ' -f1)
	extlines_total=$((extlines_total+extlines_j))
done

# Lines in simplified instance with reconstruction stack
newlines=$((numlines+extlines_total))

# Output final simplified instance
echo "p cnf $numvars $newlines" > "$f".simp
tail simp/"$f".simp"$i" -n +2 >> "$f".simp
for j in $(seq 1 "$i")
do
	awk "sqrt(\$(NF-1)*\$(NF-1))<=$m" "simp/"$f".ext$j" | sed 's/ 0.*/ 0/' >> "$f".simp
done

#remove intermediate simp files
rm simp/"$f"*
