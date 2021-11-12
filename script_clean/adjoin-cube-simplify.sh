#!/bin/bash

# Ensure parameters are specified on the command-line
if [ -z "$3" ]
then
	echo "Instance filename, cube filename, and index of the cube to adjoin"
	exit
fi

f=$1
c=$2
i=$3
dir=$f-$c-simp
adj=$dir/$c$i.adj # Instance with adjoined cube
cnf=$dir/$c$i.cnf # Simplified instance
ext=$dir/$c$i.ext # Extension stack
cnfext=$dir/$c$i.cnfext # Simplified instance with extension stack
mkdir -p "$dir"

# Determine the number of unit clauses to add
unitlines=0
for b in $(sed "$((i+1))q;d" "$c")
do
    if [[ "$b" != "a" && "$b" != "0" ]]
    then
        unitlines=$((unitlines+1))
    fi
done
numvars=$(head -n 1 "$f" | cut -d' ' -f3)
numlines=$(head -n 1 "$f" | cut -d' ' -f4)
newlines=$((numlines+unitlines))

# Write instance with adjoined cube
echo "p cnf $numvars $newlines" > "$adj"
tail "$f" -n +2 >> "$adj"

for b in $(sed "$((i+1))q;d" "$c")
do
    if [[ "$b" != "a" && "$b" != "0" ]]
    then
        echo "$b 0" >> "$adj"
    fi
done

# Use CaDiCaL to simplify instance with adjoined cube
command="./cadical $adj -n -c 200000 -o $cnf -e $ext | tee $dir/$c$i.log"
echo "$command"
eval "$command"

# Write simplified instance with extension stack
numvars=$(head -n 1 "$cnf" | cut -d' ' -f3)
numlines=$(head -n 1 "$cnf" | cut -d' ' -f4)
extlines=$(wc -l "$ext" | cut -d' ' -f1)
newlines=$((numlines+extlines))

echo "p cnf $numvars $newlines" > "$cnfext"
tail "$cnf" -n +2 >> "$cnfext"
cat "$ext" >> "$cnfext"
sed -i 's/ 0.*/ 0/' "$cnfext"
