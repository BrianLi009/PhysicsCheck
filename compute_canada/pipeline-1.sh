i=$1 #input instance file
c=$2 #cubing fuke

set -x

echo "#!/bin/bash" > simplify-$i-$c
numline=$(< "$c" wc -l)
index=$((numline-1))
echo "#SBATCH --array=0-${index}" >> simplify-$i-$c
echo "#SBATCH --time=01:00:00" >> simplify-$i-$c
echo "#SBATCH --account=def-janehowe" >> simplify-$i-$c
echo "#SBATCH --mem-per-cpu=4G" >> simplify-$i-$c
echo "./adjoin-cube-simplify.sh $i $c \$SLURM_ARRAY_TASK_ID 70" >> simplify-$i-$c

sbatch simplify-$i-$c #compute canada execute adjoin and simplification
