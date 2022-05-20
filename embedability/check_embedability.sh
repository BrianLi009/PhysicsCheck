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
index=0

touch embeddable$n.txt

while read line; do
    python3 main.py "$line" $n $index True nonembeddable_$n.txt embeddable_$n.txt
done < $n.exhaust

cd ..

cp embedability/embeddable$n.txt .
sort -u embeddable$n.txt -o ks_solution_uniq_$n.exhaust
rm embeddable$n.txt

