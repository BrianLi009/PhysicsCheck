#!/bin/bash
#SBATCH --account=def-vganesh
#SBATCH --time=50:00:00
#SBATCH --mem-per-cpu=10G

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
o=${4:-c} #simplification option, option "c" means simplifying for t conflicts, option "v" means simplify until t% of variables are eliminated
t=${5:-100000} #conflicts for which to simplify each time CaDiCal is called, or % of variables to eliminate
s=${6:-2} #by default we only simplify the instance using CaDiCaL after adding noncanonical blocking clauses
b=${7:-2} #by default we generate noncanonical blocking clauses in real time
r=${8:-0} #number of variables to eliminate until the cubing terminates

./main.sh $d $n $p $q $o $t $s $b $r
