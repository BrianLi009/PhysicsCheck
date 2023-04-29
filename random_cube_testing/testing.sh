#!/bin/bash
#SBATCH --account=def-vganesh
#SBATCH --time=00:30:00
#SBATCH --mem-per-cpu=2G

n=$1 #order
f=$2 #folder name

dir=$f
echo $dir

for logfile in $dir/${n}-solve/*-solve.simplog; do
# Extract simptime from current logfile and add it to the total
	time=$(grep "total process time since initialization" "$logfile" | cut -d' ' -f15)
        #cube_num=${$logfile%-*}
	#echo $cube_num $time
	echo $logfile $time >> ${dir}/times.log
done
echo "solve times" >> $dir/times.log
for logfile in $dir/${n}-solve/*-solve.log; do
# Extract simptime from current logfile and add it to the total
        time=$(grep "CPU time" "$logfile" | cut -b 25-32)
        #cube_num=${$logfile%-*}
        #echo $cube_num $time
        echo $logfile $time >> ${dir}/times.log
done
~

