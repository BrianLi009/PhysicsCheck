#!/bin/bash

set -x 
n=$1 #order
r=$2 #number of variables to eliminate
f=$3 #instance file name


./gen_cubes/cube.sh $n $f $r #cube till r varaibles are eliminated

#find the deepest cube file
cube_file=$(find . -type f -wholename "./$n-cubes/*.cubes" -exec grep -H -c '[^[:space:]]' {} \; | sort -nr -t":" -k2 | awk -F: '{print $1; exit;}')

cp $(echo $cube_file) .

cube_file=$(echo $cube_file | sed 's:.*/::')

numline=$(< $cube_file wc -l)
new_index=$((numline-1))
for i in $(seq 0 $new_index)
do 
    ./adjoin-cube-simplify.sh $f $cube_file $i 50
    #join the cube to the instance, simplified until 50% of the variables are eliminated
    ./maplesat-ks/simp/maplesat_static $cube_file$i.adj.simp -no-pre -exhaustive=$n.exhaust -order=$n
done