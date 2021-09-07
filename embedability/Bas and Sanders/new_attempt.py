from bas_and_sanders_modification import *
from z3 import *

def cross(v,w):
    return (v[1]*w[2]-v[2]*w[1], v[2]*w[0]-v[0]*w[2], v[0]*w[1]-v[1]*w[0])

def dot(v,w):
    return (v+'[0]'+'*'+w+'[0]' + '+' + v+'[1]'+'*'+w+'[1]' + '+' + v +'[2]'+'*'+w+'[2]')

def nested_cross(x):
    if isinstance(x, tuple):
        return 'cross({},{})'.format(*map(nested_cross, x))
    str = 'v{}'.format(x)
    return str

def determine_embed(g, assignment, filename):
    f = open(filename + ".py", "w")
    f.write('from z3 import * \n')
    f.write('from new_attempt import * \n')
    f.write('import multiprocessing \n')
    f.write('def test_embed(): \n')
    f.write(' '*4 + 'f = open("embed_result.txt", "a") \n')
    f.write(' '*4+'s = Solver() \n')
    global v_dict
    v_dict = {}
    for i in range(len(assignment.var)):
        f.write(' '*4 + 'v'+str(i)+'c1 = Real("v'+ str(i) + 'c1")\n')
        f.write(' '*4 + 'v'+str(i)+'c2 = Real("v'+ str(i) + 'c2")\n')
        f.write(' '*4 + 'v'+str(i)+'c3 = Real("v'+ str(i) + 'c3")\n')
        f.write(' '*4 + 'v' + str(i) + '= (' + 'v' + str(i) + 'c1, v' + str(i) + 'c2, v' + str(i) + 'c3)\n')
        v_dict[i] = ('v'+str(i)+'c1', 'v'+str(i)+'c2', 'v'+str(i)+'c3') #{0: (v0c1, v0c2, v0c3)}
    f.write(' '*4 +'s.add('+v_dict[0][0] +'== 1) \n')
    f.write(' '*4 +'s.add('+v_dict[0][1] +'== 0) \n')
    f.write(' '*4 +'s.add('+v_dict[0][2] +'== 0) \n')
    f.write(' '*4 +'s.add('+v_dict[1][0] +'== 0) \n')
    f.write(' '*4 +'s.add('+v_dict[1][1] +'== 1) \n')
    f.write(' '*4 +'s.add('+v_dict[1][2] +'== 0) \n')
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
            f.write('s.add('+v_dict[i][0]+' == 0)')
            fvars.remove(v_dict[i][0])
        elif y in g[assignment.var[i]]:
            f.write('s.add('+v_dict[i][1]+' == 0)')
            fvars.remove(v_dict[i][1])
        elif z in g[assignment.var[i]]:
            f.write('s.add('+v_dict[i][2]+' == 0)')
            fvars.remove(v_dict[i][2])
    cross_product = nested_cross(assignment.eqs[0])
    f.write(' '*4 + 's.add(' + cross_product + '[0] == 0) \n')
    f.write(' '*4 + 's.add(' + cross_product + '[1] == 0) \n')
    f.write(' '*4 + 's.add(' + cross_product + '[2] == 0) \n')
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
            f.write(' '*4 + 's.add(Or(Not(' + cross_product + '[0] == 0), Not(' + cross_product + '[1] == 0), Not(' + cross_product + '[2] == 0)))\n')
    for dot_relation in assignment.ortho:
        v = nested_cross(dot_relation[0])
        w = nested_cross(dot_relation[1])
        f.write(' '*4 + 's.add(' + dot(v,w) + '== 0) \n')
    f.close()

"""graph_dict = g6_to_dict("IpD?GUbV?")
#print (graph_dict)
assignment = find_assignments(graph_dict)
assignment_1 = assignment[0]
determine_embed(graph_dict, assignment_1, "test")"""