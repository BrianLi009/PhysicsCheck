from pysat.formula import CNF
from pysat.solvers import *
import itertools

def colorable(edge_lst, solver_type):
    """
    given a list of edges, return a valid coloring if possible
    we can move this function to PySAT to change the SAT solver we are using.
    """
    formula = CNF()
    for edge in edge_lst:
        formula.append([-edge[0],-edge[1]]) #no two adjacent vertices can be both 1
    vertices_lst = list(range(1, (max(max(edge_lst,key=lambda item:item[1])))+1))
    potential_triangles = list(itertools.combinations(vertices_lst, 3))
    for triangle in potential_triangles:
        v1 = triangle[0]
        v2 = triangle[1]
        v3 = triangle[2]
        if ((v1, v2) in edge_lst or (v2,v1) in edge_lst) and ((v2, v3) in edge_lst or (v3, v2) in edge_lst) and ((v1, v3) in edge_lst or (v3,v1) in edge_lst):
            formula.append([v1,v2,v3])
            formula.append([-v1, -v2])
            formula.append([-v2, -v3])
            formula.append([-v1, -v3])
        """
        if the triangle exists in this particular graph, it must satisfy 010 coloring
        """
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
    s.append_formula(formula.clauses)
    if s.solve() == True:
        return s.get_model()
    return False

def coloring_to_constraint(coloring):
    """given a list of coloring of the vertices, the function will generate the constraints to block"""
    clauses = []
    n = len(coloring) # number of vertices
    lst_0 , lst_1 =[i for i in coloring if i<0 ],[j for j in coloring if j>0]
    edge_dict = {}
    counter = 1
    vertices_lst = list(range(1, n+1))
    edge_lst = list(itertools.combinations(vertices_lst, 2))
    edge_lst.sort(key=lambda x:x[1]) #this is all we have to do to switch the order of edge_lst
    extra_var_count = len(edge_lst)+1
    extra_var_dict = {}
    for triangle in list(itertools.combinations(vertices_lst, 3)):
        extra_var_dict[triangle] = extra_var_count
        extra_var_count += 1
    for edge in edge_lst:
        edge_dict[edge] = counter
        counter += 1
    all_triangles = list(itertools.combinations(lst_0, 3))
    all_triangles = [tuple(map(abs, el)) for el in all_triangles]
    for edge in list(itertools.combinations(lst_1, 2)): 
        clauses = clauses + [edge_dict[edge]]
    for triangle in all_triangles:
        clauses = clauses + [extra_var_dict[triangle]]
    return clauses
