""" Tries to determine, using quantifier elimination, whether a graph is
    embeddable on the sphere. """

import collections
import subprocess
import threading
from io import StringIO
import textwrap
import random
import networkx as nx
import shutil

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
eqs=[(((((2, 0), 0), ((2, 1), 1)), ((2, 1), 2)), (((2, 0), 0), ((2, 1), 2)))]
def check_sphere_embeddability(g, assignment, guess=False):
    """ Checks whether g is sphere embeddable using the given assignment.
        Use `find_assignments' to generate assignments.
        If `guess' is True, the function will guess the position of some
        of the points.  It will not be able to determine whether a graph
        is not embeddable.  However, if a graph is embeddable, it might
        find out, and if it does, it will be quite a bit faster than
        without guessing. """
    # Generate the reduce script.
    edges = set()
    for v in g:
        for w in g[v]:
            edges.add((v,w))
    f = assignment
    io = StringIO()
    io.write(textwrap.dedent("""
            from z3 import * 
            import multiprocessing  
            f = open("embed_result.txt", "a") 
            s = Solver() 
                """))
    for i in range(len(f.var)):
        io.write(textwrap.dedent("""
    x{i} = Real('x_{i}')""".format(i=i))) #assign the starting variables
    vertex_assignment = assignment.assign
    sort_vertex = dict(sorted(vertex_assignment.items(), key=lambda item: depth(item)))
    vertex_relation_dict = {}
    print (sort_vertex)
    for v in sort_vertex: #assign the rest of the variables in terms of the starting variables
        if isinstance(vertex_assignment[v], int):
            vertex_relation_dict[v] = vertex_assignment[v]
        else:
            v1 = vertex_assignment[v][0]
            v2 = vertex_assignment[v][1]
            while not isinstance(vertex_assignment[v1], int):
                vertex_assignment[v1] = vertex_assignment[v1]
            while not isinstance(vertex_assignment[v2], int):
                vertex_relation_dict[v2] = vertex_assignment[v2]
    print (vertex_relation_dict)

    with open('file', 'w') as fd:
        io.seek(0)
        shutil.copyfileobj(io, fd)

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


g = g6_to_dict("P?AAD@OI@aP_AcooBCbH_Da_")
assignment = find_assignments(g)
assignment_1 = assignment[0]
print (assignment_1)
check_sphere_embeddability(g, assignment_1, guess=False)
        