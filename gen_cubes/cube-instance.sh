#!/bin/bash

# Ensure necessary parameters are provided on the command-line
if [ -z $5 ]
then
	echo "Need order, instance filename, number of edge variables to remove, depth, cube index, and optionally a simplification mode parameter"
	exit
fi

n=$1 # Order
f=$2 # Instance filename
r=$3 # Number of free edge variables to remove
i=$4 # Depth
c=$5 # Cube index
s=$6 # Simplification mode parameter

m=$((n*(n-1)/2)) # Number of edge variables in instance
dir=$n-cubes # Directory to store cubes
logdir=$n-log # Directory to store logs

# Get the c-th cube
cubeline=`head $dir/$((i-1)).cubes -n $c | tail -n 1`
echo "Processing $cubeline..."

# Check if no simplification mode (or mode -m) or at initial depth
if [ -z $s ] || [ "$s" == "-m" ] || (( i == 1 ))
then
	# Adjoin the literals in the current cube to the instance and simplify the resulting instance with CaDiCaL
	command="./gen_cubes/apply.sh $f $dir/$((i-1)).cubes $c | ./cadical/build/cadical -o $dir/$((i-1)).cubes$c.simp -e $dir/$((i-1)).cubes$c.ext -n -c 10000 > $logdir/$((i-1)).cubes$c.simp"
	echo $command
	eval $command

	if [ "$s" == "-m" ]
	then
		# Run MapleSAT for 10000 conflicts to check if unsatisfiability can be discovered
		command="./gen_cubes/concat-edge.sh $m $dir/$((i-1)).cubes$c.simp $dir/$((i-1)).cubes$c.ext | ./maplesat-ks/simp/maplesat_static -order=$n -max-conflicts=10000 -noncanonical-out=$dir/$((i-1)).cubes$c.noncanon > $logdir/$((i-1)).cubes$c.mslog"
		echo $command
		eval $command
		if grep -q "UNSATISFIABLE" $logdir/$((i-1)).cubes$c.mslog
		then
			echo "Instance was determined to be unsatisfiable by MapleSAT"
			# If MapleSAT determines there are no solutions make the instance trivially unsatisfiable
			echo "0" >> $dir/$((i-1)).cubes$c.simp
		else
			printf "Adding %d noncanonical blocking clauses into instance\n" $(wc -l < $dir/$((i-1)).cubes$c.noncanon)
			# Add noncanonical blocking clauses into simplified instance
			mv $dir/$((i-1)).cubes$c.simp $dir/$((i-1)).cubes$c.simp-tmp
			./gen_cubes/concat.sh $dir/$((i-1)).cubes$c.simp-tmp $dir/$((i-1)).cubes$c.noncanon > $dir/$((i-1)).cubes$c.simp
			rm $dir/$((i-1)).cubes$c.simp-tmp
		fi
	fi
# Check if current cube appears in previous list of cubes
elif grep -q "$cubeline" $dir/$((i-2)).cubes
then
	# Line number of current cube in previous list of cubes
	l=$(grep -n "$cubeline" $dir/$((i-2)).cubes | cut -d':' -f1)

	cp $dir/$((i-2)).cubes$l.simp $dir/$((i-1)).cubes$c.simp
	cp $dir/$((i-2)).cubes$l.ext $dir/$((i-1)).cubes$c.ext
