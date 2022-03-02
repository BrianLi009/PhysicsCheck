n=$1

#check embedability of order n, given that $n.exhaust exists

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

