from main import main_single_graph
from itertools import islice

def solve_range(n, start, end, file_to_solve, using_subgraph, normalize, output_unsat_f, output_sat_f):
    """
    example for calling this function:
    solve_range(19, 2, 6, "embedability/19.exhaust", "False", "False", "unsat_19.out", "sat_19.out")
    """
    with open(file_to_solve, 'r') as f:
    # Skip the lines before start
        start_line = start
        for _ in range(start_line):
            next(f)
        # Read the next end-start lines
        num_lines = end-start
        for line in islice(f, num_lines):
            print (line)
            main_single_graph(line, n, 0, using_subgraph, normalize, output_unsat_f, output_sat_f, verify="False")