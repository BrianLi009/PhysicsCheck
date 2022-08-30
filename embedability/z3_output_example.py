from helper import cross 
from z3 import * 
s = Solver()
v0c1 = Real("v0c1")
v0c2 = Real("v0c2")
v0c3 = Real("v0c3")
v0= (v0c1, v0c2, v0c3)
s.add(v0c3 >= 0)
v1c1 = Real("v1c1")
v1c2 = Real("v1c2")
v1c3 = Real("v1c3")
v1= (v1c1, v1c2, v1c3)
s.add(v1c3 >= 0)
v2c1 = Real("v2c1")
v2c2 = Real("v2c2")
v2c3 = Real("v2c3")
v2= (v2c1, v2c2, v2c3)
s.add(v2c3 >= 0)
v3c1 = Real("v3c1")
v3c2 = Real("v3c2")
v3c3 = Real("v3c3")
v3= (v3c1, v3c2, v3c3)
s.add(v3c3 >= 0)
ver0c1 = Real("ver0c1")
ver0c2 = Real("ver0c2")
ver0c3 = Real("ver0c3")
ver0= (ver0c1, ver0c2, ver0c3)
s.add(ver0c3 >= 0)
ver7c1 = Real("ver7c1")
ver7c2 = Real("ver7c2")
ver7c3 = Real("ver7c3")
ver7= (ver7c1, ver7c2, ver7c3)
s.add(ver7c3 >= 0)
ver1c1 = Real("ver1c1")
ver1c2 = Real("ver1c2")
ver1c3 = Real("ver1c3")
ver1= (ver1c1, ver1c2, ver1c3)
s.add(ver1c3 >= 0)
ver5c1 = Real("ver5c1")
ver5c2 = Real("ver5c2")
ver5c3 = Real("ver5c3")
ver5= (ver5c1, ver5c2, ver5c3)
s.add(ver5c3 >= 0)
ver9c1 = Real("ver9c1")
ver9c2 = Real("ver9c2")
ver9c3 = Real("ver9c3")
ver9= (ver9c1, ver9c2, ver9c3)
s.add(ver9c3 >= 0)
ver3c1 = Real("ver3c1")
ver3c2 = Real("ver3c2")
ver3c3 = Real("ver3c3")
ver3= (ver3c1, ver3c2, ver3c3)
s.add(ver3c3 >= 0)
ver6c1 = Real("ver6c1")
ver6c2 = Real("ver6c2")
ver6c3 = Real("ver6c3")
ver6= (ver6c1, ver6c2, ver6c3)
s.add(ver6c3 >= 0)
ver4c1 = Real("ver4c1")
ver4c2 = Real("ver4c2")
ver4c3 = Real("ver4c3")
ver4= (ver4c1, ver4c2, ver4c3)
s.add(ver4c3 >= 0)
ver8c1 = Real("ver8c1")
ver8c2 = Real("ver8c2")
ver8c3 = Real("ver8c3")
ver8= (ver8c1, ver8c2, ver8c3)
s.add(ver8c3 >= 0)
ver2c1 = Real("ver2c1")
ver2c2 = Real("ver2c2")
ver2c3 = Real("ver2c3")
ver2= (ver2c1, ver2c2, ver2c3)
s.add(ver2c3 >= 0)
s.add(ver0[0]==v0[0]) 
s.add(ver0[1]==v0[1]) 
s.add(ver0[2]==v0[2]) 
s.add(ver7[0]==v1[0]) 
s.add(ver7[1]==v1[1]) 
s.add(ver7[2]==v1[2]) 
s.add(ver1[0]==v2[0]) 
s.add(ver1[1]==v2[1]) 
s.add(ver1[2]==v2[2]) 
s.add(Or(ver5[0]==cross(v2,v1)[0],ver5[0]==cross(v1,v2)[0]))
s.add(Or(ver5[1]==cross(v2,v1)[1],ver5[1]==cross(v1,v2)[1]))
s.add(Or(ver5[2]==cross(v2,v1)[2],ver5[2]==cross(v1,v2)[2]))
s.add(Or(ver9[0]==cross(v2,v0)[0],ver9[0]==cross(v0,v2)[0]))
s.add(Or(ver9[1]==cross(v2,v0)[1],ver9[1]==cross(v0,v2)[1]))
s.add(Or(ver9[2]==cross(v2,v0)[2],ver9[2]==cross(v0,v2)[2]))
s.add(Or(ver3[0]==cross(cross(v2,v1),v1)[0],ver3[0]==cross(v1,cross(v2,v1))[0]))
s.add(Or(ver3[1]==cross(cross(v2,v1),v1)[1],ver3[1]==cross(v1,cross(v2,v1))[1]))
s.add(Or(ver3[2]==cross(cross(v2,v1),v1)[2],ver3[2]==cross(v1,cross(v2,v1))[2]))
s.add(Or(ver6[0]==cross(cross(v2,v0),v2)[0],ver6[0]==cross(v2,cross(v2,v0))[0]))
s.add(Or(ver6[1]==cross(cross(v2,v0),v2)[1],ver6[1]==cross(v2,cross(v2,v0))[1]))
s.add(Or(ver6[2]==cross(cross(v2,v0),v2)[2],ver6[2]==cross(v2,cross(v2,v0))[2]))
s.add(ver4[0]==v3[0]) 
s.add(ver4[1]==v3[1]) 
s.add(ver4[2]==v3[2]) 
s.add(Or(ver8[0]==cross(v3,v0)[0],ver8[0]==cross(v0,v3)[0]))
s.add(Or(ver8[1]==cross(v3,v0)[1],ver8[1]==cross(v0,v3)[1]))
s.add(Or(ver8[2]==cross(v3,v0)[2],ver8[2]==cross(v0,v3)[2]))
s.add(Or(ver2[0]==cross(cross(v3,v0),cross(cross(v2,v0),v2))[0],ver2[0]==cross(cross(cross(v2,v0),v2),cross(v3,v0))[0]))
s.add(Or(ver2[1]==cross(cross(v3,v0),cross(cross(v2,v0),v2))[1],ver2[1]==cross(cross(cross(v2,v0),v2),cross(v3,v0))[1]))
s.add(Or(ver2[2]==cross(cross(v3,v0),cross(cross(v2,v0),v2))[2],ver2[2]==cross(cross(cross(v2,v0),v2),cross(v3,v0))[2]))
s.add(v0c1 == 1) 
s.add(v0c2 == 0) 
s.add(v0c3 == 0) 
s.add(v1c1 == 0) 
s.add(v1c2 == 1) 
s.add(v1c3 == 0) 
s.add(Or(Not(cross(ver1,ver3)[0] == 0), Not(cross(ver1,ver3)[1] == 0), Not(cross(ver1,ver3)[2] == 0)))
s.add(Or(Not(cross(ver1,ver2)[0] == 0), Not(cross(ver1,ver2)[1] == 0), Not(cross(ver1,ver2)[2] == 0)))
s.add(Or(Not(cross(ver1,ver0)[0] == 0), Not(cross(ver1,ver0)[1] == 0), Not(cross(ver1,ver0)[2] == 0)))
s.add(Or(Not(cross(ver1,ver7)[0] == 0), Not(cross(ver1,ver7)[1] == 0), Not(cross(ver1,ver7)[2] == 0)))
s.add(Or(Not(cross(ver1,ver8)[0] == 0), Not(cross(ver1,ver8)[1] == 0), Not(cross(ver1,ver8)[2] == 0)))
s.add(Or(Not(cross(ver1,ver4)[0] == 0), Not(cross(ver1,ver4)[1] == 0), Not(cross(ver1,ver4)[2] == 0)))
s.add(Or(Not(cross(ver5,ver6)[0] == 0), Not(cross(ver5,ver6)[1] == 0), Not(cross(ver5,ver6)[2] == 0)))
s.add(Or(Not(cross(ver5,ver2)[0] == 0), Not(cross(ver5,ver2)[1] == 0), Not(cross(ver5,ver2)[2] == 0)))
s.add(Or(Not(cross(ver5,ver0)[0] == 0), Not(cross(ver5,ver0)[1] == 0), Not(cross(ver5,ver0)[2] == 0)))
s.add(Or(Not(cross(ver5,ver8)[0] == 0), Not(cross(ver5,ver8)[1] == 0), Not(cross(ver5,ver8)[2] == 0)))
s.add(Or(Not(cross(ver5,ver4)[0] == 0), Not(cross(ver5,ver4)[1] == 0), Not(cross(ver5,ver4)[2] == 0)))
s.add(Or(Not(cross(ver5,ver9)[0] == 0), Not(cross(ver5,ver9)[1] == 0), Not(cross(ver5,ver9)[2] == 0)))
s.add(Or(Not(cross(ver3,ver6)[0] == 0), Not(cross(ver3,ver6)[1] == 0), Not(cross(ver3,ver6)[2] == 0)))
s.add(Or(Not(cross(ver3,ver2)[0] == 0), Not(cross(ver3,ver2)[1] == 0), Not(cross(ver3,ver2)[2] == 0)))
s.add(Or(Not(cross(ver3,ver0)[0] == 0), Not(cross(ver3,ver0)[1] == 0), Not(cross(ver3,ver0)[2] == 0)))
s.add(Or(Not(cross(ver3,ver8)[0] == 0), Not(cross(ver3,ver8)[1] == 0), Not(cross(ver3,ver8)[2] == 0)))
s.add(Or(Not(cross(ver3,ver4)[0] == 0), Not(cross(ver3,ver4)[1] == 0), Not(cross(ver3,ver4)[2] == 0)))
s.add(Or(Not(cross(ver3,ver9)[0] == 0), Not(cross(ver3,ver9)[1] == 0), Not(cross(ver3,ver9)[2] == 0)))
s.add(Or(Not(cross(ver6,ver0)[0] == 0), Not(cross(ver6,ver0)[1] == 0), Not(cross(ver6,ver0)[2] == 0)))
s.add(Or(Not(cross(ver6,ver7)[0] == 0), Not(cross(ver6,ver7)[1] == 0), Not(cross(ver6,ver7)[2] == 0)))
s.add(Or(Not(cross(ver6,ver8)[0] == 0), Not(cross(ver6,ver8)[1] == 0), Not(cross(ver6,ver8)[2] == 0)))
s.add(Or(Not(cross(ver6,ver4)[0] == 0), Not(cross(ver6,ver4)[1] == 0), Not(cross(ver6,ver4)[2] == 0)))
s.add(Or(Not(cross(ver2,ver0)[0] == 0), Not(cross(ver2,ver0)[1] == 0), Not(cross(ver2,ver0)[2] == 0)))
s.add(Or(Not(cross(ver2,ver7)[0] == 0), Not(cross(ver2,ver7)[1] == 0), Not(cross(ver2,ver7)[2] == 0)))
s.add(Or(Not(cross(ver2,ver4)[0] == 0), Not(cross(ver2,ver4)[1] == 0), Not(cross(ver2,ver4)[2] == 0)))
s.add(Or(Not(cross(ver2,ver9)[0] == 0), Not(cross(ver2,ver9)[1] == 0), Not(cross(ver2,ver9)[2] == 0)))
s.add(Or(Not(cross(ver0,ver4)[0] == 0), Not(cross(ver0,ver4)[1] == 0), Not(cross(ver0,ver4)[2] == 0)))
s.add(Or(Not(cross(ver7,ver8)[0] == 0), Not(cross(ver7,ver8)[1] == 0), Not(cross(ver7,ver8)[2] == 0)))
s.add(Or(Not(cross(ver7,ver4)[0] == 0), Not(cross(ver7,ver4)[1] == 0), Not(cross(ver7,ver4)[2] == 0)))
s.add(Or(Not(cross(ver7,ver9)[0] == 0), Not(cross(ver7,ver9)[1] == 0), Not(cross(ver7,ver9)[2] == 0)))
s.add(Or(Not(cross(ver8,ver9)[0] == 0), Not(cross(ver8,ver9)[1] == 0), Not(cross(ver8,ver9)[2] == 0)))
s.add(Or(Not(cross(ver4,ver9)[0] == 0), Not(cross(ver4,ver9)[1] == 0), Not(cross(ver4,ver9)[2] == 0)))
s.set("timeout", 10000) 
result = s.check() 
if result == unknown: 
    index = int(index) + 1 
    main(g_sat, order, index, using_subgraph, output_unsat_f, output_sat_f) 
if result == unsat: 
    with open(output_unsat_f, "a+") as f: 
        f.write(g_sat + "\n") 
if result == sat: 
    with open(output_sat_f, "a+") as f: 
        f.write(g_sat + "\n") 
else: 
    print (result)
