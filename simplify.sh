#!/bin/bash

# Ensure parameters are specified on the command-line
if [ -z "$2" ]
then
	echo "Need filename and the number of times to run the simplification"
	exit
fi

f=$1
m=$2

# Directory to log simplification output
mkdir -p log

# Directory for simplified output
mkdir -p simp

# Simplify m times
./cadical/build/cadical "$f" -o simp/"$f".simp1 -e simp/"$f".ext1 -n -c 200000 | tee log/"$f".simp1
for i in $(seq 1 $((m-1)))
do
	./cadical/build/cadical simp/"$f".simp"$i" -o simp/"$f".simp$((i+1)) -e simp/"$f".ext$((i+1)) -n -c 200000 | tee log/"$f".simp$((i+1))
done

# Number of variables and lines in the final simplified instance
numvars=$(head -n 1 simp/"$f".simp"$m" | cut -d' ' -f3)
numlines=$(head -n 1 simp/"$f".simp"$m" | cut -d' ' -f4)

# Lines in reconstruction stack
extlines_total=0
for i in $(seq 1 "$m")
do
	extlines_i=$(wc -l simp/"$f".ext"$i" | cut -d' ' -f1)
	extlines_total=$((extlines_total+extlines_i))
done

# Lines in simplified instance with reconstruction stack
newlines=$((numlines+extlines_total))

# Output final simplified instance
echo "p cnf $numvars $newlines" > "$f".simp
tail simp/"$f".simp"$m" -n +2 >> "$f".simp
for i in $(seq 1 "$m")
do
	cat simp/"$f".ext"$i" >> "$f".simp
done
sed -i 's/ 0.*/ 0/' "$f".simp
