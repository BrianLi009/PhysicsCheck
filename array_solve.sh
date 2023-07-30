#!/bin/bash
#SBATCH --account=def-vganesh
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=4G
#SBATCH --array=25-36
#SBATCH --constraint=broadwell

n=$1 #order
p=$2
q=$3
t=${4:-100000} #conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate
s=${5:-2} #by default we only simplify the instance using CaDiCaL after adding noncanonical blocking clauses
b=${6:-2} #by default we generate noncanonical blocking clauses in real time
r=${7:-0} #number of variables to eliminate until the cubing terminates
a=${8:-10}
lower=${9:-0}
upper=${10:-0}

echo "lower" $((SLURM_ARRAY_TASK_ID - 25))
./main.sh $SLURM_ARRAY_TASK_ID $p $q $o $t $s $b $r $((SLURM_ARRAY_TASK_ID - 25)) 17
