#!/bin/bash

#set -x

f1=$1 #current cube file
f2=$2 #next cube file
i=$3 #job id
str=""

for f in *slurm-$i*
do
	if grep -q "DUE TO TIME LIMIT" $f
	then
		fileindex=${f#*_}
		index=${fileindex%.*} #Index of the cube needed extension
		index=$((index+1))
		line=$(sed "${index}q;d" $f1)
		cube=$(echo "${line::-2}")
		indices=$(grep -n "$cube" $f2 | cut -f1 -d:)
		IFS=$'\n'
		for ind in $indices
		do
			ind=$((ind-1))
			str="$str$ind,"	
		done
	fi
done
echo ${str::-1}
