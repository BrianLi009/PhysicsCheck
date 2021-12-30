#!/bin/bash

#set -xi

i=$1 # Job ID
sum=0
timeouts=0
completed=0
runtime=0
total_files=0
max_job=0

#computing expected number of solutions
for f in *slurm-$i*
do 	
total_files=$((total_files+1))
if grep -q "Number of solutions" $f
then
	number=( $(grep "Number of solutions"  $f | cut -f2 -d:) )
	sum=$((sum += $number))
fi
if grep -q "DUE TO TIME LIMIT" $f
then
	timeouts=$((timeouts+1)) 
fi
if grep -q "UNSATISFIABLE" $f
then
	completed=$((completed+1))
	job_runtime=( $(grep "CPU time"  $f | cut -f2 -d:) )
	job_runtime=${job_runtime%.*}
	if (( $job_runtime > $max_job ))
		then max_job=$job_runtime
	fi
	runtime=$((runtime += $job_runtime))
fi
done
echo "Expecting $sum Kochen Specker candidates"
echo "$timeouts timeout jobs."
echo "$completed completed jobs."
total_found=$(( $timeouts+$completed))
if (( $total_files == $total_found ))
then
	echo "VERIFIED"
else
	echo "POTENTIAL ERROR"
fi
echo "Total job runtime is $runtime."
echo "Maximum job runtime is $max_job."

