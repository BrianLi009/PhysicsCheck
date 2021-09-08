""" Tries to determine, using quantifier elimination, whether a graph is
    embeddable on the sphere. """

import collections
import subprocess
import threading
from io import StringIO
import textwrap
import random
import os
import networkx as nx
import shutil
import csv
from networkx.algorithms.clique import enumerate_all_cliques

from networkx.algorithms.operators.unary import complement
from z3.z3printer import _ASSOC_OPS

def g6_to_dict(g6):
    """ Input a g6 string, output a dictionary representing a graph that can be inputted in find_assignments"""
    graph_dict = {}
    G = nx.from_graph6_bytes(bytes(g6, encoding='ascii'))
    for v in list(G.nodes()):
        graph_dict[v] = (list(G.neighbors(v)))
    return graph_dict


def find_assignments(g):
    """ Find all possible crossproduct assignments for the graph g. """
    # TODO compute automorphism group first?
    # Create list of edges
    edges_without_duplicates = set()
    edges = set()
    for v in g:
        for w in g[v]:
            if (w, v) not in edges:
                edges_without_duplicates.add((v, w))
            edges.add((v,w))
    # Fill stack with choices of initial edge
    frame = collections.namedtuple('frame',
                                ('first_edge',
                                 'to_visit',
                                 'nvar',
                                 'ortho',
                                 'eqs',
                                 'var',
                                 'assign',
                                 'easily_embeddable',
                                 'iterative_assignment',
                                 'base',
                                 'touched_by',
                                 'edges_used'))
    batch = list()
    for first_edge in edges_without_duplicates:
        f = frame(
                first_edge=first_edge,
                to_visit=set(first_edge),
                nvar=0,
                ortho=[],
                eqs=[],
                var=[first_edge[0], first_edge[1]],
                assign={first_edge[0]: 0,
                        first_edge[1]: 1},
                easily_embeddable=True,
                iterative_assignment=True,
                base=set(first_edge),
                touched_by={first_edge[0]: first_edge[1],
                            first_edge[1]: first_edge[0]},
                edges_used=set([first_edge, (first_edge[1], first_edge[0])]))
        for z in (frozenset(g[first_edge[0]]) &
                  frozenset(g[first_edge[1]])):
            f.base.add(z)
            f.assign[z] = (0, 1)
            f.edges_used.add((first_edge[0], z))
            f.edges_used.add((first_edge[1], z))
            f.edges_used.add((z, first_edge[0]))
            f.edges_used.add((z, first_edge[1]))
            f.to_visit.add(z)
            f.touched_by[z] = first_edge[0]
        batch.append(f)
    completed = []
    while batch:
        new_batch = []
        for f in batch:
            # First, deduce all assignments
            while f.to_visit:
                v = f.to_visit.pop()
                for w in g[v]:
                    # Skip the edge, if it is already used
                    if (v, w) in f.edges_used:
                        continue
                    if w not in f.touched_by:
                        # If the node has not been touched before, touch it
                        # and continue
                        if w not in f.assign:
                            f.touched_by[w] = v
                            continue
                        # It is a variable.  Record the orthogonality
                        f.edges_used.add((v, w))
                        f.edges_used.add((w, v))
                        f.ortho.append((f.assign[v], f.assign[w]))
                        continue
                    # The node has been touched before.  We now can derive a
                    # cross-product expression for this node.  Two cases:
                    #  (i) the node has already been assigned a value: we can
                    #      derive a new equation; or (ii) the node has not been
                    #      assigned a value: we will assign one.  In both cases:
                    v2 = f.touched_by[w]
                    assert v != v2
                    f.edges_used.add((v, w))
                    f.edges_used.add((w, v))
                    # (i) the node has been assigned a value; derive an equation
                    if w in f.assign:
                        f = f._replace(easily_embeddable=False)
                        f.ortho.append((f.assign[w], f.assign[v]))
                        f.eqs.append(((f.assign[v], f.assign[v2]),
                                       f.assign[w]))
                        continue
                    # (ii) the node has not been assigned a value --- assign it
                    f.edges_used.add((v2, w))
                    f.edges_used.add((w, v2))
                    f.assign[w] = (f.assign[v], f.assign[v2])
                    f.to_visit.add(w)
            # Check whether finished
            if len(f.assign) == len(g):
                for v1, v2 in edges_without_duplicates - f.edges_used:
                    f.ortho.append((f.assign[v1], f.assign[v2]))
                    f = f._replace(easily_embeddable=False)
                #if f.easily_embeddable:
                #    return (True, 'easily')
                completed.append(f)
                continue
            # If not: consider every possible node for the new variable
            for v in g:
                if v in f.assign:
                    continue
                new_var = len(f.var)
                f2 = frame(
                        first_edge=f.first_edge,
                        to_visit=set([v]),
                        nvar=f.nvar+3,
                        ortho=list(f.ortho),
                        eqs=list(f.eqs),
                        var=f.var + [v],
                        assign=dict(f.assign),
                        easily_embeddable=f.easily_embeddable,
                        iterative_assignment=f.iterative_assignment,
                        base=f.base,
                        touched_by=dict(f.touched_by),
                        edges_used=set(f.edges_used))
                f2.assign[v] = new_var
                for b in f2.base:
                    if v in g[b]:
                        f2 = f2._replace(nvar=f2.nvar - 1)
                        break
                iterative_step = False
                for w in g[v]:
                    if w in f.assign:
                        f2.ortho.append((f2.assign[v], f2.assign[w]))
                        f2.edges_used.add((v, w))
                        f2.edges_used.add((w, v))
                        iterative_step = True
                if not iterative_step:
                    f2 = f2._replace(easily_embeddable=False,
                                     iterative_assignment=False)
                new_batch.append(f2)
        batch = new_batch
    # Find best assignment: we want the least number of variables;
    # then the least number of cross-product equations and finally
    # the least number of orthogonallity requirements.
    completed.sort(key=lambda f: (f.nvar, len(f.eqs), len(f.ortho)))
    return completed

