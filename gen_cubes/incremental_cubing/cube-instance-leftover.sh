#!/bin/bash

# Ensure necessary parameters are provided on the command-line
if [ -z $5 ]
then
	echo "Need order, instance filename, number of edge variables to remove, depth, cube index, and optionally a simplification mode parameter"
	exit
fi

n=$1 # Order
f=$2 # Instance filename
d=$3 # name of the current cube
r=$4 # Number of free edge variables to remove
i=$5 # Depth
c=$6 # Cube index
s=$7 # Simplification mode parameter

m=$((n*(n+1)/2)) # Number of edge variables in instance
dir=$n-cubes # Directory to store cubes
logdir=$n-log # Directory to store logs

# Get the c-th cube
cubeline=`head $dir/$d -n $c | tail -n 1`
echo "Processing $cubeline..."

if [ -z $s ] || (( i == 1 ))
then
	# Adjoin the literals in the current cube to the instance and simplify the resulting instance with CaDiCaL
	command="./apply.sh $f $dir/$d $c | ./cadical -o $dir/$d$c.simp -e $dir/$d$c.ext -n -c 10000 > $logdir/$d$c.simp"
	echo $command
	eval $command
else
	# Parent cube
	parentcube=$(echo "$cubeline" | xargs -n 1 | head -n -2 | xargs)

	# Line number of parent cube
	l=$(grep -n "$parentcube" $dir/$((i-2)).cubes | cut -d':' -f1)

	# Adjoin the literals in the current cube to the simplified parent instance and simplify the resulting instance with CaDiCaL
	command="./concat-edge-and-apply.sh $m $dir/$((i-2)).cubes$l.simp $dir/$((i-2)).cubes$l.ext $dir/$d $c | ./cadical -o $dir/$d$c.simp -e $dir/$d$c.ext -n -c 10000 > $logdir/$d$c.simp"
	echo $command
	eval $command

	if [ "$s" == "-b" ]
	then
		# Run MapleSAT for 10000 conflicts and output noncanonical blocking clauses
		rm $dir/$d$c.noncanon 2> /dev/null
		command="./concat-edge.sh $m $dir/$d$c.simp $dir/$d$c.ext | ./maplesat_static -order=$n -exhaustive=$dir/$d$c.exhaust -keep-blocking=2 -noncanonical-out=$dir/$d$c.noncanon -max-conflicts=10000"
		echo $command
		eval $command
		rm $dir/$d$c.exhaust
		printf "Adding %d noncanonical blocking clauses into instance\n" $(wc -l < $dir/$d$c.noncanon)

		# Add noncanonical blocking clauses into simplified instance
		mv $dir/$d$c.simp $dir/$d$c.simp-tmp
		./concat.sh $dir/$d$c.simp-tmp $dir/$d$c.noncanon > $dir/$d$c.simp
		rm $dir/$d$c.simp-tmp
	fi
fi

# Check if simplified instance was unsatisfiable
if grep -q "^0$" $dir/$d$c.simp
then
	removedvars=$m # Instance was unsatisfiable so all variables were removed
else
	# Determine how many edge variables were removed
	removedvars=$(sed -E 's/.* 0 [-]*([0-9]*) 0$/\1/' < $dir/$d$c.ext | awk "\$0<=$m" | sort | uniq | wc -l)
fi

# Check if current cube should be split
if (( removedvars <= r ))
then
	echo "  Depth $i instance $c has $removedvars removed edge variables; splitting..."
	# Split this cube by running march_cu on the simplified instance
	command="./march_cu $dir/$d$c.simp -o $dir/$d$c.cubes -d 1 -m $m | tee $logdir/$d$c.log"
	echo $command
	eval $command
	echo "c Depth $i instance $c has $removedvars removed edge variables" >> $logdir/$d$c.log
	# Adjoin the newly generated cubes to the literals in the current cube
	cubeprefix=`head $dir/$d -n $c | tail -n 1 | sed -E 's/(.*) 0/\1/'`
	sed -E "s/^a (.*)/$cubeprefix \1/" $dir/$d$c.cubes > $dir/$i-$c.cubes
else
	# Current cube should not be split
	echo "  Depth $i instance $c has $removedvars removed edge variables; not splitting"
	head $dir/$d -n $c | tail -n 1 > $dir/$i-$c.cubes
fi
# Delete simplified instance if not needed anymore
if [ -z $s ]
then
	rm $dir/$d$c.simp
fi
