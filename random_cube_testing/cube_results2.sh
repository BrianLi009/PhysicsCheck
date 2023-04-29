#!/bin/sh
#SBATCH --account=def-vganesh
#SBATCH --time=00:10:00
#SBATCH --mem-per-cpu=4G

#array size is number of cubes
n=$1
p=$2
q=$3
f=$4
for i in {0..1000}
do
	runtime=$(grep 'CPU' ./c_c_solves/result_${n}_${p}_${q}_${i} | cut -f2 -d:)
	result=$(tail -2 ./c_c_solves/result_${n}_${p}_${q}_${i} )
	echo $i $runtime $result >> ./cubing_result2_old_${n}_${p}_${q}.log
done
