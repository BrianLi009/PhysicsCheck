#!/bin/bash
n=$1 #order

if [ -f constraints_$n ]
then
    echo "instance already generated"
else
    python3 gen_instance/generate.py $n #generate the instance of order n
fi