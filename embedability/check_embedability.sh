[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    This script takes in an exhaust file with kochen specker candidates, and determine whether each
    of them is embeddable, if it is embeddable, then it will be outputted into a file as a Kochen
    Specker graph. We require the existance of n.exhaust in the directory.

Usage:
    ./check_embedability.sh n

Options:
    <n>: the order of the instance/number of vertices in the graph
" && exit

n=$1

set -e 
count=0
while read line; do
    index=0
    while ! grep -q "  $count  " embed_result.txt; do
        python3 main.py "$line" $n $count $index
        if ! grep -q "  $count  " embed_result.txt; then
            timeout 10 python3 test.py
        fi
        index=$((index+1))
    done
    count=$((count+1))
done < $n.exhaust

#output the ks system if there is any
touch ks_solution_$n.exhaust
while read p; do
	if [[ $p == *"  sat"* ]]; then
		index=$(echo $p | cut -d ' ' -f1)
		sed "${index}q;d" $n.exhaust >> ks_solution_$n.exhaust	
	fi
done < embed_result.txt

cd ..

mv embedability/ks_solution_$n.exhaust .
sort -u ks_solution_$n.exhaust -o ks_solution_uniq_$n.exhaust
rm  ks_solution_$n.exhaust

