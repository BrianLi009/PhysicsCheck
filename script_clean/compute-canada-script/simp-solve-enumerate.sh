#!/bin/bash
i=$1
c=$2
s=$3
x=$(wc -l < $c)
o=$4
#SBATCH --array=0-$x:1
#SBATCH --time=00-00:20
#SBATCH --mem=4G
#SBATCH --account=def-janehowe
./adjoin-cube-simplify.sh $i $c ${SLURM_ARRAY_TASK_ID} $s
./maplesat-ks/simp/maplesat_static "$c""${SLURM_ARRAY_TASK_ID}".adj.simp -no-pre -exhaustive="$o".exhaust -order=$o
