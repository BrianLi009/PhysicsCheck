#!/bin/bash
#SBATCH --account=def-vganesh
#SBATCH --time=05:00:00
#SBATCH --mem-per-cpu=4G

awk '{s+=$1} END {print s}' simp_times.log 
