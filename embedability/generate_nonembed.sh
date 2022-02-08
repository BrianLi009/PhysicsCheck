#!/bin/bash

#set -x

if cd nauty27r3
then
	echo "nauty installed"
else
	wget https://pallini.di.uniroma1.it/nauty27r3.tar.gz
	tar xvzf nauty27r3.tar.gz
	./configure && make
fi

cd -

if [ ! -f order_10.out ]
then
	./nauty27r3/geng -Cf -h -l 10 order_10.out
fi

if [ ! -f order_11.out ]
then
	./nauty27r3/geng -Cf -h -l 11 order_11.out
fi

if [ ! -f order_12.out ]
then
	./nauty27r3/geng -Cf -h -l 12 order_12.out
fi

#check embedability of each graph

touch embed_result_g6.txt

for o in 10 11 12
do
	sed -i 's/>>graph6<<//g' order_$o.out
	while read -r str
	do
  		index=0
    	while ! grep -Fq "  $str  " embed_result_g6.txt; do
        	python3 main_g6.py "$str" $index
        	if ! grep -Fq "  $str  " embed_result_g6.txt; then
            	timeout 10 python3 test.py
        	fi
        	index=$((index+1))
    	done
	done <order_$o.out
done