def generate_z3(G, assignment_1, filename):
    """
    generate z3 script
    """
    f = open(filename + ".py", "w")
    f.write('from z3 import * \n')
    f.write('import multiprocessing \n')
    f.write('def test_embed(): \n')
    f.write(' '*4 + 'f = open("embed_result.txt", "a") \n')
    clauses = ''
    assignment = translation(assignment_1)
    n = len(set(list(assignment.keys())))
    variable_lst = []
    v_lst = range(0, n) #we can either do (0, n) or (1, n+1) depending on whether the edge list starts from 0 or 1
    for v in v_lst: 
        x_v = 'x' + '_' + str(v)
        y_v = 'y' + '_' + str(v)
        z_v = 'z' + '_' + str(v)
        variable_lst += [x_v, y_v, z_v]
    for variable in variable_lst:
        clause = ' '*4+ variable + ' = Real(' + '\''  + variable + '\'' + ')' + '\n'
        clauses = clauses + clause
    f.write(' '*4+'s = Solver() \n')
    original_assign = assignment_1.assign
    for v_1, v_2 in assignment_1.ortho:
        #their dot product is 0
        label_1 = list(original_assign.keys())[list(original_assign.values()).index(v_1)]
        label_2 = list(original_assign.keys())[list(original_assign.values()).index(v_2)]
        equation_1 = ' '*4+"s.add(" + 'x_' + str(label_1) +'*'+'x_' + str(label_2)+'+'+ 'y_' + str(label_1) +'*'+'y_' + str(label_2)+'+'+'z_' + str(label_1)+'*'+'z_' + str(label_2)+' == 0' + ")" + '\n'
        clauses = clauses + equation_1
    cross_dict = translate_cross(assignment_1.eqs, {})
    for vertex in cross_dict.keys():
        v_1 = cross_dict[vertex][0]
        v_2 = cross_dict[vertex][1]
        label_1 = list(original_assign.keys())[list(original_assign.values()).index(v_1)]
        label_2 = list(original_assign.keys())[list(original_assign.values()).index(v_2)]
        x_1 = 'x_' + str(label_1)
        y_1 = 'y_' + str(label_1)
        z_1 = 'z_' + str(label_1)
        x_2 = 'x_' + str(label_2)
        y_2 = 'y_' + str(label_2)
        z_2 = 'z_' + str(label_2)
        vector_3 = cross_product(x_1, y_1, z_1, x_2, y_2, z_2)
        v = list(original_assign.keys())[list(original_assign.values()).index(vertex)]
        x_3 = 'x_' + str(v)
        y_3 = 'y_' + str(v)
        z_3 = 'z_' + str(v)
        double_cross = cross_product(vector_3[0], vector_3[1], vector_3[2], x_3, y_3, z_3)
        equation_5 = ' '*4+"s.add(" + double_cross[0] + '==0) \n'
        equation_6 = ' '*4+"s.add(" + double_cross[1] + '==0) \n'
        equation_7 = ' '*4+"s.add(" + double_cross[2] + '==0) \n'
        clauses = clauses + equation_5 + equation_6 + equation_7
    for pair in list(complement(G).edges()):
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
        if isinstance(assignment[vertex], tuple):
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
    triangle = find_triangle(G)[0]
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
    for i in list(G.nodes()):
        if i not in triangle:
            equation_1 = ' '*4+"s.add(" + 'x_' + str(i) + "**2+" + 'y_' + str(i) + "**2+" + 'z_' + str(i) + "**2" + " == 1" + ")" + '\n'
            equation_2 = ' '*4+"s.add(" + 'z_' + str(i) + ' >= 0' + ")" + '\n'
            equation_3 = ' '*4+"s.add(" + "Implies(" + 'z_' + str(i) + " == 0, " + 'y_' + str(i) + " > 0))" + '\n'
            clauses = clauses + equation_1 + equation_2 + equation_3
    f.write(clauses)
    f.write(' '*4 + 'dir = __file__\n')
    f.write(' '*4 + "dir = dir.split('\\\\')\n")
    f.write(' '*4 + 'row = int(dir[-1][:-3])\n')
    f.write(' '*4 + "f.write('  ' + str(row) + ', ' + str(s.check()) + '  ')\n")
    f.write("if __name__ == '__main__': \n")
    f.write(' '*4 + "p = multiprocessing.Process(target=test_embed) \n")
    f.write(' '*4 + "p.start() \n")
    f.write(' '*4 + "p.join(10) \n")
    f.write(' '*4 + "if p.is_alive(): \n")
    f.write(' '*8 + "print (" + str(filename) + ")" + "\n")
    f.write(' '*8 + "p.terminate() \n")
    f.write(' '*8 + "p.join() \n")
    f.write(' '*4 + "else: \n")
    f.write(' '*8 + "p.terminate() \n")
    f.write(' '*8 + "p.join() \n")
    f.close()

