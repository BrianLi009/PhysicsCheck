#!/bin/bash
#SBATCH --account=def-vganesh
#SBATCH --time=2:00:00
#SBATCH --mem-per-cpu=2G


start_d=$1 #directory to get times for
n=$2
v=$3
a=$4



times=()

function real_time () {
        local d=$1 #local of current directory to get times for
        local t=$2 #local of time spent so far to get to this node on cubing tree
        n=$3
        local current_var_eliminated=$4
        increment=$5

        cube_folder=$(echo "$d" | sed 's|\(.*\)/.*|\1|')
        echo $cube_folder

        cube_time=$(grep -r 'time' $cube_folder/${current_var_eliminated}/${n}-log/*.log | cut -f4 -d ' ' | awk '{s+=$1} END {print s}' )
        #echo "cube" $cubetime


        #need to account for simp timessss somewhere
        #and cube times
        for logfile in $d/*.log
        do

        if grep -qE 'SATISFIABLE|UNSATISFIABLE' $logfile;then
                solve_time=$(grep "CPU time" "$logfile" | cut -f2 -d: | head -c -2) #using different format here as '0 s' wa giving issue if solved by simp
                simptime=$(grep "c total process time since initialization" "$logfile" | grep -oP '\d+\.\d+')

                #echo "s" $solve_time "t" $t $logfile
                times+=($(echo "$solve_time + $simptime + $t + $cube_time" | bc))
                #echo "end"
        else

                simptime=$(grep "c total process time since initialization" "$logfile" | grep -oP '\d+\.\d+')
                solve_time=$(grep "CPU time" "$logfile" | grep -oP '\d+\.\d+')
                #echo 2 "s" $solve_time "t" $t $logfile

                new_time=$(echo "$solve_time + $simptime + $t + $cube_time" | bc)


                index=$(echo "$logfile" | grep -oP '(?<=/)\d+(?=-solve\.log)')
                result="$current_var_eliminated-$index"
                new_var_to_cube=$(echo "$current_var_eliminated + $increment" | bc)
                dir="${d%%/$current_var_eliminated*}"
                new_dir=$dir/$result/$new_var_to_cube/$n-solve

                #echo $new_dir
                ###if ERROR: if there was a addition error, $new_time is often NULL, which affects the below call
                command="real_time $new_dir $new_time $n $new_var_to_cube $increment"
                #echo $command
                eval $command

        fi
        done

}


directory=$start_d/$v/$n-solve
real_time "$directory" 0 $n $v $a
echo $times
echo "${times[*]}" | sort -nr | head -n1

 
