import sys
import os
from subprocess import call
import time
def solve_line(n, line_index, file_to_solve):
    line_index = int(line_index)
    n = int(n)
    f = open(file_to_solve)
    lines = f.readlines()
    line = lines[n]
    start_time = time.time()
    call(['python', 'main.py', str(line), n, "0", "False", "False", "test_unsat.txt", "test_sat.txt", "False", "False"])
    runtime = time.time() - start_time
    file_object = open('runtime_' + str(order) + '.txt', 'a')
    file_object.write(str(n) + ": " + str(runtime) + "\n")
    # Close the file
    file_object.close()
    
if __name__ == "__main__":
	solve_by_line(sys.argv[1], sys.argv[2], sys.argv[3])
