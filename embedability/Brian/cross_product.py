import timeit
import networkx as nx
from networkx.algorithms.cluster import triangles
from embedability import embedability, sort_by_degree
import networkx as nx
import itertools
import csv
import subprocess
import os 

def maple_to_edges(input, v):
    str_lst = input.split()[1:-1]
    edge_lst = []
    for j in range(0, v):
        for i in range(0,v):
            if i < j:
                edge_lst.append((i,j))
    actual_edges = []
    for i in str_lst:
        indicator = int(i)
        if indicator > 0:
            actual_edges.append(edge_lst[int(i)-1])
    return actual_edges

def Reverse(tuples):
    new_tup = tuples[::-1]
    return new_tup

def g6_to_edge(g6_string):
    """return a list of edges as sublists"""
    G = nx.from_graph6_bytes(bytes(g6_string, encoding='ascii'))
    return sorted(G.edges())

def cross_product(x_1, y_1, z_1, x_2, y_2, z_2):
    x_3 = '(' + y_1 + '*' + z_2 + '-' + z_1 + '*' + y_2 + ')'
    y_3 = '(' + z_1 + '*' + x_2 + '-' + x_1 + '*' + z_2 + ')'
    z_3 = '(' + x_1 + '*' + y_2 + '-' + y_1 + '*' + x_2 + ')'
    return (x_3, y_3, z_3)

def find_triangle(edge_lst):
    """given a edge_lst, return a arbitrary triangle that exists in the form of (v_1,v_2,v_3)"""
    n = len(set([item for sublist in edge_lst for item in sublist]))
    vertices_lst = list(range(0, n)) #we will assume the edge_lst starts with vertex "0" instead of "1"
    all_triangles = itertools.combinations(vertices_lst, 3)
    for triangle in all_triangles:
        e_1 = (triangle[0], triangle[1])
        e_2 = (triangle[0], triangle[2])
        e_3 = (triangle[1], triangle[2])
        if (e_1 in edge_lst or Reverse(e_1) in edge_lst) and (e_2 in edge_lst or Reverse(e_2) in edge_lst) and (e_3 in edge_lst or Reverse(e_3) in edge_lst):
            return triangle
    return False

def output_clause(relations, filename, triangle):
    """take input from the output of embedability() function, write to executable python file"""
    f = open(filename + ".py", "w")
    f.write('from z3 import * \n')
    f.write('import multiprocessing \n')
    f.write('def test_embed(): \n')
    f.write(' '*4 + 'f = open("embed_result_subgraph.txt", "a") \n')
    clauses = ''
    orthogonal_relations = relations[0]
    colinear_relations = relations[1]
    assignment = relations[2]
    variable_lst = []
    vertices_lst = relations[3]
    for v in vertices_lst: 
        x_v = 'x' + '_' + str(v)
        y_v = 'y' + '_' + str(v)
        z_v = 'z' + '_' + str(v)
        variable_lst += [x_v, y_v, z_v]
    for variable in variable_lst:
        clause = ' '*4+ variable + ' = Real(' + '\''  + variable + '\'' + ')' + '\n'
        clauses = clauses + clause
    f.write(' '*4+'s = Solver() \n')
    for pair in orthogonal_relations:
        #their dot product is 0
        v_1 = pair[0]
        v_2 = pair[1]
        equation_1 = ' '*4+"s.add(" + 'x_' + str(v_1) +'*'+'x_' + str(v_2)+'+'+ 'y_' + str(v_1) +'*'+'y_' + str(v_2)+'+'+'z_' + str(v_1)+'*'+'z_' + str(v_2)+' == 0' + ")" + '\n'
        clauses = clauses + equation_1
    for pair in colinear_relations:
        #their cross product is not the zero vector
        v_1 = pair[0]
        v_2 = pair[1]
        x_1 = 'x_' + str(v_1)
        y_1 = 'y_' + str(v_1)
        z_1 = 'z_' + str(v_1)
        x_2 = 'x_' + str(v_2)
        y_2 = 'y_' + str(v_2)
        z_2 = 'z_' + str(v_2)
        vector_3 = cross_product(x_1, y_1, z_1, x_2, y_2, z_2)
        x_3 = vector_3[0]
        y_3 = vector_3[1]
        z_3 = vector_3[2]
        equation_2 = ' '*4+"s.add("+ 'Or(' + 'Not(' + x_3 + '==0)'+ ', Not(' + y_3 + '==0)' + ', Not(' + z_3 + '==0))) \n'
        clauses = clauses + equation_2
    for vertex in assignment.keys():
        if len(assignment[vertex]) == 2:
            #assignment[vertex][0] cross assignment[vertex][1] = vertex or -vertex
            v_1 = assignment[vertex][0]
            v_2 = assignment[vertex][1]
            x_1 = 'x_' + str(v_1)
            y_1 = 'y_' + str(v_1)
            z_1 = 'z_' + str(v_1)
            x_2 = 'x_' + str(v_2)
            y_2 = 'y_' + str(v_2)
            z_2 = 'z_' + str(v_2)
            vector_3 = cross_product(x_1, y_1, z_1, x_2, y_2, z_2)
            #vector_3 cross (x_3,y_3,z_3) should be 0 vector
            x_3 = 'x_' + str(vertex)
            y_3 = 'y_' + str(vertex)
            z_3 = 'z_' + str(vertex)
            double_cross = cross_product(vector_3[0], vector_3[1], vector_3[2], x_3, y_3, z_3)
            equation_5 = ' '*4+"s.add(" + double_cross[0] + '==0) \n'
            equation_6 = ' '*4+"s.add(" + double_cross[1] + '==0) \n'
            equation_7 = ' '*4+"s.add(" + double_cross[2] + '==0) \n'
            clauses = clauses + equation_5 + equation_6 + equation_7
    try:
        tri_1 = triangle[0]
        tri_2 = triangle[1]
        tri_3 = triangle[2]
        equation_8 = ' '*4+"s.add(" + 'x_' + str(tri_1) + " == 0) \n"
        equation_9 = ' '*4+"s.add(" + 'y_' + str(tri_1) + " == 0) \n"
        equation_10 = ' '*4+"s.add(" + 'z_' + str(tri_1) + " == 1) \n" 
        equation_11 = ' '*4+"s.add(" + 'x_' + str(tri_2) + " == 0) \n"
        equation_12 = ' '*4+"s.add(" + 'y_' + str(tri_2) + " == 1) \n"
        equation_13 = ' '*4+"s.add(" + 'z_' + str(tri_2) + " == 0) \n" 
        equation_14 = ' '*4+"s.add(" + 'x_' + str(tri_3) + " == 1) \n"
        equation_15 = ' '*4+"s.add(" + 'y_' + str(tri_3) + " == 0) \n"
        equation_16 = ' '*4+"s.add(" + 'z_' + str(tri_3) + " == 0) \n" 
        clauses = clauses + equation_8 + equation_9 + equation_10 + equation_11 + equation_12 + equation_13 + equation_14 + equation_15 + equation_16
    except:
        print ("no triangle or not considered")
    f.write(clauses)
    f.write(' '*4 + 'dir = __file__\n')
    f.write(' '*4 + "dir = dir.split('\\\\')\n")
    f.write(' '*4 + 'row = int(dir[-1][:-3])\n')
    f.write(' '*4 + "f.write('  ' + str(row) + ', ' + str(s.check()) + '  ')\n")
    f.write("if __name__ == '__main__': \n")
    f.write(' '*4 + "p = multiprocessing.Process(target=test_embed) \n")
    f.write(' '*4 + "p.start() \n")
    f.write(' '*4 + "p.join(5) \n")
    f.write(' '*4 + "if p.is_alive(): \n")
    f.write(' '*8 + "print (" + str(filename) + ")" + "\n")
    f.write(' '*8 + "p.terminate() \n")
    f.write(' '*8 + "p.join() \n")
    f.write(' '*4 + "else: \n")
    f.write(' '*8 + "p.terminate() \n")
    f.write(' '*8 + "p.join() \n")
    f.close()

