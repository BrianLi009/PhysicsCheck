#!/bin/bash
n=$1 # Order
f=$2 #Instance filename
r=$3 #number of free variables to remove
m=$((n*(n-1)/2)) # Number of edge variables in instance
dir=$n-cubes # Directory to store cubes
logdir=$n-log # Directory to store logs
mkdir -p $dir
mkdir -p $logdir

# Check that instance exists
if [ ! -s $f ]
then
	echo "File $f must exist and be nonempty"
	exit
fi

# Get starting depth
if [ -z $4 ]
then
	# Start from depth 0 by default
	d=0
else
	d=$4
fi

if [ "$d" == "0" ]
then
	if [ ! -s $dir/0.cubes ]
	then
		echo "#!/bin/bash" > "$n"."$d".sh
		echo "#SBATCH --account=def-janehowe" >> "$n"."$d".sh
		echo "#SBATCH --time=00:03:00" >> "$n"."$d".sh
		echo "#SBATCH --mem=1G" >> "$n"."$d".sh
		echo ""./CnC/march_cu/march_cu $f -o $dir/0.cubes -d 1 -m $m | tee $logdir/0.log" " >> "$n"."$d".sh
		echo "./dnc.sh "$n" "$f" "$r" "$((d+1))" " >> "$n"."$d".sh
		sbatch "$n"."$d".sh
	fi
else
	# Clear cube file at depth i if it already exists
	rm $dir/$d.cubes 2> /dev/null

	# Number of cubes at the previous depth
	numcubes=`wc -l < $dir/$((d-1)).cubes`
	# Generate a new instance for every cube generated from the previous depth
	for c in `seq 1 $numcubes`
	do
		# Get the c-th cube
		cubeline=`head $dir/$((d-1)).cubes -n $c | tail -n 1`
		echo "Processing $cubeline..."

		# Skip processing this cube entirely if it was not split on the previous depth (can be turned off with -a)
		if [ "$a" != "-a" ] && grep -q "$cubeline" $dir/$((d-2)).cubes 2> /dev/null
		then
			echo "  Depth $i instance $c was not split at previous depth; skipping"
			head $dir/$((d-1)).cubes -n $c | tail -n 1 >> $dir/$d.cubes															   
			continue
		fi
		echo "#!/bin/bash" > "$n"."$d"."$c".sh
		echo "#SBATCH --account=def-janehowe" >> "$n"."$d"."$c".sh
		echo "#SBATCH --time=00:03:00" >> "$n"."$d"."$c".sh
		echo "#SBATCH --mem=1G" >> "$n"."$d"."$c".sh
		echo "./apply.sh $f $dir/$((d-1)).cubes $c | ./cadical/build/cadical -q -o $dir/$((d-1)).cubes$c.simp -e $dir/$((d-1)).cubes$c.ext -n -c 20000" >> "$n"."$d"."$c".sh
		echo "if grep -q \"^0\$\" $dir/$((d-1)).cubes$c.simp" >> "$n"."$d"."$c".sh
		echo "then" >> "$n"."$d"."$c".sh
		echo "removedvars=$m" >> "$n"."$d"."$c".sh
		echo "else" >> "$n"."$d"."$c".sh
		echo "removedvars=\$(sed -E 's/.* 0 [-]*([0-9]*) 0\$/\1/' < $dir/$((d-1)).cubes$c.ext | awk \"\\\$0<=$m\" | sort | uniq | wc -l)" >> "$n"."$d"."$c".sh
		echo "fi " >> "$n"."$d"."$c".sh
		echo "if (( removedvars <= $r )) " >> "$n"."$d"."$c".sh
		echo "then " >> "$n"."$d"."$c".sh
		echo "./CnC/march_cu/march_cu $dir/$((d-1)).cubes$c.simp -o $dir/$((d-1)).cubes$c.cubes -d 1 -m $m | tee $logdir/$((d-1)).cubes$c.log " >> "$n"."$d"."$c".sh
		echo "chmod u+r+x $dir/$((d-1)).cubes" >> "$n"."$d"."$c".sh
		echo "cubeprefix=\`head $dir/$((d-1)).cubes -n $c | tail -n 1 | sed -E 's/(.*) 0/\\1/'\`" >> "$n"."$d"."$c".sh
		echo "sed -E \"s/^a (.*)/"\$cubeprefix" \1/\" $dir/$((d-1)).cubes$c.cubes >> $dir/$d.cubes " >> "$n"."$d"."$c".sh
		echo "else " >> "$n"."$d"."$c".sh
		echo "head $dir/$((d-1)).cubes -n $c | tail -n 1 >> $dir/$d.cubes " >> "$n"."$d"."$c".sh
		echo "fi" >> "$n"."$d"."$c".sh
		echo "awk -i inplace '!seen[\$0]++' $dir/$d.cubes" >> "$n"."$d"."$c".sh
		if [ "$d" == "10" ]
		then
			continue
		else
			echo "./dnc.sh "$n" "$f" "$r"  "$((d+1))" " >> "$n"."$d"."$c".sh
		fi
		sbatch "$n"."$d"."$c".sh
	done
fi
