#!/usr/bin/python

#embeddability checking script but in complex hilbert space
from io import StringIO
from networkx.algorithms import isomorphism
import os
import csv
import networkx as nx
import collections
import itertools
from collections import defaultdict

from networkx.algorithms.isomorphism.isomorph import is_isomorphic
from networkx.generators.classic import cycle_graph
from helper import *

import sys, getopt
current_dir = os.getcwd()

from z3 import * 

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
            f.assign[z] = (first_edge[0], first_edge[1])
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
                        continue
                    # (ii) the node has not been assigned a value --- assign it
                    f.edges_used.add((v2, w))
                    f.edges_used.add((w, v2))
                    f.assign[w] = (v, v2)
                    f.to_visit.add(w)
            # Check whether finished
            if len(f.assign) == len(g):
                for v1, v2 in edges_without_duplicates - f.edges_used:
                    f.ortho.append((f.assign[v1], f.assign[v2]))
                    f = f._replace(easily_embeddable=False)
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
    completed.sort(key=lambda f: (f.nvar, len(f.ortho)))
    return completed

def not_zero_c(a):
    return Or(Not(a[0].r==0), Not(a[1].r==0), Not(a[2].r==0), Not(a[0].i==0), Not(a[1].i==0), Not(a[2].i==0))

def determine_embed(g, assignment, g_sat, order, index, using_subgraph, output_unsat_f, output_sat_f, verify):
    s = Solver()
    ver = {}
    assign_inv = defaultdict(list)
    for k, v in assignment.assign.items():
        assign_inv[v].append(k)
    for i in range(order):
        ver[i] = (Complex("ver{0}c1".format(i)), Complex("ver{0}c2".format(i)), Complex("ver{0}c3".format(i)))

    base = list(assignment.base)
    for i in base:
        if assignment.assign[i] == 0:
            base_1 = i
        if assignment.assign[i] == 1:
            base_2 = i
    s.add(ver[base_1][0].r == 1)
    s.add(ver[base_1][1].r == 0)
    s.add(ver[base_1][2].r == 0)
    s.add(ver[base_2][0].r == 0)
    s.add(ver[base_2][1].r == 1)
    s.add(ver[base_2][2].r == 0)
    s.add(ver[base_1][0].i == 0)
    s.add(ver[base_1][1].i == 0)
    s.add(ver[base_1][2].i == 0)
    s.add(ver[base_2][0].i == 0)
    s.add(ver[base_2][1].i == 0)
    s.add(ver[base_2][2].i == 0)
    
    for i in assignment.assign:
        if not isinstance(assignment.assign[i], int):
            s.add(ver[i][0] == crossc(ver[assignment.assign[i][0]], ver[assignment.assign[i][1]])[0])
            s.add(ver[i][1] == crossc(ver[assignment.assign[i][0]], ver[assignment.assign[i][1]])[1])
            s.add(ver[i][2] == crossc(ver[assignment.assign[i][0]], ver[assignment.assign[i][1]])[2])

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
            s.add(not_zero_c(crossc(ver[v1], ver[v2])))
    
    #normalize
    #s.add(dotc(ver[i], ver[i]) == 1)

    for dot_relation in assignment.ortho:
        if len(assign_inv[dot_relation[0]]) > 1:
            for v_base in assign_inv[dot_relation[0]]:
                if v_base in assignment.base:
                    v = v_base
        else:
            v = assign_inv[dot_relation[0]][0]
        if len(assign_inv[dot_relation[1]]) > 1:
            for w_base in assign_inv[dot_relation[1]]:
                if w_base in assignment.base:
                    w = w_base
        else:
            w = assign_inv[dot_relation[1]][0]
        #add dot product constraints
        s.add(dotc(ver[v],ver[w]).r == 0)
        s.add(dotc(ver[v],ver[w]).i == 0)
    s.set("timeout", 30000)
    result = s.check()
    if result == unknown:
        print("Timeout reached: Embeddability unknown, checking next intepretation")
        index = int(index) + 1
        s.reset()
        main_single_graph(g_sat, order, index, using_subgraph, output_unsat_f, output_sat_f, verify)
    if result == unsat:
        with open(output_unsat_f, "a+") as f:
            f.write(g_sat + "\n")
    if result == sat:
        with open(output_sat_f, "a+") as f:
            f.write(g_sat + "\n")
        if verify:
            m = s.model()
            #check all vectors are nonzero
            for vec in g:
                if m.evaluate(ver[vec][0].r == 0) and m.evaluate(ver[vec][0].i == 0) and m.evaluate(ver[vec][1].r == 0) and m.evaluate(ver[vec][1].i == 0) and m.evaluate(ver[vec][2].r == 0) and m.evaluate(ver[vec][2].i == 0):
                    print ("vector is the zero vector")
                    return
            #check non-colinear between all vertices
            for vec_1 in g:
                for vec_2 in g:
                    if vec_1 != vec_2:
                        dot_prod = dotc(ver[vec_1], ver[vec_2]) 
                        if m.evaluate(dot_prod * dot_prod == normc2(ver[vec_1]) * normc2(ver[vec_2])):
                            print ("vectors are colinear, verification failed")
                            return
            #check orthgonality between all connected vertices
            for vec in g:
                for adj_vec in g[vec]:
                    real_dot = (m.evaluate(dotc(ver[vec], ver[adj_vec]).r == 0))
                    img_dot = (m.evaluate(dotc(ver[vec], ver[adj_vec]).i == 0))
                    if not real_dot or not img_dot:
                        print ("connected vertices are not orthogonal, verification failed")
                        return
            #check three mutually connected vertices satisfy u=v cross w in some order
            for vec in g:
                for vec_1 in g[vec]:
                    for vec_2 in g[vec]:
                        if vec_1 != vec_2:
                            cross_prod_1 = crossc(ver[vec_1], ver[vec_2])
                            cross_prod_2 = crossc(ver[vec], cross_prod_1)
                            if (not m.evaluate(cross_prod_2[0].r==0)) or (not m.evaluate(cross_prod_2[0].i==0)) or (not m.evaluate(cross_prod_2[1].r==0)) or (not m.evaluate(cross_prod_2[1].i==0)) or (not m.evaluate(cross_prod_2[2].r==0)) or (not m.evaluate(cross_prod_2[2].i==0)):
                                print ("mutually orthogonal vectors does not satisfy cross product constraint")
                                return

                        
