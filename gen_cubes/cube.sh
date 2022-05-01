#!/bin/bash

# Process options
while getopts "apsb" opt
do
	case $opt in
		a) a="-a" ;;
		p) p="-p" ;;
		s) s="-s" ;;
		b) s="-b" ;;
	esac
done
shift $((OPTIND-1))

# Ensure necessary parameters are provided on the command-line
if [ -z $3 ]
then
	echo "Need order, filename, and number of variables to be removed in every cube (and optionally the depth to start and end at)"
	echo "Usage: $0 [-a] [-p] [-s] [-b] n f r [d] [e]"
	echo "  n is the instance order"
	echo "  f is the instance filename"
	echo "  r is the number of edge variables to remove from each cube before splitting stops"
	echo "  d is the starting depth (generate d.cubes assuming (d-1).cubes is already generated)"
	echo "  e is the ending depth"
	echo "Options:"
	echo "  -a always check # of free edge variables at the starting depth (instead of skipping instances not split at the previous depth)"
	echo "  -p run cubing in parallel"
	echo "  -s apply CaDiCaL on the instances simplified on the previous depth"
	echo "  -b apply noncanonical clauses to simplified instance (implies -s)"
	exit
fi

n=$1 # Order
f=$2 # Instance filename
r=$3 # Number of free edge variables to remove
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

# Get ending depth
if [ -z $5 ]
then
	# Default finish depth is maximum possible
	e=$((n*(n-1)/2))
else
	e=$5
fi

# Solve initial depth if d is 0 and the top-level cube file doesn't exist
if [ "$d" == "0" ]
then
	if [ ! -s $dir/0.cubes ]
	then
		command="./gen_cubes/march_cu/march_cu $f -o $dir/0.cubes -d 1 -m $m | tee $logdir/0.log"
		echo $command
		eval $command
	fi
	d=1
fi

# Solve depths d to e
for i in $(seq $d $e)
do
	if [ ! -f $dir/$((i-1)).cubes ]
	then
		echo "$dir/$((i-1)).cubes doesn't exist; stopping"
		break
	fi

	# Clear cube/commands files at depth i if it already exists
	rm $dir/$i.cubes 2> /dev/null
	rm $dir/$i.commands 2> /dev/null

	# Number of cubes at the previous depth
	numcubes=`wc -l < $dir/$((i-1)).cubes`
	echo "$numcubes cubes in $dir/$((i-1)).cubes"

	# Generate a new instance for every cube generated from the previous depth
	for c in `seq 1 $numcubes`
	do
		# Get the c-th cube
		cubeline=`head $dir/$((i-1)).cubes -n $c | tail -n 1`

		# Skip processing this cube entirely if it was not split on the previous depth (can be turned off with -a; ignore option when i > d)
		if ([ "$a" != "-a" ] || (( i > d ))) && grep -q "$cubeline" $dir/$((i-2)).cubes 2> /dev/null
		then
			if [ "$s" == "-s" ]
			then
				# Line number of parent cube
				l=$(grep -n "$cubeline" $dir/$((i-2)).cubes | cut -d':' -f1)
				# Update location of simplified instance
				cp $dir/$((i-2)).cubes$l.ext $dir/$((i-1)).cubes$c.ext
				cp $dir/$((i-2)).cubes$l.simp $dir/$((i-1)).cubes$c.simp
			fi
			echo "  Depth $i instance $c was not split at previous depth; skipping"
			head $dir/$((i-1)).cubes -n $c | tail -n 1 > $dir/$i-$c.cubes
			continue
		fi

		command="./gen_cubes/cube-instance.sh $n $f $r $i $c $s"
		echo $command >> $dir/$i.commands
		if [ "$p" != "-p" ]
		then
			eval $command
		fi
	done
	if [ "$p" == "-p" ]
	then
		parallel --will-cite < $dir/$i.commands
	fi
	for c in `seq 1 $numcubes`
	do
		cat $dir/$i-$c.cubes >> $dir/$i.cubes
	done
	rm $dir/$i-*.cubes

	# Remove unnecessary files
	rm $dir/$i.commands 2> /dev/null
	rm $dir/$i-*.cubes 2> /dev/null
	rm $dir/$((i-1)).cubes*.cubes 2> /dev/null
	rm $dir/$((i-2)).cubes*.ext 2> /dev/null
	rm $dir/$((i-2)).cubes*.simp 2> /dev/null

	# Stop cubing when no additional cubes have been generated
	if [ "$(wc -l < $dir/$((i-1)).cubes)" == "$(wc -l < $dir/$i.cubes)" ]
	then
		break
	fi
done
