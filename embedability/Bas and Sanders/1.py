from z3 import * 
import multiprocessing 

def cross(v,w):
    return (v[1]*w[2]-v[2]*w[1], v[2]*w[0]-v[0]*w[2], v[0]*w[1]-v[1]*w[0])

def non_zero(v):
    return 

def test_embed(): 
    f = open("embed_result.txt", "a") 
    s = Solver() 
    v0c1 = Real('v0c1')
    v0c2 = Real('v0c2')
    v0c3 = Real('v0c3')
    v0 = (v0c1, v0c2, v0c3)
    v1c1 = Real('v1c1')
    v1c2 = Real('v1c2')
    v1c3 = Real('v1c3')
    v1 = (v1c1, v1c2, v1c3)
    v2c1 = Real('v2c1')
    v2c2 = Real('v2c2')
    v2c3 = Real('v2c3')
    v2 = (v2c1, v2c2, v2c3)
    s.add(v0[0] == 1)
    s.add(v0[1] == 0)
    s.add(v0[2] == 0)
    s.add(v1[0] == 0)
    s.add(v1[1] == 1)
    s.add(v1[2] == 0)
    s.add(Or(Not(cross(v0, v2)[0] == 0), Not(cross(v0, v2)[1] == 0), Not(cross(v0, v2)[2] == 0)))
    print (cross(cross(v2, v1), v2))
    
    dir = __file__
    dir = dir.split('\\')
    row = int(dir[-1][:-3])
    f.write('  ' + str(row) + ', ' + str(s.check()) + '  ')
    print (s.check())

test_embed()
