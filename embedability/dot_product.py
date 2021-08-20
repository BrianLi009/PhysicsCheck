from z3 import *
import csv
import timeit
import itertools
import networkx as nx
import os
#start = timeit.default_timer()

def Reverse(tuples):
    new_tup = tuples[::-1]
    return new_tup

def g6_to_edge(g6_string):
    """return a list of edges as sublists"""
    G = nx.from_graph6_bytes(bytes(g6_string, encoding='ascii'))
    return sorted(G.edges())

def find_triangle(edge_lst, n):
    """given a edge_lst, return a arbitrary triangle that exists in the form of (v_1,v_2,v_3)"""
    vertices_lst = list(range(0, n)) #we will assume the edge_lst starts with vertex "0" instead of "1"
    all_triangles = itertools.combinations(vertices_lst, 3)
    for triangle in all_triangles:
        e_1 = (triangle[0], triangle[1])
        e_2 = (triangle[0], triangle[2])
        e_3 = (triangle[1], triangle[2])
        if (e_1 in edge_lst or Reverse(e_1) in edge_lst) and (e_2 in edge_lst or Reverse(e_2) in edge_lst) and (e_3 in edge_lst or Reverse(e_3) in edge_lst):
            return triangle
    return False

def output_clause(g6_string, filename):
    """given the list of edges of a graph, we output the system of equations for embedability checking"""
    edge_lst = g6_to_edge(g6_string) #we need a function to convert g6 format to edge list
    n = len(set([item for sublist in edge_lst for item in sublist])) #number of vertices
    f = open('g' + str(count) + ".py", "w")
    f.write('from z3 import * \n')
    f.write('import multiprocessing \n')
    f.write('def test_embed(): \n')
    f.write(' '*4 + 'f = open("embed_result_dot.txt", "a") \n')
    variable_dict = {}
    edge_to_var = {}
    setup = ''
    clauses = ''
    v_lst = range(0, n) #we can either do (0, n) or (1, n+1) depending on whether the edge list starts from 0 or 1
    for v in v_lst: 
        x_v = 'x' + '_' + str(v)
        y_v = 'y' + '_' + str(v)
        z_v = 'z' + '_' + str(v)
        variable_dict[x_v] = x_v
        variable_dict[y_v] = y_v
        variable_dict[z_v] = z_v
        edge_to_var[v] = [x_v, y_v, z_v]
    variables = list(variable_dict.keys())
    for variable in variables:
        clause = ' '*4+ variable + ' = Real(' + '\''  + variable_dict[variable] + '\'' + ')' + '\n'
        setup = setup + clause
    f.write(setup)
    f.write(' '*4+'s = Solver() \n')
    ignore_v = []
    if find_triangle(edge_lst, n) != False:
        triangle = find_triangle(edge_lst, n)
        ignore_v.append(triangle[0] * 3)
        ignore_v.append(triangle[0] * 3+1)
        ignore_v.append(triangle[0] * 3+2)
        ignore_v.append(triangle[1] * 3)
        ignore_v.append(triangle[1] * 3+1)
        ignore_v.append(triangle[1] * 3+2)
        ignore_v.append(triangle[2] * 3)
        ignore_v.append(triangle[2] * 3+1)
        ignore_v.append(triangle[2] * 3+2)
    for i in range (len(variables)):
        if i%3 == 0 and i not in ignore_v: #a new vector
            x_i = variables[i]
            y_i = variables[i+1]
            z_i = variables[i+2]
            equation_1 = ' '*4+"s.add(" + x_i + "**2+" + y_i + "**2+" + z_i + "**2" + " == 1" + ")" + '\n'
            equation_2 = ' '*4+"s.add(" + z_i + ' >= 0' + ")" + '\n'
            equation_3 = ' '*4+"s.add(" + "Implies(" + z_i + " == 0, " + y_i + " > 0))" + '\n'
            #equation_4 = ' '*4+"s.add(" + "Implies(And(" + z_i+ " == 0, " + y_i + " == 0), " + x_i + " == 1))" + "\n"
            clauses = clauses + equation_1 + equation_2 +equation_3
    for edge in edge_lst:
        vertex_1 = edge_to_var[edge[0]]
        vertex_2 = edge_to_var[edge[1]]
        equation_5 = ' '*4+"s.add(" + vertex_1[0] +'*'+vertex_2[0]+'+'+ vertex_1[1] +'*'+vertex_2[1]+'+'+vertex_1[2]+'*'+vertex_2[2]+' == 0' + ")" + '\n'
        clauses = clauses + equation_5
    for pair in list(itertools.combinations(v_lst, 2)):
        v_1 = pair[0]
        v_2 = pair[1]
        x_1 = variables[v_1 * 3]
        y_1 = variables[v_1 * 3+1]
        z_1 = variables[v_1 * 3+2]
        x_2 = variables[v_2 * 3]
        y_2 = variables[v_2 * 3+1]
        z_2 = variables[v_2 * 3+2]
        equation_6 = ' '*4+"s.add(" + "Or(Not(" + x_1 + " == " + x_2 + "), Not(" + y_1 + " == " + y_2 + "), Not(" + z_1 + " == " + z_2 + "))) \n"
        clauses = clauses + equation_6
    if find_triangle(edge_lst, n) != False:
        triangle = find_triangle(edge_lst, n)
        tri_1 = triangle[0]
        tri_2 = triangle[1]
        tri_3 = triangle[2]
        x_1 = variables[tri_1 * 3]
        y_1 = variables[tri_1 * 3+1]
        z_1 = variables[tri_1 * 3+2]
        x_2 = variables[tri_2 * 3]
        y_2 = variables[tri_2 * 3+1]
        z_2 = variables[tri_2 * 3+2]
        x_3 = variables[tri_3 * 3]
        y_3 = variables[tri_3 * 3+1]
        z_3 = variables[tri_3 * 3+2]
        equation_7 = ' '*4+"s.add(" + x_1 + " == 1) \n" 
        equation_8 = ' '*4+"s.add(" + y_1 + " == 0) \n" 
        equation_9 = ' '*4+"s.add(" + z_1 + " == 0) \n" 
        equation_10 = ' '*4+"s.add(" + x_2 + " == 0) \n" 
        equation_11 = ' '*4+"s.add(" + y_2 + " == 1) \n" 
        equation_12 = ' '*4+"s.add(" + z_2 + " == 0) \n" 
        equation_13 = ' '*4+"s.add(" + x_3 + " == 0) \n" 
        equation_14 = ' '*4+"s.add(" + y_3 + " == 0) \n" 
        equation_15 = ' '*4+"s.add(" + z_3 + " == 1) \n" 
        clauses = clauses + equation_7 + equation_8 + equation_9 + equation_10 + equation_11 + equation_12 + equation_13 + equation_14 + equation_15
    f.write(clauses)
    f.write(' '*4 + 'dir = __file__\n')
    f.write(' '*4 + "dir = dir.split('\\\\')\n")
    f.write(' '*4 + 'row = int(dir[-1][1:-3])\n')
    f.write(' '*4 + "f.write(str(row) + ', ' + str(s.check()) + '   ')\n")
    f.write("if __name__ == '__main__': \n")
    f.write(' '*4 + "p = multiprocessing.Process(target=test_embed) \n")
    f.write(' '*4 + "p.start() \n")
    f.write(' '*4 + "p.join(3) \n")
    f.write(' '*4 + "if p.is_alive(): \n")
    f.write(' '*8 + "print (" + str(filename) + ")" + "\n")
    f.write(' '*8 + "p.terminate() \n")
    f.write(' '*8 + "p.join() \n")
    f.write(' '*4 + "else: \n")
    f.write(' '*8 + "p.terminate() \n")
    f.write(' '*8 + "p.join() \n")
    f.close()

"""with open('small_graph_new.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    count = 0
    next(csv_reader)
    for row in csv_reader:
        count += 1
        print (count)
        g6_string = row[0]
        #result = row[2]
        output_clause(g6_string, count)"""

with open('small_graph_new.csv') as csv_file:
    starttime = timeit.default_timer()
    csv_reader = csv.reader(csv_file, delimiter=',')
    count = 0
    next(csv_reader)
    for row in csv_reader:
        count += 1
        #g6_string = row[0]
        try:
            os.system("g" + str(count)+'.py')
        except:
            continue
    print("Runtime :", timeit.default_timer() - starttime)

