#verify then generate more cubes into a file, then redirect back to pipeline-1.sh
d=$1 #directory of log file to verify
c=$2 #current cubing depth
n=$3 #order

#set -x

#./verify.sh $d

for f in $d/*.out
do
if grep -q "DUE TO TIME LIMIT" $f
then
	fileindex=${f#*_}
	index=${fileindex%.*} #Index of the cube needed extending
	./cube-instance.sh $n constraints_$n 125 
	echo $cube >> $n-cubes/$c-remain.cubes $d $index
fi
done