#graph in sat labeling format

def maple_to_edges(input, v):
    str_lst = input.split()[1:-1]
    edge_lst = []
    for j in range(0, v):
        for i in range(0, j):
            edge_lst.append((i,j))
    actual_edges = []
    for i in str_lst:
        indicator = int(i)
        if indicator > 0:
            actual_edges.append(edge_lst[int(i)-1])
    return actual_edges

def main_single_graph(g, order, index, using_subgraph, output_unsat_f, output_sat_f, verify):
    """takes in graph in maplesat output format, order of the graph, count corresponds to the line
       number of the candidates, and index indicates which vector assignment we will be using. """
    order = int(order)
    edge_lst = maple_to_edges(g, int(order))
    G = nx.Graph()
    G.add_edges_from(edge_lst)
    if using_subgraph:
        #print ("Checking minimum nonembeddable subgraph")
        file_path = os.path.join(current_dir, "embedability/min_nonembed_graph_10-12-c.txt")
        my_file = open(file_path, "r")
        content = my_file.read()
        min_non_subgraphs = content.split("\n")
        my_file.close()
        for string in min_non_subgraphs:
            min_g = nx.from_graph6_bytes(bytes(string, encoding='utf-8'))
            gm = isomorphism.GraphMatcher(G, min_g)
            if gm.subgraph_is_monomorphic():
                with open(output_unsat_f, "a+") as f:
                    f.write(g + "\n")
                    return
        #check if G contains a minimum nonembedabble subgraph
        print ("this graph does not contain known minimal nonembeddable subgraph")
        graph_dict = {}
        for v in list(G.nodes()):
            graph_dict[v] = (list(G.neighbors(v)))
        assignments = find_assignments(graph_dict)
        assignment = assignments[int(index)]
        determine_embed(graph_dict, assignment, g, order, index, using_subgraph, output_unsat_f, output_sat_f, verify) #write the file
    else:
        graph_dict = {}
        for v in list(G.nodes()):
            graph_dict[v] = (list(G.neighbors(v)))
        assignments = find_assignments(graph_dict)
        assignment = assignments[int(index)]
        determine_embed(graph_dict, assignment, g, order, index, using_subgraph, output_unsat_f, output_sat_f, verify) #write the file
        
def main(file_to_solve, order, index, using_subgraph, output_unsat_f="output_unsat_f", output_sat_f="output_sat_f", verify=True):
    with open(file_to_solve) as f:
        for line in f:
            line = line.rstrip()
            main_single_graph(line, order, index, using_subgraph, output_unsat_f, output_sat_f, verify)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]=="True", sys.argv[5], sys.argv[6], sys.argv[7]=="True")
