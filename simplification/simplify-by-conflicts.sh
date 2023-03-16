#!/bin/bash

# Ensure parameters are specified on the command-line
if [ -z "$2" ]
then
	echo "Need filename, order, and the number of conflicts for which to simplify"
	exit
fi

f=$1 # Filename
o=$2 # Order
m=$3 # Number of conflicts
e=$((o*(o-1)/2)) # Number of edge variables

# Directory to log simplification output
mkdir -p log

# Directory for simplified output
mkdir -p simp

# Simplify m seconds
echo "simplifying for $m conflicts"
i=1
./cadical/build/cadical "$f" -o simp/"$f".simp1 -e simp/"$f".ext1 -n -c $m | tee log/"$f".simp1
str=$(less log/"$f".simp1 | grep "c conflicts:")
conf_used=$(echo $str | awk -F ' ' '{print $3; exit;}')
echo "$conf_used conflicts used for simplification"

if grep -q "UNSATISFIABLE" log/"$f".simp1
then
	conf_left=0
else
	conf_left=$(echo $m-$conf_used | bc)
fi

while [ $(echo "$conf_used < $m" | bc) -ne 0 ] && [ "$conf_left" != 0 ]
do
	conf_left=$(echo $m-$conf_used | bc)
	./gen_cubes/concat-edge.sh $o simp/"$f".simp"$i" simp/"$f".ext"$i" | ./cadical/build/cadical -o simp/"$f".simp$((i+1)) -e simp/"$f".ext$((i+1)) -n -c $conf_left | tee log/"$f".simp$((i+1))
	rm simp/"$f".simp"$i" simp/"$f".ext"$i" 2>/dev/null
	str=$(less log/"$f".simp$((i+1)) | grep "c conflicts:")
	conf_used_2=$(echo $str | awk -F ' ' '{print $3; exit;}')
	conf_used=$(echo $conf_used+$conf_used_2 | bc)
	echo "$conf_used conflicts used for simplification"
	((i+=1))
	if grep -q "UNSATISFIABLE" log/"$f".simp$i
	then
		break
	fi
done

echo "Called CaDiCaL $i times"

# Output final simplified instance
./gen_cubes/concat-edge.sh $o simp/"$f".simp"$i" simp/"$f".ext"$i" > "$f".simp
