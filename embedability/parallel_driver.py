import sys
from main import main
import time

"""
Script used to compute embeddability check in parallel by varying the line_index.
order: order of the graph to be solved
line_index: index of the graph to be solved in file_to_solve
file_to_solve: name of the file containing graphs to solve
"""

def solve_by_line(order, line_index, file_to_solve):
    line_index = int(line_index)
    order = int(order)
    f = open(file_to_solve)
    lines = f.readlines()
    line = lines[line_index]
    start_time = time.time()
    main(line, order, 0, False, False, "test_unsat.txt", "test_sat.txt", False, True)
    runtime = time.time() - start_time
    file_object = open('runtime_' + str(order) + '.txt', 'a')
    file_object.write(str(line_index) + ": " + str(runtime) + "\n")
    file_object.close()

if __name__ == "__main__":
	solve_by_line(sys.argv[1], sys.argv[2], sys.argv[3])
