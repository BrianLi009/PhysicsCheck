#!/bin/bash
set -x
# Ensure parameters are specified on the command-line
if [ -z "$3" ]
then
    echo "Need instance filename, cube filename, and the index of the cube to adjoin (zero-based indexing)"
    exit
fi

f=$1
c=$2
i=$3
s=$4
adj=$c$i.adj # Instance with adjoined cube
cnf=$c$i.cnf # Simplified instance
ext=$c$i.ext # Extension stack
cnfext=$c$i.cnfext # Simplified instance with extension stack

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
newlines=$((numlines+unitlines-1))

# Write instance with adjoined cube
echo "p cnf $numvars $newlines" > "$adj"
tail "$f" -n +2 | head -n -1 >> "$adj"

for b in $(sed "$((i+1))q;d" "$c")
do
    if [[ "$b" != "a" && "$b" != "0" ]]
    then
        echo "$b 0" >> "$adj"
    fi
done

sed -i '$ d' "$adj"

# Use CaDiCaL to simplify instance with adjoined cube
./simplify.sh "$adj" $s
