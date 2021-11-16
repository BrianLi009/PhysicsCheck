#!/bin/bash
for i in {0..585..1}
do
	./adjoin-cube-simplify.sh constraints_21_10.simp constraints_21_10.simp5.1476.cubes $i
done
