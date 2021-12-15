#!/bin/bash
n=$1 # Order
f=$1 #Instance filename
r=$3
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

if [ "$d" == "0" ]
then
        if [ ! -s $dir/0.cubes ]
        then
                command="./CnC/march_cu/march_cu $f -o $dir/0.cubes -d 1 -m $m | tee $logdir/0.log"
                echo "#!/bin/bash" > "$n"."$d".sh
                echo "#SBATCH --account=def-janehowe" >> "$n"."$d".sh
                echo "#SBATCH --time=00-01:00" >> "$n"."$d".sh
                echo "#SBATCH --mem=1G" >> "$n"."$d".sh
                echo command >> "$n"."$d".sh
                echo "./dnc.sh "$n" "$f" "$r" "$d+1" " >> "$n"."$d".sh
                sbatch "$n"."$d".sh
        fi
else
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
                echo "#!/bin/bash" > "$n"."$d".sh
                echo "#SBATCH --account=def-janehowe" >> "$n"."$d".sh
                echo "#SBATCH --time=00-01:00" >> "$n"."$d".sh
                echo "#SBATCH --mem=1G" >> "$n"."$d".sh
		echo "./apply.sh $f $dir/$((i-1)).cubes $c | ./cadical -q -o $dir/$((i-1)).cubes$c.simp -e $dir/$((i-1)).cubes$c.ext -n -c 20000" >> "$n"."$d".sh
                echo "if grep -q "^0$" $dir/$((i-1)).cubes$c.simp" >> "$n"."$d".sh
                echo "then" >> "$n"."$d".sh
                echo "removedvars=$m" >> "$n"."$d".sh
                echo "else" >> "$n"."$d".sh
                echo "removedvars=$(sed -E 's/.* 0 [-]*([0-9]*) 0$/\1/' < $dir/$((i-1)).cubes$c.ext | awk "\$0<=$m" | sort | uniq | wc -l) " >> "$n"."$d".sh
                echo "fi " >> "$n"."$d".sh
                echo "if (( removedvars <= r )) " >> "$n"."$d".sh
                echo "then " >> "$n"."$d".sh
                echo "./march_cu $dir/$((i-1)).cubes$c.simp -o $dir/$((i-1)).cubes$c.cubes -d 1 -m $m | tee $logdir/$((i-1)).cubes$c.log " >> "$n"."$d".sh
                echo "cubeprefix=`head $dir/$((i-1)).cubes -n $c | tail -n 1 | sed -E 's/(.*) 0/\1/'` " >> "$n"."$d".sh
                echo "sed -E "s/^a (.*)/$cubeprefix \1/" $dir/$((i-1)).cubes$c.cubes >> $dir/$i.cubes " >> "$n"."$d".sh
                echo "else " >> "$n"."$d".sh
                echo "head $dir/$((i-1)).cubes -n $c | tail -n 1 >> $dir/$i.cubes " >> "$n"."$d".sh
                echo "fi " >> "$n"."$d".sh
                echo "./dnc.sh "$n" "$f" "$r" "$d+1" " >> "$n"."$d".sh
                sbatch "$n"."$d".sh