#!/bin/bash

#set -x

# Ensure parameters are specified on the command-line
if [ -z "$2" ]
then
	echo "Need filename and the percentage of variables to remove"
	exit
fi

f="$1"
p="$2"

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
	extlines_j=$(wc -l simp/"$f".ext"$j" | cut -d' ' -f1)
	extlines_total=$((extlines_total+extlines_j))
done

# Lines in simplified instance with reconstruction stack
newlines=$((numlines+extlines_total))

# Output final simplified instance
echo "p cnf $numvars $newlines" > "$f".simp
tail simp/"$f".simp"$i" -n +2 >> "$f".simp
for j in $(seq 1 "$i")
do
	cat simp/"$f".ext"$j" >> "$f".simp
done
sed -i 's/ 0.*/ 0/' "$f".simp
