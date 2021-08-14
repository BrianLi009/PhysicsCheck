import itertools
import numpy as np
import pickle
import timeit
from indicate_colorability import *

from pysat.formula import CNF
from pysat.solvers import *


def construct_graph(solution, num_vertices):
    """
    given solution in the solver's format and number of vertices, it outputs a list of edges that can be passed
    into Sage to construct a graph"""
    vertices_lst = list(range(1, num_vertices+1))
    edge_lst = list(itertools.combinations(vertices_lst, 2))
    true_edge_lst = []
    for i in range(len(edge_lst)):
        edge = edge_lst[i]
        if solution[i] > 0:
            true_edge_lst.append(edge)
    return true_edge_lst

def count_1(coloring):
    count = 0
    for i in coloring:
        if i > 0:
            count += 1
    return count

def solve_cnf_pickle(file, num_vertices, solver_type): #example: solver = Lingeling()
    """
    similar to the above function, but instead of returning a list, we directly dump the solution into a file
    solver_type: int
    """
    print ("solving...")
    num_1_dict = {}
    start = timeit.default_timer()
    num_edges = int(np.math.factorial(num_vertices)/(np.math.factorial(2)*np.math.factorial(num_vertices-2)))
    cnf = CNF()
    cnf.from_file(file)
    if solver_type == 1:
        s = Cadical()
    elif solver_type == 2:
        s = Gluecard3()
    elif solver_type == 3:
        s = Gluecard4()
    elif solver_type == 4:
        s = Glucose3()
    elif solver_type == 5:
        s = Glucose4()
    elif solver_type == 6:
        s = Lingeling()
    elif solver_type == 7:
        s = MapleChrono()
    elif solver_type == 8:
        s = MapleCM()
    elif solver_type == 9:
        s = Maplesat()
    elif solver_type == 10:
        s = Mergesat3()
    elif solver_type == 11:
        s = Minicard()
    elif solver_type == 12:
        s = Minisat22()
    elif solver_type == 13:
        s = MinisatGH()   
    else:
        print ("no solver specificed.")
    solution_exist = True
    s.append_formula(cnf.clauses)
    count = 0
    total_count = 0
    file = "candidates_"+str(num_vertices)+"v"
    #outfile = open(file,'wb')
    outfile = open(file,'w') #for directly writing file without constructing edges
    while solution_exist == True:
        solve = s.solve()
        solution = s.get_model()
        if solve == True:
            total_count += 1
            edges = construct_graph(solution[:num_edges], num_vertices)
            coloring = colorable(edges, solver_type)
            if coloring == False:
                outfile.write(str(solution[:num_edges]) + "/n") #if it is not colorable, we should save it as a solution
                count += 1
                print (count)
            else:
                #it's colorable and we should block this coloring
                try:
                    num_1_dict[count_1(coloring)] += 1
                except:
                    num_1_dict[count_1(coloring)] = 1
                colorability_constraint = coloring_to_constraint(coloring)
                #print ("coloring:" + str(coloring))
                #print ("generated constraint: " + str(colorability_constraint))
                s.add_clause(colorability_constraint)
            #pickle.dump(edges,outfile)
            #print (timeit.default_timer())
            #print ("solution: " + str(solution[:num_edges]))
            assumption = [ -i for i in solution[:num_edges] ] #we should block the graph regardless if it's colorable or not
            s.add_clause(assumption)
            if total_count%5000 == 0:
                print (num_1_dict)
        else:
            solution_exist == False
            break
    stop = timeit.default_timer()
    print (str(num_vertices) + " has " + str(count) + " solutions")
    print ("runtime: " + str(stop - start))
    print (num_1_dict)
    outfile.close()
    return stop-start

solve_cnf_pickle("fly_version_all_constraints_10", 10, 1)