def find_triangle(G):
    triangle_cliques = []
    for clique in nx.enumerate_all_cliques(G):
        if len(clique) == 3:
            triangle_cliques.append(clique)
    return triangle_cliques

#import from small_graph_new.csv
"""with open('small_graph_new.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    count = 0
    next(csv_reader)
    for row in csv_reader:
        count += 1
        g6_string = row[0]
        G = nx.from_graph6_bytes(bytes(g6_string, encoding='ascii'))
        edge_lst = g6_to_edge(g6_string)
        degree_sorted = sorted(G.degree, key=lambda x: x[1], reverse=False)
        vertices_lst = []
        for vertex in degree_sorted:
            vertices_lst.append(vertex[0])
        assignment = embedability(edge_lst, vertices_lst)
        if find_triangle(G) == []:
            continue
        for triangle in find_triangle(G):
            print ("generating for " + str(count))
            output_clause(assignment, str(count), triangle)
            os.system(str(count)+'.py')
            with open('embed_result.txt') as f:
                if ('  ' + str(count) + ', ' in f.read()):
                    print (str(count) + ' solved')
                    break"""

#import from maplesat output

file1 = open('canonical_subgraphs\canonical-19.out', 'r')
Lines = file1.readlines()
count = 0
for line in Lines:
    count += 1
    edge_lst = maple_to_edges(line, 17)
    G = nx.Graph()
    G.add_edges_from(edge_lst)
    degree_sorted = sorted(G.degree, key=lambda x: x[1], reverse=False)
    if degree_sorted == []:
        continue
    vertices_lst = []
    for vertex in degree_sorted:
        vertices_lst.append(vertex[0])
    for vertex in range(17):
        if vertex not in vertices_lst:
            vertices_lst.append(vertex)
    assignment = embedability(edge_lst, vertices_lst)
    print (count)
    print ("generating for " + str(count))
    if find_triangle(G) == []:
        output_clause(assignment, str(count), [])
        os.system(str(count)+'.py')
        with open('embed_result_subgraph.txt') as f:
            if ('  ' + str(count) + ', ' in f.read()):
                print (str(count) + ' solved')
    else:
        for triangle in find_triangle(G):
            print ("generating for " + str(count))
            output_clause(assignment, str(count), triangle)
            os.system(str(count)+'.py')
            with open('embed_result_subgraph.txt') as f:
                if ('  ' + str(count) + ', ' in f.read()):
                    print (str(count) + ' solved')
                    break
    