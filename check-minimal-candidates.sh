[ "$1" = "-h" -o "$1" = "--help" -o "$#" -ne 2 ] && echo "
Description:
        Need file name and order.
" && exit

file=$1
n=$2
m=$((n*(n-1)/2)) # Number of edge variables in instance

if [ -f "non_minimal_$n" ]
    then
        rm non_minimal_$n
fi

touch non_minimal_$n

while read line; do
    count=0
    while [ "$count" -lt "$m" ]
    do
        if [ -f "temp.txt" ]
        then
            rm temp.txt
        fi
        touch temp.txt
        echo "removing edge $count..."
        if [ -f "non_colorable_check_$n" ]
        then
            rm non_colorable_check_$n
        fi
        python3 check-minimal-candidates.py "$line" $n $count
        if [ -f "non_colorable_check_$n" ]
        then
            if cadical/build/cadical non_colorable_check_$n | grep -q "exit 20"
            then
                echo "non_colorable"
                echo "$line" >> temp.txt
            else
                echo "colorable, not satisfied"
            fi
        else
            echo "no valid edge selected"
        fi
        occurence=($(grep -o "$line" temp.txt | wc -l))
        if [ "$occurence" -eq "2" ]
        then
            echo "$line" >> non_minimal_$n
            break
        fi
        count=$((count+1))
    done
done < $file