def cross_product(x_1, y_1, z_1, x_2, y_2, z_2):
    x_3 = '(' + y_1 + '*' + z_2 + '-' + z_1 + '*' + y_2 + ')'
    y_3 = '(' + z_1 + '*' + x_2 + '-' + x_1 + '*' + z_2 + ')'
    z_3 = '(' + x_1 + '*' + y_2 + '-' + y_1 + '*' + x_2 + ')'
    return (x_3, y_3, z_3)

def dot_product(x_1, y_1, z_1, x_2, y_2, z_2):
    return x_1 + '*' + x_2 + y_1 + '*' + y_2 + z_1 + '*' + z_2 

def depth(t):
    """ input a tuple and determine its nested level (depth) """
    try:
        return 1+max(map(depth,t))
    except:
        return 0

def translation(assignment):
    """
    transition a nested assignment dictionary to non-nested
    """
    assign_dict = {}
    dict = assignment.assign
    d = 0 #n is the max nested tuple depth
    entered = True
    while entered == True:
        entered =  False
        for keys in dict.keys():
            if depth(dict[keys]) == d and d < 1:
                entered = True
                assign_dict[keys] = list(dict.keys())[list(dict.values()).index(dict[keys])]
            if depth(dict[keys]) == d and d >= 1:
                entered = True
                assign_dict[keys] = (list(dict.keys())[list(dict.values()).index(dict[keys][0])], list(dict.keys())[list(dict.values()).index(dict[keys][1])])
        d += 1
    return assign_dict

def translate_ortho(ortho, dot_lst):
    for i in ortho:
        if not isinstance(i, int):
            dot_lst.append((i[0], i[1]))
            translate_ortho(i, dot_lst)
    return (dot_lst)

def find_triangle(G):
    triangle_cliques = []
    for clique in enumerate_all_cliques(G):
        if len(clique) == 3:
            triangle_cliques.append(clique)
    return triangle_cliques

def translate_cross(eqs, cross_dict):
    for i, eq in enumerate(eqs):
        cross_dict[eq[1]] = eq[0]
    return (cross_dict)
    
"""with open('small_graph_new.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    count = 0
    next(csv_reader)
    for row in csv_reader:
        count += 1
        g6_string = row[0]
        graph_dict = g6_to_dict(g6_string)
        G = nx.from_graph6_bytes(bytes(g6_string, encoding='ascii'))
        if find_triangle(G) == []:
            continue
        for assignment in find_assignments(graph_dict):
            print (assignment)
            generate_z3(G, assignment, str(count))
            os.system(str(count)+'.py')
            with open('embed_result.txt') as f:
                if ('  ' + str(count) + ', ' in f.read()):
                    print (str(count) + ' solved')
                    break"""

