#verify then generate more cubes into a file, then redirect back to pipeline-1.sh
d=$1 #directory of log file to verify
c=$2 #initial cube file

set -x

#./verify.sh $d

for f in $d/*.out
do
if grep -q "DUE TO TIME LIMIT" $f
then
	fileindex=${f#*_}
	index=${fileindex%.*} #Index of the cube needed extending
	index=$((index+1))
	line=$(sed "${index}q;d" $c)
	cube=$(echo "${line::-2}")
	echo $cube >> $c-tocube.cubes 
fi
done
echo "output remaining cubes to $c-tocube.cubes"
