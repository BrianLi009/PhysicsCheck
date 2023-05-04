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

# Return the constraint that c = ±(a × b) for complex numbers
def cross_constraint(a, b, c):
    return Or(And(c[0]==crossc(a,b)[0], c[1]==crossc(a,b)[1], c[2]==crossc(a,b)[2]), And(c[0]==crossc(b,a)[0], c[1]==crossc(b,a)[1], c[2]==crossc(b,a)[2]))

def determine_embed(g, assignment, g_sat, order, index, using_subgraph):
    s = Solver()
    v = {}
    ver = {}
    for i in range(len(assignment.var)):
        v[i] = (Complex("v{0}c1".format(i)), Complex("v{0}c2".format(i)), Complex("v{0}c3".format(i)))
    for i in assignment.assign:
        #now define every vertex
        ver[i] = (Complex("ver{0}c1".format(i)), Complex("ver{0}c2".format(i)), Complex("ver{0}c3".format(i)))
    for i in assignment.assign:
        #s.add() its corresponding vector as a condition
        if isinstance(assignment.assign[i], int):
            s.add(ver[i][0]==v[assignment.assign[i]][0])
            s.add(ver[i][1]==v[assignment.assign[i]][1])
            s.add(ver[i][2]==v[assignment.assign[i]][2])
        else:
            if i in assignment.base:
                s.add(cross_constraint(v[assignment.assign[i][0]], v[assignment.assign[i][1]], ver[i]))
            else:
                s.add(cross_constraint(ver[assignment.assign[i][0]], ver[assignment.assign[i][1]], ver[i]))
    s.add(dotc(ver[i], ver[i]) == 1) #live on unit complex sphere
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
            s.add(Not(And(ver[v1][0]==ver[v2][0], ver[v1][1]==ver[v2][1], ver[v1][2]==ver[v2][2])))#cannot be equal
            s.add(Not(And(ver[v1][0].r==-ver[v2][0].r, ver[v1][1].r==-1*ver[v2][1].r, ver[v1][2].r==-1*ver[v2][2].r)))#cannot be opposite
            s.add(Not(And(ver[v1][0].i==-ver[v2][0].i, ver[v1][1].i==-1*ver[v2][1].i, ver[v1][2].i==-1*ver[v2][2].i)))
    #revert assign dict
    assign_inv = defaultdict(list)
    for k, v in assignment.assign.items():
        assign_inv[v].append(k)
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
        s.add(dotc(ver[v],ver[w]) == 0)
    #s.set("timeout", 10000)
    result = s.check()
    if result == sat:
        print (s.model())

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

def main(g, order, index, using_subgraph):
    """takes in graph in maplesat output format, order of the graph, count corresponds to the line
       number of the candidates, and index indicates which vector assignment we will be using. """
    order = int(order)
    edge_lst = maple_to_edges(g, int(order))
    G = nx.Graph()
    G.add_edges_from(edge_lst)
    degree_sequence = [d for n, d in G.degree()]
    if nx.is_empty(G) or (not nx.is_connected(G)) or (1 in degree_sequence) or (nx.is_isomorphic(G, cycle_graph(order))):
        print ("sat")
    else:
        if using_subgraph:
            print ("Checking minimum nonembeddable subgraph")
            my_file = open("min_nonembed_graph_10-12-c.txt", "r")
            content = my_file.read()
            min_non_subgraphs = content.split("\n")
            my_file.close()
            for string in min_non_subgraphs:
                min_g = nx.Graph()
                min_g.add_edges_from(maple_to_edges(string, 11))
                gm = isomorphism.GraphMatcher(G, min_g)
                if gm.subgraph_is_monomorphic():
                    print ("unsat")
                    return
            #check if G contains a minimum nonembedabble subgraph
            print ("this graph does not contain known minimal nonembeddable subgraph")
            graph_dict = {}
            for v in list(G.nodes()):
                graph_dict[v] = (list(G.neighbors(v)))
            assignments = find_assignments(graph_dict)
            assignment = assignments[int(index)]
            determine_embed(graph_dict, assignment, g, order, index, using_subgraph) #write the file
        else:
            graph_dict = {}
            for v in list(G.nodes()):
                graph_dict[v] = (list(G.neighbors(v)))
            assignments = find_assignments(graph_dict)
            assignment = assignments[int(index)]
            determine_embed(graph_dict, assignment, g, order, index, using_subgraph) #write the file

"""
testing function call
main('a -1 -2 -3 -4 -5 -6 -7 -8 -9 -10 -11 -12 -13 14 15 -16 -17 18 -19 20 -21 -22 -23 24 25 -26 -27 -28 -29 30 -31 -32 33 -34 -35 36 37 -38 -39 40 -41 -42 43 -44 -45 46 47 48 -49 -50 51 -52 -53 -54 -55 0', 11, 0, False)
"""