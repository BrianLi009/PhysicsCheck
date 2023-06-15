#!/bin/sh

[ "$1" = "-h" -o "$1" = "--help" -o "$#" -ne 3 ] && echo "
Description:
    A helper script to append string to file

Usage:
    ./append old_file_name new_file_name string
" && exit

old_f=$1
new_f=$2
string=$3

echo $string > $new_f;
cat $old_f >> $new_f;
mv $new_f $old_f
