file=$1
n=$2

touch not_verified_$n

echo "verifying KS candidates of order $n in $file..."

if [ -f "non_colorable_check_$n" ]
    then
        rm non_colorable_check_$n
    fi

python3 verify.py $file $n

echo "checking solutions are unique up to isomorphism..."
python3 non_iso_verify.py $file $n

sort -u not_verified_$n -o not_verified_$n
num=$(wc -l not_verified_$n)
num=$(echo $num | cut -d' ' -f1)
echo "$num candidates do not satisfy some constraints"
echo "constraint verification complete"