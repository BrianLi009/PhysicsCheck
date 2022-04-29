#!/bin/bash
set -x
# Ensure parameters are specified on the command-line
if [ -z "$2" ]
then
	echo "Need filename, option (t/s), and the number of times to run the simplification/total times to simplify"
	exit
fi

f=$1
o=$2 
m=$3

# Directory to log simplification output
mkdir -p log

# Directory for simplified output
mkdir -p simp

# Simplify m times
if [ $o = "t" ]
then
	echo "simplifying for $m times"
	./cadical/build/cadical "$f" -o simp/"$f".simp1 -e simp/"$f".ext1 -n -c 200000 | tee log/"$f".simp1
	for i in $(seq 1 $((m-1)))
	do
		./cadical/build/cadical simp/"$f".simp"$i" -o simp/"$f".simp$((i+1)) -e simp/"$f".ext$((i+1)) -n -c 200000 | tee log/"$f".simp$((i+1))
	done
elif [ $o = "s" ]
then
	echo "simplifying for $m seconds"
	end=$((SECONDS+$m))
	i=1
	./cadical/build/cadical "$f" -o simp/"$f".simp1 -e simp/"$f".ext1 -n -c 200000 | tee log/"$f".simp1
	while [ $SECONDS -lt $end ]
	do
		./cadical/build/cadical simp/"$f".simp"$i" -o simp/"$f".simp$((i+1)) -e simp/"$f".ext$((i+1)) -n -c 200000 | tee log/"$f".simp$((i+1))
		((i+=1))
	done
	./cadical/build/cadical simp/"$f".simp"$i" -o simp/"$f".simp$((i+1)) -e simp/"$f".ext$((i+1)) -n -c 200000 | tee log/"$f".simp$((i+1))
else
	echo "invalid command."
fi

if [ $o = "s" ]
then
	m=$(echo ls "simp/$f".simp* | tail -1 | egrep -o [0-9]+ | cut -f1 | tail -1)
	echo "$m"
fi
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
