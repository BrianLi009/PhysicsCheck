#!/bin/bash
d=$1 #directory for iterative cubing
v=$2 #initial amount of variables to eliminate during iterative cubing
a=$3 #amount of additonal variable to eliminate in each cubing stage
n=$4 #order

cd $d

cubetime=$(find . -type f -name "*.log" -exec grep -h "c time * *[0-9]*\.*[0-9]*" {} + | awk '{total += $(NF-1)} END {print total}')
simptime=$(find . -type f -name "*.simp" -exec grep -h "c total process time since initialization: * *[0-9]*\.*[0-9]*" {} + | awk '{total += $(NF-1)} END {print total}')
simptime2=$(find . -type f -name "*.log" -exec grep -h "c total process time since initialization: * *[0-9]*\.*[0-9]*" {} + | awk '{total += $(NF-1)} END {print total}')
solvetime=$(find . -type f -name "*.log" -exec grep -h "CPU time * *[0-9]*\.*[0-9]*" {} + | awk '{total += $(NF-1)} END {print total}')
verifytime=$(find . -type f -name "*.log" -exec grep -h "verification time: * *[0-9]*\.*[0-9]*" {} + | awk '{total += $(NF-1)} END {print total}')
conflicts=$(find . -type f -name "*.log" -exec grep -h "conflicts             : * *[0-9]*\.*[0-9]*" {} + | awk '{total += $(NF-2)} END {print total}')
total_cubes=$(find . -type f -name "*.cubes" -exec cat {} + | wc -l)

printf "%-15s %-15s %-15s %-15s %-15s\n" "cubing time" "cube simp time" "solve simp time" "solve time" "verify time"
printf "%-15s %-15s %-15s %-15s %-15s\n" "${cubetime} secs" "${simptime} secs" "${simptime2} secs" "${solvetime} secs" "${verifytime} secs"

printf "total number of conflicts: $conflicts"
printf "total number of cubes: $total_cubes"

cd -

time_wasted=0

#verify

perform_verification() {
    local directory_to_verify=$1
    local current_var_eliminated=$2
    local increment=$3

    if [ ! -d "$directory_to_verify" ] || [ -z "$(ls -A "$directory_to_verify")" ]; then
        echo "Error: $directory_to_verify cannot be found or is empty, verification failed"
        exit 0
    fi

    for file in $directory_to_verify/*.log; do
        if grep -q "UNSATISFIABLE" "$file"; then
            if grep -q "c VERIFIED" "$file" && grep -q "s VERIFIED" "$file"; then
                echo "$file verified"
            else
                echo "$file is solved but not verified"
            fi
        else
            echo "$file is not solved, needs to be extended"
            solve_time=( $(grep "CPU time"  $file | cut -f2 -d:) )
            solve_time_int=${solve_time%.*}
            time_wasted=$((time_wasted += $solve_time_int))
            index=$(echo "$file" | grep -oP '(?<=/)\d+(?=-solve\.log)')
            result="$current_var_eliminated-$index"
            new_var_to_cube=$(echo "$current_var_eliminated + $increment" | bc)
            d="${directory_to_verify%%/$current_var_eliminated*}"
            new_dir=$d/$result/$new_var_to_cube/$n-solve
            command="perform_verification $new_dir $new_var_to_cube $a"
            #echo $command
            eval $command
        fi
    done
}


directory_to_verify=$d/$v/$n-solve
perform_verification "$directory_to_verify" $v $a

echo "Total time wasted on solving: $time_wasted secs"