o=$1 #order
c=$2 #cubing fuke
t=$3

set -x

echo "#!/bin/bash" > solve-$o-$c
numline=$(< "$c" wc -l)
index=$((numline-1))
echo "#SBATCH --array=0-${index}" >> solve-$o-$c
echo "#SBATCH --time=$t" >> solve-$o-$c
echo "#SBATCH --mem=4G" >> solve-$o-$c
echo "#SBATCH --account=def-janehowe" >> solve-$o-$c
echo "./maplesat-ks/simp/maplesat_static $c\${CLURM_ARRAY_TASK_ID}.adj.simp -no-pre -exhaustive=$o.exhaust - order=$o" >> solve-$o-$c

sbatch solve-$o-$c