else
	# Parent cube
	parentcube=$(echo "$cubeline" | xargs -n 1 | head -n -2 | xargs)

	# Line number of parent cube
	l=$(grep -n "$parentcube" $dir/$((i-2)).cubes | cut -d':' -f1)

	# Adjoin the literals in the current cube to the simplified parent instance and simplify the resulting instance with CaDiCaL
	command="./gen_cubes/concat-edge-and-apply.sh $n $dir/$((i-2)).cubes$l.simp $dir/$((i-2)).cubes$l.ext $dir/$((i-1)).cubes $c | ./cadical/build/cadical -o $dir/$((i-1)).cubes$c.simp -e $dir/$((i-1)).cubes$c.ext -n -c 10000 > $logdir/$((i-1)).cubes$c.simp"
	echo $command
	eval $command

	if [ "$s" == "-b" ]
	then
		# Run MapleSAT for 10000 conflicts and output noncanonical blocking clauses
		rm $dir/$((i-1)).cubes$c.noncanon 2> /dev/null
		command="./gen_cubes/concat-edge.sh $m $dir/$((i-1)).cubes$c.simp $dir/$((i-1)).cubes$c.ext | ./maplesat-ks/simp/maplesat_static -order=$n -exhaustive=$dir/$((i-1)).cubes$c.exhaust -keep-blocking=2 -noncanonical-out=$dir/$((i-1)).cubes$c.noncanon -max-conflicts=10000 > $logdir/$((i-1)).cubes$c.ncgen"
		echo $command
		eval $command
		printf "Adding %d noncanonical blocking clauses into instance\n" $(wc -l < $dir/$((i-1)).cubes$c.noncanon)
		if grep -q "UNSATISFIABLE" $logdir/$((i-1)).cubes$c.ncgen
		then
			numsols=$(wc -l < $dir/$((i-1)).cubes$c.exhaust)
			echo "Instance was determined to have ${numsols} solutions by MapleSAT"
			# If MapleSAT determines there are no solutions make the instance trivially unsatisfiable
			if [ $numsols -eq 0 ]
			then
				echo "0" >> $dir/$((i-1)).cubes$c.simp
			fi
		fi
		rm $dir/$((i-1)).cubes$c.exhaust

		# Add noncanonical blocking clauses into simplified instance
		mv $dir/$((i-1)).cubes$c.simp $dir/$((i-1)).cubes$c.simp-tmp
		./gen_cubes/concat.sh $dir/$((i-1)).cubes$c.simp-tmp $dir/$((i-1)).cubes$c.noncanon > $dir/$((i-1)).cubes$c.simp
		rm $dir/$((i-1)).cubes$c.simp-tmp
	fi
fi

# Check if simplified instance was unsatisfiable
if grep -q "^0$" $dir/$((i-1)).cubes$c.simp
then
	removedvars=$m # Instance was unsatisfiable so all variables were removed
	echo "  Depth $i instance $c was shown to be UNSAT; skipping"
	head $dir/$((i-1)).cubes -n $c | tail -n 1 > $dir/$i-$c.cubes
	sed 's/a/u/' $dir/$i-$c.cubes -i # Mark cubes that have been shown to be unsatisfiable with 'u'
	unsat=1
else
	# Determine how many edge variables were removed
	removedvars=$(sed -E 's/.* 0 [-]*([0-9]*) 0$/\1/' < $dir/$((i-1)).cubes$c.ext | awk "\$0<=$m" | sort | uniq | wc -l)
fi

# Check if current cube should be split
if (( removedvars <= r ))
then
	echo "  Depth $i instance $c has $removedvars removed edge variables; splitting..."
	# Split this cube by running march_cu on the simplified instance
	command="./gen_cubes/march_cu/march_cu $dir/$((i-1)).cubes$c.simp -o $dir/$((i-1)).cubes$c.cubes -d 1 -m $m | tee $logdir/$((i-1)).cubes$c.log"
	echo $command
	eval $command
	echo "c Depth $i instance $c has $removedvars removed edge variables" >> $logdir/$((i-1)).cubes$c.log
	# Adjoin the newly generated cubes to the literals in the current cube
	cubeprefix=`head $dir/$((i-1)).cubes -n $c | tail -n 1 | sed -E 's/(.*) 0/\1/'`
	sed -E "s/^a (.*)/$cubeprefix \1/" $dir/$((i-1)).cubes$c.cubes > $dir/$i-$c.cubes
elif [ -z $unsat ]
then
	# Current cube should not be split
	echo "  Depth $i instance $c has $removedvars removed edge variables; not splitting"
	head $dir/$((i-1)).cubes -n $c | tail -n 1 > $dir/$i-$c.cubes
fi
# Delete simplified instance if not needed anymore
if [ -z $s ] || [ "$s" == "-m" ]
then
	rm $dir/$((i-1)).cubes$c.simp 2> /dev/null
	rm $dir/$((i-1)).cubes$c.ext 2> /dev/null
fi
