file=$1
n=$2

touch not_verified_$n
while read line; do
    if [ -f "non_colorable_check_$n" ]
    then
        rm non_colorable_check_$n
    fi
    python3 verify-constraints.py "$line" $n
    if cadical/build/cadical non_colorable_check_$n | grep -q "exit 10"
    then
        echo "$line" >> not_verified_$n
    fi
done < $file

sort -u not_verified_$n -o not_verified_$n
num=$(wc -l not_verified_$n)
num=$(echo $num | cut -d' ' -f1)
echo "$num candidates do not satisfy some constraints"
echo "constraint verification complete"

