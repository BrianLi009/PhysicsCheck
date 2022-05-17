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

if test -f "embeddable.txt"
then
    echo "embeddable.txt exists, delete or rename the file to continue"
    exit 0
else
    touch embeddable.txt
fi

while read line; do
    python3 main.py "$line" $n $index True nonembeddable.txt embeddable.txt
done < $n.exhaust

cd ..

cp embedability/embeddable.txt .
sort -u embeddable.txt -o ks_solution_uniq_$n.exhaust
rm embeddable.txt

