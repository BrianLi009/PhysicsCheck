#!/bin/bash
#SBATCH --account=def-vganesh
#SBATCH --time=60:00:00
#SBATCH --mem-per-cpu=4G
#SBATCH --constraint=skylake

while getopts "apsbm" opt
do
    case $opt in
        p) d="-p" ;;
        m) m="-m" ;;
        *) echo "Invalid option: -$OPTARG. Only -p and -m are supported. Use -h or --help for help" >&2
           exit 1 ;;

        esac
done
shift $((OPTIND-1))

n=$1 #order
p=$2
q=$3
t=${4:-100000} #conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate
s=${4:-2} #by default we only simplify the instance using CaDiCaL after adding noncanonical blocking clauses
b=${6:-2} #by default we generate noncanonical blocking clauses in real time
r=${7:-0} #number of variables to eliminate until the cubing terminates
a=${8:-10}
lower=${9:-0}
upper=${10:-0}

./main.sh $d $n $p $q $t $s $b $r $a $lower $upper
