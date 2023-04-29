#!/bin/bash
#SBATCH --account=def-vganesh
#SBATCH --time=01:00:00
#SBATCH --mem-per-cpu=4G

n=$1 #order
f=$2 #folder name

dir=$f
echo $dir
solve=$(grep -h 'CPU time' $dir/${n}-solve/*.log | cut -b 25-32 | awk '{s+=$1} END {print s}')
simp=$(grep -h "total process time since initialization" *$dir/${n}-solve/*.simplog | cut -d' ' -f15 | awk '{s+=$1} END {print s}')
	
echo "simp" $simptime
echo "solve" $solve
