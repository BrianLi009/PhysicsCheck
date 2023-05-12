[ "$1" = "-h" -o "$1" = "--help" -o "$#" -ne 2 ] && echo "
Description:
    Verify the output of the pipeline by checking the following:
    1. solutions are not 010-colorable
    2. solutions are unique up to isomorphism

Usage:
    ./verify.sh <file with KS candidates> <order of the graph>
" && exit

file=$1
n=$2

touch not_verified_$n

echo "verifying KS candidates of order $n in $file..."
while read line; do
    if [ -f "non_colorable_check_$n" ]
    then
        rm non_colorable_check_$n
    fi
    python3 verify.py "$line" $n
    if cadical/build/cadical non_colorable_check_$n | grep -q "exit 10"
    then
        echo "$line" >> not_verified_$n
    fi
done < $file

echo "checking solutions are unique up to isomorphism..."
python3 non_iso_verify.py $file $n

sort -u not_verified_$n -o not_verified_$n
num=$(wc -l not_verified_$n)
num=$(echo $num | cut -d' ' -f1)
echo "$num candidates do not satisfy some constraints"
echo "constraint verification complete"

