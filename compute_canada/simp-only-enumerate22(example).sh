#!/bin/bash
#SBATCH --array=1442-1451
#SBATCH --time=03:00:00
#SBATCH --account=def-janehowe
#SBATCH --mem-per-cpu=8G
./adjoin-cube-simplify.sh constraints_half_22_noncan.simp constraints_22_11.simp5.1728.cubes $SLURM_ARRAY_TASK_ID 70
