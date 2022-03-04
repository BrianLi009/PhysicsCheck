i=$1 #input instance file
f=$2 #cubing file
o=$3 #instance order
c=$4 #cube depth
sub_dir=$(echo "${f%%/*}")
#set -x
echo "#!/bin/bash" > simp-solve-$i-$c.sh
numline=$(< "$f" wc -l)
index=$((numline-1))
echo "#SBATCH --array=0-${index}" >> simp-solve-$i-$c.sh
echo "#SBATCH --time=72:00:00" >> simp-solve-$i-$c.sh
echo "#SBATCH --account=def-janehowe" >> simp-solve-$i-$c.sh
echo "#SBATCH --mem=4G" >> simp-solve-$i-$c.sh
echo "./adjoin-cube-simplify.sh $i $f \$SLURM_ARRAY_TASK_ID 70" >> simp-solve-$i-$c.sh
echo "if [[ \$(wc -l < $sub_dir/$c.cubes\${SLURM_ARRAY_TASK_ID}.adj.simp) -ge 3 ]]" >> simp-solve-$i-$c.sh
echo "then" >> simp-solve-$i-$c.sh
echo "./maplesat-ks/simp/maplesat_static $sub_dir/$c.cubes\${SLURM_ARRAY_TASK_ID}.adj.simp -no-pre -exhaustive=$o.exhaust -order=$o" >> simp-solve-$i-$c.sh
echo "else" >> simp-solve-$i-$c.sh
echo "echo "UNSATISFIABLE"" >> simp-solve-$i-$c.sh
echo "fi" >> simp-solve-$i-$c.sh
sbatch simp-solve-$i-$c.sh #compute canada execute adjoin and simplification

