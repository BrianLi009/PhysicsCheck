#!/bin/bash

[ "$1" = "-h" -o "$1" = "--help" ] && echo "
Description:
    This script takes in an exhaust file with kochen specker candidates, and determine whether each
    of them is embeddable, if it is embeddable, then it will be outputted into a file as a Kochen
    Specker graph. We require the existance of n.exhaust in the directory.

Usage:
    Must be called from the root directory
    ./embedability/check_embedability.sh [-s] [-p] [-v] n f

Options:
    [-s]: check if a graph contains a minimal unembeddable subgraph, if it does, it's not embeddable
    [-p]: applying proposition 1 and skip graph with vertex of degree less than 2
    [-v]: verify satisfiable embeddability result
    <n>: the order of the instance/number of vertices in the graph
    <f>: file to check embedability on
    <s>: optional parameter to specify starting index of f
    <e>: optional parameter to specify ending index of f. If s is provided, e must be provided.
" && exit

while getopts "spv" opt
do
    case $opt in
        s) s="-s" ;;
        p) p="-p" ;;
        v) v="-v" ;;
    esac
done
shift $((OPTIND-1))

if [ -z "$1" ]
then
    echo "Need the order of the instance and file to check embedability on, use -h or --help for further instruction"
    exit
fi

using_subgraph=False
if [ "$s" == "-s" ]
    then
        echo "enabling using minimal nonembeddable subgraph"
        using_subgraph=True
    fi

verify=False
if [ "$v" == "-v" ]
    then
        echo "enable embeddability verification"
        verify=True
    fi

n=$1
f=$2
s=${3:-none}
e=${4:-none}

index=0

touch $f-embeddable.txt
touch $f-nonembeddable.txt

#if $f is empty, nothing to check and exit
if [ ! -s "$f" ]; then
    echo "File $f is empty. No candidate to check. Exiting embedability check..."
    exit 1
fi

python3 embedability/main.py "$f" "$n" "$index" $using_subgraph False $f-nonembeddable.txt $f-embeddable.txt $verify $s $e

noncount=`wc -l "$f-nonembeddable.txt" | awk '{print $1}'`
count=`wc -l "$f-embeddable.txt" | awk '{print $1}'`

echo $noncount nonembeddable candidates
echo $count embeddable candidates


