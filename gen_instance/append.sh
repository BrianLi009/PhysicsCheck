#!/bin/sh

old_f=$1
new_f=$2
string=$3

echo $string > $new_f;
cat $old_f >> $new_f;
mv $new_f $old_f
