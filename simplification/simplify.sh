#!/bin/bash
#set -x
# Ensure parameters are specified on the command-line
if [ -z "$2" ]
then
	echo "Need filename, option (t/s), and the number of times to run the simplification/total times to simplify"
	exit
fi

f=$1
m=$2

set -x

# Directory to log simplification output
mkdir -p log

# Directory for simplified output
mkdir -p simp

# Simplify m seconds
echo "simplifying for $m seconds"
i=1
./cadical/build/cadical "$f" -o simp/"$f".simp1 -e simp/"$f".ext1 -n -c 200000 -t $m | tee log/"$f".simp1
str=$(less log/"$f".simp1 | grep "total process time since initialization:")
time_used=$(echo $str | awk -F ' ' '{print $7; exit;}')
while [ $(echo "$time_used < $m" | bc) -ne 0 ]
do
	time_left=$(echo $m-$time_used | bc)
	time_left=$(printf "%.0f\n" "$time_left")
	./cadical/build/cadical simp/"$f".simp"$i" -o simp/"$f".simp$((i+1)) -e simp/"$f".ext$((i+1)) -n -c 200000 -t $time_left | tee log/"$f".simp$((i+1))
	str=$(less log/"$f".simp$((i+1)) | grep "total process time since initialization:")
	time_used_2=$(echo $str | awk -F ' ' '{print $7; exit;}')
	time_used=$(echo $time_used+$time_used_2+1 | bc)
	((i+=1))
done

m=$(echo ls "simp/$f".simp* | tail -1 | egrep -o [0-9]+ | cut -f1 | tail -1)
echo "$m"

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
