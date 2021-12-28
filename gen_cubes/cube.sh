#!/bin/bash

# Ensure necessary parameters are provided on the command-line
if [ -z $3 ]
then
	echo "Need order, filename, and number of variables to be removed in every cube (and optionally the depth to start and end at)"
	echo "Usage: $0 [-a] n f r [d] [e]"
	echo "  n is the instance order"
	echo "  f is the instance filename"
	echo "  r is the number of edge variables to remove from each cube before splitting stops"
	echo "  d is the starting depth"
	echo "  e is the ending depth"
	echo "Options:"
	echo "  -a always check # of free edge variables instead of skipping instances not split at the previous depth"
	exit
fi

# Process options
while getopts "a" opt
do
	case $opt in
		a) a="-a" ;;
	esac
done
shift $((OPTIND-1))

n=$1 # Order
f=$2 # Instance filename
r=$3 # Number of free edge variables to remove
m=$((n*(n+1)/2)) # Number of edge variables in instance
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

# Get ending depth
if [ -z $5 ]
then
	# Default finish depth is maximum possible
	e=$((n*(n+1)/2))
else
	e=$5
fi

# Solve initial depth if d is 0 and the top-level cube file doesn't exist
if [ "$d" == "0" ]
then
	if [ ! -s $dir/0.cubes ]
	then
		command="./march_cu $f -o $dir/0.cubes -d 1 -m $m | tee $logdir/0.log"
		echo $command
		eval $command
	fi
	d=1
fi

# Solve depths d to e
for i in $(seq $d $e)
do
	# Clear cube file at depth i if it already exists
	rm $dir/$i.cubes 2> /dev/null

	# Number of cubes at the previous depth
	numcubes=`wc -l < $dir/$((i-1)).cubes`

	# Generate a new instance for every cube generated from the previous depth
	for c in `seq 1 $numcubes`
	do
		# Get the c-th cube
		cubeline=`head $dir/$((i-1)).cubes -n $c | tail -n 1`
		echo "Processing $cubeline..."

		# Skip processing this cube entirely if it was not split on the previous depth (can be turned off with -a)
		if [ "$a" != "-a" ] && grep -q "$cubeline" $dir/$((i-2)).cubes 2> /dev/null
		then
			echo "  Depth $i instance $c was not split at previous depth; skipping"
			head $dir/$((i-1)).cubes -n $c | tail -n 1 >> $dir/$i.cubes
			continue
		fi

		# Adjoin the literals in the current cube to the instance and simplify the resulting instance with CaDiCaL
		./apply.sh $f $dir/$((i-1)).cubes $c | ./cadical -q -o $dir/$((i-1)).cubes$c.simp -e $dir/$((i-1)).cubes$c.ext -n -c 20000

		# Check if simplified instance was unsatisfiable
		if grep -q "^0$" $dir/$((i-1)).cubes$c.simp
		then
			removedvars=$m # Instance was unsatisfiable so all variables were removed
		else
			# Determine how many edge variables were removed
			removedvars=$(sed -E 's/.* 0 [-]*([0-9]*) 0$/\1/' < $dir/$((i-1)).cubes$c.ext | awk "\$0<=$m" | sort | uniq | wc -l)
		fi

		# Check if current cube should be split
		if (( removedvars <= r ))
		then
			echo "  Depth $i instance $c has $removedvars removed edge variables; splitting..."
			# Split this cube by running march_cu on the simplified instance
			command="./march_cu $dir/$((i-1)).cubes$c.simp -o $dir/$((i-1)).cubes$c.cubes -d 1 -m $m | tee $logdir/$((i-1)).cubes$c.log"
			echo $command
			eval $command
			# Adjoin the newly generated cubes to the literals in the current cube
			cubeprefix=`head $dir/$((i-1)).cubes -n $c | tail -n 1 | sed -E 's/(.*) 0/\1/'`
			sed -E "s/^a (.*)/$cubeprefix \1/" $dir/$((i-1)).cubes$c.cubes >> $dir/$i.cubes
		else
			# Current cube should not be split
			echo "  Depth $i instance $c has $removedvars removed edge variables; not splitting"
			head $dir/$((i-1)).cubes -n $c | tail -n 1 >> $dir/$i.cubes
		fi
	done

	# Stop cubing when no additional cubes have been generated
	if [ "$(wc -l < $dir/$((i-1)).cubes)" == "$(wc -l < $dir/$i.cubes)" ]
	then
		break
	fi
done
