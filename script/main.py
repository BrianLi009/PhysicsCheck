from solve_DIMACS import *
from generate_DIMACS import *
import numpy as np
import pysat
from pysat.solvers import *
import itertools
import matplotlib.pyplot as plt
import math

def automate(min_n, max_n, solver_lst):
    """
    n: number of vertices, solver_lst: a list of solver
    """
    data_dict = {}
    for n in range(min_n, max_n+1):
        print ("solving for " + str(n))
        generate_dimacs(n) #produce and save the dimacs file
        file = "constraints_" + str(n)
        for solver_type in solver_lst:
            runtime = solve_cnf_pickle(file, n, solver_type)
            try:
                data_dict[solver_type].append([n, runtime])
            except:
                data_dict[solver_type] = [[n, runtime]]
    return data_dict

def plot_data(data_dict):
    """we take in the data_dict generated by automate, then plot a graph where the y axis is n vertices, and x axis is the runtime of each solver"""
    solver_dict = {1: "Cadical", 2: "Gluecard3", 3: "Gluecard4" , 4: "Glucose3", 5: "Glucose4", 6: "Lingeling" , 7: "MapleChrono" , 8: "MapleCM" , 9: "Maplesat" , 10: "Mergesat3" , 11: "Minicard" , 12: "Minisat22" , 13: "MinisatGH"} 
    for solver in data_dict.keys():
        x_value = [item[0] for item in data_dict[solver]]
        y_value = [item[1] for item in data_dict[solver]]
        plt.plot(x_value, y_value, label = solver_dict[solver])
    new_list = range(math.floor(min(x_value)), math.ceil(max(x_value))+1)
    plt.xticks(new_list)
    plt.legend()
    plt.show()

#plot_data(automate(17, 17, [1]))



