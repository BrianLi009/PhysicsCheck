#!/bin/bash
#SBATCH --account=def-vganesh
#SBATCH --time=1:00:00
#SBATCH --mem-per-cpu=4G


n=$1
p=$2
q=$3

for i in $( eval echo {4..$n} )
do
        logfile=constraints_${i}_${p}_${q}_c_100000_2_2_0_final.simp.log
        time=$(grep "CPU time" "$logfile" | grep -oP '\d+\.\d+')
        echo $i $time >> results_${p}_${q}.log
done

