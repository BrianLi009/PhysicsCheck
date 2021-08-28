""" Tries to determine, using quantifier elimination, whether a graph is
    embeddable on the sphere. """
import csv
import collections
import subprocess
import threading
from io import StringIO
import textwrap
import random
import networkx as nx
import shutil

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
                        #f.eqs.append(((f.assign[v], f.assign[v2]),
                        #               f.assign[w]))
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

def check_sphere_embeddability(g, assignment, filename, guess=False):
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
    def assign_to_reduce(x):
        if isinstance(x, tuple):
            return 'k({},{})'.format(*map(assign_to_reduce, x))
        return 'v{}'.format(x)
    io = StringIO()
    io.write(textwrap.dedent("""
            load_package redlog;
            rlset R;
            procedure d(x,y);
                (first x) * (first y) +
                (second x) * (second y) +
                (third x) * (third y);
            procedure k(x,y);
                {(second x)*(third y) - (third x)*(second y),
                 (third x)*(first y) - (first x)*(third y),
                 (first x)*(second y) - (second x)*(first y)};
            v0c1 := 1; v0c2 := 0; v0c3 := 0;
            v1c1 := 0; v1c2 := 1; v1c3 := 0;
                 """))
    for i in range(len(f.var)):
        io.write(textwrap.dedent("""
            v{i} := {{v{i}c1, v{i}c2, v{i}c3}}; """.format(i=i)))
    x = f.var[0]
    y = f.var[1]
    fvars = set()
    try:
        z = next(iter(f.base - set([x, y])))
    except StopIteration:
        z = None
    for i in range(2, len(f.var)):
        fvars.add('v%sc1' % i)
        fvars.add('v%sc2' % i)
        fvars.add('v%sc3' % i)
        if x in g[f.var[i]]:
            io.write("\nv{i}c1 := 0;".format(i=i))
            fvars.remove('v%sc1' % i)
        elif y in g[f.var[i]]:
            io.write("\nv{i}c2 := 0;".format(i=i))
            fvars.remove('v%sc2' % i)
        elif z in g[f.var[i]]:
            io.write("\nv{i}c3 := 0;".format(i=i))
            fvars.remove('v%sc3' % i)
    for i, eq in enumerate(f.eqs):
        io.write(textwrap.dedent("""
            eq{i}z := {eq}; """.format(i=i, eq=assign_to_reduce(eq))))
    had = set()
    nneq = 0
    for v1 in g:
        for v2 in g:
            if v1 == v2:
                continue
            if (v1, v2) in edges:
                continue
            if (v2, v1) in had:
                continue
            had.add((v1, v2))
            io.write(textwrap.dedent("""
                neq{i} := {eq}; """.format(i=nneq,
                        eq=assign_to_reduce((f.assign[v1], f.assign[v2])))))
            nneq += 1
    if guess:
        for i in range(random.randint(1,2)):
            tmp = list(sorted(fvars))
            random.shuffle(tmp)
            guessvar = tmp[0]
            fvars.remove(guessvar)
            io.write("{} := {};".format(guessvar, random.randint(-3, 3)))
    io.write(textwrap.dedent("""
            phi := """))
    for i, eq in enumerate(f.eqs):
        io.write(textwrap.dedent("""
            first eq{i}z = 0 and
            second eq{i}z = 0 and
            third eq{i}z = 0 and """.format(i=i)).replace('\n','\n       '))
    for i in range(nneq):
        io.write(textwrap.dedent("""
            (first neq{i} neq 0 or
             second neq{i} neq 0 or
             third neq{i} neq 0) and """.format(i=i)).replace('\n','\n       '))
    #for i in range(2, len(f.var)):
    #    io.write(textwrap.dedent("""
    #        v{i}c3^2 = 1 - v{i}c1^2 - v{i}c2^2 and """.format(
    #                    i=i)).replace('\n', '\n       '))
    for v1, v2 in f.ortho:
        io.write(textwrap.dedent("""
            d({},{}) = 0 and """.format(
                        assign_to_reduce(v1),
                        assign_to_reduce(v2))
                                ).replace('\n', '\n       '))
    io.write(textwrap.dedent("""
                    true;
            rlqe """))
    for fvar in fvars:
        io.write("\n     ex({},".format(fvar))
    io.write('phi')
    io.write(')' * len(fvars))
    io.write(';\n')
    io.write('off echo')
    with open(filename + '.red', 'w') as fd:
        io.seek(0)
        shutil.copyfileobj(io, fd)
    """pipe = subprocess.Popen(['reduce', '-w'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE)
    timed_out, result = popen_communicate_timeout(pipe, io.getvalue(), 2)
    if timed_out:
        return None
    embed = None
    for bit in reversed(result[0].split('\n')):
        if bit in ('false', 'true'):
            embed = (bit == 'true')
            break
    if embed is None:
        return None
    if not embed and guess:
        return None
    return (embed, io.getvalue())"""

def popen_communicate_timeout(pipe, s, timeout=2.5):
    """ Communicates with a Popen object with a timeout """
    timed_out = [False]
    def timer_callback(timed_out):
        timed_out[0] = True
        pipe.terminate()
    timer = threading.Timer(timeout, timer_callback, (timed_out,))
    timer.start()
    result = pipe.communicate(s)
    timer.cancel()
    return (timed_out[0], result)

def g6_to_dict(g6):
    """ Input a g6 string, output a dictionary representing a graph that can be inputted in find_assignments"""
    graph_dict = {}
    G = nx.from_graph6_bytes(bytes(g6, encoding='ascii'))
    for v in list(G.nodes()):
        graph_dict[v] = (list(G.neighbors(v)))
    return graph_dict

"""with open('small_graph_new.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    count = 0
    for row in csv_reader:
        if count > 0:
            filename = row[0]
            g = g6_to_dict(filename)
            assignment = find_assignments(g)
            assignment_1 = assignment[0]
            check_sphere_embeddability(g, assignment_1, str(count), guess=False)
        count += 1"""

g = g6_to_dict("IpD?GUbV?")
assignment = find_assignments(g)
print (assignment[0])