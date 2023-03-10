#!/bin/bash
n=$1
p=$2
q=$3
v=$4
c=$5

#Part of CNF file creation
#v= total num var in cnf file
#c= total num constraints in cnf file

echo "p cnf ${v} ${c}" > ./temp_head_${n}_${p}_${q} #create cnf file and header
cat ./temp_head_${n}_${p}_${q} ./constraints_temp_${n}_${p}_${q} > ./constraints_${n}_${p}_${q} #write constraints in temp_n_p_q to constraints

rm constraints_temp_${n}_${p}_${q}
rm temp_head_${n}_${p}_${q}
