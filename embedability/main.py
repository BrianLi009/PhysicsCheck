from io import StringIO
from networkx.algorithms.cycles import find_cycle
from z3 import *
import os
import csv
import networkx as nx
import collections
import itertools
from collections import Counter
from helper import cross, dot, nested_cross

def g6_to_dict(g6):
    """ Input a g6 string, output a dictionary representing a graph that can be inputted in find_assignments"""
    graph_dict = {}
    G = nx.from_graph6_bytes(bytes(g6, encoding='ascii'))
    for v in list(G.nodes()):
        graph_dict[v] = (list(G.neighbors(v)))
    return graph_dict

def find_assignments(g):
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
                        """f.eqs.append(((f.assign[v], f.assign[v2]),
                                       f.assign[w]))"""
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
                """if f.easily_embeddable:
                    print ("easily embeddable")
                    num_vertices = len(g)
                    num_edges = int(len(edges)/2)
                    file = open("embed_result.txt", "a")
                    file.write('  ' + str(label) + ', ' + 'sat' + ' ' + str(num_vertices) + ' ' + str(num_edges) )
                    break"""
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

def determine_embed(g, assignment,label):
    io = StringIO()
    io.write('from helper import cross, dot, nested_cross \n')
    io.write('from z3 import * \n')
    io.write('import multiprocessing \n')
    io.write("def solve(): \n")
    io.write("    s = Solver()\n")
    v_dict = {}
    for i in range(len(assignment.var)):
        io.write( '    v'+str(i)+'c1 = Real("v'+ str(i) + 'c1")\n')
        io.write( '    v'+str(i)+'c2 = Real("v'+ str(i) + 'c2")\n')
        io.write( '    v'+str(i)+'c3 = Real("v'+ str(i) + 'c3")\n')
        io.write( '    v' + str(i) + '= (' + 'v' + str(i) + 'c1, v' + str(i) + 'c2, v' + str(i) + 'c3)\n')
        v_dict[i] = ('v'+str(i)+'c1', 'v'+str(i)+'c2', 'v'+str(i)+'c3') #{0: (v0c1, v0c2, v0c3)}
    io.write('    s.add('+v_dict[0][0] +'== 1) \n')
    io.write('    s.add('+v_dict[0][1] +'== 0) \n')
    io.write('    s.add('+v_dict[0][2] +'== 0) \n')
    io.write('    s.add('+v_dict[1][0] +'== 0) \n')
    io.write('    s.add('+v_dict[1][1] +'== 1) \n')
    io.write('    s.add('+v_dict[1][2] +'== 0) \n')
    x = assignment.var[0]
    y = assignment.var[1]
    fvars = set()
    try:
        z = next(iter(assignment.base - set([x, y])))
    except StopIteration:
        z = None
    for i in range(2, len(assignment.var)):
        fvars.add(v_dict[i][0])
        fvars.add(v_dict[i][1])
        fvars.add(v_dict[i][2])
        if x in g[assignment.var[i]]:
            io.write('    s.add('+v_dict[i][0]+' == 0)\n')
            fvars.remove(v_dict[i][0])
        elif y in g[assignment.var[i]]:
            io.write('    s.add('+v_dict[i][1]+' == 0)\n')
            fvars.remove(v_dict[i][1])
        elif z in g[assignment.var[i]]:
            io.write('    s.add('+v_dict[i][2]+' == 0)\n')
            fvars.remove(v_dict[i][2])
    try:
        cross_product = nested_cross(assignment.eqs[0])
        io.write('    s.add(' + cross_product + '[0] == 0) \n')
        io.write('    s.add(' + cross_product + '[1] == 0) \n')
        io.write('    s.add(' + cross_product + '[2] == 0) \n')
    except:
        pass
    edges = set()
    for v in g:
        for w in g[v]:
            edges.add((v,w))
    had = set()
    for v1 in g:
        for v2 in g:
            if v1 == v2:
                continue
            if (v1, v2) in edges:
                continue
            if (v2, v1) in had:
                continue
            had.add((v1, v2))
            cross_product = nested_cross((assignment.assign[v1], assignment.assign[v2]))
            io.write('    s.add(Or(Not(' + cross_product + '[0] == 0), Not(' + cross_product + '[1] == 0), Not(' + cross_product + '[2] == 0)))\n')
    for dot_relation in assignment.ortho:
        v = nested_cross(dot_relation[0])
        w = nested_cross(dot_relation[1])
        io.write('    s.add(' + dot(v,w) + '== 0) \n')
    #io.write('    print (s.check()) \n')
    io.write('    f = open("embed_result.txt", "a") \n')
    io.write('    f.write(' + ' "  "+ ' + 'str(' + str(label) + ') +' + ' "  "  ' + '+' + 'str(s.check()))\n')
    io.write("if __name__ == '__main__':\n")
    io.write("    p = multiprocessing.Process(target=solve) \n")
    io.write("    p.start()\n")
    io.write("    p.join(10)\n")
    io.write("    if p.is_alive(): \n")
    io.write("        print ('running... kill it...') \n")
    io.write("        p.terminate() \n")
    io.write("        p.join() \n")
    io.write("    else: \n")
    io.write("        p.terminate() \n")
    io.write("        p.join() \n")
    with open('test.py', mode = 'w') as f:
        f.write(io.getvalue())

#graph in sat labeling format

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
"""
#taking file in the SAT output format
file1 = open('22partial.exhaust', 'r')
Lines = file1.readlines()
count = 0
for line in Lines:
    if count == 60457:
        print ("solving " + str(count))
        edge_lst = maple_to_edges(line, 22)
        G = nx.Graph()
        G.add_edges_from(edge_lst)
        graph_dict = {}
        for v in list(G.nodes()):
            graph_dict[v] = (list(G.neighbors(v)))
        assignments = find_assignments(graph_dict)
        print ("assignments found")
        for assignment in assignments:
            determine_embed(graph_dict, assignment, str(count)) #write the file
            os.system('test.py')
            with open('embed_result.txt', 'r+') as f:
                if ('  ' + str(count) + '  ' in f.read()):
                    print (str(count) + ' solved')
                    break
    count += 1"""

#takes in file with graph6 format
file1 = open('min_non_embed_13_candidate.txt', 'r')
Lines = file1.readlines()
count = 0
for line in Lines:
    print ("solving " + str(count))
    print (line[:-1])
    G = nx.from_graph6_bytes(bytes(line[:-1], encoding='utf-8'))
    graph_dict = {}
    for v in list(G.nodes()):
        graph_dict[v] = (list(G.neighbors(v)))
    assignments = find_assignments(graph_dict)
    print ("assignments found")
    for assignment in assignments:
        determine_embed(graph_dict, assignment, str(count)) #write the file
        os.system('test.py')
        with open('embed_result.txt', 'r+') as f:
            if ('  ' + str(count) + '  ' in f.read()):
                print (str(count) + ' solved')
                break
    count += 1