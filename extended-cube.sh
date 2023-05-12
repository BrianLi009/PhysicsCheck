#!/bin/bash

o=$1 #first index of cube files to check within directory d
i=$2 #last index of cube files to check within directory d
d=$3 #all log files should be stored in a directory
c=$4 #directory of cubes


files=$(ls $c/*.cubes)
current_cube=$(echo "$files" | awk -F '[./]' '{print $(NF-1)}' | sort -nr | head -n 1)
new_cube=$((current_cube + 1))
current_cube_file=$c/$current_cube.cubes
new_cube_file=$c/$new_cube.cubes

terminate=True

for index in $(seq $o $i)
do
        file="$d/$index-solve.log"
        echo $file
        if grep -q "UNSATISFIABLE" $file 
        then
                #do something
                continue
        elif grep -q "SATISFIABLE" $file
        then
                #do something
                continue
        else
                terminate=False
                #add the cube to extended cubing: looking into file, find corresponding cube index, find the cube
                cube_index=$(grep -m1 ".cubes" $file | grep -oP "(?<=\.cubes)\d+")
                echo $cube_index
                command="sed -n '${cube_index}p' $current_cube_file >> $new_cube_file"
                echo $command
                eval $command
        fi
done

if [ $terminate = True ]; then
        echo "Instance full solved, terminating..."
fi